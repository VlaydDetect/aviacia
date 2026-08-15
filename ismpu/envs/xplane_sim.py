"""X-Plane 12 backend полного маршрута APPROACH → ROLLOUT → TAXI."""

from __future__ import annotations

import logging
import math
import random
import time
from pathlib import Path

from ismpu.config.aircraft_profiles import A330_300, AircraftProfile
from ismpu.config.approach import APPROACH_DEFAULT
from ismpu.config.constants import DT
from ismpu.config.envelope import measured_landing_flaps
from ismpu.config.ics import FlightPhase
from ismpu.config.segments import FlightSegment
from ismpu.config.scenarios import ApproachSetup, Scenario, SensorNoise, TouchdownSetup
from ismpu.config.runway_profiles import RunwayProfile, UUEE_06R, _destination
from ismpu.control.channels import ControlsState
from ismpu.control.failures import FailureMode
from ismpu.control.runway_tracker import RunwayTracker
from ismpu.envs.ics_sim import Telemetry, TelemetryExtensions
from ismpu.envs.sim_interface import (
    ApproachData, ShutdownReport, XPlaneDiagnostics, SimInterface, StartMode,
)
from ismpu.envs.weather import WeatherState
from ismpu.io import datarefs as dr
from ismpu.io.xplane_connector import XPlaneConnector
from ismpu.utils.converts import Converts

logger = logging.getLogger(__name__)

SUPPORTED_XPLANE_ROLLOUT_FAILURES = frozenset({
    FailureMode.ENGINE_OUT_LEFT,
    FailureMode.ENGINE_OUT_RIGHT,
    FailureMode.REVERSE_LEFT_FAIL,
    FailureMode.REVERSE_RIGHT_FAIL,
    FailureMode.NWS_FAIL,
})


