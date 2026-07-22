# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

An autonomous landing-rollout controller for an aircraft (A330-class) running against the **customer's
test bench (стенд)** over the ПИВ/ICS protocol. On touchdown it holds the runway centerline and
decelerates from ~200 kts to taxi speed along a reference velocity curve, while modeling and
compensating for equipment failures (engine out, reverser fail, nose-wheel-steering fail, etc.).
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
**A330-300** and **МС-21**.

> **The X-Plane path is gone.** The project used to train against X-Plane 12 behind a two-backend
> `SimInterface` abstraction. Everything now runs against the bench: one transport (`io/ics_connector.py`),
> one sim object (`envs/ics_sim.ICSSim`), no backend switch. The consequences are structural, not
> cosmetic — **we no longer own the environment**. There is no teleport, no episode reset, no weather
> lever and no failure injection; the bench operator sets the conditions and reports them as telemetry.
> Anything in older commits or the plan that "applies" a scenario to the simulator is obsolete.

## Planning & reference documents

Read these before making architectural changes — they define the target design and the acceptance criteria:

- **[`implementation_plan.md`](implementation_plan.md)** — the phased plan for the neural-control rework:
  target package layout (`ismpu/`), the full Observation/Action spaces, Shield, PPO + multi-component loss,
  and the observer seams. **This is the source of truth for where the project is going**. It predates the
  X-Plane removal in places; where it says "X-Plane", read "bench", and where it describes setting up the
  environment, see the note above.
- **[`PIDNN.mmd`](PIDNN.mmd)** — Mermaid diagram of the full architecture (scenario selection, bench,
  PINN observer, NPGS multi-head actor, Shield, classical control, PPO loop, deployment). Data-flow reference.
- **[`ТЗ_Интеграл-КБО-МС_ИСМПУ_итог_ф.pdf`](ТЗ_Интеграл-КБО-МС_ИСМПУ_итог_ф.pdf)** — the customer's
  technical spec (ТЗ). Section 5 holds the hard acceptance numbers that become reward gates and eval
  criteria: centerline ±3 m on rollout / ±1 m taxi, heading ±5° under NWS or thrust/reverse fault down to
  <30 kts, μ/crosswind/aquaplaning diagnostics, and delivery as an `.exe` over the agreed UDP protocol (ПИВ).
- **[`ICSInterface.cs`](ICSInterface.cs)** — the bench's own `ICSInputs`/`ICSOutputs` struct definitions with
  units in the doc-comments. The authoritative field list, but an **incomplete slice**: it omits
  `AgentIsActive`, which the bench does process. Verify against the running bench, not this file.

## Environment & running

- Dependencies are in `pyproject.toml` / `requirements.txt` (also live in the committed-out `.venv/`,
  Python 3.14): `numpy`, `pandas`, `termcolor`, `pytest`, plus Jupyter (`ipykernel`). `torch` (2.12,
  **cu132** — installed in `.venv`) and `gymnasium` are the optional `rl` extra: `torch` is used by the
  NPGS/PPO layer (Phase 4); `gymnasium` stays optional (`rollout_env` works without it).
- Activate the venv before running: `.venv\Scripts\Activate.ps1` (PowerShell). **The `.venv` is the real
  environment** — bare `python` on PATH is a separate 3.14 without torch/pytest. Run tests and training via
  `.venv\Scripts\python.exe` (or the activated venv).
- **Run the controller:** `python -m ismpu.runtime.loop` (or the thin `main.ipynb`). Listens for the bench
  on `127.0.0.1:3030`; the bench's own address is taken from the first incoming packet, so it is not
  configured. The 20 Hz loop runs until taxi speed or `KeyboardInterrupt`, which resets all controls.
  `main()` with no argument **picks the preset by telemetry** (`select_for_telemetry`); pass a name
  (`main("nws_fail")`) to force one — see `ismpu.envs.scenario.SCENARIO_PRESETS`.
- **SFT warm-start (do this first):** `python -m ismpu.runtime.pretrain` (needs the bench). Captures
  classical rollouts of the non-draft presets and behavior-clones the NPGS toward their coefficients →
  `checkpoints/npgs_sft.pt`. Offline validation: `ismpu.runtime.pretrain.smoke_pretrain(env, scenarios)`
  (see `tests/test_pretrain.py`).
