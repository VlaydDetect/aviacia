"""Тесты SimInterface, бэкендов и генератора сценариев (без реального симулятора)."""

from dataclasses import fields

import pytest

from ismpu.control.channels import ControlsState
from ismpu.control.failures import FailureMode
from ismpu.envs.sim_interface import XPlaneBackend, ICSBackend, Telemetry
from ismpu.envs.scenario import Scenario, TouchdownSetup, SensorNoise
from ismpu.envs.scenario_generator import ScenarioGenerator
from ismpu.envs.weather import WeatherState, RunwayCondition, FrictionProfile, WEATHER_PRESETS
from ismpu.io.datarefs import (
    LATITUDE, LONGITUDE, GROUNDSPEED, TRUE_PSI, G_AXIL,
    FAIL_ENGINE, FAIL_REVERSER, FAILURE_ENUM_INOP, FAILURE_ENUM_OK,
    LEFT_BRAKE_RATIO, YOKE_HEADING_RATIO,
)


class FakeXPC:
    """Мок XPlaneConnectX: пишет всё в списки, subscribe эмулирует получение значений."""

    def __init__(self):
        self.sent = []
        self.ctrl = []
        self.posi = []
        self.paused = []
        self.current_dref_values = {}

    def sendDREF(self, dref, value):
        self.sent.append((dref, value))

    def sendCTRL(self, **kw):
        self.ctrl.append(kw)

    def sendPOSI(self, **kw):
        self.posi.append(kw)

    def sendCMND(self, cmd):
        self.sent.append((cmd, None))

    def pauseSIM(self, flag):
        self.paused.append(flag)

    def subscribeDREFs(self, subs, timeout=5.0):
        for dref, _freq in subs:
            self.current_dref_values.setdefault(dref, {"value": 0.0})

    def getDREF(self, dref):
        return 0.0

    def last(self, dref):
        for d, v in reversed(self.sent):
            if d == dref:
                return v
        raise KeyError(dref)


# --------------------------------------------------------------------------- #
# XPlaneBackend
# --------------------------------------------------------------------------- #

def test_xplane_reset_sequence_and_failure_injection():
    fake = FakeXPC()
    be = XPlaneBackend(xpc=fake, settle_s=0.0)
    scenario = Scenario(
        scenario_id="t", seed=1, control_preset="default",
        weather=WeatherState(runway_friction=RunwayCondition.WET.value),
        failures=(FailureMode.ENGINE_OUT_LEFT,),
        touchdown=TouchdownSetup(lateral_offset_m=3.0, heading_offset_deg=2.0),
    )
    telem = be.reset(scenario)

    assert fake.paused == [True, False]        # пауза на конфигурацию, затем снятие
    assert fake.posi, "должен быть телепорт (sendPOSI)"
    assert fake.ctrl, "должна быть конфигурация органов (sendCTRL)"
    assert fake.last(f"{FAIL_ENGINE}0") == pytest.approx(FAILURE_ENUM_INOP)  # левый двигатель отказал
    assert FailureMode.ENGINE_OUT_LEFT in be.active_failures
    assert telem.valid


def test_xplane_nws_failure_has_no_sim_dataref_but_is_tracked():
    fake = FakeXPC()
    be = XPlaneBackend(xpc=fake, settle_s=0.0)
    be.inject_failure(FailureMode.NWS_FAIL)
    assert FailureMode.NWS_FAIL in be.active_failures
    # У NWS нет failure-датарефа → в sent не должно быть failure-строк
    assert not any(str(d).startswith("sim/operation/failures") for d, _ in fake.sent)


def test_xplane_clear_failures_resets_injected_drefs():
    fake = FakeXPC()
    be = XPlaneBackend(xpc=fake, settle_s=0.0)
    be.inject_failure(FailureMode.REVERSE_RIGHT_FAIL)
    assert fake.last(f"{FAIL_REVERSER}1") == pytest.approx(FAILURE_ENUM_INOP)
    be.clear_failures()
    assert fake.last(f"{FAIL_REVERSER}1") == pytest.approx(FAILURE_ENUM_OK)
    assert be.active_failures == set()


def test_xplane_read_telemetry_maps_drefs():
    fake = FakeXPC()
    fake.current_dref_values = {
        LATITUDE: {"value": 55.97}, LONGITUDE: {"value": 37.39},
        GROUNDSPEED: {"value": 50.0}, TRUE_PSI: {"value": 75.0},
        G_AXIL: {"value": -0.3},
    }
    be = XPlaneBackend(xpc=fake, settle_s=0.0)
    telem = be.read_telemetry()
    assert telem.lat == pytest.approx(55.97)
    assert telem.groundspeed_ms == pytest.approx(50.0)
    assert telem.heading_true_deg == pytest.approx(75.0)
    assert telem.accel_long_g == pytest.approx(-0.3)
    assert telem.valid


def test_xplane_read_telemetry_invalid_when_missing():
    be = XPlaneBackend(xpc=FakeXPC(), settle_s=0.0)
    telem = be.read_telemetry()  # ничего не подписано → значения None
    assert telem.valid is False


def test_xplane_step_sends_control_commands():
    fake = FakeXPC()
    be = XPlaneBackend(xpc=fake, settle_s=0.0)
    cmd = ControlsState()
    cmd.cmd_brake_l = 0.5
    cmd.rudder_cmd = -0.2
    be.step(cmd)
    assert fake.last(LEFT_BRAKE_RATIO) == pytest.approx(0.5)
    assert fake.last(YOKE_HEADING_RATIO) == pytest.approx(-0.2)