class XPlaneSim(SimInterface):
    backend_name = "xplane"

    def __init__(
            self,
            connector: XPlaneConnector | None = None,
            *,
            ip: str = "127.0.0.1",
            port: int = 49000,
            xplane_root: str | Path | None = None,
            aircraft_profile: AircraftProfile = A330_300,
            runway_profile: RunwayProfile = UUEE_06R,
            stale_after_s: float = 0.35,
            subscription_timeout_s: float = 0.0,
            reload_each_reset: bool = True,
            ready_timeout_s: float = 25.0,
            ils_verify_timeout_s: float = 3.0,
            settle_s: float = 0.2,
    ) -> None:
        self.connector = connector or XPlaneConnector(ip=ip, port=port)
        self.profile = aircraft_profile
        self.profile.require_xplane()
        self.runway = runway_profile
        self.xplane_root = Path(xplane_root) if xplane_root is not None else None
        self.stale_after_s = stale_after_s
        self.reload_each_reset = reload_each_reset
        self.ready_timeout_s = ready_timeout_s
        self.ils_verify_timeout_s = ils_verify_timeout_s
        self.settle_s = settle_s
        self._tracker = RunwayTracker(runway_profile=runway_profile)
        self._active_failures: set[FailureMode] = set()
        self._ignored_failures: set[FailureMode] = set()
        self._engaged = False
        self._mode = "rollout"
        self._last_telemetry = Telemetry.invalid()
        self._weather = WeatherState()
        self._distance_m = 0.0
        self._last_friction = None
        self._closed = False
        self._shutdown_report: ShutdownReport | None = None
        self._ready = False
        self._missing_or_stale: tuple[str, ...] = ()
        self._sensor_noise = SensorNoise()
        self._scenario: Scenario | None = None
        self._entered_segment: FlightSegment | None = None
        self._random = random.Random(0)
        self.ils_station = None
        self.connector.subscribe(
            self.profile.subscriptions,
            frequency_hz=20,
            timeout_s=subscription_timeout_s,
        )

    @property
    def aircraft_profile_name(self) -> str:
        return self.profile.name

    @property
    def engaged(self) -> bool:
        return self._engaged

    @property
    def active_failures(self) -> frozenset[FailureMode]:
        return frozenset(self._active_failures)

    @property
    def ignored_failures(self) -> frozenset[FailureMode]:
        return frozenset(self._ignored_failures)

    @property
    def diagnostics(self) -> XPlaneDiagnostics:
        return XPlaneDiagnostics(
            ready=self._ready,
            ignored_failures=tuple(sorted(f.name for f in self._ignored_failures)),
            missing_or_stale_datarefs=self._missing_or_stale,
            last_flight_time=self.connector.value(dr.TOTAL_FLIGHT_TIME),
        )

    def reset(
            self,
            scenario: "Scenario | None" = None,
            *,
            start: StartMode | None = None,
    ) -> "Telemetry":
        if self._closed:
            raise RuntimeError("XPlaneSim уже закрыт")
        scenario = scenario or Scenario.from_preset("default")
        self._scenario = scenario
        self._entered_segment = None
        self._sensor_noise = scenario.sensor_noise
        self._random = random.Random(scenario.seed)
        mode = (start or "rollout").lower()
        if mode not in {"approach", "rollout", "taxi"}:
            raise ValueError("start должен быть 'approach', 'rollout' или 'taxi'")

        if self.reload_each_reset:
            self.connector.reload_aircraft()
            if hasattr(self.connector, "clear_samples"):
                self.connector.clear_samples()
            self.connector.subscribe(
                self.profile.subscriptions, frequency_hz=20, timeout_s=0.0)
            self._wait_until_ready()
        else:
            self.connector.fix_all_systems()

        self.connector.pause(True)
        self._capture_overrides()
        try:
            self.clear_failures()
            segment = (
                FlightSegment.APPROACH if mode == "approach"
                else FlightSegment.TAXI if mode == "taxi"
                else FlightSegment.ROLLOUT)
            conditions = scenario.conditions_for(segment)
            self.apply_weather(conditions.weather)
            if mode == "approach":
                self._configure_ils()
                self.teleport_approach(scenario.approach)
            else:
                self.teleport_rollout(scenario.touchdown)
            for failure in conditions.failures:
                self.inject_failure(failure)
            self._entered_segment = segment
            self._mode = mode
            self._distance_m = 0.0
            self.connector.pause(False)
            self._engaged = True
        except Exception:
            self._release_overrides()
            self._engaged = False
            self.connector.pause(False)
            raise
        if self.settle_s > 0:
            time.sleep(self.settle_s)
        return self.read_telemetry()

    def enter_segment(
        self,
        scenario: Scenario,
        segment: FlightSegment,
        telemetry: Telemetry | None = None,
    ) -> None:
        """Применить только дельту условий при переходе между участками."""
        del telemetry
        target = scenario.conditions_for(segment)
        current = self._active_failures | self._ignored_failures
        for failure in current - target.failures:
            self.clear_failure(failure)
        for failure in target.failures - current:
            self.inject_failure(failure)
        if target.weather != self._weather:
            self.apply_weather(target.weather)
        self._scenario = scenario
        self._entered_segment = segment

    def warm_up(self, timeout_s: float = 10.0, dt: float = DT) -> bool:
        del timeout_s, dt
        if not self._engaged:
            self._capture_overrides()
            self._engaged = True
        return True

    def read_telemetry(self) -> Telemetry:
        values = self.connector.snapshot(max_age_s=self.stale_after_s)
        required = (dr.LATITUDE, dr.LONGITUDE, dr.GROUNDSPEED, dr.TRUE_PSI)
        if any(name not in values or not math.isfinite(values[name]) for name in required):
            self._last_telemetry = Telemetry.invalid()
            return self._last_telemetry
        if (
                self._sensor_noise.dropout_prob > 0.0
                and self._random.random() < self._sensor_noise.dropout_prob
        ):
            self._last_telemetry = Telemetry.invalid()
            return self._last_telemetry

        def value(name: str, fallback: float = 0.0) -> float:
            raw = values.get(name, fallback)
            return float(raw) if math.isfinite(raw) else float(fallback)

        lat = value(dr.LATITUDE)
        lon = value(dr.LONGITUDE)
        if self._sensor_noise.pos_sigma_m > 0.0:
            displacement = abs(self._random.gauss(
                0.0, self._sensor_noise.pos_sigma_m))
            bearing = self._random.uniform(0.0, 360.0)
            lat, lon = _destination(lat, lon, bearing, displacement)
        groundspeed = max(
            0.0,
            value(dr.GROUNDSPEED)
            + self._random.gauss(0.0, self._sensor_noise.speed_sigma_ms),
        )
        heading_noise = self._random.gauss(
            0.0, self._sensor_noise.heading_sigma_deg)
        true_heading = (value(dr.TRUE_PSI) + heading_noise) % 360.0
        magnetic_available = dr.MAG_PSI in values and dr.MAG_TRACK in values
        mag_heading = (
            (value(dr.MAG_PSI) + heading_noise) % 360.0
            if magnetic_available else math.nan)
        mag_track = (
            (value(dr.MAG_TRACK) + heading_noise) % 360.0
            if magnetic_available else math.nan)
        mag_variation = value(dr.MAGNETIC_VARIATION)
        true_track = (
            (mag_track + mag_variation) % 360.0
            if magnetic_available else true_heading)
        runway_mag = (self.runway.heading_true_deg - mag_variation) % 360.0
        radio_alt = max(0.0, value(dr.RADIO_ALT_FT, value(dr.Y_AGL) / Converts.FT_TO_M))
        ias = max(0.0, value(dr.IAS_KTS, groundspeed / Converts.KTS_TO_MS))
        tas = max(0.0, value(dr.TAS_KTS, ias))
        vertical_speed = value(dr.VVI_FPM, value(dr.LOCAL_VY) / Converts.FTM_TO_MS)
        flap_angle = max(0.0, value(dr.FLAP_RATIO)) * self.profile.flap_full_deg
        gear = tuple(value(name) >= 0.5 for name in self.profile.gear_refs)
        nose, left_main, right_main = gear
        ils_valid = bool(value(dr.NAV1_GS_FLAG, 1.0) == 0.0
                         and value(dr.NAV1_FROM_TO, 0.0) != 0.0)
        left_throttle, right_throttle = (
            value(name) * 40.0 for name in self.profile.throttle_feedback_refs)
        loc_ddm = value(dr.NAV1_HDEF_DOTS) * APPROACH_DEFAULT.loc_full_scale_ddm
        gs_ddm = value(dr.NAV1_VDEF_DOTS) * APPROACH_DEFAULT.gs_full_scale_ddm

        approach = ApproachData(
            RadioAltitude=radio_alt,
            IndicatedAirspeed=ias,
            TrueAirspeed=tas,
            GroundSpeed=groundspeed / Converts.KTS_TO_MS,
            VerticalSpeed=vertical_speed,
            PitchAngle=value(dr.TRUE_THETA),
            RollAngle=value(dr.TRUE_PHI),
            TrkAngleMagnetic=mag_track,
            MagneticHeading=mag_heading,
            RunwayHeading=runway_mag,
            LocDeviation=loc_ddm,
            GSDeviation=gs_ddm,
            FlapsAngle=flap_angle,
            LeftThrottleAngle=left_throttle,
            RightThrottleAngle=right_throttle,
            BodyPitchRate=math.degrees(value(dr.QRAD)),
            BodyRollRate=math.degrees(value(dr.PRAD)),
            BodyYawRate=math.degrees(value(dr.RRAD)),
            BodyNormAccel=value(dr.G_NRML),
            AirfieldTemp=self._weather.temperature_c,
        )
        lateral = self._tracker.get_cross_track_error(lat, lon)
        wind_speed = value(dr.WX_AC_WIND_SPEED_MSC, 0.0)
        wind_dir = value(dr.WX_AC_WIND_DIR_DEGT, self._weather.wind_dir_from_degt)
        on_all_gear = nose and left_main and right_main
        main_contact = left_main or right_main
        self._last_telemetry = Telemetry(
            lat=lat,
            lon=lon,
            groundspeed_ms=groundspeed,
            heading_true_deg=true_heading,
            heading_magnetic_deg=(mag_heading if magnetic_available else None),
            track_magnetic_deg=(mag_track if magnetic_available else None),
            track_true_deg=true_track,
            runway_heading_true_deg=self.runway.heading_true_deg,
            runway_heading_magnetic_deg=runway_mag,
            pitch_deg=approach.PitchAngle,
            roll_deg=approach.RollAngle,
            elevation_m=value(dr.ELEVATION),
            agl_m=radio_alt * Converts.FT_TO_M,
            vy_ms=vertical_speed * Converts.FTM_TO_MS,
            p_rad=value(dr.PRAD),
            q_rad=value(dr.QRAD),
            r_rad=value(dr.RRAD),
            accel_long_g=value(dr.G_AXIL),
            accel_norm_g=value(dr.G_NRML),
            accel_side_g=value(dr.G_SIDE),
            wind_speed_ms=wind_speed,
            wind_dir_from_deg=wind_dir,
            runway_profile=self.runway,
            approach_inputs=approach,
            extensions=TelemetryExtensions(
                ias_ms=ias * Converts.KTS_TO_MS,
                radio_altitude_ft=radio_alt,
                ils_valid=ils_valid,
                landing_flaps=measured_landing_flaps(flap_angle),
                main_gear_contact=main_contact,
                runway_heading_true_deg=self.runway.heading_true_deg,
                runway_heading_magnetic_deg=runway_mag,
                runway_length_m=self.runway.length_m,
                runway_width_m=self.runway.width_m,
                lateral_deviation_m=lateral,
                weight_on_wheels=on_all_gear,
                flight_phase=(
                    FlightPhase.LAND_RUN if main_contact
                    else FlightPhase.APPROACH_ABOVE_30M),
                faults=frozenset(self._active_failures),
                weather=self._weather,
                agent_is_active=self._engaged,
            ),
            ias_ms_direct=ias * Converts.KTS_TO_MS,
            radio_altitude_ft_direct=radio_alt,
            ils_valid_direct=ils_valid,
            landing_flaps_direct=measured_landing_flaps(flap_angle),
            main_gear_contact_direct=main_contact,
            runway_heading_deg_direct=runway_mag,
            runway_length_m_direct=self.runway.length_m,
            runway_width_m_direct=self.runway.width_m,
            lateral_deviation_m_direct=lateral,
            weight_on_wheels_direct=on_all_gear,
            flight_phase_direct=(
                int(FlightPhase.LAND_RUN) if main_contact else int(FlightPhase.APPROACH_ABOVE_30M)),
            faults_direct=frozenset(self._active_failures),
            weather_direct=self._weather,
            agent_is_active_direct=self._engaged,
        )
        return self._last_telemetry

    def step(self, command: ControlsState) -> Telemetry:
        if not self._engaged:
            return self.read_telemetry()
        commands = (
            self.profile.airborne_commands(command)
            if self._mode == "approach"
            else self.profile.ground_commands(command)
        )
        print(commands)
        for name, value in commands.items():
            self.connector.send_dref(name, value)
        if self._mode != "approach":
            self._distance_m += max(0.0, self._last_telemetry.groundspeed_ms) * DT
            self.update(self._distance_m)
        return self.read_telemetry()

    def request_rollout(self) -> None:
        self._mode = "rollout"

    def request_landing(self) -> bool:
        # В X-Plane Landing остаётся фазой того же воздушного набора DataRef-команд.
        return self._mode == "approach"

    def request_taxi(self) -> bool:
        self._mode = "taxi"
        return True

    def pause(self, flag: bool) -> None:
        self.connector.pause(flag)

    def teleport_rollout(self, setup: TouchdownSetup) -> None:
        lat, lon = self._offset_point(
            self.runway.threshold_lat, self.runway.threshold_lon, setup.lateral_offset_m)
        heading = self.runway.heading_true_deg + setup.heading_offset_deg
        self._set_position_and_velocity(
            lat=lat,
            lon=lon,
            elevation_m=self.runway.elevation_m + setup.elevation_m,
            heading_deg=heading,
            pitch_deg=setup.pitch_deg,
            speed_knots=setup.speed_knots,
            vertical_speed_fpm=-abs(setup.descent_rate_fpm),
            flap_ratio=1.0,
            speedbrakes_ratio=-0.5
        )

        self.connector.sendCMND("sim/view/chase")
        self.connector.sendCMND("sim/general/up_fast")
        self.connector.sendCMND("sim/general/up_fast")
        self.connector.sendCMND("sim/general/up_fast")
        self.connector.sendCMND("sim/general/up_fast")
        self.connector.sendCMND("sim/general/up_fast")
        self.connector.sendCMND("sim/general/up_fast")
        self.connector.sendCMND("sim/general/up_fast")
        self.connector.sendCMND("sim/general/up_fast")
        self.connector.sendCMND("sim/general/up_fast")

    def teleport_approach(self, setup: ApproachSetup) -> None:
        altitude_m = setup.radio_altitude_ft * Converts.FT_TO_M
        actual_glideslope_deg = (
                setup.glideslope_deg
                + setup.gs_offset_dots * APPROACH_DEFAULT.gs_full_scale_deg
        )
        distance_m = altitude_m / math.tan(math.radians(actual_glideslope_deg))
        lat, lon = self.runway.point_on_centerline(distance_m)
        loc_offset_m = distance_m * math.tan(math.radians(
            setup.loc_offset_dots * APPROACH_DEFAULT.loc_full_scale_deg))
        lat, lon = self._offset_point(
            lat, lon, setup.lateral_offset_m + loc_offset_m)
        heading = self.runway.heading_true_deg + setup.heading_offset_deg
        self._set_position_and_velocity(
            lat=lat,
            lon=lon,
            elevation_m=self.runway.elevation_m + altitude_m,
            heading_deg=heading,
            pitch_deg=2.5,
            speed_knots=setup.ias_knots,
            vertical_speed_fpm=setup.vertical_speed_fpm,
            flap_ratio=setup.flap_ratio,
            speedbrakes_ratio=0.0
        )

    def _set_position_and_velocity(
            self,
            *,
            lat: float,
            lon: float,
            elevation_m: float,
            heading_deg: float,
            pitch_deg: float,
            speed_knots: float,
            vertical_speed_fpm: float,
            flap_ratio: float,
            speedbrakes_ratio: float,
    ) -> None:
        self.connector.send_position(
            lat=lat,
            lon=lon,
            elevation_m=elevation_m,
            roll_deg=0.0,
            pitch_deg=pitch_deg,
            heading_true_deg=heading_deg,
        )
        self.connector.sendCTRL(
            lat_control=0.0,
            lon_control=0.0,
            rudder_control=0.0,
            throttle=0.0,
            gear=1,
            flaps=flap_ratio,
            speedbrakes=speedbrakes_ratio,
            park_brake=0.0,
        )
        heading_rad = math.radians(heading_deg)
        speed_ms = speed_knots * Converts.KTS_TO_MS
        self.connector.send_dref(dr.LOCAL_VX, speed_ms * math.sin(heading_rad))
        self.connector.send_dref(dr.LOCAL_VY, vertical_speed_fpm * Converts.FTM_TO_MS)
        self.connector.send_dref(dr.LOCAL_VZ, -speed_ms * math.cos(heading_rad))
        for ref in (dr.POS_P, dr.POS_Q, dr.POS_R):
            self.connector.send_dref(ref, 0.0)

    def _offset_point(self, lat: float, lon: float, offset_m: float) -> tuple[float, float]:
        if not offset_m:
            return lat, lon
        bearing = self.runway.heading_true_deg + (90.0 if offset_m > 0 else -90.0)
        return _destination(lat, lon, bearing, abs(offset_m))

    def _configure_ils(self) -> None:
        if self.xplane_root is None:
            raise ValueError("для старта approach требуется --xplane-root с earth_nav.dat")
        station = self.runway.discover_ils(self.xplane_root)
        requested = station.frequency_hz / 10_000
        self.connector.send_dref(dr.NAV1_FREQ_HZ, requested)
        deadline = time.monotonic() + self.ils_verify_timeout_s
        while self.ils_verify_timeout_s > 0 and time.monotonic() < deadline:
            actual = self.connector.value(dr.NAV1_FREQ_HZ, max_age_s=self.stale_after_s)
            if actual is not None and abs(actual - requested) < 0.5:
                break
            time.sleep(0.02)
        else:
            if self.ils_verify_timeout_s > 0:
                raise RuntimeError(
                    f"X-Plane не подтвердил NAV1 {requested:.0f} (ILS "
                    f"{station.airport} {station.runway})")
        self.ils_station = station

    def apply_weather(self, weather: WeatherState) -> None:
        self._weather = weather
        self.connector.send_dref(dr.WX_CHANGE_MODE, 3.0)
        speed_ms = weather.wind_speed_kts * Converts.KTS_TO_MS
        gust_ms = weather.gust_kts * Converts.KTS_TO_MS
        for layer in range(13):
            self.connector.send_dref(f"{dr.WX_WIND_SPEED_MSC}[{layer}]", speed_ms)
            self.connector.send_dref(f"{dr.WX_WIND_DIR_DEGT}[{layer}]",
                                     weather.wind_dir_from_degt)
            self.connector.send_dref(f"{dr.WX_SHEAR_SPEED_MSC}[{layer}]", gust_ms)
            self.connector.send_dref(f"{dr.WX_TURBULENCE}[{layer}]", weather.turbulence)
        friction = (
            weather.friction_profile.at(0.0)
            if weather.friction_profile else weather.runway_friction)
        self.connector.send_dref(dr.WX_RUNWAY_FRICTION, friction)
        self._last_friction = friction
        self.connector.send_dref(dr.WX_VARIABILITY_PCT, weather.variability_pct)
        self.connector.send_dref(dr.WX_RAIN_PERCENT, weather.rain_pct)
        self.connector.send_dref(dr.WX_VISIBILITY_SM, weather.visibility_m / 1609.344)
        self.connector.send_dref(dr.WX_SEALEVEL_TEMP_C, weather.temperature_c)
        self.connector.send_dref(dr.WX_UPDATE_IMMEDIATELY, 1.0)

    def update(self, distance_m: float) -> None:
        profile = self._weather.friction_profile
        if profile is None:
            return
        friction = profile.at(distance_m)
        if self._last_friction is None or abs(friction - self._last_friction) > 1e-9:
            self.connector.send_dref(dr.WX_RUNWAY_FRICTION, friction)
            self._last_friction = friction

    def inject_failure(self, mode: FailureMode) -> None:
        if mode is FailureMode.NONE:
            return
        if mode not in SUPPORTED_XPLANE_ROLLOUT_FAILURES:
            self._ignored_failures.add(mode)
            logger.info("[X-Plane] отказ %s проигнорирован для rollout", mode.name)
            return
        left, right = self.profile.engine_indices
        mapping = {
            FailureMode.ENGINE_OUT_LEFT: f"{dr.FAIL_ENGINE}[{left}]",
            FailureMode.ENGINE_OUT_RIGHT: f"{dr.FAIL_ENGINE}[{right}]",
            FailureMode.REVERSE_LEFT_FAIL: f"{dr.FAIL_REVERSER}[{left}]",
            FailureMode.REVERSE_RIGHT_FAIL: f"{dr.FAIL_REVERSER}[{right}]",
        }
        dataref = mapping.get(mode)
        if dataref is not None:
            self.connector.send_dref(dataref, dr.FAILURE_ENUM_INOP)
        # NWS не имеет переносимого failure DataRef и моделируется командным
        # уровнем: опубликованный отказ обнуляет steering_eff в FailureManager.
        self._active_failures.add(mode)

    def clear_failure(self, mode: FailureMode) -> None:
        """Снять один отказ, не переинициализируя отказ, продолжающийся на новом участке."""
        left, right = self.profile.engine_indices
        mapping = {
            FailureMode.ENGINE_OUT_LEFT: f"{dr.FAIL_ENGINE}[{left}]",
            FailureMode.ENGINE_OUT_RIGHT: f"{dr.FAIL_ENGINE}[{right}]",
            FailureMode.REVERSE_LEFT_FAIL: f"{dr.FAIL_REVERSER}[{left}]",
            FailureMode.REVERSE_RIGHT_FAIL: f"{dr.FAIL_REVERSER}[{right}]",
        }
        dataref = mapping.get(mode)
        if dataref is not None:
            self.connector.send_dref(dataref, dr.FAILURE_ENUM_OK)
        self._active_failures.discard(mode)
        self._ignored_failures.discard(mode)

    def clear_failures(self) -> None:
        for index in self.profile.engine_indices:
            self.connector.send_dref(f"{dr.FAIL_ENGINE}[{index}]", dr.FAILURE_ENUM_OK)
            self.connector.send_dref(f"{dr.FAIL_REVERSER}[{index}]", dr.FAILURE_ENUM_OK)
        self._active_failures.clear()
        self._ignored_failures.clear()

    def _capture_overrides(self) -> None:
        for name in (
                dr.OVERRIDE_ROLL, dr.OVERRIDE_PITCH, dr.OVERRIDE_HEADING,
                dr.OVERRIDE_THROTTLES, dr.OVERRIDE_TOE_BRAKES,
        ):
            self.connector.send_dref(name, 1.0)

    def _release_overrides(self) -> None:
        for name in (
                dr.OVERRIDE_ROLL, dr.OVERRIDE_PITCH, dr.OVERRIDE_HEADING,
                dr.OVERRIDE_THROTTLES, dr.OVERRIDE_TOE_BRAKES,
        ):
            self.connector.send_dref(name, 0.0)

    def deactivate(self, frames: int = 10, dt: float = DT) -> None:
        neutral = ControlsState()
        for _ in range(max(1, frames)):
            for name, value in {
                **self.profile.airborne_commands(neutral),
                **self.profile.ground_commands(neutral),
            }.items():
                self.connector.send_dref(name, value)
            if dt > 0:
                time.sleep(dt)
        self._release_overrides()
        self._engaged = False

    def __enter__(self) -> "XPlaneSim":
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        self.shutdown()
        return False

    def shutdown(self, frames: int = 10, dt: float = DT) -> ShutdownReport:
        if self._shutdown_report is not None:
            return self._shutdown_report
        actions: list[str] = []
        errors: list[str] = []
        try:
            self.deactivate(frames=frames, dt=dt)
            actions.extend(("commands_neutralized", "overrides_released"))
        except Exception as exc:
            errors.append(f"deactivate: {type(exc).__name__}: {exc}")
            logger.exception("[X-Plane] ошибка снятия управления")
            try:
                self._release_overrides()
                actions.append("overrides_released")
            except Exception as release_exc:
                errors.append(
                    f"release_overrides: {type(release_exc).__name__}: {release_exc}")
        try:
            self.connector.close()
            actions.append("transport_closed")
        except Exception as exc:
            errors.append(f"transport_close: {type(exc).__name__}: {exc}")
            logger.exception("[X-Plane] ошибка закрытия транспорта")
        self._engaged = False
        self._closed = True
        self._shutdown_report = ShutdownReport(
            backend=self.backend_name, actions=tuple(actions), errors=tuple(errors))
        return self._shutdown_report

    def close(self) -> None:
        self.shutdown(frames=1, dt=0.0)

    def _wait_until_ready(self) -> None:
        if self.ready_timeout_s <= 0:
            self._ready = True
            return
        deadline = time.monotonic() + self.ready_timeout_s
        previous = None
        increasing = 0
        self.connector.pause(False)
        while time.monotonic() < deadline:
            current = self.connector.value(dr.TOTAL_FLIGHT_TIME, max_age_s=self.stale_after_s)
            if current is not None and previous is not None and current > previous:
                increasing += 1
                if increasing >= 3:
                    self._ready = True
                    self._missing_or_stale = ()
                    return
            else:
                increasing = 0
            previous = current
            time.sleep(0.1)
        missing = [
            name for name in self.profile.subscriptions
            if self.connector.value(name, max_age_s=self.stale_after_s) is None
        ]
        self._ready = False
        self._missing_or_stale = tuple(missing)
        raise TimeoutError(
            f"X-Plane не подтвердил готовность за {self.ready_timeout_s:.1f} с; "
            f"last_flight_time={previous!r}; missing_or_stale={missing}")
