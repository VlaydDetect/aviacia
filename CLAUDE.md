# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

An autonomous landing-rollout controller for an aircraft (A330-class) in the **X-Plane 12** flight
simulator. On touchdown it holds the runway centerline and decelerates from ~200 kts to taxi speed
along a reference velocity curve, while modeling and compensating for equipment failures (engine out,
reverser fail, nose-wheel-steering fail, etc.). Target scenario is Sheremetyevo (UUEE), runway 06R.
Code comments and console output are in Russian.

This is the R&D project **ИСМПУ** (shifr `Интеграл-КБО-МС-ГосНИИАС-ИСМПУ-2026`, due 2026-07-28). The
work is moving from the current classical-PID prototype toward a **hybrid neural controller**: the
classical PID loop stays as the plant, and a neural PIDNN actor (trained with PPO) generates
*multiplicative corrections* to the PID gains plus channel-influence weights, guarded by a
deterministic **Shield** and, later, an optional physics-informed **PINN observer**.

## Planning & reference documents

Read these before making architectural changes — they define the target design and the acceptance criteria:

- **[`implementation_plan.md`](implementation_plan.md)** — the phased plan for the neural-control rework:
  target package layout (`ismpu/`), the full Observation/Action spaces, the `SimInterface` abstraction
  (X-Plane for training ↔ ICS bench for deployment), Shield, PPO + multi-component loss, and the observer
  seams. **This is the source of truth for where the project is going**; the notebook is where it is today.
- **[`PIDNN.mmd`](PIDNN.mmd)** — Mermaid diagram of the full architecture (scenario generator, sim env,
  PINN observer, PIDNN multi-head actor, Shield, classical control, PPO loop, deployment). Data-flow reference.
- **[`ТЗ_Интеграл-КБО-МС_ИСМПУ_итог_ф.pdf`](ТЗ_Интеграл-КБО-МС_ИСМПУ_итог_ф.pdf)** — the customer's
  technical spec (ТЗ). Section 5 holds the hard acceptance numbers that become reward gates and eval
  criteria: centerline ±3 m on rollout / ±1 m taxi, heading ±5° under NWS or thrust/reverse fault down to
  <30 kts, μ/crosswind/aquaplaning diagnostics, and delivery as an `.exe` over the agreed UDP protocol (ПИВ).
- **`DataRefs.txt`** — the master X-Plane 12 DataRef dictionary (tab-separated: name, type, writable, unit,
  description; 600 KB). Grep it to find valid DataRefs; note the `writable` column before trying to send one.

## Environment & running

- Dependencies are in `pyproject.toml` / `requirements.txt` (also live in the committed-out `.venv/`,
  Python 3.14): `numpy`, `pandas`, `termcolor`, `pytest`, plus Jupyter (`ipykernel`). `torch`/`gymnasium`
  are declared as the optional `rl` extra for the upcoming neural work but not yet used.
- Activate the venv before running: `.venv\Scripts\Activate.ps1` (PowerShell).
- **Run the controller:** `python -m ismpu.runtime.loop` (or the thin `main.ipynb`, which just imports
  from `ismpu` and calls `run(...)`). Requires a running X-Plane 12 on `127.0.0.1:49000`. The 20 Hz loop
  runs until `KeyboardInterrupt`, which resets all controls. Pick a scenario via
  `ismpu.config.scenarios.SCENARIOS["nws_fail" | "default" | ...]`.
- **Tests:** `python -m pytest` (from repo root; a root `conftest.py` puts `ismpu` on the path). These are
  simulator-free — they check PID numerics, tracker geodesy, reference-speed curves, and one full
  `control_step` through a mock connector. Full-trajectory parity with the old notebook still needs X-Plane
  and is a manual check.
- `main.py` and `env.py` at the repo root are **superseded, untracked experiments** — ignore them; the
  package is the source of truth. They can be deleted.

## Package layout (Phase 0 restructure — see `implementation_plan.md`)