- **Train the NPGS:** `python -m ismpu.runtime.train` (needs the bench). Builds env + controller over one
  `ICSSim`, PPO + curriculum, checkpoints to `checkpoints/`. Set `TrainConfig.init_from="checkpoints/npgs_sft.pt"`
  to start from the SFT warm-start (strongly recommended — a cold net emits DEFAULT gains, unsafe on failures).
  Offline (no bench) validation of the PPO loop: `ismpu.runtime.train.smoke_train(env, provider, updates=...)`
  with a scripted bench (see `tests/fakes.py`, `tests/test_ppo.py`).
- **Tests:** `python -m pytest` (from repo root; a root `conftest.py` puts `ismpu` on the path). Run under the
  venv (has pytest + torch). Bench-free — PID numerics, tracker geodesy, reference-speed curves, one full
  `control_step` through a fake bench, plus the NPGS/PPO layer (network shapes/identity, GAE, loss terms,
  end-to-end PPO on a scripted bench). torch-dependent tests are guarded by `pytest.importorskip("torch")`.
  **`tests/fakes.py` is the shared fake bench** — use `make_ics_inputs` / `static_sim` / `kinematic_sim`
  rather than hand-rolling another mock.
- **Known snag:** `PIDController.compute` (and channel status lines) call `cprint` unconditionally every tick.
  Fine for one manual run, but at 20 Hz × 5 regulators it floods the console and throttles training —
  `train.py` calls `silence_control_console()` to no-op those `cprint`s during training. Consider gating the
  `cprint` in `pid.py`/`channels.py` behind the logger instead.
- `main.py` and `env.py` at the repo root are **superseded, untracked experiments** — ignore them; the
  package is the source of truth. They can be deleted.
- `roman_aviacia_ics/` (untracked) is the second НИР participant's ICS toolkit — probes, dashboards and an
  airborne PID against the same bench. Useful as a cross-check on protocol details; not part of this package.

## Package layout

- `ismpu/io/` — transport: `ics_connector.py` (`ICSInputs`/`ICSOutputs`/`ICSBenchConnector`),
  `ics_engagement.py` (the engagement state machine).
- `ismpu/control/` — the classical loop: `pid.py`, `runway_tracker.py`, `trajectory.py`, `channels.py`
  (`ControlsState` + the two channels), `system.py` (`ControllingSystem`), `failures.py`.
- `ismpu/config/` — `runway.py` (UUEE 06R geometry — the **fallback** when the bench doesn't publish runway
  data), `constants.py`, `scenarios.py` (PID presets per scenario + the conditions each was calibrated for;
  `ScenarioConfig.draft` flags uncalibrated), `ics.py` (ICD constants: units, actuator limits, valid-mask bits,
  engagement timings, flight phases), `regulators.py` (`REGULATOR_ORDER`/`GAIN_KEYS`/`N_GAINS`/`ACTION_DIM` —
  neutral, breaks a shield↔gain_space cycle), `requirements.py` (the ТЗ acceptance thresholds).
- `ismpu/runtime/` — `loop.py` (the 20 Hz loop + `main()`), `train.py` (PPO loop + `smoke_train`,
  `TrainConfig.init_from`), `pretrain.py` + `capture.py` (SFT warm-start), `evaluate.py` (ТЗ acceptance +
  baselines + admission gate). `deploy.py` comes in Phase 6.
- `ismpu/utils/converts.py` — `Converts` (unit conversions).
- `ismpu/envs/` — environment + RL layer: `ics_sim.py` (`Telemetry` + `ICSSim`), `weather.py`, `scenario.py`,
  `scenario_generator.py`, `observation.py` / `action.py` / `reward.py` / `rollout_env.py`, `splits.py`,
  `reproducibility.py`.
- `ismpu/agent/` — neural/safety layer: `shield.py` + `normalization.py` + `gain_space.py` (absolute-gain map)
  + `gain_scheduler.py` (NPGS actor+critic) + `ppo.py` + `pretrain.py` (SFT/BC) (all done). `observer.py` comes
  in Phase 7. `ismpu/gui/` — not yet created.

