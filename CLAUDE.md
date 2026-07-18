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
classical PID loop stays as the plant, and a **Neural PID Gain Scheduler (NPGS)** actor (SFT-warm-started,
then trained with PPO) predicts the **absolute PID coefficients** (kp/ki/kd × 5 regulators) plus
channel-influence weights, guarded by a deterministic **Shield** and, later, an optional physics-informed
**PINN observer**.

The NPGS is **not** a classic "PIDNN": the ТЗ forbids embedding the PID transfer function into the network,
so the net only *predicts the coefficients* the classical `PIDController` then uses — it never becomes the
controller. **The net emits absolute gains** (not multiplicative α) so a supervised warm-start (SFT/behavioral
cloning) can regress toward the hand-tuned expert presets; safety is preserved because the Shield keeps the
per-scenario preset as its bound/fallback anchor. Full architecture in `implementation_plan.md` §10; targets
**A330-300** (X-Plane training) and **МС-21** (bench deployment).

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
  Python 3.14): `numpy`, `pandas`, `termcolor`, `pytest`, plus Jupyter (`ipykernel`). `torch` (2.12,
  **cu132** — installed in `.venv`) and `gymnasium` are the optional `rl` extra: `torch` is now used by the
  NPGS/PPO layer (Phase 4); `gymnasium` stays optional (`rollout_env` works without it).
- Activate the venv before running: `.venv\Scripts\Activate.ps1` (PowerShell). **The `.venv` is the real
  environment** — bare `python` on PATH is a separate 3.14 without torch/pytest. Run tests and training via
  `.venv\Scripts\python.exe` (or the activated venv).
- **Run the controller:** `python -m ismpu.runtime.loop` (or the thin `main.ipynb`, which imports from
  `ismpu` and calls `run(...)`). Requires a running X-Plane 12 on `127.0.0.1:49000`. The 20 Hz loop runs
  until `KeyboardInterrupt`, which resets all controls. Pick a prepared preset by name —
  `main("nws_fail" | "default" | "left_reverse_fail" | "right_reverse_fail")` from
  `ismpu.envs.scenario.SCENARIO_PRESETS` (control tuning + standard weather bundled).
- **SFT warm-start (do this first):** `python -m ismpu.runtime.pretrain` (needs X-Plane). Captures classical
  rollouts of the non-draft presets and behavior-clones the NPGS toward their coefficients → `checkpoints/npgs_sft.pt`.
  Offline validation: `ismpu.runtime.pretrain.smoke_pretrain(env, scenarios)` (see `tests/test_pretrain.py`).
- **Train the NPGS:** `python -m ismpu.runtime.train` (needs X-Plane). Builds env + controller on **one
  shared connector**, PPO + curriculum, checkpoints to `checkpoints/`. Set `TrainConfig.init_from="checkpoints/npgs_sft.pt"`
  to start from the SFT warm-start (strongly recommended — a cold net emits DEFAULT gains, unsafe on failures).
  Offline (no X-Plane) validation of the PPO loop: `ismpu.runtime.train.smoke_train(env, provider, updates=...)`
  with a scripted backend (see `tests/test_ppo.py`).
- **Tests:** `python -m pytest` (from repo root; a root `conftest.py` puts `ismpu` on the path). Run under the
  venv (has pytest + torch). Simulator-free — PID numerics, tracker geodesy, reference-speed curves, one full
  `control_step` through a mock connector, plus the NPGS/PPO layer (network shapes/identity, GAE, loss terms,
  end-to-end PPO on a scripted sim). torch-dependent tests are guarded by `pytest.importorskip("torch")`.
  Full-trajectory parity with the old notebook still needs X-Plane and is a manual check.
