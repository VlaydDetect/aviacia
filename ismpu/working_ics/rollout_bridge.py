from __future__ import annotations

import socket
import time
from dataclasses import asdict

from ismpu.config.scenarios import compose_matrix_scenario
from ismpu.config.segments import FlightSegment
from ismpu.control.system import ControllingSystem
from ismpu.envs.ics_sim import ICSSim, Telemetry
from ismpu.io.ics_connector import ICSBenchConnector, ICSInputs as BenchInputs

from .protocol import ICSInputs


class VlaydRolloutBridge:
    """Hand the validated airborne session to Vlayd's existing rollout loop.

    The bridge deliberately reuses the already-bound UDP socket.  It also
    mirrors approach telemetry into Vlayd's engagement state so touchdown is a
    direct ``Approach -> Rollout`` transition, with no intermediate ``Off``.
    """

    def __init__(
        self,
        sock: socket.socket,
        sender: tuple[str, int],
        *,
        listen_ip: str,
        listen_port: int,
        aircraft_profile: str = "mc21",
    ) -> None:
        connector = ICSBenchConnector(listen_ip, listen_port, sock=sock)
        connector.send_addr = sender
        self.sim = ICSSim(
            connector=connector,
            aircraft_profile=aircraft_profile,
            validate_conditions=False,
        )
        # The working controller has already completed the real airborne
        # handshake.  Mirror that state instead of starting a second dwell.
        self.sim.engagement.request_approach()
        self.controller: ControllingSystem | None = None

    @staticmethod
    def _telemetry(state: ICSInputs) -> Telemetry:
        return Telemetry.from_ics(BenchInputs.from_dict(asdict(state)))

    def observe(
        self,
        state: ICSInputs,
        sender: tuple[str, int],
    ) -> Telemetry:
        """Keep Vlayd's engagement latch synchronized during the approach."""
        self.sim.connector.send_addr = sender
        telemetry = self._telemetry(state)
        self.sim._last_telemetry = telemetry
        self.sim.engagement.step(self.sim._engagement_inputs(telemetry))
        return telemetry

    def run(
        self,
        state: ICSInputs,
        sender: tuple[str, int],
        *,
        timeout_s: float,
        rate_hz: float,
    ) -> bool:
        """Run Vlayd's rollout until taxi speed, then send its taxi handoff."""
        telemetry = self.observe(state, sender)
        scenario = compose_matrix_scenario(
            scenario_id="working_approach_with_b_1_1_rollout",
            approach_case="А.1.2",
            ground_case="Б.1.1",
        )
        controller = ControllingSystem(sim=self.sim)
        controller.bind_scenario(scenario, "mc21")
        controller.activate_segment(FlightSegment.ROLLOUT, telemetry)
        controller.segment = FlightSegment.ROLLOUT
        controller.last_telemetry = telemetry
        self.controller = controller

        was_engaged = self.sim.engaged
        self.sim.request_rollout()
        print(
            "handoff to Vlayd rollout: Approach -> Rollout "
            f"engaged={int(was_engaged)} gs={state.GroundSpeed:.1f}kt"
        )

        deadline = time.monotonic() + timeout_s
        previous = time.monotonic()
        next_tick = previous
        first_tick = True
        disengaged_since: float | None = None
        while time.monotonic() < deadline:
            now = time.monotonic()
            if now < next_tick:
                time.sleep(next_tick - now)
                now = time.monotonic()
            dt_s = max(1e-3, min(0.25, now - previous))
            previous = now
            next_tick = now + 1.0 / rate_hz

            finished = controller.control_step(
                dt_s,
                telemetry=telemetry if first_tick else None,
                send=True,
            )
            first_tick = False
            if finished:
                taxi_sent = controller.hand_over_to_taxi()
                print(
                    "Vlayd rollout complete; "
                    f"Taxi handoff sent={int(taxi_sent)}"
                )
                return True

            if self.sim.engaged:
                disengaged_since = None
            elif disengaged_since is None:
                disengaged_since = time.monotonic()
            elif time.monotonic() - disengaged_since >= 3.0:
                print(
                    "Vlayd rollout lost ICS engagement for 3s: "
                    f"{self.sim.engagement.as_dict()}"
                )
                return False

        print(f"Vlayd rollout timeout after {timeout_s:g}s")
        return False