## Bench interface (`ismpu/io/ics_connector.py`, `ismpu/config/ics.py`)

UDP JSON bridge to the customer's bench on port 3030 — the only I/O layer and the delivery transport.

- **Encoding confirmed by the bench developer:** `Struct → Newtonsoft.Json.JsonConvert → string →
  Encoding.UTF8.GetBytes()`. Plain JSON on the wire: **no header, no CRC, no serial numbers.** Do not add
  framing — prefixed bytes break parsing on the bench side. The bench's address is taken from the incoming
  packet's UDP header.
- `ICSInputs` is the rich telemetry the bench sends; `ICSOutputs` is the control structure sent back.
  `ICSInputs.from_dict` is deliberately asymmetric: **unknown keys are ignored** (the bench may add a signal
  and that must not crash us), **missing keys raise** (zero-filling would invent telemetry we then control on).
- `ResilientSender` swallows `WSAECONNRESET` (10054), which Windows raises on a UDP socket when the receiver's
  port is closed. Dropping the control loop over that is wrong, and so is silence — hence the error counter
  and the rate-limited log.
- **All ICD constants live in `config/ics.py`**, not inline: brake pedal travel (0–36.73 mm), throttle angle
  (−26.5…55.0°), tiller/rudder limits, `ControlValid` mask bits, engagement dwell/frames, `FlightPhase`.
  Several are flagged **ТРЕБУЕТ ПОДТВЕРЖДЕНИЯ** — the mask bit layout (only bit 0 = ELEVATOR is confirmed),
  `TILLER_MAX_DEG=70`, `RUDDER_MAX_DEG=30`. They set command scale, so they gate real-bench validation.
- `ROLLOUT_CONTROL_MASK` declares only the channels the rollout loop actually drives (rudder, tiller, wheel
  brakes, reverse, throttle). Declaring a channel you don't produce means taking responsibility for an
  actuator you aren't driving.

### Engagement (`ismpu/io/ics_engagement.py`)

The bench accepts our commands **only** after a correct handshake, and **the bench decides** whether we are
engaged — it confirms with `ICSInputs.AgentIsActive = 1`. Our side must not replicate the bench's
preconditions to *decide* we're engaged (that was a real bug); we only drive the **stimulus** and read the
confirmation. Until then `ControlValidMask = 0` and no actuator commands are emitted.

- Ground engagement from standstill: hold `ControlMode = Off` + `ModeAIReady = 1` for the dwell, then flip to
  `Taxi` (the `0 → 4` edge). Adoption of a rollout already in progress (`FlightPhase = LandRun`): emit
  `ControlMode = Rollout`. Handover rollout→taxi is `3 → 4` (`request_taxi`).
- The dwell requires **both** elapsed time and `ENGAGE_MIN_READY_FRAMES` frames actually sent
  (`on_frame_sent`). Time alone would let two polls 3 s apart satisfy "2 seconds of readiness" without
  transmitting anything.
- `ICSSim.warm_up` drives the stimulus at 20 Hz until the bench confirms, and **raises** `TimeoutError` with a
  named reason (`blocking_reason`) rather than proceeding — otherwise acceptance would count a run the bench
  never accepted.

## Sim object (`ismpu/envs/ics_sim.py`)

`ICSSim` is the whole simulator seam: `read_telemetry` / `step(ControlsState)` / `warm_up` /
`request_rollout` / `request_taxi` / `reset(scenario=None)` / `close`. It lives in `envs/`, not `io/`,
because it maps `ControlsState` → `ICSOutputs` and back — more than transport.

- `reset` does **not** configure anything: it resets the engagement automaton and returns the first frame.
  There is no teleport, pause, weather or failure injection to perform; the bench owns all of it.
- `Telemetry` is the SI-normalized view of `ICSInputs`. The bench sends knots, feet, ft/min and deg/s, and
  the whole control stack works in SI — **the unit boundary is here and nowhere else**. A missed conversion
  is not cosmetic: groundspeed in knots placed in a m/s field is off by 1.94×, and the longitudinal channel
  reads 140 kts as 272 and commands full braking.
