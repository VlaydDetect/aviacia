# Graph Report - GOSNIIASProject  (2026-08-16)

## Corpus Check
- 152 files · ~177,673 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2867 nodes · 6617 edges · 197 communities (132 shown, 65 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 468 edges (avg confidence: 0.62)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `21229ca0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- run_report.py
- shield.py
- RolloutEnv
- test_weather.py
- Shield
- json_config.py
- SimInterface
- airborne_inputs
- Scenario
- GainSpace
- ground_allocator.py
- LateralChannel
- test_pretrain.py
- ControlsState
- ICSOutputs
- test_run_matrix.py
- AircraftProfile
- ._fill_airborne
- ApproachController
- ics_sim.py
- weather.py
- XPlaneSim
- WeatherState
- PIDController
- evaluate.py
- DashboardState
- test_xplane_backend.py
- test_evaluate.py
- test_ppo.py
- IcsEngagement
- XPlaneConnectX
- RunRecorder
- test_splits.py
- Graphify Pipeline
- XPlaneConnector
- .from_preset
- .from_ics
- test_ics_engagement.py
- RunReader
- FakeConnector
- pid_controller.py
- fakes.py
- NPGS
- runner.py
- test_gain_scheduler.py
- 3. Этапы реализации
- ScenarioGenerator
- ValueError
- Path
- test_full_flight.py
- test_go_around.py
- Neural PID Gain Scheduler Architecture
- test_approach_criteria.py
- ._approach_step
- run_artifacts.py
- RunwayTracker
- RomanLogImporter
- ICSInputs
- test_dashboard.py
- static_sim
- gain_space_for
- test_control_parity.py
- Project Dependencies
- test_ground_controller.py
- .invalid
- ICSInputs
- dashboard_core.py
- test_rollout_env.py
- test_working_ics_dashboard.py
- ICSOutputs
- Telemetry
- Unified Profile-Aware Scenario System
- Interactive PID Dashboard
- run_matrix.py
- ClearWeatherILSController
- scenario_signature
- ICSInterface.cs
- heading_deviation_deg
- runtime/pretrain.py
- promote_candidate.py
- ICS PID Monitor
- ICSInputs
- ICS UDP JSON Protocol
- X-Plane Dashboard and Runtime Guide
- test_working_ics_golden.py
- EpisodeObjective
- .__init__
- scenarios.py
- import_workbook
- test_approach_channel.py
- LongitudinalChannel
- test_action_contract.py
- base_gains_from_pids
- ICSSim
- loop.py
- reward.py
- conftest.py
- agent/__init__.py
- config/__init__.py
- _WarmUpSim
- control/__init__.py
- envs/__init__.py
- gui/__init__.py
- ismpu/__init__.py
- io/__init__.py
- runtime/__init__.py
- tools/__init__.py
- utils/__init__.py
- ismpu
- IntEnum
- test_campaign.py
- Q: Реализовать этап 0: baseline, golden replay и dashboard characterization
- Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md).
- ICSBenchConnector
- normalization.py
- test_ics_sim.py
- Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md).
- admit_checkpoint
- IntEnum
- ControlModeState
- ICSInputs
- ICSOutputs
- socket
- engaged_sim
- .from_json
- GuidanceState
- .compute
- train.py
- WeatherState
- Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md).
- Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md).
- pid.py
- ApproachLimits
- .enter_segment
- ApproachTelemetry
- Q: Приступай к выполнению этапа 2 плана docs/plan.md
- ICSInputs
- verdict_of
- compute_reward
- ApproachConfig
- ControllingSystem
- .rudder_cmd
- .__init__
- ControlModeState
- ApproachChannel
- ICSOutputs
- ApproachConfig
- FailureState
- AircraftProfile
- ControlsState
- PidMap
- RunwayProfile
- PidMap
- StartMode
- .enter_segment
- holdout_reason
- Scenario
- Path
- Q: Приступай к выполнению этапа 4 плана docs/plan.md
- ReferenceTrajectory
- RewardWeights
- TypedDict
- Scenario
- SimInterface
- aircraft_profiles.py
- CompletionRule
- action.py
- HandshakeBench
- ApproachSetup
- on_ground
- ICSInputs
- FailureMode
- Scenario
- ConditionMatch
- .from_ics
- ._should_go_around
- TouchdownSetup
- .__init__
- ResilientSender
- render_report
- DatagramSocket
- Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md).
- test_adopts_rollout_from_the_flight_phase
- .confirmed
- .request_landing
- AircraftProfile
- Any
- ApproachConfig
- FailureMode
- FlightSegment
- WeatherState
- StartMode
- ndarray
- ControllingSystem
- RunResult
- Scenario
- SimInterface

## God Nodes (most connected - your core abstractions)
1. `ControllingSystem` - 156 edges
2. `Telemetry` - 105 edges
3. `ControlsState` - 92 edges
4. `Scenario` - 72 edges
5. `ICSSim` - 69 edges
6. `XPlaneSim` - 54 edges
7. `PIDController` - 53 edges
8. `GainSpace` - 47 edges
9. `RolloutEnv` - 45 edges
10. `airborne_inputs()` - 45 edges

## Surprising Connections (you probably didn't know these)
- `Autonomous Landing Controller` --semantically_similar_to--> `Autonomous Landing Controller`  [INFERRED] [semantically similar]
  CLAUDE.md → AGENTS.md
- `Profile-Aware Flight Scenarios` --semantically_similar_to--> `Unified Scenario System`  [INFERRED] [semantically similar]
  docs/XPLANE_DASHBOARD.md → implementation_plan.md
- `Acceptance and Evaluation Harness` --semantically_similar_to--> `Technical-Specification Acceptance Gates`  [INFERRED] [semantically similar]
  implementation_plan.md → AGENTS.md
- `X-Plane Resettable Runtime` --semantically_similar_to--> `X-Plane Training and Evaluation Backend`  [INFERRED] [semantically similar]
  docs/XPLANE_DASHBOARD.md → implementation_plan.md
- `DatagramSocket` --uses--> `SegmentConditions`  [INFERRED]
  tests/test_xplane_backend.py → ismpu/config/scenarios.py

## Import Cycles
- 3-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 3-file cycle: `ismpu/config/scenarios.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 3-file cycle: `ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/control/channels.py`
- 3-file cycle: `ismpu/config/aircraft_profiles.py -> ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/config/aircraft_profiles.py`
- 4-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 4-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/tolerance.py -> ismpu/control/approach.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/aircraft_profiles.py -> ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py -> ismpu/config/aircraft_profiles.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/flight.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/ground_allocator.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach_criteria.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/tolerance.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`

## Hyperedges (group relationships)
- **Graphify Extraction and Build Flow** — _codex_skills_graphify_skill_structural_extraction, _codex_skills_graphify_skill_semantic_extraction, _codex_skills_graphify_references_extraction_spec_semantic_extraction_contract, _codex_skills_graphify_references_update_build_merge [EXTRACTED 1.00]
- **Hybrid Neural Landing Control** — implementation_plan_classical_pid_plant, implementation_plan_npgs, implementation_plan_deterministic_shield, implementation_plan_ppo_multicomponent_loss, implementation_plan_pinn_observer [EXTRACTED 1.00]
- **PID Dashboard Ecosystem** — docs_xplane_dashboard_pid_dashboard, ismpu_gui_dashboard_pid_dashboard, ismpu_working_ics_ics_dashboard_ics_pid_monitor [INFERRED 0.85]

## Communities (197 total, 65 thin omitted)

### Community 0 - "run_report.py"
Cohesion: 0.05
Nodes (71): lateral_limit_m(), lateral_load_situation(), lateral_situation(), normal_load_situation(), IntEnum, Критерии критичности особых ситуаций МС-21 (Приложение 1 к ТЗ). Таблица АП-25…, Классификация скорости касания относительно VAPP и VВПП пред., Классификация нормальной перегрузки посадочного удара. `heavy` — взлётный вес. (+63 more)

### Community 1 - "shield.py"
Cohesion: 0.14
Nodes (11): _clip(), GainCommand, GainMap, RegulatorKey, Shield — детерминированный защитный контур между актором и классическим PID.…, Что сделал Shield за такт: активированные правила, штрафы, fallback., Уровни 1–2. Возвращает `(effective_gains, safe_command, report)`.…, Выход актора: абсолютные коэффициенты PID + веса каналов. `gains[reg] =… (+3 more)

### Community 2 - "RolloutEnv"
Cohesion: 0.12
Nodes (12): Tensor, Шагает средой `rollout_len` тактов (сброс по завершению эпизода). → статистика., Хук L_shield (§11): барьер, отталкивающий выход от края уровня-1 Shield. По…, ndarray, Копия команды такта — для расчёта джерка на следующем такте. Копируется…, Окно истории → тензор `(history_len, OBS_DIM)` (последовательность кадров для…, Состояние для поведенческих проверок Shield. Курс здесь — отклонение от…, RolloutEnv (+4 more)

### Community 3 - "test_weather.py"
Cohesion: 0.10
Nodes (22): compose_wind(), decompose_wind(), Any, Собирает ветер из компонент относительно курса ВПП. `crosswind_kts` > 0 — ветер…, Сериализация в примитивы (для логирования/воспроизводимости сценариев)., (скорость, откуда) → (crosswind, headwind) относительно курса ВПП. crosswind >…, (crosswind, headwind) → (скорость, откуда, °). Обратна `decompose_wind`., test_scenario_roundtrip_with_weather_and_failures() (+14 more)

### Community 4 - "Shield"
Cohesion: 0.13
Nodes (26): Наблюдаемое состояние для поведенческих проверок уровня 3., Границы и веса штрафов Shield (все — настраиваемые, а не свойства сети)., Защитный контур. Детерминирован; хранит состояние прошлого такта для rate-…, Bind the guard to the same aircraft-specific space as the actor., Уровень 3. Правит небезопасные команды и возвращает `(command, report)`., Построение из словаря коэффициентов (напр. пресета сценария)., RuntimeState, Shield (+18 more)

### Community 5 - "json_config.py"
Cohesion: 0.14
Nodes (35): approach_control_from_dict(), approach_control_to_dict(), _copy_approach(), dump_scenario(), _finite_tree(), ground_control_from_dict(), ground_control_to_dict(), _legacy_ground() (+27 more)

### Community 6 - "SimInterface"
Cohesion: 0.09
Nodes (7): BaseException, Минимальный lifecycle, одинаковый для стенда и X-Plane., Результат безусловного best-effort отключения backend., ShutdownReport, SimInterface, Protocol, StartMode

### Community 7 - "airborne_inputs"
Cohesion: 0.08
Nodes (42): airborne_inputs(), Кадр «ВС на глиссаде»: стойки не обжаты, ILS валиден, скорость и высота…, _colleague_controller(), _descent_frames(), _our_channel(), Страховка от самообмана: сценарий обязан пройти выравнивание, иначе паритет его…, Угол сноса не должен превращаться в ошибку курса на локализаторе., Стенд иногда сбрасывает Valid при сохранении пригодного численного значения. (+34 more)

### Community 8 - "Scenario"
Cohesion: 0.20
Nodes (14): AircraftProfile, FailureMode, FlightSegment, match_conditions(), _profile_name(), Полный профильный сценарий APPROACH → ROLLOUT → TAXI., Условия пробега для report/eval-кода, работающего только на земле., Scenario (+6 more)

### Community 9 - "GainSpace"
Cohesion: 0.17
Nodes (10): GainKey, GainSpace, Any, ArrayLike, float64, GainMap, NDArray, RegulatorKey (+2 more)

### Community 10 - "ground_allocator.py"
Cohesion: 0.19
Nodes (15): LateralDiagnostics, LongitudinalDiagnostics, FailureState, Эффективности исполнительных органов. Аннотации типов обязательны: без них…, ActuatorFeedback, ActuatorVector, AllocationDiagnostics, _clamp() (+7 more)

### Community 11 - "LateralChannel"
Cohesion: 0.24
Nodes (6): GuidanceState, LateralChannel, Блок 2: runway guidance → единый нормированный yaw-запрос., Guidance по тому, что даёт стенд. → словарь guidance или None, если данных нет.…, Единый GuidanceState текущего кадра для control/observation/reward., RunwayTracker

### Community 12 - "test_pretrain.py"
Cohesion: 0.07
Nodes (46): _phase_labels(), pretrain_sft(), PretrainConfig, float32, GainMap, NDArray, Tensor, SFT (behavioral cloning) — предобучение NPGS предсказывать эталонные… (+38 more)

### Community 13 - "ControlsState"
Cohesion: 0.15
Nodes (24): ControlsState, Обнуляет все органы управления. Отправку делает вызывающий через `ICSSim.step`.…, Разделяемая по тактам структура команд — и наземных, и воздушных. Аннотации…, Сброс к нейтральным командам — новый эпизод начинается с чистого состояния.…, Обнулить только воздушные команды. Нужно, когда воздушный канал не может…, build_altitude_sweep(), command_for_pulse(), Безопасные elevator/altitude authority sweep без дублирования ICS runner. (+16 more)

### Community 14 - "ICSOutputs"
Cohesion: 0.11
Nodes (21): GearState, ICSOutputs, Разбор телеметрии стенда с совместимостью вперёд. Асимметрия намеренная (JSON-…, _connector(), _FakeSocket, _full_payload(), Транспорт стенда: разбор телеметрии и отправка команд. На проводе чистый JSON…, Подставить ноль значило бы выдумать телеметрию, по которой считается управление. (+13 more)

### Community 15 - "test_run_matrix.py"
Cohesion: 0.12
Nodes (21): resolve_matrix_run(), compose_matrix_scenario(), matrix_battery(), Перенести накопленные overrides одного шифра на следующее условие этого же…, Ожидаемые физические условия одного участка., Собрать сценарий из конкретных строк APPROACH/ROLLOUT/TAXI.…, Одна строка каталога → минимальный сценарий нужного участка или сквозной пары., rebind_matrix_run() (+13 more)

### Community 16 - "AircraftProfile"
Cohesion: 0.10
Nodes (10): AircraftProfile, clamp(), Преобразовать воздушные команды ICD в нормированные DataRef X-Plane., Преобразовать нормированные команды пробега в DataRef X-Plane., Расширение реестра будущим профилем МС-21 без правки XPlaneSim., Проводка и масштабы конкретного планера X-Plane., Общая идентичность ЛА и необязательная привязка к X-Plane. Профиль нужен и…, Command refs retained under the historical public name. (+2 more)

### Community 17 - "._fill_airborne"
Cohesion: 0.18
Nodes (9): ControlsState, _clamp(), Гонит стимул рукопожатия, пока стенд не подтвердит включение (`AgentIsActive =…, Желаемый уровень реверса [-1, 0] → скорость перемещения РУД (°/с). Тягой (в том…, `ControlsState` → `ICSOutputs` (единицы ICD), **по текущему участку полёта**.…, Воздушный участок: перегрузка, элероны и скорости РУД. `ModeFlare` повторяет…, Пробег и руление: тормоза, путевое управление, реверс. Путевой орган **зависит…, Фактический угол РУД из последнего кадра стенда; 0 при отсутствии кадра.… (+1 more)

### Community 18 - "ApproachController"
Cohesion: 0.13
Nodes (23): ApproachConfig, Параметры воздушного контура. Значения по умолчанию — настроенные на стенде.…, ApproachController, ApproachResult, clamp(), ApproachLimits, ApproachTelemetry, Заход по ILS с выравниванием. Телеметрию получает параметром, не читает сам.… (+15 more)

### Community 19 - "ics_sim.py"
Cohesion: 0.11
Nodes (23): Настройки воздушного участка: заход по ILS, выравнивание, управление скоростью.…, Глобальные константы контура управления (перенесены из main.ipynb)., Константы интерфейса стенда заказчика (ПИВ / ICS). Единый источник правды по…, Приёмочные пороги из ТЗ (раздел 5). Единый источник истины для reward-шейпинга…, Канонические участки управляемого интервала полёта., Воздушный канал: заход по ILS, выравнивание, управление скоростью. Перенос…, Каналы управления и общий вектор команд. `ControlsState` — разделяемая по…, Модель отказов бортового оборудования. `FailureState` хранит мультипликативные… (+15 more)

### Community 20 - "weather.py"
Cohesion: 0.08
Nodes (27): Observation Space — сборка и нормировка вектора состояния (§5). Собирает один…, Генератор сценариев обучения (domain randomization). Сэмплирует `Scenario` из…, Enum, Погодные условия эпизода: описание, шкала сцепления и разбор ветра. Модуль **не…, Состояние ВПП как **монотонная шкала скользкости** 0…15 (0 — сухо, 15 — лёд со…, Код состояния ВПП со стенда → наша шкала. Неизвестный код трактуется как `ICY`,…, runway_condition_from_bench(), RunwayCondition (+19 more)

### Community 21 - "XPlaneSim"
Cohesion: 0.11
Nodes (7): _destination(), ApproachData, Backend-независимый срез сигналов для захода и ухода на второй круг., XPlaneDiagnostics, ControlsState, StartMode, XPlaneSim

### Community 22 - "WeatherState"
Cohesion: 0.12
Nodes (20): _as_dict(), contract_for(), Any, Контракт воспроизводимости эпизода (шаг 6). Заимствовано из…, Худшая реплика по заданной метрике. Приёмка смотрит именно на худшую, а не на…, Источники случайности на стороне стенда, активные при данных условиях. Мы…, Что в эпизоде детерминировано, что нет, и сколько реплик из-за этого нужно., Даст ли повторный прогон с тем же сидом ту же траекторию. (+12 more)

### Community 23 - "PIDController"
Cohesion: 0.11
Nodes (29): PIDController, Сброс внутренних состояний (используется при выключении системы)., _legacy_reference(), Опциональная численность PID (шаг 5): каждый флаг проверяется на том дефекте,…, Если применено ровно то, что выдал PID, коррекции быть не должно., Уставка прыгает, объект стоит на месте — D-составляющая не должна реагировать.…, Выход ИЗ насыщения должен разрешаться всегда, иначе регулятор залипнет. kp…, Если насыщает уже пропорциональная часть, интегрировать нельзя вообще — и это… (+21 more)

### Community 24 - "evaluate.py"
Cohesion: 0.09
Nodes (27): compare_policies(), DefaultGainsPolicy, load_npgs_policy(), main(), NPGSPolicy, Policy, PresetPolicy, Приёмка по ТЗ (разд. 5) + обязательное сравнение с baseline'ами (Этап 5). Схема… (+19 more)

### Community 25 - "DashboardState"
Cohesion: 0.13
Nodes (7): DashboardState, GainChange, _handler_factory(), _jsonable(), Path, HTTP читает только immutable recorder objects; controller меняет control-thread., Вызывается runtime ровно в начале control tick.

### Community 26 - "test_xplane_backend.py"
Cohesion: 0.10
Nodes (15): test_xplane_ignores_failures_outside_rollout_contract(), MockXPlaneConnector, ScriptedXPlaneConnector, test_commands_failures_and_close_release_overrides(), test_exact_taxi_row_starts_xplane_and_controller_in_taxi_at_15_knots(), test_failed_approach_setup_releases_overrides_and_pause(), test_ignored_xplane_failure_participates_in_segment_delta_and_is_cleared(), test_missing_or_stale_required_data_makes_xplane_telemetry_invalid() (+7 more)

### Community 27 - "test_evaluate.py"
Cohesion: 0.16
Nodes (27): evaluate_tz(), Диагностика эпизода + сценарий → список вердиктов по пунктам ТЗ разд. 5., _by_name(), _diagnostics(), Тесты приёмки по ТЗ (Этап 5): вердикты по пунктам, правило «нет данных = FAIL»,…, Эпизод не дошёл до руления → допуск ±1 м неприменим. Это SKIP, а не тихий…, Пустой эпизод — это отсутствие данных, а не неприменимость требования., При отказе NWS руль мёртв, ось держится дифференциальным торможением → ±5 м… (+19 more)

### Community 28 - "test_ppo.py"
Cohesion: 0.13
Nodes (24): PPOConfig, PPOTrainer, Any, device, PPO-тренер + многокомпонентный loss для NPGS (план §11). `L = L_ppo +…, Собирает rollout из среды и обновляет NPGS многокомпонентным PPO-loss., Плоский буфер одного env: obs-окна, сырые действия, logp/value/reward/done., RolloutBuffer (+16 more)

### Community 29 - "IcsEngagement"
Cohesion: 0.05
Nodes (27): ControlModeState, EngagementInputs, IcsEngagement, Автомат включения. `step(inputs)` вызывается каждый такт до формирования…, Полный сброс — новый эпизод начинается с невключённого состояния., Сообщить автомату, что кадр **фактически ушёл** на стенд. Вызывается…, Подхватить уже включённый извне пробег: шлём `ControlMode = Rollout`.…, Войти в пробег самостоятельно: шлём `ControlMode = Rollout`. Это же — передача… (+19 more)

### Community 30 - "XPlaneConnectX"
Cohesion: 0.08
Nodes (13): XPlaneConnectX class initialization. Args: ip (str, optional): IP address where…, Starts a recording of the subscribed DataRefs into self.recorded_data. Data is…, Terminates the recording and returns a dictionary of lists that contain the…, Synchronize measurements from multiple sensors to a common frequency.…, Gets the current value of a DataRef. This is only intended for one-time use.…, Permanently subscribe to a list of DataRefs with a certain frequency. This is…, Writes a value to the specified DataRef provided that the DataRef is writable.…, Sends simulator commands to the simulator. These are not commands for the… (+5 more)

### Community 31 - "RunRecorder"
Cohesion: 0.15
Nodes (8): Exception, Подключить best-effort аудит сырых успешно принятых/отправленных UDP payload., Append-only writer; ошибка диска помечает прогон, но не выходит в control-loop., Атомарный incremental slice для dashboard, без чтения controller., Сохранить полный effective config; канонические config-файлы не затрагиваются., RunEvent, RunRecorder, test_recorder_pins_selected_matrix_rows_and_catalog_hash()

### Community 32 - "test_splits.py"
Cohesion: 0.12
Nodes (30): Сколько раз прогнать сценарий, чтобы результат приёмки что-то значил., required_replicas(), assert_no_leakage(), has_holdout_failure(), Детерминированное разбиение сценариев на обучение и holdout (шаг 6). Схема…, Затрагивает ли сценарий зарезервированное семейство отказов., Разбивает набор сценариев. Детерминировано и устойчиво к добавлению новых…, Проверяет, что holdout не пересекается с обучением по идентификаторам. Дешёвая… (+22 more)

### Community 33 - "Graphify Pipeline"
Cohesion: 0.08
Nodes (29): Folder Watcher, URL Ingestion, Extra Graph Exports, MCP Graph Server, Confidence Audit Trail, Deterministic Node IDs, Semantic Extraction Contract, Cross-Repository Graph Merge (+21 more)

### Community 34 - "XPlaneConnector"
Cohesion: 0.07
Nodes (12): DataRefSample, Неблокирующий UDP-клиент нативного протокола X-Plane 12., Discard pre-reload values so readiness cannot use stale telemetry., Одна подписка, один поток приёма и явное освобождение ресурсов., Send basic controls to the ego aircraft. There are hundreds of DataRefs that…, Разобрать пакет; публично для детерминированных mock-тестов., Совместимое read-only представление старого XPlaneConnectX., Совместимость с прежним клиентом. (+4 more)

### Community 35 - ".from_preset"
Cohesion: 0.10
Nodes (26): Готовый кадр `Telemetry` для прямых вызовов `control_step(dt, telemetry,…, telemetry(), Без `begin_flight` участок остаётся пробегом — среда обучения на это и…, test_the_rollout_default_keeps_the_existing_ground_behaviour(), test_failed_reverse_is_excluded_and_yaw_compensation_uses_remaining_organs(), test_reverse_failure_compensation_survives_guidance_dropout(), test_scenario_completion_rules_match_the_matrix(), Кадр без пакета стенда: пустой `faults` значит «сообщать некому», а не «всё… (+18 more)

### Community 36 - ".from_ics"
Cohesion: 0.10
Nodes (19): `ICSInputs` → `Telemetry`: поля в СИ + «сырой» пакет для property. Стенд отдаёт…, Носовая стойка обжимается позже основных — ждать её значит пропустить начало…, «Козление» после касания снимает обжатие на секунду — назад в заход…, В такте касания команда обязана быть уже наземной, а не последней командой…, Таблицы захода МС-21 к чистому крылу неприменимы — вести по ним нельзя.…, Нулевое отклонение при снятой валидности неотличимо от «точно на оси»., Ниже 80 футов до земли секунды — бросать органы там хуже, чем доработать., Пересмотр — только для отложенного решения, не для принятого. (+11 more)

### Community 37 - "test_ics_engagement.py"
Cohesion: 0.11
Nodes (43): _Clock, _engine(), _pump(), Автомат включения управления на стенде. Два раздельных предмета проверки: *…, По ICD стенд должен два секунды ПОЛУЧАТЬ ModeAIReady=1. Если считать одно лишь…, Обратная защита: 30 кадров можно выпалить за 0.1 с — время тоже обязано пройти., Срыв предусловия обнуляет и время, и счётчик кадров., Требование ICD — непрерывность: пропуск готовности рвёт серию. (+35 more)

### Community 38 - "RunReader"
Cohesion: 0.08
Nodes (20): _load_updates(), После recorder.finish держать полный run доступным, но только для чтения., Один такт: вход, команда и диагностика имеют общий ``tick_id``., RunSample, _apply_recorded_gains(), _equal(), main(), _number() (+12 more)

### Community 39 - "FakeConnector"
Cohesion: 0.10
Nodes (20): FakeConnector, make_ics_inputs(), Статический стенд: всегда один и тот же кадр, отправленное — в `sent_outputs`., Отправленные команды в нормированном виде — для сравнения траекторий.…, Полный пакет стенда: нули по умолчанию + заданные поля., Неизвестный код — не повод предполагать сухую полосу., Погоду задаёт Заказчик; наш `WeatherState` — это прочитанный кадр, а не задание., До рукопожатия заявлять каналы нельзя: стенд ещё не разрешил нам ими управлять. (+12 more)

### Community 40 - "pid_controller.py"
Cohesion: 0.13
Nodes (22): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+14 more)

### Community 41 - "fakes.py"
Cohesion: 0.10
Nodes (23): find_earth_nav_dat(), get_runway_profile(), ILSStation, parse_ils_station(), Path, Профили ВПП и разрешение ILS из установленной базы X-Plane., Найти LOC (тип 4) без хардкода частоты., RunwayProfile (+15 more)

### Community 42 - "NPGS"
Cohesion: 0.16
Nodes (13): floating, NPGS, float32, NDArray, Tensor, Neural PID Gain Scheduler: общий энкодер + головы актора (абс. gain'ы) + голова…, → (mean (B,17), value (B,), phase_logits (B,n_phases))., 17 сырых выходов → [абс. gains×15, w_lon, w_lat] (layout `REGULATOR_ORDER` +… (+5 more)

### Community 43 - "runner.py"
Cohesion: 0.18
Nodes (20): ControlResult, airborne_control_mode(), airborne_flare_mode(), deactivate(), live_main(), main(), main_gear_contact(), make_airborne_output() (+12 more)

### Community 44 - "test_gain_scheduler.py"
Cohesion: 0.07
Nodes (28): int64, ActorOutput, build_npgs(), _init_log_std(), layer_init(), _mlp_head(), NPGSConfig, phase_labels_from_groundspeed_kts() (+20 more)

### Community 45 - "3. Этапы реализации"
Cohesion: 0.09
Nodes (21): 1. Подтверждённые проблемы и целевое состояние, 2. Ключевые интерфейсы, 3. Этапы реализации, 4. Тестирование и критерии готовности, 5. Зафиксированные допущения, 6.1. Один dashboard вместо двух, 6.2. Единый источник данных, 6.3. Представления (+13 more)

### Community 46 - "ScenarioGenerator"
Cohesion: 0.15
Nodes (10): Один случайный сценарий. `difficulty=None` → случайная сложность., ScenarioGenerator, test_battery_covers_key_cases_and_roundtrips(), test_generator_embeds_control_config(), test_generator_high_difficulty_produces_failures(), test_generator_is_deterministic_for_same_seed(), test_generator_samples_are_valid_and_serializable(), test_generator_zero_difficulty_has_no_failures() (+2 more)

### Community 47 - "ValueError"
Cohesion: 0.10
Nodes (15): Any, compose_scenario(), ControlProfile, _materialize_override(), Применить одноуровневый sparse patch и вернуть полный неизменяемый config., Базовые законы одного профиля ЛА и sparse override конкретных строк матрицы., Совместимое чтение старого контракта; канонический источник — ``statuses``., Serialize only the canonical profile- and matrix-aware schema v3. (+7 more)

### Community 49 - "test_full_flight.py"
Cohesion: 0.10
Nodes (33): IntFlag, ControlValid, Биты `ControlValidMask`: какие каналы несёт команда. **Один бит на одно…, EngagementState, Enum, Состояние **исходящего стимула** (что мы шлём стенду), а не факта включения.…, _air(), _Clock (+25 more)

### Community 50 - "test_go_around.py"
Cohesion: 0.14
Nodes (25): GoAroundManeuver, Состояние идущего ухода на второй круг. Пока он активен, заход не ведётся., _armed_controller(), _drive(), _frame(), Уход на второй круг (fallback в воздухе): условия срабатывания и передача…, На пробеге ухода нет — segment guard (козление удерживает защёлка сегмента,…, Если реверс уже включён — взлёт невозможен, ухода нет. (+17 more)

### Community 51 - "Neural PID Gain Scheduler Architecture"
Cohesion: 0.19
Nodes (19): Hybrid Neural PID Controller, Neural PID Gain Scheduler, PPO Training Loop, Preset-Anchored Deterministic Shield, SFT Behavioral-Cloning Warm Start, Absolute-Gain Action Space, Classical PID as the Plant, Deterministic Deployment Runtime (+11 more)

### Community 52 - "test_approach_criteria.py"
Cohesion: 0.19
Nodes (12): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, Отдельный монитор критерия А.1.1 (не участвует в go-around)., Захватывает А.1.1 после входа в допуск и завершает оценку на 300 ft., frame() (+4 more)

### Community 53 - "._approach_step"
Cohesion: 0.08
Nodes (22): approach_blocker(), ApproachRefused, at_lateral_alignment_gate(), ils_blocker(), in_terminal_window(), Последние футы перед касанием, где прерывать заход опаснее, чем доработать.…, Полоса подхода к гейту совмещения с осью ± 5 м: `(30 м, 30 м + band]`. Только в…, Почему нельзя продолжать заход по этому кадру. `None` — можно. Закон читает… (+14 more)

### Community 54 - "run_artifacts.py"
Cohesion: 0.18
Nodes (17): controller_pids(), _csv_value(), default_runs_root(), _effective_configs(), gains_snapshot(), _git_state(), _jsonable(), _matrix_rows() (+9 more)

### Community 55 - "RunwayTracker"
Cohesion: 0.12
Nodes (11): Точка на продолжении оси; положительное расстояние — до порога., Решить прямую геодезическую задачу на сферической Земле., Геодезическое guidance в истинной системе направлений., Guidance по курсу ВПП и измеренному отклонению — без собственной геодезии.…, Возвращает отклонение от осевой линии в метрах. >0 - правее оси, <0 - левее., Геодезическое наведение на ось ВПП с упреждением по скорости., RunwayTracker, GainSpace (+3 more)

### Community 56 - "RomanLogImporter"
Cohesion: 0.19
Nodes (10): _number(), Path, Импорт и проверка внешних CSV-прогонов roman_aviacia_ics., Потоково нормализует основной и authority CSV Романа., RomanLogImporter, verify_manifest(), fixture, roman_csv() (+2 more)

### Community 57 - "ICSInputs"
Cohesion: 0.13
Nodes (14): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, ICSInputs, Evaluate the A.1.1 approach segment and stop at a radio-altitude floor., ControlModeState (+6 more)

### Community 58 - "test_dashboard.py"
Cohesion: 0.20
Nodes (13): _live(), _post(), parametrize, test_active_pid_is_editable_in_classical_and_shadow(), test_gain_change_is_queued_bumpless_and_records_full_event(), test_http_api_is_incremental_pending_and_loopback_only(), test_incremental_snapshot_uses_recorder_objects_and_stays_small_when_idle(), test_live_and_replay_use_the_same_dashboard_snapshot() (+5 more)

### Community 59 - "static_sim"
Cohesion: 0.13
Nodes (16): decode_outputs(), `ICSOutputs` → (brake_l, brake_r, thr_l_rate, thr_r_rate, steer), всё…, (sim, connector) с неизменным кадром у порога ВПП. Скорость задаётся в **м/с**.…, static_sim(), NWS_FAIL отключает стойку/педаль, но оставляет руль и дифференциальные органы., test_control_step_emits_five_bounded_commands(), test_control_step_stops_and_sends_nothing_on_missing_telemetry(), test_default_preset_leaves_all_actuators_healthy() (+8 more)

### Community 60 - "gain_space_for"
Cohesion: 0.25
Nodes (11): gain_space_for(), _profile_name(), Профильное пространство абсолютных PID-коэффициентов NPGS., Профильные пространства абсолютных PID-коэффициентов NPGS., test_every_profile_preset_gain_is_inside_its_band(), test_gain_space_can_be_built_from_external_scenario_registry(), test_normalization_endpoints_and_nonpositive_guard(), test_profile_spaces_have_stable_17_action_contract_and_independent_identity() (+3 more)

### Community 61 - "test_control_parity.py"
Cohesion: 0.11
Nodes (16): Генератор эталонной кривой скорости (Колокол Гаусса)., Начать профиль с фактической скорости текущего участка., То же без лишнего round-trip м/с → узлы → м/с на касании., Возвращает идеальную скорость (м/с) для текущей точки пути., ReferenceTrajectory, TrajectoryState, Тесты паритета после выноса контура из main.ipynb в пакет ismpu. Полный паритет…, test_equally_slow_law_endpoints() (+8 more)

### Community 62 - "Project Dependencies"
Cohesion: 0.18
Nodes (13): Autonomous Landing Controller, Repository Guidance for Codex, Autonomous Landing Controller, Repository Guidance for Claude Code, Neural Landing Implementation Plan, Unified Scenario System, Optional Gymnasium, NumPy (+5 more)

### Community 63 - "test_ground_controller.py"
Cohesion: 0.22
Nodes (13): parametrize, _direct_ground_frame(), Контракты наземного контура этапа 2., test_ground_pids_use_working_ics_numerics_and_explicit_integrator_limits(), test_ground_step_returns_three_typed_diagnostics_and_rate_limits_handover(), test_guidance_dropout_removes_the_previous_turn_immediately(), test_nws_failure_keeps_rudder_and_redistributes_to_differential_brakes(), test_operator_ends_matrix_taxi_as_completed() (+5 more)

### Community 64 - ".invalid"
Cohesion: 0.13
Nodes (16): initial_segment(), is_airborne(), FlightSegment, Сообщает ли стенд, что ВС в воздухе и достаточно высоко для приёма захода.…, С какого участка начинать. Пробег — ответ по умолчанию (см. модуль)., Кадр «связи со стендом нет». Нули, а не None: контур проверяет `valid` первым., Стенд при обрыве связи отдаёт НУЛИ с valid=False, а не None. Проверка «поле is…, test_control_step_stops_on_invalid_frame_even_with_numeric_fields() (+8 more)

### Community 66 - "dashboard_core.py"
Cohesion: 0.10
Nodes (14): _allocator_stage(), DashboardServer, DashboardSnapshot, _finite(), _first_present(), _gain_ranges(), _gains_from_manifest(), _gains_from_samples() (+6 more)

### Community 67 - "test_rollout_env.py"
Cohesion: 0.15
Nodes (18): ObservationBuilder, Строит нормированный вектор наблюдения одного кадра., excess(), graded(), Чистый hinge: превышение допуска, нормированное на допуск. Внутри допуска = 0., Штраф с гейтом ТЗ: мягкий линейный наклон внутри допуска + резкий рост за…, Тесты Этапа 2: Observation/Action/reward/RolloutEnv + инвариант identity ==…, Без аннотаций типов @dataclass не видит полей, и тогда любые два экземпляра… (+10 more)

### Community 68 - "test_working_ics_dashboard.py"
Cohesion: 0.35
Nodes (10): ClearWeatherILSController, DashboardState, _controller(), _inputs(), Characterization tests for the bench-validated ``working_ics`` dashboard., _record(), test_dashboard_records_four_airborne_views_and_diagnostics(), test_gain_updates_are_immediate_validated_and_share_pitch_with_flare() (+2 more)

### Community 70 - "Telemetry"
Cohesion: 0.07
Nodes (20): Такт манёвра ухода. → True, когда набор устойчив (пора отдать управление…, Набор устойчив: есть и вертикальная скорость вверх, и прирост радиовысоты над…, Результат проверки допусков захода на одном такте. `landing_allowed` — все ли…, ToleranceReport, _faults_from_inputs(), Невалидные ICS-сигналы, которые воздушный закон читает безусловно., Приборная скорость (kt → м/с). Отсечки реверса заданы по ней, а не по путевой., Радиовысота **в футах** — единицы стенда. Порог воздушного включения (400… (+12 more)

### Community 71 - "Unified Profile-Aware Scenario System"
Cohesion: 0.22
Nodes (9): Technical-Specification Acceptance Gates, Bench-Validated ILS Approach Channel, Forward-Only Flight Segment Supervisor, Tolerance-Gated Go-Around, Longitudinal and Lateral Ground Channels, PID Run Matrix, Unified Profile-Aware Scenario System, Legacy Scenario Preset Model (+1 more)

### Community 72 - "Interactive PID Dashboard"
Cohesion: 0.25
Nodes (9): Nine-View PID Dashboard, Run Recording Artifacts, buildTabs, draw, Gain Tuning and Snapshot Export, Interactive PID Dashboard, refresh, render (+1 more)

### Community 73 - "run_matrix.py"
Cohesion: 0.05
Nodes (21): cases_for_segment(), ground_runs(), MatrixCase, MatrixCondition, MatrixRun, normalize_code(), _number(), Any (+13 more)

### Community 74 - "ClearWeatherILSController"
Cohesion: 0.15
Nodes (7): DashboardServer, DashboardState, Any, ICSInputs, ClearWeatherILSController, test_roundout_commands_a_material_pitch_increase_before_touchdown(), test_terminal_pitch_hold_starts_before_last_five_feet_guidance_cutoff()

### Community 75 - "scenario_signature"
Cohesion: 0.18
Nodes (9): is_signature_holdout(), PartitionedScenarioProvider, Устойчивая комбинация условий, а не имя или целое семейство отказов., Каноническая дискретизация условий для train/eval split., Фильтр над единым sampler с непересекающимися train/eval signatures., scenario_signature(), ScenarioSignature, RuntimeError (+1 more)

### Community 76 - "ICSInterface.cs"
Cohesion: 0.36
Nodes (7): External.Systems.ICS, ControlModeState, GearState, ICSInputs, ICSOutputs, ReverseEngineType, UInt64

### Community 77 - "heading_deviation_deg"
Cohesion: 0.19
Nodes (12): heading_deviation_deg(), Отклонение курса ВС от направления ВПП — приёмочная величина ТЗ 5.1.3.3 /…, Телеметрия ВС на оси ВПП, смещённого вбок на `offset_m` и с заданным курсом.…, ТЗ 5.1.3.3 нормирует курс «от направления ВПП». Смещение от оси на него не…, На стенде курс ВПП приходит телеметрией; конфиг — только значение по умолчанию., Таблица из находки: раньше оба случая давали противоположный результат., _telemetry_at(), test_heading_deviation_ignores_lateral_offset() (+4 more)

### Community 78 - "runtime/pretrain.py"
Cohesion: 0.23
Nodes (15): ground_cases(), build_capture_stack(), build_scenarios(), matrix_preset_names(), PretrainRunConfig, Оркестрация SFT-подогрева NPGS (план Stage B): захват классических прогонов на…, Имена наземных пресетов матрицы прогонов (пригодных для SFT) в порядке матрицы.…, (env, net) поверх выбранного backend; env без Shield (чистая классика). (+7 more)

### Community 79 - "promote_candidate.py"
Cohesion: 0.33
Nodes (15): _gain_patch(), main(), promote_candidate(), PromotionError, Path, Проверяемое продвижение dashboard candidate в sparse scenario override., Пересчитать matrix/config hashes, а не доверять двум согласованно изменённым…, Проверить run и записать новый scenario JSON; registry исходников не меняется. (+7 more)

### Community 80 - "ICS PID Monitor"
Cohesion: 0.29
Nodes (7): buildControls, draw, formatTime, Four-Loop PID Tuning, ICS PID Monitor, Live and Historical Timeline, refresh

### Community 81 - "ICSInputs"
Cohesion: 0.06
Nodes (35): IntEnum, FlightPhase, Фаза полёта, сообщаемая стендом (`ICSInputs.FlightPhase`)., FlightSegment, Enum, str, Участок, для которого выбираются закон управления и условия сценария., Типизированные backend-расширения общего SI-кадра. (+27 more)

### Community 82 - "ICS UDP JSON Protocol"
Cohesion: 0.33
Nodes (6): Fourteen-Bit ControlValidMask Layout, Dual-Backend SimInterface, Two-Factor ICS Engagement Handshake, ICS UDP JSON Protocol, Telemetry SI Unit Boundary, ICS-Only Backend Guidance

### Community 83 - "X-Plane Dashboard and Runtime Guide"
Cohesion: 0.60
Nodes (6): Aircraft-Profile Checkpoint Isolation, Live A330 Acceptance Checklist, Profile-Aware Flight Scenarios, X-Plane Dashboard and Runtime Guide, X-Plane Resettable Runtime, X-Plane Training and Evaluation Backend

### Community 84 - "test_working_ics_golden.py"
Cohesion: 0.26
Nodes (11): Касание: обжата **любая основная** стойка. Носовая не участвует — она…, _assert_numeric_result(), ICSInputs, Characterization baseline of the bench-validated ``working_ics`` approach., Канонический контур и формирователь пакета совпадают с эталоном до 1e-12., _replay(), _rows(), _state() (+3 more)

### Community 85 - "EpisodeObjective"
Cohesion: 0.20
Nodes (8): EpisodeObjective, Накопитель по эпизоду: собирает потактовые отсчёты → сводные компоненты.…, Фиксированный приёмочный набор (детерминированный, без RNG)., Отсутствие данных даёт None, а не 0 — приёмка обязана трактовать это как FAIL., p95 темпа не ловится одиночным выбросом — в отличие от максимума., test_episode_objective_p95_rate_is_robust_to_a_single_spike(), test_episode_objective_reports_none_for_unobserved_phases(), test_episode_objective_separates_rollout_and_taxi_phases()

### Community 86 - ".__init__"
Cohesion: 0.29
Nodes (7): RewardWeights, _make_box(), GainSpace, SimInterface, Минимальная замена gym.spaces.Box, когда gymnasium не установлен., _SimpleBox, test_reward_counts_shield_and_jerk()

### Community 87 - "scenarios.py"
Cohesion: 0.13
Nodes (19): _copy_approach(), _copy_ground(), _ground_segments_for_spec(), GroundControlConfig, _GroundPresetSpec, _install_approach_scenarios(), _install_through_scenarios(), _matrix_draft() (+11 more)

### Community 88 - "import_workbook"
Cohesion: 0.33
Nodes (9): import_workbook(), main(), Any, Path, Одноразовый импорт исходной Excel-матрицы в runtime-каталог JSON., Прочитать книгу целиком; функция не используется production runtime., _scalar(), write_catalog() (+1 more)

### Community 89 - "test_approach_channel.py"
Cohesion: 0.08
Nodes (35): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+27 more)

### Community 90 - "LongitudinalChannel"
Cohesion: 0.20
Nodes (6): CompletionRule, LongitudinalChannel, Блок 1: скорость → симметричная база тормозов и реверса., Сбросить PID и привязать начало профиля к фактической скорости касания/старта., PidMap, VelocityLaw

### Community 91 - "test_action_contract.py"
Cohesion: 0.11
Nodes (19): ControlArchitecture, Канонический порядок регуляторов, размерности действия и **контракт обучаемого…, Фиксированный порядок слоёв и роль обучаемого компонента., Проверяет контракт обучаемого слоя. Нарушение → `ValueError` на старте…, Один регулятор, коэффициенты которого (kp/ki/kd) разрешено настраивать сети., RegulatorSpec, validate_action_contract(), Контракт обучаемого слоя (Этап 4): что именно сеть имеет право менять. Аргумент… (+11 more)

### Community 92 - "base_gains_from_pids"
Cohesion: 0.10
Nodes (31): apply_gains_to_pids(), base_gains_from_pids(), PidMap, Снимок (kp, ki, kd) регуляторов — пресет-якорь для Shield и т.п., Записывает эффективные gain'ы обратно в регуляторы (перед control_step)., apply_corrections(), decode(), preset_action() (+23 more)

### Community 93 - "ICSSim"
Cohesion: 0.10
Nodes (12): ICSSim, FailureMode, SimInterface, Обмен со стендом заказчика: телеметрия внутрь, команды наружу. Управление…, Принимает ли стенд наши команды. До включения любой `step` уходит вхолостую., Войти в пробег самостоятельно (`ControlMode 0 → 3`)., Перейти `Approach → Landing`; сессия и воздушные каналы сохраняются., На стенде отказы приходят телеметрией, а не инжектируются нами. (+4 more)

### Community 94 - "loop.py"
Cohesion: 0.14
Nodes (19): ControllingSystem, Сценарий по имени либо шифру матрицы, без различия раскладки А/B., resolve_scenario(), Enum, str, RunResult, RunStopReason, cli() (+11 more)

### Community 95 - "reward.py"
Cohesion: 0.11
Nodes (20): _command_jerk(), _component(), _effort_saturated(), _ground_steering(), ObjectiveWeights, _p95(), Objective — единое определение «хорошего пробега» (§11 + приёмка ТЗ разд. 5).…, Упёрлась ли команда в границу **со стороны усилия**. Важное различие: нулевая… (+12 more)

### Community 99 - "_WarmUpSim"
Cohesion: 0.18
Nodes (7): ObserverEstimate, Оценки PINN-обсервера (§12). Заглушка нулями до Этапа 7., Стенд, включающий управление только после N тактов прогрева. Само рукопожатие…, Такты рукопожатия — не шаги эпизода: в это время ВС нами не управлялось. Иначе…, test_env_reports_engagement_state_in_info(), test_warm_up_runs_before_the_episode_and_is_not_counted(), _WarmUpSim

### Community 110 - "test_campaign.py"
Cohesion: 0.21
Nodes (19): campaign_phase(), campaign_rows(), campaign_summary(), _config_status(), main(), next_campaign_row(), Path, Порядок и фактический статус кампании из 280 матричных прогонов. (+11 more)

### Community 111 - "Q: Реализовать этап 0: baseline, golden replay и dashboard characterization"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Реализовать этап 0: baseline, golden replay и dashboard characterization, Source Nodes

### Community 112 - "Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md)., Source Nodes

### Community 114 - "normalization.py"
Cohesion: 0.19
Nodes (12): clip_unit(), linear(), log_norm(), Фиксированная нормализация Observation Space — единый контракт train ↔ deploy.…, Лог-нормировка неотрицательной величины (видимость): log1p(x)/log1p(scale)., Отображает [lo, hi] → [-1, 1] (для PID output по его границам)., Сериализуемый слепок контракта нормировки (сохраняется вместе с весами).…, snapshot() (+4 more)

### Community 115 - "test_ics_sim.py"
Cohesion: 0.07
Nodes (26): _cold_sim(), Тесты стенда (`ICSSim`), подбора сценария и генератора — без реального стенда., Заявить канал, который не формируешь, — взять ответственность за неуправляемый…, 31 — единственная маска, с которой заход реально прошёл на стенде. Проверяется…, Один бит на одно командное поле `ICSOutputs` — иначе заявка попадает не в тот…, Иначе поставленная система на любой ВПП поедет по осевой Шереметьево из конфига., Характеризация стендового кадра: direct-пара имеет приоритет над UUEE fallback., Сквозной прогрев: маска нулевая, пока стенд не подтвердил `AgentIsActive = 1`. (+18 more)

### Community 116 - "Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)., Source Nodes

### Community 117 - "admit_checkpoint"
Cohesion: 0.16
Nodes (17): AdmissionResult, admit_checkpoint(), Пропускать ли чекпоинт дальше. Отсутствующая/нечисловая метрика = отказ.…, _battery(), Отсутствующая метрика = отказ, а не «нет данных — значит нет проблемы»., Формально в допуске, но авторитет исчерпан — режим держится на грани., Если сеть не бьёт классику, она не окупается — выпускать её нечего., Канал не двигался за эпизод → p95 = None. Это не дефект. (+9 more)

### Community 123 - "engaged_sim"
Cohesion: 0.12
Nodes (16): engaged_sim(), (sim, connector) с завершённым рукопожатием: стенд подтвердил `AgentIsActive =…, Регресс: расширение структуры не должно протащить руль высоты в маску пробега., test_ground_frame_still_declares_only_the_ground_channels(), Разделение органов из таблицы Заказчика: тиллер — на рулении, педальный пост —…, Базовый контур на стенде: `control_step` сам читает телеметрию и сам отправляет., На стенде каждый лишний `read_telemetry` — лишний приём UDP. Кадр, вернувшийся…, Замолчать нельзя: последнее отклонение осталось бы приложенным до сторожа на… (+8 more)

### Community 124 - ".from_json"
Cohesion: 0.29
Nodes (6): _pid_from_colleague(), Загрузка настроек из JSON коллеги (`config/ics_clear_weather_pid.json`). Секции…, `PIDConfig` коллеги → аргументы нашего `PIDController`. Предел интегратора у…, Path, Наши умолчания и его файл — одно и то же. Разойдутся — расхождение должно быть…, test_config_from_the_colleague_json_matches_our_defaults()

### Community 125 - "GuidanceState"
Cohesion: 0.29
Nodes (3): GuidanceState, Совместимость с прежним атрибутом; новый термин явно указывает ось., Совместимость со старым словарным API.

### Community 126 - ".compute"
Cohesion: 0.18
Nodes (5): → (интеграл только с утечкой, интеграл с утечкой и приращением). Оба уже зажаты., Такт регулятора. `measurement` обязателен при `derivative_on_measurement=True`., Back-calculation: подтянуть интегратор к фактически применённой команде. No-op…, Сменить коэффициенты без сброса D-history и с компенсацией интегратором.…, Вес апериодического фильтра D-составляющей за такт `dt`.

### Community 127 - "train.py"
Cohesion: 0.12
Nodes (18): build_sim(), Any, Path, Создать backend; для ICS геодезия включается только явным ``runway_profile``., build_ics_stack(), build_training_stack(), CSVLogger, make_curriculum_provider() (+10 more)

### Community 129 - "Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md)., Source Nodes

### Community 130 - "Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md)., Source Nodes

### Community 131 - "pid.py"
Cohesion: 0.24
Nodes (7): PIDDiagnostics, Пропорционально-интегрально-дифференциальный регулятор. Класс сохраняет прежнюю…, Типизированный снимок последнего такта регулятора., apply_ground_control(), build_pids(), Сборка классического контура из неизменяемой конфигурации., Фабрики stateful-объектов; config-модули хранят только данные.

### Community 133 - ".enter_segment"
Cohesion: 0.25
Nodes (4): FailureMode, FlightSegment, Применить только дельту условий при переходе между участками., Снять один отказ, не переинициализируя отказ, продолжающийся на новом участке.

### Community 135 - "Q: Приступай к выполнению этапа 2 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 2 плана docs/plan.md, Source Nodes

### Community 137 - "verdict_of"
Cohesion: 0.22
Nodes (8): _check(), Criterion, _range_check(), Один пункт ТЗ: предел, измеренное значение, вердикт и его причина., Строит вердикт. Неприменимо → SKIP; применимо, но данных нет → FAIL., Проверить несимметричный интервал; отсутствие измерения остаётся отказом., Итог эпизода: FAIL, если провален хоть один применимый критерий., verdict_of()

### Community 138 - "compute_reward"
Cohesion: 0.15
Nodes (13): compute_reward(), TypedDict, Считает компоненты и суммарный reward. Все компоненты ≥ 0; reward = −Σ…, Допуск по оси ВПП для текущей фазы: пробег ±3 м, руление ±1 м (ТЗ 5.1.3.1)., RewardComponents, xte_limit_for(), Перелёт по скорости к концу ВПП опаснее недолёта — симметричным модулем не…, Тормоз на 0 = «торможение не требуется», а не «авторитет исчерпан». Иначе флаг… (+5 more)

### Community 140 - "ControllingSystem"
Cohesion: 0.09
Nodes (15): ControllingSystem, FailureMode, Связать сценарий с контуром; PID активируются после определения участка., Обновить параметры геометрического наведения латерального канала. Имя сохранено…, Веса влияния каналов (актор, §6): множители к выходам каналов. 1.0 = классика., Привести модель отказов к тому, что сообщает борт (`ICSInputs.Fault*`). Отказы…, Такт управления. → True, если управление окончено (или телеметрия невалидна).…, Прервать заход с названной причиной. → True (управлять больше нечем). (+7 more)

### Community 142 - ".__init__"
Cohesion: 0.29
Nodes (5): AircraftProfile, Path, RunwayProfile, WeatherState, XPlaneConnector

### Community 154 - ".enter_segment"
Cohesion: 0.15
Nodes (8): ConditionMatch, EngagementInputs, FlightSegment, Scenario, Начало эпизода: сброс рукопожатия и первый кадр со стенда. Средой распоряжается…, Сверить ожидаемые условия; стендовые условия никогда не изменяются кодом., Передать управление в руление (`3 → 4`) — по решению вызывающего, что пробег…, Признаки для автомата включения. `agent_is_active` — подтверждение стенда:…

### Community 155 - "holdout_reason"
Cohesion: 0.20
Nodes (11): _hash_unit(), holdout_reason(), is_marked_holdout(), SHA-256 от идентификатора → число в [0, 1). Стабильно между запусками и…, Помечен ли сценарий как holdout своим именем., Почему сценарий в holdout, или `None` если он обучающий. Причина всегда…, SHA-256, а не встроенный hash(): последний рандомизирован солью процесса., Пин на конкретное значение: смена алгоритма перетасовала бы всё разбиение молча. (+3 more)

### Community 158 - "Q: Приступай к выполнению этапа 4 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 4 плана docs/plan.md, Source Nodes

### Community 164 - "aircraft_profiles.py"
Cohesion: 0.22
Nodes (6): IcsEngagement, get_aircraft_profile(), Профили преобразования команд ИСМПУ в органы управления X-Plane., Единая фабрика backend: ICS по умолчанию, X-Plane явно., Курируемый набор DataRef X-Plane 12, используемый ИСМПУ., RunwayProfile

### Community 165 - "CompletionRule"
Cohesion: 0.27
Nodes (8): CompletionRule, Enum, Генератор эталонной кривой скорости пробега. Два закона замедления: колокол…, Как активный наземный сценарий заканчивает управление., VelocityLaw, EpisodeInfo, TypedDict, str

### Community 166 - "action.py"
Cohesion: 0.36
Nodes (9): action_high(), action_low(), float32, NDArray, Применение абсолютных коэффициентов PID, выданных NPGS. Действие: вектор…, reference_action(), test_output_bounded_to_physical_band(), test_reference_action_is_default_gains() (+1 more)

### Community 167 - "HandshakeBench"
Cohesion: 0.20
Nodes (4): HandshakeBench, Стенд, включающий управление только после корректного рукопожатия. Ждёт…, Стенд включается по полученной готовности, а не по нашему представлению о ней., test_the_airborne_handshake_is_actually_transmitted_before_approach()

### Community 169 - "on_ground"
Cohesion: 0.20
Nodes (10): on_ground(), Кадр «ВС на полосе»: обжаты все стойки, курс/координаты у порога UUEE 06R., Пресет — стартовое предположение; фактическую конфигурацию сообщает борт., Отказ может быть снят — накапливающий учёт держал бы орган мёртвым до конца…, Единичный таймаут — не повод вернуть рулю авторитет, которого у него нет., test_controller_takes_failures_from_the_bench_not_from_the_preset(), test_failures_are_cleared_when_the_bench_stops_reporting_them(), test_ics_requires_profile_and_records_nonfatal_transition_mismatch() (+2 more)

### Community 171 - "FailureMode"
Cohesion: 0.28
Nodes (5): FailureManager, FailureMode, Enum, Проецирует набор дискретных отказов в эффективности исполнительных органов., Привести состояние ровно к набору `modes` (то, что сообщил стенд). Пересборка с…

### Community 173 - "ConditionMatch"
Cohesion: 0.25
Nodes (4): ConditionMatch, Сверка ожидаемых условий с фактической телеметрией backend., Погода остаётся отчётной; неверный отказ делает прогон недопустимым., Совместимое имя для прежних потребителей допуска к приёмке.

### Community 174 - ".from_ics"
Cohesion: 0.25
Nodes (6): Фактические погодные условия со стенда (ветер, сцепление, осадки, видимость)., `ICSInputs` → `WeatherState`. Единственный источник фактической погоды. Стенд…, `Visibility` в футах. Без пересчёта 16000 футов читались бы как «ясно» вместо…, test_visibility_is_converted_from_feet(), Стенд шлёт узлы и **футы**; в WeatherState видимость — в метрах., test_from_ics_converts_units()

### Community 175 - "._should_go_around"
Cohesion: 0.29
Nodes (5): above_decision_height(), ВС выше высоты решения ухода на второй круг (30 м по ТЗ 5.1.1.2). → уход…, Реверс убран: команды обратной тяги нулевые. В воздухе реверс не выдаётся…, Нужно ли уходить на второй круг по этому такту. → причина или `None`. Только…, ToleranceReport

### Community 177 - ".__init__"
Cohesion: 0.40
Nodes (4): ApproachConfig, ApproachController, SimInterface, Пересобрать воздушный канал под заданные настройки. → новый канал. Именно…

### Community 178 - "ResilientSender"
Cohesion: 0.33
Nodes (3): Отправка best-effort со счётчиком ошибок и разрежённым логом. Windows отдаёт…, → True если отправлено. Исключение наружу не выпускается., ResilientSender

### Community 179 - "render_report"
Cohesion: 0.33
Nodes (6): Markdown-отчёт приёмки. Отрицательные результаты не скрываются — они и есть…, Пишет `evaluation.json` + `report.md`. → пути записанных файлов., render_report(), write_report(), Отрицательный результат должен быть виден в отчёте, а не спрятан., test_report_shows_failures_and_baseline_comparison()

### Community 181 - "Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md)., Source Nodes

### Community 182 - "test_adopts_rollout_from_the_flight_phase"
Cohesion: 0.33
Nodes (4): Валидный кадр с AgentIsActive = 0 — стенд снял активацию, значит и мы больше не…, `ControlMode` нет во входной структуре, поэтому подхват опирается на фазу…, test_adopts_rollout_from_the_flight_phase(), test_confirmation_clears_when_the_bench_deactivates()

## Ambiguous Edges - Review These
- `Unified Profile-Aware Scenario System` → `Legacy Scenario Preset Model`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to
- `Dual-Backend SimInterface` → `ICS-Only Backend Guidance`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **73 isolated node(s):** `Answer`, `Outcome`, `Source Nodes`, `ismpu`, `Answer` (+68 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **65 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `loop.py` (2× useful, score=1.985905178) _(code changed — re-verify)_
- `ICSSim` (2× useful, score=1.969863406)
- `LateralChannel` (2× useful, score=1.948518111)
- `ObservationBuilder` (2× useful, score=1.92877006)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Unified Profile-Aware Scenario System` and `Legacy Scenario Preset Model`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Dual-Backend SimInterface` and `ICS-Only Backend Guidance`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `ControllingSystem` connect `ControllingSystem` to `RolloutEnv`, `pid.py`, `compute_reward`, `test_pretrain.py`, `test_run_matrix.py`, `ics_sim.py`, `evaluate.py`, `test_xplane_backend.py`, `test_evaluate.py`, `test_ppo.py`, `.from_preset`, `.from_ics`, `CompletionRule`, `action.py`, `FakeConnector`, `on_ground`, `fakes.py`, `._should_go_around`, `.__init__`, `test_full_flight.py`, `test_go_around.py`, `test_approach_criteria.py`, `._approach_step`, `DatagramSocket`, `test_dashboard.py`, `static_sim`, `test_control_parity.py`, `test_ground_controller.py`, `.invalid`, `test_rollout_env.py`, `Telemetry`, `runtime/pretrain.py`, `ICSInputs`, `.__init__`, `LongitudinalChannel`, `test_action_contract.py`, `base_gains_from_pids`, `ICSSim`, `reward.py`, `_WarmUpSim`, `test_campaign.py`, `test_ics_sim.py`, `engaged_sim`, `train.py`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Why does `Telemetry` connect `Telemetry` to `run_report.py`, `.enter_segment`, `ground_allocator.py`, `LateralChannel`, `ControllingSystem`, `ControlsState`, `ICSOutputs`, `._fill_airborne`, `ApproachController`, `ics_sim.py`, `weather.py`, `XPlaneSim`, `.enter_segment`, `.from_preset`, `.from_ics`, `FakeConnector`, `HandshakeBench`, `fakes.py`, `.from_ics`, `._should_go_around`, `test_full_flight.py`, `test_go_around.py`, `test_approach_criteria.py`, `._approach_step`, `static_sim`, `test_control_parity.py`, `.invalid`, `test_rollout_env.py`, `heading_deviation_deg`, `ICSInputs`, `test_working_ics_golden.py`, `test_approach_channel.py`, `LongitudinalChannel`, `_WarmUpSim`, `test_ics_sim.py`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Why does `ControlsState` connect `ControlsState` to `shield.py`, `RolloutEnv`, `Shield`, `airborne_inputs`, `ground_allocator.py`, `compute_reward`, `.rudder_cmd`, `AircraftProfile`, `ics_sim.py`, `PIDController`, `test_xplane_backend.py`, `aircraft_profiles.py`, `CompletionRule`, `FakeConnector`, `.__init__`, `test_control_parity.py`, `test_rollout_env.py`, `Telemetry`, `ICSInputs`, `test_working_ics_golden.py`, `EpisodeObjective`, `.__init__`, `test_approach_channel.py`, `test_action_contract.py`, `reward.py`, `_WarmUpSim`, `test_ics_sim.py`, `engaged_sim`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `ControllingSystem` (e.g. with `Telemetry` and `EpisodeInfo`) actually correct?**
  _`ControllingSystem` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `Telemetry` (e.g. with `ApproachController` and `ApproachResult`) actually correct?**
  _`Telemetry` has 32 INFERRED edges - model-reasoned connections that need verification._