- **Known snag:** `PIDController.compute` (and channel status lines) call `cprint` unconditionally every tick.
  Fine for one manual run, but at 20 Hz × 5 regulators it floods the console and throttles training —
  `train.py` calls `silence_control_console()` to no-op those `cprint`s during training. Consider gating the
  `cprint` in `pid.py`/`channels.py` behind the logger instead.
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
  `scenarios.py` (PID presets per scenario + each preset's weather; `ScenarioConfig.draft` flags uncalibrated),
  `regulators.py` (`REGULATOR_ORDER`/`GAIN_KEYS`/`N_GAINS`/`ACTION_DIM` — neutral, breaks a shield↔gain_space cycle),
  `requirements.py` (the ТЗ acceptance thresholds), `aircraft.py`.
- `ismpu/runtime/` — `setup.py` (`setup_touchdown_uuee`), `loop.py` (the 20 Hz loop + `main()`), `train.py`
  (PPO loop + `smoke_train`, `TrainConfig.init_from`), `pretrain.py` + `capture.py` (SFT warm-start). `evaluate.py`/`deploy.py` come in Phases 5/6.
- `ismpu/utils/converts.py` — `Converts` (unit conversions).
- `ismpu/envs/` — environment + RL layer: `weather.py`, `sim_interface.py`, `scenario.py`,
  `scenario_generator.py` (Phase 1) and `observation.py` / `action.py` / `reward.py` / `rollout_env.py` (Phase 2).
- `ismpu/agent/` — neural/safety layer: `shield.py` + `normalization.py` + `gain_space.py` (absolute-gain map)
  + `gain_scheduler.py` (NPGS actor+critic) + `ppo.py` + `pretrain.py` (SFT/BC) (all done). `observer.py` comes
  in Phase 7. `ismpu/gui/` — not yet created.

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
  - **`XPlaneBackend`** (training) — wraps `XPlaneConnectX`: extended telemetry subscription, weather
    via `WeatherManager`, and failure injection via the real engine/reverser DataRefs (`rel_engfai{N}` /
    `rel_revers{N}`, enum `6`=fail). **NWS and thrust-degrade have no X-Plane failure DataRef** → they're only
    tracked in `active_failures`; their effect comes from the controller's command degradation (`FailureManager`).
    - **`reset()` reloads the airframe every episode** (`reload_each_reset=True`): `reload_aircraft_no_art`
      (~12–14 s) wipes accumulated damage/wear/brake-heat that would otherwise carry over and poison training
      (esp. failure scenarios — NWS steers/brakes at the cost of gear/tire/brake wear). Readiness is detected
      **dynamically** (not a blind sleep): after reload it re-subscribes (RREF stream may drop on reload) and
      polls `total_flight_time_sec` until it rises steadily (physics stepping), with a `ready_timeout` fallback
      that warns and proceeds. Then the atomic teleport runs under pause. `reload_each_reset=False` (unit tests
      on a mock connector) keeps the old lean teleport-only reset. `setup_view=True` re-adds the chase/zoom view
      commands (eval/GUI only; training is headless). `teleport_touchdown` is now positioning-only.
  - **`ICSBackend`** (deployment) — wraps `ICSBenchConnector`: `ICSInputs → Telemetry`, `ControlsState →
    ICSOutputs` (mapping provisional pending the ПИВ spec). Weather/failures/teleport are the bench's job → no-ops.
- **`scenario.py`** — `Scenario` is the **single unified episode descriptor** (fixes the earlier split where
  the generator made `Scenario` but the loop used bare `ScenarioConfig`). It **embeds** the control tuning
  object `control: ScenarioConfig` (from `config.scenarios`, PID unchanged) plus `weather` (`WeatherState`),
  `failures`, `touchdown` (`TouchdownSetup` with lateral/heading offset), `sensor_noise`. Serializable
  (`to_dict`/`from_dict`; `control` stored by its preset name). `SCENARIO_PRESETS` = ready-to-run scenarios,
  same keys as `config.scenarios.SCENARIOS`, each bundling a control preset with **standard weather (clear /
  calm / dry)**. `scenario.apply_control(controller)` sets up the PIDs; `SimInterface.reset` applies the
  environment parts. **The 20 Hz loop selects a preset by name** — `python -m ismpu.runtime.loop` runs
  `main("nws_fail")`; `run()` applies the scenario's weather via `WeatherManager` before the episode.
- **`scenario_generator.py`** — `ScenarioGenerator(seed)`: domain randomization across all axes, curriculum via
  `difficulty ∈ [0,1]` (harder → more/heavier failures, stronger crosswind, lower μ, more noise). Deterministic
  per seed. `battery()` is the fixed acceptance set (nominal + failures + weather + combos).

## RL environment (`ismpu/envs/`, Phase 2)

The Gymnasium-compatible training env wrapping `SimInterface` + the classical controller (plan §5/§6).

- **`observation.py`** — `ObservationBuilder.build(telemetry, controller, weather, observer)` → a **56-dim**
  normalized frame (geometry 4 / speed 4 / last controls 5 / PID×5 dynamic state 30 / failure flags 3 / weather 5
  / **observer slots 5**). The PID `kp/ki/kd` slots now encode the **absolute** current gains in gain-space
  log-norm (`gain_space.gain_norm_scalar`, = the net's previous output; no `base_gains` arg anymore).
  `GAIN_FEATURE_INDICES` lists those 15 slots (used by ppo's `L_smooth` and SFT's anti-copycat masking).
  `FEATURE_NAMES` fixes the order; invalid telemetry → zero frame.
- **`agent/normalization.py`** — fixed physical scales (constants, not batch stats); `snapshot()` includes the
  `gain_space` table and is serialized with the weights.
- **`action.py`** — action is `(17,) = [gains×15, w_lon, w_lat]` (**absolute** kp/ki/kd, `GainCommand` layout).
  `apply_corrections(command, preset_gains, controller, shield)` writes the gains into `controller.pids` and
  channel weights (optionally via the preset-anchored Shield). `REFERENCE_ACTION` = DEFAULT gains; `preset_action(preset)`
  (float64, exact) reproduces a scenario's classical behaviour.
- **`reward.py`** — per-component reward (lateral / speed / jerk / shield / heading / instability), thresholds
  from `config/requirements.py`. Pure function.
- **`rollout_env.py`** — `RolloutEnv(reset/step)`, obs-history ring buffer emitting the window as a
  **sequence `(history_len, 56)`** (the NPGS input; changed from the old flat vector in Phase 4), optional
  Shield in the inference path. Gymnasium is imported **optionally** (spaces are `Box` if installed, else a
  tiny `_SimpleBox`). **Parity:** `env.step(preset_action(preset))` (shield off) is bit-for-bit equal to the
  classical `control_step` for that scenario (test `test_env_preset_action_parity...`).
- Small additive control-loop hooks (classical behaviour unchanged at defaults): `PIDController.last_output`,
  channel `w_lon`/`w_lat` (× PID outputs before `clamp_all`), `ControllingSystem.control_step(send=False)` and
  `set_channel_weights`. The env sends commands via `SimInterface.step`, but the controller reads telemetry from
  `xpc.current_dref_values`, so for training `sim` and `controller` must share one X-Plane connector.

## Shield — safety contour (`ismpu/agent/shield.py`)

Deterministic guard between the (future) neural actor and the classical PID loop (plan §9). It is **not**
trained, is always active, and the network can't issue a command that bypasses it. Built and unit-tested
standalone, ahead of the actor.

- The actor's output is `GainCommand`: **absolute** `kp/ki/kd` per regulator (5 × 3 = 15) plus channel weights
  `w_lon/w_lat` (`ACTION_DIM = 17`; `from_vector`/`to_vector`/`from_gains`).
- **The per-scenario preset is the safety anchor** (passed to `guard_coefficients` as `preset_gains`): the net
  emits absolute gains, but the Shield still centers the allowed corridor on the certified preset.
- **Three levels + fallback:** (1) clip gains to the physical band `[lo,hi]` (`gain_space`), weights to `[0,2]`;
  (2) hard bounds `[hard_low·preset, hard_high·preset]` + non-negativity + per-tick rate-limit + OOD detector;
  (3) runtime checks on the resulting `ControlsState` — reverse below 60 kts, brake jerk, heading divergence.
  OOD or a gross heading blow-out latches a **fallback** that writes the **preset gains** directly (certified
  classical). This preset-as-bound/fallback is the ТЗ-compliance argument (bounded advisory, not "net is controller").
- `ShieldReport` carries per-level flags, `l_shield`/`l_smooth` accumulators, and triggered rules (ТЗ 5.1.5).
- **Parity (plan §1):** feeding a `GainCommand` equal to the scenario preset → effective gains == preset and the
  Shield stays silent (the absolute-gain analog of the old α=1 identity).
- Integration: `guard_coefficients(gain_command, preset_gains)` runs *before* `control_step`;
  `guard_command(command, runtime_state)` runs *after*. Bridge helpers `base_gains_from_pids` /
  `apply_gains_to_pids` connect it to `ControllingSystem.pids`.

## Gain space (`ismpu/agent/gain_space.py`) — single source of truth

The NPGS outputs **absolute** coefficients, so there's a fixed physical map from the net's raw output `z` to a
gain, per (regulator, kp|ki|kd) slot — 15 slots in `REGULATOR_ORDER × (kp,ki,kd)` order (=`config/regulators.py`).
`gain_i = ref_i · exp(s_i · tanh(z_i))` (⇒ bounded to `[lo_i, hi_i]`); inverse `inv_gain` (for SFT targets);
`gain_norm`/`gain_norm_scalar` (obs normalization = `tanh(z)`). The table (`GAIN_REF/S/LO/HI/DEFAULT` + `*_MAP`
dicts) is **computed from the preset family** `config.scenarios.SCENARIOS` at import (geometric-midpoint `ref`,
log half-width `s` sized to span the presets ± `EXPAND`) and frozen into `normalization.snapshot()` → the
checkpoint pins the whole gain space. Because presets span up to ~70× on some gains, this log-space map (not a
±50% band) is what makes SFT-to-preset expressible. `config/regulators.py` holds `REGULATOR_ORDER`/`GAIN_KEYS`/
`N_GAINS`/`ACTION_DIM` (neutral module so `shield` and `gain_space` avoid an import cycle; `shield` re-exports).

## Neural PID Gain Scheduler (NPGS) — actor/critic (`ismpu/agent/gain_scheduler.py`, plan §10)

The neural actor+critic (~1.4 M params). **Renamed from "PIDNN"** because the ТЗ forbids embedding the PID
transfer function in the net — NPGS keeps the classical PID as plant and only predicts its coefficients. It emits
**absolute gains** (not multiplicative α), which is what makes the SFT warm-start toward expert presets work.

- **Input:** a window of `T` observation frames → `(B, T, 56)` (`T≈16` ≈ 0.8 s at 20 Hz; `NPGSConfig.window`).
  Windowed-recurrent, deterministic for deploy. `rollout_env` emits the window as a **sequence** `(T,56)`.
- **Shared encoder** (`encode()`, actor + critic share it): input `LayerNorm` → time-distributed
  `Linear(56→256)→GELU→Linear(256→256)→GELU` (+residual) → `GRU(256)×2` → `MultiheadAttention(256,4)` (+residual,
  LayerNorm) → learned-query attention pooling → shared trunk `Linear(256→256)→Linear(256→128)` (+skip) → `z_shared`.
- **Context Fusion:** a branch off `z_shared` → **movement-phase** context `c (128)` (`phase_head` +
  `phase_labels_from_groundspeed_kts` feed an optional aux loss). Every head receives `[z_shared ⊕ c]`.
- **Heads** (`Linear(256→64)→GELU→Linear(64→32)→GELU→Linear(32→out)`): Heading→runway_center(3), Brake→L/R(6),
  Reverse→L/R(6), Weights→`(w_lon,w_lat)`. **17 policy outputs = ACTION_DIM** (L/R brake/reverse are now
  **independent** — asymmetric-brake presets like reverse-fail need it; SFT provides the symmetry prior the old
  weight-sharing used to bake in). `to_gains(u)`: first 15 → `ref·exp(s·tanh(z))` (absolute gains), last 2 →
  `1+tanh(z)` (weights). Gain heads init with a **DEFAULT bias** (`gain_space.default_bias()`) → cold-net output
  ≈ classical DEFAULT (safe start).
- **Policy:** plain Gaussian over the raw `u` (17-dim); `to_gains` is a deterministic env-side squash (no tanh
  Jacobian in the log-prob). `log_std` is a **per-output vector** init so `s_i·std_z_i ≈ exploration_frac` (uniform
  multiplicative exploration ±15% across gains despite very different `s_i`). Greedy (deploy) = mean; `act_numpy`.
- **Critic:** a **head** off `z_shared` → `V(s)`.
- **"Identity"/parity:** there's no α=1 identity; the analog is `preset_action(preset)` (write the scenario's
  preset gains exactly, float64) → env reproduces classical `control_step` bit-for-bit (`REFERENCE_ACTION` = DEFAULT).
  Safety on failures rests on SFT-init + Shield, not on a default-identity.
- **Serialization:** `NPGS.save/load` bundle weights + `NPGSConfig` + normalization `snapshot()` (incl. gain space).
- **Downstream:** every output passes through the Shield (preset-anchored) before reaching the PID loop.

## SFT warm-start (`ismpu/agent/pretrain.py`, `ismpu/runtime/{capture,pretrain}.py`, plan Stage B)

Supervised pretraining (behavioral cloning) so PPO starts near the expert presets instead of DEFAULT — PPO alone
converges slowly. `runtime/capture.py` runs the **classical** controller in-process inside `RolloutEnv` (action =
`preset_action(preset)`) and records `(obs_window, target_z)` where `target_z = inv_gain(preset gains)` (weights→0).
Obs must come from the live `ObservationBuilder` (the PID block — integral/deriv/last_output — isn't in any
telemetry DataRef, so raw-DataRef reconstruction is wrong). `agent/pretrain.py::pretrain_sft` regresses the policy
`mean → target_z` (MSE, `log_std` frozen). **Anti-copycat (critical):** the obs carries "previous gains" and the
BC target is constant per rollout, so the net could just copy the input; `pretrain` replaces the gain features with
**fresh U(−1,1) noise per batch** (not zeros — real values are in `[−1,1]` too, so no train/inference shift),
forcing the net to key on the disturbance (failure/weather) features. Canonical labeling: each **non-draft** preset
(`ScenarioConfig.draft`) is its own regime run in its own conditions; never mix inconsistent labels.
`runtime/pretrain.py` orchestrates capture→BC→checkpoint (`npgs_sft.pt`); `smoke_pretrain(env, scenarios)` is the
offline (no-X-Plane) path used in `tests/test_pretrain.py`. `train.py` loads it via `TrainConfig.init_from`;
`ppo.lambda_anchor>0` additionally keeps a frozen SFT copy as `trainer.sft_reference` (anti-forgetting).

## PPO training (`ismpu/agent/ppo.py`, `ismpu/runtime/train.py`, plan §11)

Compact CleanRL-style PPO over a **single** env (X-Plane is one instance). `PPOTrainer.collect` fills a
`RolloutBuffer`, `compute_gae` does GAE(λ) with a done-mask bootstrap, `update` runs minibatch epochs with a
clipped surrogate + value-clipping, advantage normalization, entropy bonus, grad-clip 0.5, KL early-stop, and
LR annealing. Multi-component loss `L = L_ppo + λs·L_smooth + λp·L_phys(=0) + λsh·L_shield(=0)`:
- **L_smooth** is a *differentiable* temporal-smoothness penalty: `(tanh(mean) − prev_gain_norm)²` where
  `prev_gain_norm` is the obs's encoded previous gains — plus an optional SFT-prior anchor to a frozen SFT copy
  (`lambda_anchor`, anti-forgetting) set via `PPOTrainer.sft_reference`.
- Non-differentiable penalties (jerk, Shield intervention, heading, instability) enter through the **reward**
  (`envs/reward.py`), so they shape the advantage — the correct way to inject them into PPO.
- **L_phys** (observer residual, §12) and **L_shield** (a `tanh(mean)⁴` band-barrier) are wired hooks with
  default weight 0.
`runtime/train.py` builds env + controller on **one shared connector** (the env sends commands via
`SimInterface.step`, the controller reads telemetry from the same `xpc.current_dref_values` — they must share
it), curriculum ramps `difficulty` via `ScenarioGenerator`, Shield sits in the actor's inference path, and it
checkpoints weights+normalization + a per-term CSV. `smoke_train(env, provider)` runs the loop offline (no
X-Plane) — see `tests/test_ppo.py`'s scripted backend.

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