- Bench-specific signals are **not duplicated into fields**. The raw packet rides along as `ics_inputs`, and
  `weight_on_wheels`, `flight_phase`, `runway_heading_deg`, `lateral_deviation_m`, `faults`, `weather`,
  `runway_condition`, `ias_ms`, `agent_is_active` are `@property` derived from it — one source of truth. They
  are therefore **not** constructor kwargs: to build bench-shaped telemetry, attach `ics_inputs=` (or use
  `from_ics`). `Telemetry.invalid()` is the "no link" frame — zeros with `valid=False`.
- `Telemetry.valid` must be checked **before** any field: on a receive timeout the frame is zeros, not `None`,
  and `groundspeed_ms = 0.0` is indistinguishable from "taxi speed reached".

## Control architecture (`ismpu/control/`)

The loop runs at 20 Hz (`DT = 0.05`). `ControllingSystem.control_step(dt)` syncs failures from telemetry,
calls two channels, applies failure degradation, then sends commands:

- **`LongitudinalChannel`** — speed control. Integrates traveled distance, looks up the target speed on
  a `ReferenceTrajectory` (default `GAUSS_BELL` decay curve; `EQUALLY_SLOW` = constant deceleration is
  the alternative), and drives four independent `PIDController`s: left/right hydraulic brakes and
  left/right thrust reversers. Reverser PIDs are bounded to `[-1, 0]`, so their output is already the
  negative-thrust value (no separate sign flip); reverse is force-disabled below 60 kts (with integrator
  reset). `rollout_started` latches once above 30 kts — without it a stationary aircraft trivially satisfies
  "taxi speed reached" and the loop dies on tick 1, before the 2 s handshake can even complete.
- **`LateralChannel`** — centerline hold. Guidance comes from **whatever the bench publishes**: if it reports
  `RunwayHeading` + `LateralDeviation`, `RunwayTracker.guidance_from_deviation` uses them directly; otherwise
  the geodetic path falls back to the runway endpoints in `config/runway.py`. Using hardcoded Sheremetyevo
  geometry on a different runway would steer the aircraft down someone else's centerline. One PID converts
  heading error to a rudder command, from which two differential mixes are added on top of the longitudinal
  commands: **differential braking** (`steering_brake_gain`) and **asymmetric thrust** (`steering_rev_gain`,
  only above 60 kts). The mixing runs *after* the longitudinal channel sets brake/reverse, so ordering matters.

`ControlsState` is the shared per-tick command struct (brakes, reversers, rudder) in **normalized** units —
millimetres and degrees appear only at the transport boundary (`ICSSim._to_outputs`). `break_control=True`
signals the loop to stop (target speed reached or missing telemetry). Hard output bounds are applied
**last**: `control_step` calls `ControlsState.clamp_all(pids)` after both channels, re-clamping every
command to its PID's `[min_out, max_out]` *after* the differential mixes. `control_exception` sends a
**neutral command**, not silence: going quiet leaves the last deflection applied until the bench's watchdog
fires.

### Failures (`FailureMode` / `FailureManager` / `FailureState`)

`FailureState` holds per-actuator efficiency multipliers (0.0–1.0). `ControlsState.apply_failures()`
multiplies the computed commands by them just before sending.

- **The bench is the source of truth.** Failures arrive as telemetry (`ICSInputs.Fault*` →
  `Telemetry.faults`), and `ControllingSystem.sync_failures` rebuilds the state **every tick** — a failure
  can appear mid-rollout, which "activated once at episode start" doesn't cover. `FailureManager.sync`
  rebuilds from scratch rather than accumulating, so a *cleared* failure is actually cleared.
- Two deliberate exceptions to syncing: an **invalid** frame leaves the state alone (one lost packet doesn't
  repair an actuator), and a frame with **no bench packet at all** (`ics_inputs is None` — synthetic telemetry
  in tests and offline analysis) is ignored entirely, because an empty `faults` there means "nobody reported",
  not "all healthy".
