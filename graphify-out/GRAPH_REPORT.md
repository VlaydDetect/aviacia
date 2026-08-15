# Graph Report - .  (2026-08-12)

## Corpus Check
- 132 files · ~128,316 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2334 nodes · 6068 edges · 109 communities (91 shown, 18 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 641 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Approach Limits and Tolerances
- Scenario Splits and Reproducibility
- Rollout Rewards and Gates
- Weather and Run Conditions
- Deterministic Safety Shield
- Scenario Configuration Parsing
- Simulator Interface and Telemetry
- Approach Channel Parity
- Flight Control Supervisor
- ICS Protocol Data Structures
- Flight Phase Telemetry
- Segment Transitions and Runtime
- SFT Pretraining Pipeline
- Scenario Registry and Matrix
- ICS UDP Connector
- ICS Simulator Engagement Tests
- Aircraft Profiles and Scenarios
- ICS Simulator Runtime
- Approach Control Configuration
- Telemetry Condition Matching
- Neural Action Encoding
- X-Plane Simulator Lifecycle
- Gain and Observation Normalization
- PID Controller Numerics
- Policy Evaluation Baselines
- PPO Training Runtime
- X-Plane Backend Tests
- Acceptance Evaluation Tests
- PPO Agent Learning
- ICS Engagement State
- Legacy X-Plane Client
- Rollout Observation Environment
- Wind Decomposition Models
- Graphify Query Workflow
- X-Plane Connector Protocol
- Rollout Shield Integration
- Physical Gain Mapping
- ICS Engagement Tests
- Bench Diagnostic Tools
- Fake ICS Connector Tests
- Legacy Approach Controller
- Engagement Timing Tests
- NPGS Policy Admission
- Legacy ICS Runner
- Action Contract Definition
- SFT Capture Runtime
- Scenario Generation
- Engagement Input Processing
- Run Artifact Recording
- Full Flight Test Helpers
- Go-Around Tests
- Neural Architecture Plan
- Approach Criteria Monitor
- Dashboard Runtime Integration
- Dashboard State and Configuration
- Runway Guidance Tracking
- Roman Log Import
- Legacy Approach Criteria
- Runway Profile Configuration
- Checkpoint Admission Battery
- Legacy Controller Configuration
- Reference Speed Trajectory
- Project Dependency Architecture
- NPGS Phase Encoding
- Lateral Guidance Channel
- Bench Failure Sync Tests
- Failure Degradation Management
- Gain Action Application
- Weather and RREF Models
- Classical Control Parity
- PID Anti-Windup Logic
- System Requirements Guidance
- PID Dashboard Ecosystem
- Control Factory Wiring
- Legacy Dashboard State
- Legacy ICS Protocol
- Bench C Sharp Interface
- Invalid Telemetry Handling
- Legacy Rollout Bridge
- Dashboard HTTP Server
- Legacy Dashboard Frontend
- X-Plane Wire Compatibility
- ICS Backend Architecture
- X-Plane Runtime Architecture
- Colleague Configuration Parity
- Control Neutralization
- Dashboard JSON Serialization
- RREF Packet Handling
- NPGS Policy Loading
- Legacy Dashboard Server
- Bench Fault Decoding
- Acceptance Criterion Checks
- Altitude Dependent Roll Limits
- Go-Around Maneuver
- Acceptance Report Rendering
- Final Command Clamping
- Pytest Package Bootstrap
- Neural Agent Package
- Configuration Package
- Tunable Regulator Definition
- Classical Control Package
- Simulation Environment Package
- PID Dashboard Package
- ISMPU Package Root
- Bench Transport Package
- Runtime Entry Points
- Bench Diagnostic Package
- Conversion Utilities Package
- Project Package Metadata

## God Nodes (most connected - your core abstractions)
1. `ControllingSystem` - 170 edges
2. `ControlsState` - 122 edges
3. `Telemetry` - 120 edges
4. `ICSSim` - 88 edges
5. `Scenario` - 79 edges
6. `FailureMode` - 77 edges
7. `FlightSegment` - 69 edges
8. `XPlaneSim` - 65 edges
9. `PIDController` - 64 edges
10. `RolloutEnv` - 62 edges

## Surprising Connections (you probably didn't know these)
- `Autonomous Landing Controller` --semantically_similar_to--> `Autonomous Landing Controller`  [INFERRED] [semantically similar]
  CLAUDE.md → AGENTS.md
- `Profile-Aware Flight Scenarios` --semantically_similar_to--> `Unified Scenario System`  [INFERRED] [semantically similar]
  docs/XPLANE_DASHBOARD.md → implementation_plan.md
- `Acceptance and Evaluation Harness` --semantically_similar_to--> `Technical-Specification Acceptance Gates`  [INFERRED] [semantically similar]
  implementation_plan.md → AGENTS.md
- `X-Plane Resettable Runtime` --semantically_similar_to--> `X-Plane Training and Evaluation Backend`  [INFERRED] [semantically similar]
  docs/XPLANE_DASHBOARD.md → implementation_plan.md
- `test_phase_labels_from_groundspeed()` --calls--> `phase_labels_from_groundspeed_kts()`  [EXTRACTED]
  tests/test_gain_scheduler.py → ismpu/agent/gain_scheduler.py

## Import Cycles
- 3-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 3-file cycle: `ismpu/config/scenarios.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 3-file cycle: `ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/control/channels.py`
- 3-file cycle: `ismpu/config/aircraft_profiles.py -> ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/config/aircraft_profiles.py`
- 4-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 4-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/flight.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/tolerance.py -> ismpu/control/approach.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/aircraft_profiles.py -> ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py -> ismpu/config/aircraft_profiles.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach_criteria.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/tolerance.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`

## Hyperedges (group relationships)
- **Graphify Extraction and Build Flow** — _codex_skills_graphify_skill_structural_extraction, _codex_skills_graphify_skill_semantic_extraction, _codex_skills_graphify_references_extraction_spec_semantic_extraction_contract, _codex_skills_graphify_references_update_build_merge [EXTRACTED 1.00]
- **Hybrid Neural Landing Control** — implementation_plan_classical_pid_plant, implementation_plan_npgs, implementation_plan_deterministic_shield, implementation_plan_ppo_multicomponent_loss, implementation_plan_pinn_observer [EXTRACTED 1.00]
- **PID Dashboard Ecosystem** — docs_xplane_dashboard_pid_dashboard, ismpu_gui_dashboard_pid_dashboard, ismpu_working_ics_ics_dashboard_ics_pid_monitor [INFERRED 0.85]

## Communities (109 total, 18 thin omitted)

### Community 0 - "Approach Limits and Tolerances"
Cohesion: 0.05
Nodes (69): lateral_limit_m(), lateral_load_situation(), lateral_situation(), normal_load_situation(), IntEnum, Критерии критичности особых ситуаций МС-21 (Приложение 1 к ТЗ). Таблица АП-25…, Классификация скорости касания относительно VAPP и VВПП пред., Классификация нормальной перегрузки посадочного удара. `heavy` — взлётный вес. (+61 more)

### Community 1 - "Scenario Splits and Reproducibility"
Cohesion: 0.05
Nodes (61): _as_dict(), contract_for(), Any, Сколько раз прогнать сценарий, чтобы результат приёмки что-то значил., Источники случайности на стороне стенда, активные при данных условиях. Мы…, Строит контракт воспроизводимости для сценария., required_replicas(), stochastic_sources() (+53 more)

### Community 2 - "Rollout Rewards and Gates"
Cohesion: 0.05
Nodes (58): _command_jerk(), _component(), compute_reward(), _effort_saturated(), excess(), graded(), ObjectiveWeights, _p95() (+50 more)

### Community 3 - "Weather and Run Conditions"
Cohesion: 0.05
Nodes (50): cases_for_segment(), _kts(), MatrixCondition, Матрица прогонов для настройки базовых ПИД-регуляторов. Машиночитаемая форма…, Шифры одного участка: `approach` / `rollout` / `taxi` / `through`., Матрица задаёт ветер в м/с, телеметрия приходит в узлах., Условие прогона из справочника матрицы (П.1–П.5 для захода, У.1–У.8 для ВПП).…, Геометрия целевой ВПП и высоты установки ЛА. Смена целевой полосы = правка… (+42 more)

### Community 4 - "Deterministic Safety Shield"
Cohesion: 0.07
Nodes (41): apply_gains_to_pids(), _clip(), GainCommand, GainMap, PidMap, RegulatorKey, Shield — детерминированный защитный контур между актором и классическим PID.…, Наблюдаемое состояние для поведенческих проверок уровня 3. (+33 more)

### Community 5 - "Scenario Configuration Parsing"
Cohesion: 0.09
Nodes (49): approach_control_from_dict(), approach_control_to_dict(), _copy_approach(), dump_scenario(), _finite_tree(), ground_control_from_dict(), ground_control_to_dict(), _legacy_ground() (+41 more)

### Community 6 - "Simulator Interface and Telemetry"
Cohesion: 0.07
Nodes (27): BaseException, Профили преобразования команд ИСМПУ в органы управления X-Plane., Каналы управления и общий вектор команд. `ControlsState` — разделяемая по…, FailureMode, Enum, Модель отказов бортового оборудования. `FailureState` хранит мультипликативные…, Слежение за осью ВПП: геодезия, cross-track error, guidance с look-ahead.…, Единая фабрика backend: ICS по умолчанию, X-Plane явно. (+19 more)

### Community 7 - "Approach Channel Parity"
Cohesion: 0.08
Nodes (51): angle_error_deg(), Разность курсов, приведённая к (-180, 180]., airborne_inputs(), Кадр «ВС на глиссаде»: стойки не обжаты, ILS валиден, скорость и высота…, _colleague_controller(), _descent_frames(), _our_channel(), Воздушный канал: заход по ILS, выравнивание, скоростной канал. Главный тест… (+43 more)

### Community 8 - "Flight Control Supervisor"
Cohesion: 0.05
Nodes (35): ControllingSystem, Связать сценарий с контуром; PID активируются после определения участка., Обновить параметры геометрического наведения латерального канала. Имя сохранено…, Веса влияния каналов (актор, §6): множители к выходам каналов. 1.0 = классика., Привести модель отказов к тому, что сообщает борт (`ICSInputs.Fault*`). Отказы…, Такт управления. → True, если управление окончено (или телеметрия невалидна).…, Прервать заход с названной причиной. → True (управлять больше нечем)., Реверс убран: команды обратной тяги нулевые. В воздухе реверс не выдаётся… (+27 more)

### Community 9 - "ICS Protocol Data Structures"
Cohesion: 0.06
Nodes (35): FlightPhase, IntEnum, Константы интерфейса стенда заказчика (ПИВ / ICS). Единый источник правды по…, Фаза полёта, сообщаемая стендом (`ICSInputs.FlightPhase`)., ControlModeState, GearState, ICSInputs, IntEnum (+27 more)

### Community 10 - "Flight Phase Telemetry"
Cohesion: 0.05
Nodes (46): IntFlag, ControlValid, Биты `ControlValidMask`: какие каналы несёт команда. **Один бит на одно…, is_airborne(), Сообщает ли стенд, что ВС в воздухе и достаточно высоко для приёма захода.…, `ICSInputs` → `Telemetry`: поля в СИ + «сырой» пакет для property. Стенд отдаёт…, Готовый кадр `Telemetry` для прямых вызовов `control_step(dt, telemetry,…, telemetry() (+38 more)

### Community 11 - "Segment Transitions and Runtime"
Cohesion: 0.07
Nodes (38): Глобальные константы контура управления (перенесены из main.ipynb)., Приёмочные пороги из ТЗ (раздел 5). Единый источник истины для reward-шейпинга…, FlightSegment, str, Участок, для которого выбираются закон управления и условия сценария., above_decision_height(), approach_blocker(), ApproachRefused (+30 more)

### Community 12 - "SFT Pretraining Pipeline"
Cohesion: 0.09
Nodes (41): _phase_labels(), pretrain_sft(), PretrainConfig, float32, GainMap, NDArray, Tensor, SFT (behavioral cloning) — предобучение NPGS предсказывать эталонные… (+33 more)

### Community 13 - "Scenario Registry and Matrix"
Cohesion: 0.07
Nodes (33): Настройки воздушного участка: заход по ILS, выравнивание, управление скоростью.…, compose_matrix_scenario(), compose_scenario(), _install_through_scenarios(), match_conditions(), matrix_battery(), _matrix_draft(), Единая профильная модель сценариев всего интервала полёта. `Scenario` —… (+25 more)

### Community 14 - "ICS UDP Connector"
Cohesion: 0.07
Nodes (28): ICSBenchConnector, ICSOutputs, main(), Отправка best-effort со счётчиком ошибок и разрежённым логом. Windows отдаёт…, → True если отправлено. Исключение наружу не выпускается., Мост к стенду: JSON поверх UDP, адрес стенда определяется из входящего пакета., Приём телеметрии стенда. Адрес отправителя определяется автоматически., Отправка управления на стенд. → отправлено ли (исключение наружу не… (+20 more)

### Community 15 - "ICS Simulator Engagement Tests"
Cohesion: 0.06
Nodes (38): engaged_sim(), (sim, connector) с завершённым рукопожатием: стенд подтвердил `AgentIsActive =…, _cold_sim(), Тесты стенда (`ICSSim`), подбора сценария и генератора — без реального стенда., Разделение органов из таблицы Заказчика: тиллер — на рулении, педальный пост —…, Заявить канал, который не формируешь, — взять ответственность за неуправляемый…, 31 — единственная маска, с которой заход реально прошёл на стенде. Проверяется…, Один бит на одно командное поле `ICSOutputs` — иначе заявка попадает не в тот… (+30 more)

### Community 16 - "Aircraft Profiles and Scenarios"
Cohesion: 0.08
Nodes (14): AircraftProfile, clamp(), Преобразовать воздушные команды ICD в нормированные DataRef X-Plane., Преобразовать нормированные команды пробега в DataRef X-Plane., Расширение реестра будущим профилем МС-21 без правки XPlaneSim., Проводка и масштабы конкретного планера X-Plane., Общая идентичность ЛА и необязательная привязка к X-Plane. Профиль нужен и…, Command refs retained under the historical public name. (+6 more)

### Community 17 - "ICS Simulator Runtime"
Cohesion: 0.08
Nodes (19): _clamp(), ICSSim, ICSOutputs, StartMode, Обмен со стендом заказчика: телеметрия внутрь, команды наружу. Управление…, Принимает ли стенд наши команды. До включения любой `step` уходит вхолостую., Начало эпизода: сброс рукопожатия и первый кадр со стенда. Средой распоряжается…, Гонит стимул рукопожатия, пока стенд не подтвердит включение (`AgentIsActive =… (+11 more)

### Community 18 - "Approach Control Configuration"
Cohesion: 0.14
Nodes (22): ApproachConfig, Параметры воздушного контура. Значения по умолчанию — настроенные на стенде.…, ApproachChannel, ApproachResult, clamp(), ApproachLimits, ApproachTelemetry, Заход по ILS с выравниванием. Телеметрию получает параметром, не читает сам.… (+14 more)

### Community 19 - "Telemetry Condition Matching"
Cohesion: 0.06
Nodes (18): ConditionMatch, Сверка ожидаемых условий с фактической телеметрией backend., GoAroundManeuver, Нужно ли уходить на второй круг по этому такту. → причина или `None`. Только…, Начать уход: зафиксировать состояние манёвра и высоту входа., Состояние идущего ухода на второй круг. Пока он активен, заход не ведётся., Приборная скорость (kt → м/с). Отсечки реверса заданы по ней, а не по путевой., Радиовысота **в футах** — единицы стенда. Порог воздушного включения (400… (+10 more)

### Community 20 - "Neural Action Encoding"
Cohesion: 0.09
Nodes (23): device, Веса + конфиг + слепок нормировки (включая gain-пространство) одним артефактом., action_high(), action_low(), decode(), ArrayLike, float32, NDArray (+15 more)

### Community 21 - "X-Plane Simulator Lifecycle"
Cohesion: 0.10
Nodes (5): _destination(), StartMode, Применить только дельту условий при переходе между участками., Снять один отказ, не переинициализируя отказ, продолжающийся на новом участке., XPlaneSim

### Community 22 - "Gain and Observation Normalization"
Cohesion: 0.11
Nodes (26): gain_space_for(), _profile_name(), Профильное пространство абсолютных PID-коэффициентов NPGS., _regulator_config(), clip_unit(), linear(), log_norm(), Фиксированная нормализация Observation Space — единый контракт train ↔ deploy.… (+18 more)

### Community 23 - "PID Controller Numerics"
Cohesion: 0.09
Nodes (29): Регуляторы канала по именам — для логов и приёмки, не для…, PIDController, Сброс внутренних состояний (используется при выключении системы)., _legacy_reference(), Опциональная численность PID (шаг 5): каждый флаг проверяется на том дефекте,…, При `steering_eff = 0` применяется 0 вместо выхода PID — интегратор обязан это…, Если применено ровно то, что выдал PID, коррекции быть не должно., Уставка прыгает, объект стоит на месте — D-составляющая не должна реагировать.… (+21 more)

### Community 24 - "Policy Evaluation Baselines"
Cohesion: 0.10
Nodes (25): Худшая реплика по заданной метрике. Приёмка смотрит именно на худшую, а не на…, worst_replica(), compare_policies(), DefaultGainsPolicy, main(), Policy, PresetPolicy, ndarray (+17 more)

### Community 25 - "PPO Training Runtime"
Cohesion: 0.11
Nodes (21): PPOTrainer, Tensor, Собирает rollout из среды и обновляет NPGS многокомпонентным PPO-loss., Шагает средой `rollout_len` тактов (сброс по завершению эпизода). → статистика., Хук L_shield (§11): барьер, отталкивающий выход от края уровня-1 Shield. По…, build_ics_stack(), build_training_stack(), CSVLogger (+13 more)

### Community 26 - "X-Plane Backend Tests"
Cohesion: 0.10
Nodes (14): get_aircraft_profile(), test_xplane_ignores_failures_outside_rollout_contract(), MockXPlaneConnector, ScriptedXPlaneConnector, test_commands_failures_and_close_release_overrides(), test_failed_approach_setup_releases_overrides_and_pause(), test_ignored_xplane_failure_participates_in_segment_delta_and_is_cleared(), test_missing_or_stale_required_data_makes_xplane_telemetry_invalid() (+6 more)

### Community 27 - "Acceptance Evaluation Tests"
Cohesion: 0.15
Nodes (31): evaluate_tz(), Диагностика эпизода + сценарий → список вердиктов по пунктам ТЗ разд. 5., Итог эпизода: FAIL, если провален хоть один применимый критерий., verdict_of(), _by_name(), _diagnostics(), Тесты приёмки по ТЗ (Этап 5): вердикты по пунктам, правило «нет данных = FAIL»,…, Эпизод не дошёл до руления → допуск ±1 м неприменим. Это SKIP, а не тихий… (+23 more)

### Community 28 - "PPO Agent Learning"
Cohesion: 0.12
Nodes (24): build_npgs(), NPGSConfig, Any, Гиперпараметры архитектуры NPGS (замораживаются вместе с весами при поставке)., PPOConfig, Any, device, PPO-тренер + многокомпонентный loss для NPGS (план §11). `L = L_ppo +… (+16 more)

### Community 29 - "ICS Engagement State"
Cohesion: 0.07
Nodes (16): IcsEngagement, Автомат включения. `step(inputs)` вызывается каждый такт до формирования…, Полный сброс — новый эпизод начинается с невключённого состояния., Сообщить автомату, что кадр **фактически ушёл** на стенд. Вызывается…, Войти в заход самостоятельно: шлём `ControlMode = Approach`. Обычно вызывать не…, Выдержка под текущую цель: воздушная длиннее наземной (2.2 с против 2.0)., Уже гоним какой-то режим (Approach/Rollout/Taxi), а не заявку готовности., Признак стенда `AgentIsActive`: интерфейс ICS активен. Необходимое условие. (+8 more)

### Community 30 - "Legacy X-Plane Client"
Cohesion: 0.08
Nodes (13): XPlaneConnectX class initialization. Args: ip (str, optional): IP address where…, Starts a recording of the subscribed DataRefs into self.recorded_data. Data is…, Terminates the recording and returns a dictionary of lists that contain the…, Synchronize measurements from multiple sensors to a common frequency.…, Gets the current value of a DataRef. This is only intended for one-time use.…, Permanently subscribe to a list of DataRefs with a certain frequency. This is…, Writes a value to the specified DataRef provided that the DataRef is writable.…, Sends simulator commands to the simulator. These are not commands for the… (+5 more)

### Community 31 - "Rollout Observation Environment"
Cohesion: 0.09
Nodes (23): ObservationBuilder, ObserverEstimate, Оценки PINN-обсервера (§12). Заглушка нулями до Этапа 7., Строит нормированный вектор наблюдения одного кадра., EpisodeObjective, Накопитель по эпизоду: собирает потактовые отсчёты → сводные компоненты.…, EpisodeInfo, _make_box() (+15 more)

### Community 32 - "Wind Decomposition Models"
Cohesion: 0.08
Nodes (24): compose_wind(), decompose_wind(), Any, Собирает ветер из компонент относительно курса ВПП. `crosswind_kts` > 0 — ветер…, Сериализация в примитивы (для логирования/воспроизводимости сценариев)., (скорость, откуда) → (crosswind, headwind) относительно курса ВПП. crosswind >…, (crosswind, headwind) → (скорость, откуда, °). Обратна `decompose_wind`., test_scenario_roundtrip_with_weather_and_failures() (+16 more)

### Community 33 - "Graphify Query Workflow"
Cohesion: 0.08
Nodes (29): Folder Watcher, URL Ingestion, Extra Graph Exports, MCP Graph Server, Confidence Audit Trail, Deterministic Node IDs, Semantic Extraction Contract, Cross-Repository Graph Merge (+21 more)

### Community 34 - "X-Plane Connector Protocol"
Cohesion: 0.11
Nodes (6): Discard pre-reload values so readiness cannot use stale telemetry., Одна подписка, один поток приёма и явное освобождение ресурсов., Send basic controls to the ego aircraft. There are hundreds of DataRefs that…, Совместимое read-only представление старого XPlaneConnectX., Совместимость с прежним клиентом., XPlaneConnector

### Community 35 - "Rollout Shield Integration"
Cohesion: 0.12
Nodes (21): base_gains_from_pids(), Снимок (kp, ki, kd) регуляторов — пресет-якорь для Shield и т.п., preset_action(), float64, 17-мерное действие, точно воспроизводящее коэффициенты пресета (веса = 1).…, ndarray, Окно истории → тензор `(history_len, OBS_DIM)` (последовательность кадров для…, RolloutEnv (+13 more)

### Community 36 - "Physical Gain Mapping"
Cohesion: 0.14
Nodes (12): GainKey, ActorOutput, TypedDict, Тензоры одного прохода актора, до преобразования в NumPy., GainSpace, Any, ArrayLike, float64 (+4 more)

### Community 37 - "ICS Engagement Tests"
Cohesion: 0.15
Nodes (26): _engine(), Автомат включения управления на стенде. Два раздельных предмета проверки: *…, По ICD стенд должен два секунды ПОЛУЧАТЬ ModeAIReady=1. Если считать одно лишь…, Неудачная отправка (сокет вернул False) выдержку не продвигает., Что бы мы ни слали, включены мы только когда стенд ответил AgentIsActive = 1., Единичный потерянный пакет не должен «выключать» нас на такт., Валидный кадр с AgentIsActive = 0 — стенд снял активацию, значит и мы больше не…, `ControlMode` нет во входной структуре, поэтому подхват опирается на фазу… (+18 more)

### Community 38 - "Bench Diagnostic Tools"
Cohesion: 0.20
Nodes (21): ControlsState, Разделяемая по тактам структура команд — и наземных, и воздушных. Аннотации…, build_altitude_sweep(), command_for_pulse(), Безопасные elevator/altitude authority sweep без дублирования ICS runner., Чистое преобразование, пригодное и для dry-run, и для ICSSim., safety_reason(), SweepLimits (+13 more)

### Community 39 - "Fake ICS Connector Tests"
Cohesion: 0.10
Nodes (20): FakeConnector, make_ics_inputs(), Отправленные команды в нормированном виде — для сравнения траекторий.…, Полный пакет стенда: нули по умолчанию + заданные поля., Статический стенд: всегда один и тот же кадр, отправленное — в `sent_outputs`., Погоду задаёт Заказчик; наш `WeatherState` — это прочитанный кадр, а не задание., До рукопожатия заявлять каналы нельзя: стенд ещё не разрешил нам ими управлять., Стенд отдаёт узлы, футы, футы/мин и градусы/с — граница пересчёта проходит… (+12 more)

### Community 40 - "Legacy Approach Controller"
Cohesion: 0.19
Nodes (17): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+9 more)

### Community 41 - "Engagement Timing Tests"
Cohesion: 0.12
Nodes (20): _Clock, _pump(), Обратная защита: 30 кадров можно выпалить за 0.1 с — время тоже обязано пройти., Срыв предусловия обнуляет и время, и счётчик кадров., Требование ICD — непрерывность: пропуск готовности рвёт серию., Порог задан в узлах. 1.5 узла — стимул идёт; 2.9 узла — нет. Пересчёт…, Прямой тест главного дефекта: наша выдержка 2 с сама по себе включения не даёт., Обратная сторона: `AgentIsActive` появляется, как только оператор включил ICS в… (+12 more)

### Community 42 - "NPGS Policy Admission"
Cohesion: 0.14
Nodes (13): floating, NPGS, float32, Tensor, Neural PID Gain Scheduler: общий энкодер + головы актора (абс. gain'ы) + голова…, → (mean (B,17), value (B,), phase_logits (B,n_phases))., 17 сырых выходов → [абс. gains×15, w_lon, w_lat] (layout `REGULATOR_ORDER` +…, Один шаг актора. `action` (…,17) — абс. gain'ы для среды; `raw` (…,17) — сэмпл… (+5 more)

### Community 43 - "Legacy ICS Runner"
Cohesion: 0.20
Nodes (21): airborne_control_mode(), airborne_flare_mode(), deactivate(), live_main(), main(), main_gear_contact(), make_airborne_output(), ControlModeState (+13 more)

### Community 44 - "Action Contract Definition"
Cohesion: 0.12
Nodes (18): ControlArchitecture, Фиксированный порядок слоёв и роль обучаемого компонента., Проверяет контракт обучаемого слоя. Нарушение → `ValueError` на старте…, validate_action_contract(), Контракт обучаемого слоя (Этап 4): что именно сеть имеет право менять. Аргумент…, Полный слепок настраиваемого состояния контура — всё, что действие могло бы…, Пустое обоснование = контракт непредъявим по ТЗ., Машиночитаемое утверждение «сеть не является регулятором». (+10 more)

### Community 45 - "SFT Capture Runtime"
Cohesion: 0.16
Nodes (20): ground_cases(), Шифры, у которых настраиваются коэффициенты **пробега** (пригодны для SFT).…, build_sim(), Any, Path, Создать явно выбранный backend с общим контрактом :class:`SimInterface`., build_capture_stack(), build_scenarios() (+12 more)

### Community 46 - "Scenario Generation"
Cohesion: 0.13
Nodes (12): Any, Serialize only the canonical profile-aware schema v2., Один случайный сценарий. `difficulty=None` → случайная сложность., ScenarioGenerator, test_battery_covers_key_cases_and_roundtrips(), test_generator_embeds_control_config(), test_generator_high_difficulty_produces_failures(), test_generator_is_deterministic_for_same_seed() (+4 more)

### Community 47 - "Engagement Input Processing"
Cohesion: 0.11
Nodes (11): EngagementInputs, ControlModeState, Подхватить уже включённый извне пробег: шлём `ControlMode = Rollout`.…, Войти в пробег самостоятельно: шлём `ControlMode = Rollout`. Это же — передача…, Передать управление в руление (`ControlMode 3 → 4`). → удался ли переход.…, Продвинуть автомат: снять признак стенда и обновить исходящий стимул.…, Оба условия сразу: прошло время И столько же кадров реально ушло. Время…, Под какой режим гнать стимул. `None` — предусловий нет ни для одного. Воздушный… (+3 more)

### Community 48 - "Run Artifact Recording"
Cohesion: 0.17
Nodes (10): default_runs_root(), _jsonable(), Path, Единый CSV-регистратор прогонов ICS и X-Plane., Один раз сохранить накопленные кадры и итоговые артефакты прогона., Единый каталог прогонов, не зависящий от cwd процесса/Jupyter., RunRecorder, test_run_recorder_writes_replayable_run_and_non_destructive_gain_export() (+2 more)

### Community 49 - "Full Flight Test Helpers"
Cohesion: 0.16
Nodes (17): _air(), _Clock, _pump(), После касания режим меняется на пробег — но не раньше: смена режима на глиссаде…, Ниже 80 футов потеря `AgentIsActive` не повод бросать органы: до земли секунды., Окно только удерживает подтверждение. Само оно включения не даёт., Воздушное включение — это фронт `Off → Approach` после выдержки, а не сразу…, 2.2 с — подтверждённое на стенде значение; наземные 2.0 для захода недостаточны. (+9 more)

### Community 50 - "Go-Around Tests"
Cohesion: 0.19
Nodes (19): _armed_controller(), _drive(), _frame(), Уход на второй круг (fallback в воздухе): условия срабатывания и передача…, После установившегося набора цикл снимает заявку каналов (ControlMode=Off,…, Контур на заходе: `begin_flight` по кадру в воздухе выше 400 футов., Устойчивое превышение курсового допуска выше высоты решения → уход на второй…, Один-два кадра за допуском ухода не вызывают — нужен устойчивый выход (дебаунс). (+11 more)

### Community 51 - "Neural Architecture Plan"
Cohesion: 0.19
Nodes (19): Hybrid Neural PID Controller, Neural PID Gain Scheduler, PPO Training Loop, Preset-Anchored Deterministic Shield, SFT Behavioral-Cloning Warm Start, Absolute-Gain Action Space, Classical PID as the Plant, Deterministic Deployment Runtime (+11 more)

### Community 52 - "Approach Criteria Monitor"
Cohesion: 0.19
Nodes (12): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, Отдельный монитор критерия А.1.1 (не участвует в go-around)., Захватывает А.1.1 после входа в допуск и завершает оценку на 300 ft., frame() (+4 more)

### Community 53 - "Dashboard Runtime Integration"
Cohesion: 0.17
Nodes (11): _finite_or_none(), GainUpdateRequest, Unified local dashboard for the three airborne and five ground PIDs., Валидировать HTTP-запрос и передать запись control-потоку., ViewSpec, controller_pids(), gains_snapshot(), pid_operating_points() (+3 more)

### Community 54 - "Dashboard State and Configuration"
Cohesion: 0.17
Nodes (9): DashboardState, _handler_factory(), Path, Применяется только control-потоком в начале такта., Thread-safe live state or an immutable CSV replay., configured_controller(), test_capture_export_and_replay_common_run(), test_dashboard_http_api_is_local_and_monitor_only() (+1 more)

### Community 55 - "Runway Guidance Tracking"
Cohesion: 0.20
Nodes (6): Решить прямую геодезическую задачу на сферической Земле., Guidance по курсу ВПП и измеренному отклонению — без собственной геодезии.…, Возвращает отклонение от осевой линии в метрах. >0 - правее оси, <0 - левее., Геодезическое наведение на ось ВПП с упреждением по скорости., RunwayTracker, test_runway_profile_delegates_geometry_to_tracker()

### Community 56 - "Roman Log Import"
Cohesion: 0.19
Nodes (10): _number(), Path, Импорт и проверка внешних CSV-прогонов roman_aviacia_ics., Потоково нормализует основной и authority CSV Романа., RomanLogImporter, verify_manifest(), fixture, roman_csv() (+2 more)

### Community 57 - "Legacy Approach Criteria"
Cohesion: 0.18
Nodes (9): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, ICSInputs, Evaluate the A.1.1 approach segment and stop at a radio-altitude floor., ICSInputs (+1 more)

### Community 58 - "Runway Profile Configuration"
Cohesion: 0.18
Nodes (11): find_earth_nav_dat(), get_runway_profile(), ILSStation, parse_ils_station(), Path, Профили ВПП и разрешение ILS из установленной базы X-Plane., Точка на продолжении оси; положительное расстояние — до порога., Найти LOC (тип 4) без хардкода частоты. (+3 more)

### Community 59 - "Checkpoint Admission Battery"
Cohesion: 0.18
Nodes (16): admit_checkpoint(), Пропускать ли чекпоинт дальше. Отсутствующая/нечисловая метрика = отказ.…, _battery(), Отсутствующая метрика = отказ, а не «нет данных — значит нет проблемы»., Если сеть не бьёт классику, она не окупается — выпускать её нечего., Канал не двигался за эпизод → p95 = None. Это не дефект., Отрицательный результат должен быть виден в отчёте, а не спрятан., Сводка прогона под одной политикой из списка диагностик. (+8 more)

### Community 60 - "Legacy Controller Configuration"
Cohesion: 0.17
Nodes (9): ControllerConfig, PID, PIDConfig, Path, Filtered PID with conditional-integration anti-windup., test_future_go_around_pitch_envelope_does_not_expand_landing_flare(), test_roundout_commands_a_material_pitch_increase_before_touchdown(), test_validated_controller_config_is_packaged() (+1 more)

### Community 61 - "Reference Speed Trajectory"
Cohesion: 0.18
Nodes (8): LongitudinalChannel, Управление скоростью по эталонной кривой. Телеметрию получает параметром, не…, PidMap, Генератор эталонной кривой скорости (Колокол Гаусса)., Возвращает идеальную скорость (м/с) для текущей точки пути., ReferenceTrajectory, test_equally_slow_law_endpoints(), test_gauss_bell_endpoints_and_monotonicity()

### Community 62 - "Project Dependency Architecture"
Cohesion: 0.18
Nodes (13): Autonomous Landing Controller, Repository Guidance for Codex, Autonomous Landing Controller, Repository Guidance for Claude Code, Neural Landing Implementation Plan, Unified Scenario System, Optional Gymnasium, NumPy (+5 more)

### Community 63 - "NPGS Phase Encoding"
Cohesion: 0.22
Nodes (11): int64, _init_log_std(), layer_init(), _mlp_head(), phase_labels_from_groundspeed_kts(), ArrayLike, NDArray, Neural PID Gain Scheduler (NPGS) — актор + критик (план §10; выход — АБСОЛЮТНЫЕ… (+3 more)

### Community 64 - "Lateral Guidance Channel"
Cohesion: 0.21
Nodes (6): LateralChannel, Удержание оси ВПП. Телеметрию получает параметром, не читает сам., Guidance по тому, что даёт стенд. → словарь guidance или None, если данных нет.…, Единый GuidanceState текущего кадра для control/observation/reward., GuidanceState, Совместимость со старым словарным API.

### Community 65 - "Bench Failure Sync Tests"
Cohesion: 0.17
Nodes (11): engaged_inputs(), on_ground(), ICSInputs, Кадр «ВС на полосе»: обжаты все стойки, курс/координаты у порога UUEE 06R., Кадр стенда, который уже принял управление: `AgentIsActive = 1`, идёт пробег., Пресет — стартовое предположение; фактическую конфигурацию сообщает борт., Отказ может быть снят — накапливающий учёт держал бы орган мёртвым до конца…, test_controller_takes_failures_from_the_bench_not_from_the_preset() (+3 more)

### Community 66 - "Failure Degradation Management"
Cohesion: 0.21
Nodes (6): Деградация команд по эффективности актуаторов — **только наземные органы**.…, FailureManager, FailureState, Эффективности исполнительных органов. Аннотации типов обязательны: без них…, Проецирует набор дискретных отказов в эффективности исполнительных органов., Привести состояние ровно к набору `modes` (то, что сообщил стенд). Пересборка с…

### Community 67 - "Gain Action Application"
Cohesion: 0.18
Nodes (8): apply_corrections(), GainMap, Применяет абсолютные gain'ы к контуру. Возвращает `(effective_gains,…, Копия команды такта — для расчёта джерка на следующем такте. Копируется…, Состояние для поведенческих проверок Shield. Курс здесь — отклонение от…, _snapshot_command(), Действие сети меняет только kp/ki/kd и веса каналов — всё остальное…, test_applying_an_action_moves_nothing_but_gains()

### Community 68 - "Weather and RREF Models"
Cohesion: 0.18
Nodes (4): FrictionProfile, Ступенчатый профиль сцепления по дистанции пробега., DatagramSocket, test_rref_subscription_packet_and_freshness()

### Community 69 - "Classical Control Parity"
Cohesion: 0.18
Nodes (10): Тесты паритета после выноса контура из main.ipynb в пакет ismpu. Полный паритет…, test_guidance_on_centerline_small_heading_error(), test_pid_anti_windup_clamp(), test_pid_filtered_derivative(), test_pid_output_clamped_to_bounds(), test_pid_proportional_and_integral_accumulation(), test_pid_zero_dt_returns_zero(), test_xte_sign_left_is_negative() (+2 more)

### Community 70 - "PID Anti-Windup Logic"
Cohesion: 0.20
Nodes (4): → (интеграл только с утечкой, интеграл с утечкой и приращением). Оба уже зажаты., Такт регулятора. `measurement` обязателен при `derivative_on_measurement=True`., Back-calculation: подтянуть интегратор к фактически применённой команде. No-op…, Вес апериодического фильтра D-составляющей за такт `dt`.

### Community 71 - "System Requirements Guidance"
Cohesion: 0.22
Nodes (9): Technical-Specification Acceptance Gates, Bench-Validated ILS Approach Channel, Forward-Only Flight Segment Supervisor, Tolerance-Gated Go-Around, Longitudinal and Lateral Ground Channels, PID Run Matrix, Unified Profile-Aware Scenario System, Legacy Scenario Preset Model (+1 more)

### Community 72 - "PID Dashboard Ecosystem"
Cohesion: 0.25
Nodes (9): Nine-View PID Dashboard, Run Recording Artifacts, buildTabs, draw, Gain Tuning and Snapshot Export, Interactive PID Dashboard, refresh, render (+1 more)

### Community 73 - "Control Factory Wiring"
Cohesion: 0.31
Nodes (5): Пропорционально-интегрально-дифференциальный регулятор. Улучшенный PID с leaky-…, apply_ground_control(), build_pids(), Сборка классического контура из неизменяемой конфигурации., Фабрики stateful-объектов; config-модули хранят только данные.

### Community 74 - "Legacy Dashboard State"
Cohesion: 0.36
Nodes (3): DashboardState, Any, ICSInputs

### Community 75 - "Legacy ICS Protocol"
Cohesion: 0.31
Nodes (6): ControlModeState, GearState, ICSOutputs, Any, IntEnum, ReverseEngineType

### Community 76 - "Bench C Sharp Interface"
Cohesion: 0.36
Nodes (7): External.Systems.ICS, ControlModeState, GearState, ICSInputs, ICSOutputs, ReverseEngineType, UInt64

### Community 77 - "Invalid Telemetry Handling"
Cohesion: 0.25
Nodes (7): Кадр «связи со стендом нет». Нули, а не None: контур проверяет `valid` первым., Первый `read_telemetry` может вернуться по таймауту — это не «мы на полосе».…, test_the_segment_is_not_decided_by_a_frame_without_a_bench_packet(), Единичный таймаут — не повод вернуть рулю авторитет, которого у него нет., Без кадра о конфигурации борта неизвестно ничего — безопасен только штатный…, test_lost_packet_does_not_repair_a_failed_actuator(), test_select_for_telemetry_falls_back_to_default_without_telemetry()

### Community 78 - "Legacy Rollout Bridge"
Cohesion: 0.39
Nodes (5): ICSInputs, Hand the validated airborne session to Vlayd's existing rollout loop. The…, Keep Vlayd's engagement latch synchronized during the approach., Run Vlayd's rollout until taxi speed, then send its taxi handoff., VlaydRolloutBridge

### Community 80 - "Legacy Dashboard Frontend"
Cohesion: 0.29
Nodes (7): buildControls, draw, formatTime, Four-Loop PID Tuning, ICS PID Monitor, Live and Historical Timeline, refresh

### Community 81 - "X-Plane Wire Compatibility"
Cohesion: 0.29
Nodes (3): DatagramSocket, test_legacy_subscription_starts_at_zero_and_retries_with_diagnostics(), test_xplane_used_wire_packets_match_confirmed_original()

### Community 82 - "ICS Backend Architecture"
Cohesion: 0.33
Nodes (6): Fourteen-Bit ControlValidMask Layout, Dual-Backend SimInterface, Two-Factor ICS Engagement Handshake, ICS UDP JSON Protocol, Telemetry SI Unit Boundary, ICS-Only Backend Guidance

### Community 83 - "X-Plane Runtime Architecture"
Cohesion: 0.60
Nodes (6): Aircraft-Profile Checkpoint Isolation, Live A330 Acceptance Checklist, Profile-Aware Flight Scenarios, X-Plane Dashboard and Runtime Guide, X-Plane Resettable Runtime, X-Plane Training and Evaluation Backend

### Community 84 - "Colleague Configuration Parity"
Cohesion: 0.33
Nodes (5): _pid_from_colleague(), Загрузка настроек из JSON коллеги (`config/ics_clear_weather_pid.json`). Секции…, `PIDConfig` коллеги → аргументы нашего `PIDController`. Предел интегратора у…, Наши умолчания и его файл — одно и то же. Разойдутся — расхождение должно быть…, test_config_from_the_colleague_json_matches_our_defaults()

### Community 85 - "Control Neutralization"
Cohesion: 0.33
Nodes (3): Обнуляет все органы управления. Отправку делает вызывающий через `ICSSim.step`.…, Сброс к нейтральным командам — новый эпизод начинается с чистого состояния.…, Обнулить только воздушные команды. Нужно, когда воздушный канал не может…

### Community 87 - "RREF Packet Handling"
Cohesion: 0.33
Nodes (3): DataRefSample, Неблокирующий UDP-клиент нативного протокола X-Plane 12., Разобрать пакет; публично для детерминированных mock-тестов.

### Community 88 - "NPGS Policy Loading"
Cohesion: 0.33
Nodes (4): load_npgs_policy(), NPGSPolicy, Политика на основе обученной сети. Детерминированная (greedy) — режим поставки., Загружает чекпоинт NPGS (веса + конфиг + слепок нормировки) в политику.

### Community 90 - "Bench Fault Decoding"
Cohesion: 0.40
Nodes (4): _faults_from_inputs(), ICSInputs, Отказы, о которых сообщает борт — **единственный** источник истины об отказах.…, Сигналы отказов со стенда → наши `FailureMode`. Отказы шасси…

### Community 91 - "Acceptance Criterion Checks"
Cohesion: 0.40
Nodes (4): _check(), Criterion, Один пункт ТЗ: предел, измеренное значение, вердикт и его причина., Строит вердикт. Неприменимо → SKIP; применимо, но данных нет → FAIL.

### Community 92 - "Altitude Dependent Roll Limits"
Cohesion: 0.50
Nodes (4): Предел крена по высоте: чем ниже, тем меньше запас до касания законцовкой.…, roll_limit_deg(), Чем ниже, тем меньше запас до касания законцовкой; настроенный предел не…, test_roll_limit_tightens_towards_the_ground()

### Community 94 - "Acceptance Report Rendering"
Cohesion: 0.50
Nodes (4): Markdown-отчёт приёмки. Отрицательные результаты не скрываются — они и есть…, Пишет `evaluation.json` + `report.md`. → пути записанных файлов., render_report(), write_report()

## Ambiguous Edges - Review These
- `Dual-Backend SimInterface` → `ICS-Only Backend Guidance`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to
- `Unified Profile-Aware Scenario System` → `Legacy Scenario Preset Model`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **31 isolated node(s):** `External.Systems.ICS`, `ismpu`, `Semantic Extraction Cache`, `Graph Health Check`, `URL Ingestion` (+26 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Dual-Backend SimInterface` and `ICS-Only Backend Guidance`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Unified Profile-Aware Scenario System` and `Legacy Scenario Preset Model`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `ControllingSystem` connect `Flight Control Supervisor` to `Approach Limits and Tolerances`, `Rollout Rewards and Gates`, `Scenario Configuration Parsing`, `Simulator Interface and Telemetry`, `ICS Protocol Data Structures`, `Flight Phase Telemetry`, `Segment Transitions and Runtime`, `SFT Pretraining Pipeline`, `Scenario Registry and Matrix`, `ICS Simulator Engagement Tests`, `Aircraft Profiles and Scenarios`, `Approach Control Configuration`, `Telemetry Condition Matching`, `Neural Action Encoding`, `PID Controller Numerics`, `Policy Evaluation Baselines`, `PPO Training Runtime`, `X-Plane Backend Tests`, `Acceptance Evaluation Tests`, `PPO Agent Learning`, `Rollout Observation Environment`, `Rollout Shield Integration`, `Bench Diagnostic Tools`, `Fake ICS Connector Tests`, `NPGS Policy Admission`, `Action Contract Definition`, `SFT Capture Runtime`, `Run Artifact Recording`, `Full Flight Test Helpers`, `Go-Around Tests`, `Approach Criteria Monitor`, `Dashboard State and Configuration`, `Runway Guidance Tracking`, `Reference Speed Trajectory`, `Lateral Guidance Channel`, `Bench Failure Sync Tests`, `Failure Degradation Management`, `Weather and RREF Models`, `Classical Control Parity`, `Control Factory Wiring`, `Invalid Telemetry Handling`, `Legacy Rollout Bridge`, `X-Plane Wire Compatibility`, `NPGS Policy Loading`, `Acceptance Criterion Checks`, `Go-Around Maneuver`?**
  _High betweenness centrality (0.138) - this node is a cross-community bridge._
- **Why does `Telemetry` connect `Telemetry Condition Matching` to `Approach Limits and Tolerances`, `Rollout Rewards and Gates`, `Weather and Run Conditions`, `Scenario Configuration Parsing`, `Simulator Interface and Telemetry`, `Approach Channel Parity`, `Flight Control Supervisor`, `ICS Protocol Data Structures`, `Flight Phase Telemetry`, `Segment Transitions and Runtime`, `Scenario Registry and Matrix`, `ICS UDP Connector`, `ICS Simulator Engagement Tests`, `Aircraft Profiles and Scenarios`, `ICS Simulator Runtime`, `Approach Control Configuration`, `X-Plane Simulator Lifecycle`, `ICS Engagement State`, `Rollout Observation Environment`, `Bench Diagnostic Tools`, `Fake ICS Connector Tests`, `Engagement Input Processing`, `Full Flight Test Helpers`, `Go-Around Tests`, `Approach Criteria Monitor`, `Reference Speed Trajectory`, `Lateral Guidance Channel`, `Classical Control Parity`, `Invalid Telemetry Handling`, `Legacy Rollout Bridge`, `Dashboard JSON Serialization`, `Bench Fault Decoding`, `Go-Around Maneuver`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Why does `ControlsState` connect `Bench Diagnostic Tools` to `Approach Limits and Tolerances`, `Rollout Rewards and Gates`, `Weather and Run Conditions`, `Deterministic Safety Shield`, `Simulator Interface and Telemetry`, `Approach Channel Parity`, `Flight Control Supervisor`, `Segment Transitions and Runtime`, `ICS Simulator Engagement Tests`, `Aircraft Profiles and Scenarios`, `ICS Simulator Runtime`, `Approach Control Configuration`, `Telemetry Condition Matching`, `X-Plane Simulator Lifecycle`, `PID Controller Numerics`, `X-Plane Backend Tests`, `Rollout Observation Environment`, `Rollout Shield Integration`, `Fake ICS Connector Tests`, `Action Contract Definition`, `Runway Guidance Tracking`, `Legacy Approach Criteria`, `Legacy Controller Configuration`, `Reference Speed Trajectory`, `Lateral Guidance Channel`, `Failure Degradation Management`, `Gain Action Application`, `Weather and RREF Models`, `Control Neutralization`, `Final Command Clamping`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `ControllingSystem` (e.g. with `AircraftControlSet` and `ApproachSetup`) actually correct?**
  _`ControllingSystem` has 43 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `ControlsState` (e.g. with `GainCommand` and `RuntimeState`) actually correct?**
  _`ControlsState` has 40 INFERRED edges - model-reasoned connections that need verification._