Logic that used to live in `main.ipynb` now sits in the `ismpu/` package (moved 1:1, no behavior change
except: `PIDController` debug output went from `cprint` to `logging.debug`, silent by default; and
`ControllingSystem.setup` wires channels to `self.xpc` instead of a module global):

- `ismpu/io/` — transport: `xplane_connector.py` (`XPlaneConnectX`), `ics_connector.py`, `datarefs.py`
  (named DataRef constants — use these, not string literals).
- `ismpu/control/` — the classical loop: `pid.py`, `runway_tracker.py`, `trajectory.py`, `channels.py`
  (`ControlsState` + the two channels), `system.py` (`ControllingSystem`), `failures.py`.
- `ismpu/config/` — `runway.py` (UUEE 06R geometry — edit here to change runway), `constants.py`,
  `scenarios.py` (PID presets per scenario, extracted from the notebook cells), `requirements.py`
  (the ТЗ acceptance thresholds), `aircraft.py`.
- `ismpu/runtime/` — `setup.py` (`setup_touchdown_uuee`) and `loop.py` (the 20 Hz loop + `main()`).
- `ismpu/utils/converts.py` — `Converts` (unit conversions).
- `ismpu/envs/` — environment layer (Phase 1): `weather.py`, `sim_interface.py`, `scenario.py`,
  `scenario_generator.py`. `observation.py`/`action.py`/`reward.py`/`rollout_env.py` come in Phase 2.
- `ismpu/agent/`, `ismpu/gui/` — **not yet created**; later phases in the plan.

## X-Plane communication (`ismpu/io/xplane_connector.py`)

Self-contained UDP client for X-Plane's data protocol — the only I/O layer. Key distinction:

- `subscribeDREFs([(dref, freq), ...])` starts a **background thread** that continuously receives
  values into `xpc.current_dref_values[dref]['value']`. This is the async, high-frequency path the
  controller reads from every loop tick. It blocks on setup until every DataRef has produced a first
  value (or raises `TimeoutError` naming the bad DataRefs — usually a typo).
- `getDREF`/`getPOSI` are synchronous one-shot requests — used for setup, not the hot loop.
- `sendDREF(dref, value)` writes; `sendCTRL(...)` writes the 8 primary controls at once; `sendPOSI`
  teleports the aircraft (sent twice on purpose — elevation is miscomputed on the first packet).

Do not "fix" the double-send in `sendPOSI` or the RREF retransmission logic in `subscribeDREFs` — both
work around real UDP packet loss from X-Plane.

## Control architecture (`ismpu/control/`)

The loop runs at 20 Hz (`DT = 0.05`). `ControllingSystem.control_step(dt)` calls two channels each tick,
then applies failure degradation, then sends commands:

- **`LongitudinalChannel`** — speed control. Integrates traveled distance, looks up the target speed on
  a `ReferenceTrajectory` (default `GAUSS_BELL` decay curve; `EQUALLY_SLOW` = constant deceleration is
  the alternative), and drives four independent `PIDController`s: left/right hydraulic brakes and
  left/right thrust reversers. Reverser PIDs are bounded to `[-1, 0]`, so their output is already the
  negative-throttle value X-Plane expects (no separate sign flip); reverse is force-disabled below 60 kts
  (with integrator reset).
- **`LateralChannel`** — centerline hold. `RunwayTracker.guidance(...)` computes cross-track error and a
  Stanley-style `heading_error`, using a speed-scaled look-ahead point projected down the runway
  geodesic. One PID converts heading error to a rudder command, from which two differential mixes are
  added on top of the longitudinal commands: **differential braking** (`steering_brake_gain` — subtracted
  from one brake, added to the other) and **asymmetric thrust** (`steering_rev_gain` — added/subtracted on
  the reversers, only above 60 kts). The mixing runs *after* the longitudinal channel sets brake/reverse,
  so ordering matters.