- Why degrade a command the bench will ignore anyway: the back-calculation feedback
  (`ControllingSystem._track_applied`) uses the *applied* command, so the integrator doesn't wind up against a
  dead actuator (classic windup at `steering_eff = 0`).
- Each failure case has its own hand-tuned set of PID gains, captured as `ScenarioConfig` presets in
  `ismpu/config/scenarios.py` (`DEFAULT`, `NWS_FAIL`, `LEFT_REVERSE_FAIL`, `RIGHT_REVERSE_FAIL`, plus weather
  presets). `NWS_FAIL` is calibrated for the real NWS failure (`steering_eff = 0`, rudder killed): centerline
  hold is carried by differential braking plus asymmetric thrust. The reverse presets were carried over from
  draft notebook cells and still need calibration.

## PID conventions (`PIDController`)

- Leaky integrator: `integral_decay > 0` applies exponential decay per tick (anti-windup beyond the hard
  `anti_windup` clamp).
- Derivative is low-pass filtered (`der_filter_tf`, first-order IIR) to reject telemetry noise; first
  tick emits zero derivative to avoid a startup kick.
- Output is clamped (via the `clamp()` method) to `[min_out, max_out]`: runway-center uses `[-1, 1]`,
  brakes `[0, 1]`, reversers `[-1, 0]` (already the negative-thrust sign). The same `clamp()` is reused
  by `ControlsState.clamp_all()` to bound the final commands after the differential mixes. `compute()`
  logs its internals via `logging.debug` on the `ismpu.control.pid` logger; the per-channel status lines
  use `cprint`.
- Gains are **empirically tuned per aircraft and per failure case** and are fragile. When changing plant
  behavior, expect to re-tune rather than derive.

## Weather (`ismpu/envs/weather.py`)

A pure data/scale module — **it does not set anything.** Weather is the bench's, and it reaches us only as
telemetry.

- `WeatherState.from_ics(inp)` is the single source of actual conditions: wind (kt), runway friction,
  precipitation, visibility (**feet → metres**; missing that conversion turns 16000 ft into "clear" instead
  of 4.9 km), temperature. Frozen dataclass — it is a reading, not a lever.
- `RunwayCondition` is **our monotone slipperiness scale 0…15**, and `runway_condition_from_bench` maps the
  bench's 7 codes onto it. This is not legacy: the bench's codes are not ordered by slipperiness (ICE=2 sits
  between WET=1 and FLOODED=3), so feeding the raw code to the network would state a false ordering. An
  unknown code maps to `ICY` — assuming a dry runway would authorize maximum braking where it will break the
  aircraft off the centerline.
- **Wind matters by component, not by magnitude**, so `compose_wind`/`decompose_wind` (and
  `WeatherState.from_crosswind`) convert to/from crosswind+headwind relative to the runway heading.
- `WEATHER_PRESETS` (clear_dry / wet / puddly / icy / snowy / crosswind / low_visibility) describe the
  conditions the control presets were calibrated for, and are what scenario selection matches against.

## Scenarios (`ismpu/envs/scenario.py`, `scenario_generator.py`)

`Scenario` is the episode descriptor: `control` (a `ScenarioConfig` — the PID/guidance preset), `failures`
and `weather`. Since we can't impose any of it, **`failures`/`weather` are matching keys, not commands**:

- `select_scenario(failures, weather)` / `select_for_telemetry(telemetry)` pick the preset calibrated for
  the conditions the bench is actually reporting. Failure mismatch dominates the score
  (`FAILURE_MISMATCH_PENALTY`) — no weather similarity compensates for running an NWS-tuned preset on a
  healthy aircraft. Draft presets are excluded unless asked for. Without telemetry the answer is `default`:
  it's the only safe choice when nothing is known about the airframe's configuration.
- Only `apply_control(controller)` acts on anything (it seeds fresh, stateful PIDs and the preset's failure
  as a starting assumption; telemetry overrides it from the next tick).
- `SCENARIO_PRESETS` mirrors `config.scenarios.SCENARIOS`. Serializable via `to_dict`/`from_dict`
  (`control` stored by preset name).