def test_xplane_update_forwards_variable_friction():
    fake = FakeXPC()
    be = XPlaneBackend(xpc=fake, settle_s=0.0)
    be.apply_weather(WeatherState(friction_profile=FrictionProfile([(0.0, 0.0), (600.0, 11.0)])))
    n_before = sum(1 for d, _ in fake.sent if d == "sim/weather/region/runway_friction")
    be.update(700.0)  # перешли на лёд → одна дозапись сцепления
    n_after = sum(1 for d, _ in fake.sent if d == "sim/weather/region/runway_friction")
    assert n_after == n_before + 1


# --------------------------------------------------------------------------- #
# ICSBackend
# --------------------------------------------------------------------------- #

def _make_ics_inputs(**overrides):
    from ismpu.io.ics_connector import ICSInputs
    data = {f.name: 0 for f in fields(ICSInputs)}
    data.update(overrides)
    return ICSInputs.from_dict(data)


class FakeConnector:
    def __init__(self, inputs=None):
        self.inputs = inputs
        self.sent_outputs = []
        self.closed = False

    def receive_inputs(self, timeout=1.0):
        return self.inputs

    def send_outputs(self, outputs):
        self.sent_outputs.append(outputs)

    def close(self):
        self.closed = True


def test_ics_read_telemetry_maps_inputs():
    inp = _make_ics_inputs(Latitude=55.9, Longitude=37.4, GroundSpeed=42.0, TrueHeading=75.0,
                           BodyLongAccel=-0.25, WindSpeed=8.0, WindDirectionTrue=120.0)
    be = ICSBackend(connector=FakeConnector(inp))
    telem = be.read_telemetry()
    assert telem.lat == pytest.approx(55.9)
    assert telem.groundspeed_ms == pytest.approx(42.0)
    assert telem.accel_long_g == pytest.approx(-0.25)
    assert telem.wind_speed_ms == pytest.approx(8.0)
    assert telem.valid


def test_ics_read_telemetry_invalid_on_timeout():
    be = ICSBackend(connector=FakeConnector(None))
    assert be.read_telemetry().valid is False


def test_ics_step_maps_controls_to_outputs():
    from ismpu.io.ics_connector import ReverseEngineType, ControlModeState
    conn = FakeConnector(_make_ics_inputs(GroundSpeed=30.0))
    be = ICSBackend(connector=conn)
    cmd = ControlsState()
    cmd.cmd_brake_l, cmd.cmd_brake_r = 0.4, 0.6
    cmd.rudder_cmd = 0.1
    cmd.cmd_rev_l, cmd.cmd_rev_r = -0.7, 0.0
    be.step(cmd)
    out = conn.sent_outputs[-1]
    assert out.ControlMode == ControlModeState.Rollout
    assert out.BrakeLeftCmd == pytest.approx(0.4)
    assert out.RudderCmd == pytest.approx(0.1)
    assert out.ReverseLeftCmd == ReverseEngineType.Deploy   # cmd_rev_l < 0
    assert out.ReverseRightCmd == ReverseEngineType.Off     # cmd_rev_r == 0


def test_ics_environment_methods_are_noop():
    conn = FakeConnector(_make_ics_inputs())
    be = ICSBackend(connector=conn)
    be.apply_weather(WEATHER_PRESETS["icy"])
    be.inject_failure(FailureMode.NWS_FAIL)
    be.teleport_touchdown(TouchdownSetup())
    be.pause(True)
    assert conn.sent_outputs == []  # стенд владеет средой — ничего не отправили


# --------------------------------------------------------------------------- #
# Scenario сериализация
# --------------------------------------------------------------------------- #

def test_scenario_roundtrip_with_profile_and_failures():
    scenario = Scenario(
        scenario_id="s1", seed=7, control_preset="nws_fail",
        weather=WeatherState.from_crosswind(
            15.0, 5.0, gust_kts=8.0,
            friction_profile=FrictionProfile([(0.0, 0.0), (600.0, 11.0)]),
        ),
        failures=(FailureMode.NWS_FAIL, FailureMode.REVERSE_LEFT_FAIL),
        touchdown=TouchdownSetup(lateral_offset_m=2.0, heading_offset_deg=1.5),
        sensor_noise=SensorNoise(pos_sigma_m=0.3),
    )
    restored = Scenario.from_dict(scenario.to_dict())
    assert restored.to_dict() == scenario.to_dict()
    assert restored.failures == scenario.failures
    assert restored.weather.friction_profile.at(700.0) == pytest.approx(11.0)


# --------------------------------------------------------------------------- #
# ScenarioGenerator
# --------------------------------------------------------------------------- #

def test_generator_is_deterministic_for_same_seed():
    g1, g2 = ScenarioGenerator(seed=42), ScenarioGenerator(seed=42)
    a = [g1.sample().to_dict() for _ in range(5)]
    b = [g2.sample().to_dict() for _ in range(5)]
    assert a == b


def test_generator_zero_difficulty_has_no_failures():
    gen = ScenarioGenerator(seed=1)
    for _ in range(5):
        assert gen.sample(difficulty=0.0).failures == ()


def test_generator_high_difficulty_produces_failures():
    gen = ScenarioGenerator(seed=1)
    any_failure = any(gen.sample(difficulty=1.0).failures for _ in range(15))
    assert any_failure


def test_generator_samples_are_valid_and_serializable():
    gen = ScenarioGenerator(seed=3)
    for _ in range(10):
        s = gen.sample()
        assert 300.0 <= s.weather.visibility_m <= 16000.0
        assert Scenario.from_dict(s.to_dict()).to_dict() == s.to_dict()


def test_battery_covers_key_cases_and_roundtrips():
    battery = ScenarioGenerator(seed=0).battery()
    ids = {s.scenario_id for s in battery}
    assert {"nominal", "nws_fail", "icy", "crosswind"} <= ids
    for s in battery:
        assert Scenario.from_dict(s.to_dict()).to_dict() == s.to_dict()