`ControlsState` is the shared per-tick command struct (brakes, reversers, rudder). `break_control=True`
signals the loop to stop (target speed reached or missing telemetry). Hard output bounds are applied
**last**: `control_step` calls `ControlsState.clamp_all(pids)` after both channels, re-clamping every
command to its PID's `[min_out, max_out]` *after* the differential mixes — so the channels no longer clamp
inline. `ControllingSystem.setup` takes the five PIDs as a `dict` and stores it as `self.pids` for this.

### Failures (`FailureMode` / `FailureManager` / `FailureState`)

`FailureState` holds per-actuator efficiency multipliers (0.0–1.0). `ControlsState.apply_failures()`
multiplies the computed commands by them just before sending, simulating degraded/failed hardware. Each
failure case has its own hand-tuned set of PID gains, captured as `ScenarioConfig` presets in
`ismpu/config/scenarios.py` (`DEFAULT`, `NWS_FAIL`, `LEFT_REVERSE_FAIL`, `RIGHT_REVERSE_FAIL`).
`scenario.apply(controller)` builds fresh (stateful!) PIDs, wires up the channels, and **activates the
preset's associated `FailureMode`** (unless it is `NONE`). `NWS_FAIL` is calibrated for the real NWS
failure (`steering_eff = 0`, rudder killed): centerline hold is carried by differential braking plus
asymmetric thrust (`steering_brake_gain` / `steering_rev_gain`). The reverse presets were carried over
from draft notebook cells and still need calibration.

## PID conventions (`PIDController`)

- Leaky integrator: `integral_decay > 0` applies exponential decay per tick (anti-windup beyond the hard
  `anti_windup` clamp).
- Derivative is low-pass filtered (`der_filter_tf`, first-order IIR) to reject telemetry noise; first
  tick emits zero derivative to avoid a startup kick.
- Output is clamped (via the `clamp()` method) to `[min_out, max_out]`: runway-center uses `[-1, 1]`,
  brakes `[0, 1]`, reversers `[-1, 0]` (already the negative-throttle sign). The same `clamp()` is reused
  by `ControlsState.clamp_all()` to bound the final commands after the differential mixes. `compute()`
  logs its internals via `logging.debug` on the `ismpu.control.pid` logger; the per-channel status lines
  use `cprint`.
- Gains are **empirically tuned per aircraft and per failure case** and are fragile. When changing plant
  behavior, expect to re-tune rather than derive.

## Weather control (`ismpu/envs/weather.py`)

Standalone environment subsystem, modelled on `FailureManager` — groundwork for the scenario generator
(plan §8, `SimInterface.apply_weather`). `WeatherManager(xpc)` writes X-Plane 12's **writable** weather
via the `sim/weather/region/*` DataRefs (the old top-level `sim/weather/wind_*` are all `DEPRECATED`/
`REPLACED` — named constants live in `io/datarefs.py` under the `WX_*` prefix).

- `WeatherState` is the config dataclass (wind in **knots**, direction "from" in ° true, gusts via shear,
  turbulence 0–10, `variability_pct`, `runway_friction`, rain, visibility in **metres**, temperature).
  `WeatherManager.apply(state)` pushes it all at once (`change_mode = Static`, `update_immediately = 1` so
  it takes effect now, not on the 60 s cycle); wind/shear/turbulence are written across all 13 atmospheric
  layers.
- **Wind is set by speed + direction**, so `compose_wind`/`decompose_wind` (and `WeatherState.from_crosswind`)
  convert to/from crosswind+headwind components relative to `RWY_HEADING_TRUE`.
- **`runway_friction` is a single global enum 0–15** (Dry=0 … snowy/icy=15) — X-Plane's only μ lever;
  there is **no per-position runway friction**. `RunwayCondition` names the levels. "Variable friction along
  the runway" is therefore a `FrictionProfile` (distance→level step function): `WeatherManager.update(distance_m)`
  re-sends `runway_friction` only when the level changes, so the control loop must call it each tick when a
  profile is active.