- `ScenarioGenerator(seed)`: domain randomization across weather and failures, curriculum via
  `difficulty ∈ [0,1]`, deterministic per seed. `battery()` is the fixed acceptance set. It now enumerates
  **which conditions the bench operator should set up**, in what order — it does not configure them.
- `envs/splits.py` (deterministic train/holdout split, hash-based so adding scenarios doesn't reshuffle) and
  `envs/reproducibility.py` (which conditions force replica validation) are unchanged in purpose; the named
  stochastic sources are now the bench's (`BENCH_WIND`, `BENCH_PRECIPITATION`, `BENCH_LOW_FRICTION`).
  Nothing on the bench is bit-reproducible from our side — we have neither a teleport nor its RNG seed — so
  acceptance takes the **worst** replica, never the mean (the ТЗ states limits as bounds).

## RL environment (`ismpu/envs/`, Phase 2)

The Gymnasium-compatible training env wrapping `ICSSim` + the classical controller (plan §5/§6).

- **`observation.py`** — `ObservationBuilder.build(telemetry, controller, weather=None, observer)` → a
  **56-dim** normalized frame (geometry 4 / speed 4 / last controls 5 / PID×5 dynamic state 30 / failure
  flags 3 / weather 5 / **observer slots 5**). `weather=None` (the normal path) reads conditions off the
  telemetry itself — an "expected" scenario weather would diverge from what the aircraft is actually
  experiencing. The PID `kp/ki/kd` slots encode the **absolute** current gains in gain-space log-norm
  (`gain_space.gain_norm_scalar`, = the net's previous output). `GAIN_FEATURE_INDICES` lists those 15 slots
  (used by ppo's `L_smooth` and SFT's anti-copycat masking). `FEATURE_NAMES` fixes the order; invalid
  telemetry → zero frame.
- **`agent/normalization.py`** — fixed physical scales (constants, not batch stats); `snapshot()` includes the
  `gain_space` table and is serialized with the weights.
- **`action.py`** — action is `(17,) = [gains×15, w_lon, w_lat]` (**absolute** kp/ki/kd, `GainCommand` layout).
  `apply_corrections(command, preset_gains, controller, shield)` writes the gains into `controller.pids` and
  channel weights (optionally via the preset-anchored Shield). `REFERENCE_ACTION` = DEFAULT gains;
  `preset_action(preset)` (float64, exact) reproduces a scenario's classical behaviour.
- **`reward.py`** — per-component reward (lateral / speed / jerk / shield / heading / instability), thresholds
  from `config/requirements.py`. Pure function. `EpisodeObjective` is the episode-level version used by
  acceptance and SFT label weighting.
- **`rollout_env.py`** — `RolloutEnv(reset/step)`, obs-history ring buffer emitting the window as a
  **sequence `(history_len, 56)`** (the NPGS input), optional Shield in the inference path. Gymnasium is
  imported **optionally** (spaces are `Box` if installed, else a tiny `_SimpleBox`). `reset` runs the
  handshake **before** the first step so warm-up ticks don't land in `_steps`, the reward or the objective —
  the aircraft wasn't ours during them. **Parity:** `env.step(preset_action(preset))` (shield off) is
  bit-for-bit equal to the classical `control_step` for that scenario (`tests/test_rollout_env.py`).
- Small additive control-loop hooks (classical behaviour unchanged at defaults): `PIDController.last_output`,
  channel `w_lon`/`w_lat` (× PID outputs before `clamp_all`), `ControllingSystem.control_step(send=False)` and
  `set_channel_weights`.

## Shield — safety contour (`ismpu/agent/shield.py`)

Deterministic guard between the neural actor and the classical PID loop (plan §9). It is **not** trained,
is always active, and the network can't issue a command that bypasses it.

- The actor's output is `GainCommand`: **absolute** `kp/ki/kd` per regulator (5 × 3 = 15) plus channel weights
  `w_lon/w_lat` (`ACTION_DIM = 17`; `from_vector`/`to_vector`/`from_gains`).
- **The per-scenario preset is the safety anchor** (passed to `guard_coefficients` as `preset_gains`): the net
  emits absolute gains, but the Shield still centers the allowed corridor on the certified preset.
- **Three levels + fallback:** (1) clip gains to the physical band `[lo,hi]` (`gain_space`), weights to `[0,2]`;
  (2) hard bounds `[hard_low·preset, hard_high·preset]` + non-negativity + per-tick rate-limit + OOD detector;
  (3) runtime checks on the resulting `ControlsState` — reverse below 60 kts, brake jerk, heading divergence.
  OOD or a gross heading blow-out latches a **fallback** that writes the **preset gains** directly (certified
  classical). This preset-as-bound/fallback is the ТЗ-compliance argument (bounded advisory, not "net is
  controller").
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
  Reverse→L/R(6), Weights→`(w_lon,w_lat)`. **17 policy outputs = ACTION_DIM** (L/R brake/reverse are
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
Obs must come from the live `ObservationBuilder` (the PID block — integral/deriv/last_output — isn't in the bench's
telemetry packet, so reconstructing it from raw fields is wrong). `agent/pretrain.py::pretrain_sft` regresses the
policy `mean → target_z` (MSE, `log_std` frozen). **Anti-copycat (critical):** the obs carries "previous gains" and
the BC target is constant per rollout, so the net could just copy the input; `pretrain` replaces the gain features
with **fresh U(−1,1) noise per batch** (not zeros — real values are in `[−1,1]` too, so no train/inference shift),
forcing the net to key on the disturbance (failure/weather) features. Canonical labeling: each **non-draft** preset
(`ScenarioConfig.draft`) is its own regime run in its own conditions; never mix inconsistent labels. Which
conditions the bench actually produces is the operator's call — runs that don't match their preset are filtered by
the quality scoring in `capture.py` (ТЗ gate → reject, saturation/Shield → half weight).
`runtime/pretrain.py` orchestrates capture→BC→checkpoint (`npgs_sft.pt`); `smoke_pretrain(env, scenarios)` is the
offline (no-bench) path used in `tests/test_pretrain.py`. `train.py` loads it via `TrainConfig.init_from`;
`ppo.lambda_anchor>0` additionally keeps a frozen SFT copy as `trainer.sft_reference` (anti-forgetting).

## PPO training (`ismpu/agent/ppo.py`, `ismpu/runtime/train.py`, plan §11)

Compact CleanRL-style PPO over a **single** env (the bench is one instance). `PPOTrainer.collect` fills a
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
`runtime/train.py` builds env + controller over one `ICSSim`, the curriculum ramps `difficulty` via
`ScenarioGenerator`, Shield sits in the actor's inference path, and it checkpoints weights+normalization + a
per-term CSV. **Episode boundaries belong to the bench:** a curriculum scenario changes which preset the episode
starts from, not the environment — the conditions themselves are arranged with the bench operator.
`smoke_train(env, provider)` runs the loop offline (no bench) — see `tests/fakes.py`'s `KinematicBench`.

## Acceptance (`ismpu/runtime/evaluate.py`, Phase 5)

Per-criterion ТЗ verdicts (criterion → limit → measured → verdict) plus mandatory baseline comparison
(DEFAULT gains, scenario preset "oracle", SFT checkpoint, PPO checkpoint). Rules worth preserving: **missing
data is FAIL**, not "conditionally passed", while genuinely inapplicable criteria are `SKIP` **with a named
reason** so nothing is silently dropped; and `admit_checkpoint` gates release on how the result was achieved
(command saturation, Shield fallbacks, p95 command rate), not just on the limits. Holdout is scored separately
— mixed into training it would measure memorization, not transfer.

## Units & geo

- `ismpu.utils.converts.Converts` holds all unit conversions (kts↔m/s, ft↔m, etc.) and `dms_to_float` for
  DMS coordinates. Use these constants rather than inlining magic numbers.
- `RunwayTracker` (`ismpu/control/runway_tracker.py`) does spherical-earth geodesy (haversine distance,
  bearing, direct geodesic `destination`) plus `guidance_from_deviation` for the bench-supplied path.
  Runway endpoints and heading live in `ismpu/config/runway.py` — they are the **fallback** used only when
  the bench doesn't publish runway geometry; changing the target runway means editing `RWY_START_*`/
  `RWY_END_*`/`RWY_HEADING_TRUE` there.