- `WEATHER_PRESETS` (clear_dry / wet / puddly / icy / crosswind / gusty_crosswind / low_visibility /
  variable_friction) are the seed states the scenario generator will sample. `read_effective_wind` /
  `read_crosswind` read the aircraft-side effective wind for diagnostics/observer.

## Sim interface & scenarios (`ismpu/envs/`)

The transport-agnostic seam between the controller and whatever it runs against (plan §7/§8, Phase 1).

- **`sim_interface.py`** — `SimInterface` (ABC): `reset(scenario)` / `step(command)` / `read_telemetry` /
  `apply_weather` / `inject_failure` / `clear_failures` / `teleport_touchdown` / `pause` / `update` / `close`.
  `reset`/`step`/`read_telemetry` return a raw `Telemetry` dataclass (SI units; `None` for fields a backend
  can't supply, `valid=False` when telemetry is missing). Lives in `envs/`, **not** `io/`, because it depends
  on `WeatherState`/`FailureMode`/`Scenario` — keeping it in `io/` would break "io = transport only".
  - **`XPlaneBackend`** (training) — wraps `XPlaneConnectX`: extended telemetry subscription, a *lean* fast
    teleport (with lateral/heading offset, no `reload_scenery`/30 s wait — unlike `runtime/setup.py`), weather
    via `WeatherManager`, and failure injection via the real engine/reverser DataRefs (`rel_engfai{N}` /
    `rel_revers{N}`, enum `6`=fail). **NWS and thrust-degrade have no X-Plane failure DataRef** → they're only
    tracked in `active_failures`; their effect comes from the controller's command degradation (`FailureManager`).
  - **`ICSBackend`** (deployment) — wraps `ICSBenchConnector`: `ICSInputs → Telemetry`, `ControlsState →
    ICSOutputs` (mapping provisional pending the ПИВ spec). Weather/failures/teleport are the bench's job → no-ops.
- **`scenario.py`** — `Scenario` (serializable via `to_dict`/`from_dict` for reproducible eval batteries):
  `control_preset` (key into `config.scenarios.SCENARIOS`), `weather` (`WeatherState`), `failures`, `touchdown`
  (`TouchdownSetup` with lateral/heading offset), `sensor_noise`. `SimInterface.reset` applies the environment
  parts; the RL env (Phase 2) additionally configures the controller from `control_preset`.
- **`scenario_generator.py`** — `ScenarioGenerator(seed)`: domain randomization across all axes, curriculum via
  `difficulty ∈ [0,1]` (harder → more/heavier failures, stronger crosswind, lower μ, more noise). Deterministic
  per seed. `battery()` is the fixed acceptance set (nominal + failures + weather + combos).

## External bench interface (`ismpu/io/ics_connector.py`)

A separate UDP JSON bridge (`ICSInputs`/`ICSOutputs`/`ICSBenchConnector`) for a hardware/simulation test
bench ("стенд") on port 3030 — a parallel integration path, **not** wired into the X-Plane loop yet.
`ICSInputs` is the rich telemetry the bench sends; `ICSOutputs` is the control structure sent back. Per the
plan this becomes the deployment transport (behind the future `SimInterface`), so the ТЗ `.exe` can run on
the customer bench without changing the controller.

## Units & geo

- `ismpu.utils.converts.Converts` holds all unit conversions (kts↔m/s, ft↔m, etc.) and `dms_to_float` for
  DMS coordinates. Use these constants rather than inlining magic numbers.
- `RunwayTracker` (`ismpu/control/runway_tracker.py`) does spherical-earth geodesy (haversine distance,
  bearing, direct geodesic `destination`). Runway endpoints and heading live in `ismpu/config/runway.py` —
  changing the target runway means editing `RWY_START_*`/`RWY_END_*`/`RWY_HEADING_TRUE` there.
