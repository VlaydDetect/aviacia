# Graph Report - GOSNIIASProject  (2026-08-15)

## Corpus Check
- 141 files · ~164,945 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2649 nodes · 6116 edges · 177 communities (121 shown, 56 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 509 edges (avg confidence: 0.58)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `11e4050b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- criticality.py
- GainCommand
- train.py
- test_icd_units.py
- Shield
- test_refactoring_contracts.py
- Scenario
- ControlsState
- ControlProfile
- GainSpace
- failures.py
- LateralChannel
- test_pretrain.py
- SegmentConditions
- test_ics_connector.py
- test_run_matrix.py
- AircraftProfile
- ICSSim
- ApproachController
- Telemetry
- gain_scheduler.py
- XPlaneSim
- test_weather.py
- PIDController
- evaluate.py
- RolloutEnv
- test_xplane_backend.py
- test_evaluate.py
- test_ppo.py
- IcsEngagement
- XPlaneConnectX
- runway_profiles.py
- test_splits.py
- Graphify Pipeline
- XPlaneConnector
- ControllingSystem
- scenario.py
- test_ics_engagement.py
- test_tolerance.py
- FakeConnector
- pid_controller.py
- scenarios.py
- NPGS
- ICSInputs
- test_gain_scheduler.py
- 3. Этапы реализации
- ScenarioGenerator
- EngagementInputs
- RunRecorder
- _Clock
- test_go_around.py
- Neural PID Gain Scheduler Architecture
- test_approach_criteria.py
- ._approach_step
- .value
- RunwayTracker
- RomanLogImporter
- working_ics/approach_criteria.py
- .from_dict
- fakes.py
- gain_space_for
- test_control_parity.py
- Project Dependencies
- test_full_flight.py
- GuidanceState
- ICSInputs
- DashboardState
- heading_deviation_deg
- test_working_ics_dashboard.py
- ICSOutputs
- agent/pretrain.py
- Unified Profile-Aware Scenario System
- Interactive PID Dashboard
- MatrixRun
- DashboardState
- FailureMode
- ICSInterface.cs
- compute_reward
- runtime/pretrain.py
- PPOTrainer
- ICS PID Monitor
- ics_connector.py
- ICS UDP JSON Protocol
- X-Plane Dashboard and Runtime Guide
- test_working_ics_golden.py
- EpisodeObjective
- RuntimeError
- ConditionMatch
- .from_crosswind
- envelope.py
- LongitudinalChannel
- test_action_contract.py
- base_gains_from_pids
- test_rollout_env.py
- SimInterface
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
- protocol.py
- Q: Реализовать этап 0: baseline, golden replay и dashboard characterization
- Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md).
- build_sim
- normalization.py
- test_ics_sim.py
- Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md).
- gui/dashboard.py
- IntEnum
- ControlModeState
- ICSInputs
- ICSOutputs
- socket
- static_sim
- EngagementInputs
- .begin_flight
- .compute
- import_workbook
- .from_ics
- telemetry
- HandshakeBench
- control.py
- ApproachLimits
- .enter_segment
- ApproachTelemetry
- Q: Приступай к выполнению этапа 2 плана docs/plan.md
- _faults_from_inputs
- IcsEngagement
- .load
- ApproachConfig
- SimInterface
- SimInterface
- .__init__
- ControlModeState
- ApproachChannel
- ApproachConfig
- RunResult
- FailureState
- RunwayProfile
- ShutdownReport
- PidMap
- StartMode
- PidMap
- runway_condition_from_bench
- RolloutBuffer
- weather.py
- Scenario
- FrictionProfile
- Q: Приступай к выполнению этапа 4 плана docs/plan.md
- ReferenceTrajectory
- RewardWeights
- TypedDict
- roll_limit_deg
- ControlArchitecture
- .pids
- PIDDiagnostics
- .reset
- test_control_step_is_unchanged_when_tracking_is_off
- ApproachSetup
- ConditionMatch
- ICSInputs
- Scenario
- Scenario
- Scenario
- RunRecorder
- parametrize
- TouchdownSetup

## God Nodes (most connected - your core abstractions)
1. `ControllingSystem` - 179 edges
2. `Telemetry` - 121 edges
3. `ControlsState` - 92 edges
4. `Scenario` - 79 edges
5. `ICSSim` - 79 edges
6. `XPlaneSim` - 56 edges
7. `PIDController` - 52 edges
8. `RolloutEnv` - 52 edges
9. `GainSpace` - 47 edges
10. `IcsEngagement` - 45 edges

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
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/tolerance.py -> ismpu/control/approach.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/aircraft_profiles.py -> ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py -> ismpu/config/aircraft_profiles.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach_criteria.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/flight.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/ground_allocator.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/tolerance.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`

## Hyperedges (group relationships)
- **Graphify Extraction and Build Flow** — _codex_skills_graphify_skill_structural_extraction, _codex_skills_graphify_skill_semantic_extraction, _codex_skills_graphify_references_extraction_spec_semantic_extraction_contract, _codex_skills_graphify_references_update_build_merge [EXTRACTED 1.00]
- **Hybrid Neural Landing Control** — implementation_plan_classical_pid_plant, implementation_plan_npgs, implementation_plan_deterministic_shield, implementation_plan_ppo_multicomponent_loss, implementation_plan_pinn_observer [EXTRACTED 1.00]
- **PID Dashboard Ecosystem** — docs_xplane_dashboard_pid_dashboard, ismpu_gui_dashboard_pid_dashboard, ismpu_working_ics_ics_dashboard_ics_pid_monitor [INFERRED 0.85]

## Communities (177 total, 56 thin omitted)

### Community 0 - "criticality.py"
Cohesion: 0.09
Nodes (26): lateral_limit_m(), lateral_load_situation(), lateral_situation(), normal_load_situation(), IntEnum, Критерии критичности особых ситуаций МС-21 (Приложение 1 к ТЗ). Таблица АП-25…, Классификация скорости касания относительно VAPP и VВПП пред., Классификация нормальной перегрузки посадочного удара. `heavy` — взлётный вес. (+18 more)

### Community 1 - "GainCommand"
Cohesion: 0.13
Nodes (11): _clip(), GainCommand, GainMap, RegulatorKey, Что сделал Shield за такт: активированные правила, штрафы, fallback., Уровни 1–2. Возвращает `(effective_gains, safe_command, report)`.…, Уровень 3. Правит небезопасные команды и возвращает `(command, report)`., Выход актора: абсолютные коэффициенты PID + веса каналов. `gains[reg] =… (+3 more)

### Community 2 - "train.py"
Cohesion: 0.11
Nodes (20): Проверяет контракт обучаемого слоя. Нарушение → `ValueError` на старте…, validate_action_contract(), build_ics_stack(), build_training_stack(), CSVLogger, make_curriculum_provider(), Цикл обучения NPGS через PPO с domain randomization (план §11, Этап 4).…, Строит (env, npgs, trainer) поверх стенда. Требует работающий стенд. С… (+12 more)

### Community 3 - "test_icd_units.py"
Cohesion: 0.10
Nodes (19): Сверка каждого сигнала стенда с документами Заказчика. Два независимых…, Стенд шлёт узлы, футы, фут/мин и град/с — граница пересчёта в СИ проходит в…, 1 фут/мин = 0.3048/60 м/с. Приближение здесь копится на всём заходе., Нумерация фаз из doc-комментария `FlightPhase` в ICSInterface.cs., −26.5…55.0° — фактическое положение РУД во входной телеметрии, не команда., Наши константы обязаны совпадать с таблицей управляющих сигналов Заказчика., Тиллер задаётся ходом в миллиметрах. Отдельным тестом, потому что ошибка была…, 0–45 мм командует, 0–36.73 мм отчитывается. Подмена недодаёт ~18 % хода. (+11 more)

### Community 4 - "Shield"
Cohesion: 0.14
Nodes (25): Наблюдаемое состояние для поведенческих проверок уровня 3., Границы и веса штрафов Shield (все — настраиваемые, а не свойства сети)., Защитный контур. Детерминирован; хранит состояние прошлого такта для rate-…, Bind the guard to the same aircraft-specific space as the actor., Построение из словаря коэффициентов (напр. пресета сценария)., RuntimeState, Shield, ShieldConfig (+17 more)

### Community 5 - "test_refactoring_contracts.py"
Cohesion: 0.11
Nodes (37): approach_control_from_dict(), approach_control_to_dict(), _copy_approach(), dump_scenario(), _finite_tree(), ground_control_from_dict(), ground_control_to_dict(), _legacy_ground() (+29 more)

### Community 6 - "Scenario"
Cohesion: 0.06
Nodes (29): BaseException, Полный профильный сценарий APPROACH → ROLLOUT → TAXI., Сценарий по имени либо шифру матрицы, без различия раскладки А/B., resolve_scenario(), Scenario, select_for_telemetry(), ControlDiagnostics, Enum (+21 more)

### Community 7 - "ControlsState"
Cohesion: 0.05
Nodes (81): _pid_from_colleague(), Загрузка настроек из JSON коллеги (`config/ics_clear_weather_pid.json`). Секции…, `PIDConfig` коллеги → аргументы нашего `PIDController`. Предел интегратора у…, angle_error_deg(), Разность курсов, приведённая к (-180, 180]., ControlsState, Обнуляет все органы управления. Отправку делает вызывающий через `ICSSim.step`.…, Совместимое имя старого API; колёсные органы оно больше не обозначает. (+73 more)

### Community 8 - "ControlProfile"
Cohesion: 0.14
Nodes (13): ControlProfile, _materialize_override(), _profile_name(), ProfileStatus, AircraftProfile, ApproachConfig, Enum, FlightSegment (+5 more)

### Community 9 - "GainSpace"
Cohesion: 0.18
Nodes (9): GainKey, GainSpace, Any, ArrayLike, float64, GainMap, NDArray, RegulatorKey (+1 more)

### Community 10 - "failures.py"
Cohesion: 0.17
Nodes (16): LateralDiagnostics, LongitudinalDiagnostics, FailureState, Модель отказов бортового оборудования. `FailureState` хранит мультипликативные…, Эффективности исполнительных органов. Аннотации типов обязательны: без них…, ActuatorFeedback, ActuatorVector, AllocationDiagnostics (+8 more)

### Community 11 - "LateralChannel"
Cohesion: 0.24
Nodes (6): GuidanceState, LateralChannel, Блок 2: runway guidance → единый нормированный yaw-запрос., Guidance по тому, что даёт стенд. → словарь guidance или None, если данных нет.…, Единый GuidanceState текущего кадра для control/observation/reward., RunwayTracker

### Community 12 - "test_pretrain.py"
Cohesion: 0.12
Nodes (29): float32, GainMap, NDArray, Абсолютные коэффициенты пресета → `target_z` (17,): gains через `inv_gain`,…, target_z_from_gains(), capture_dataset(), capture_scenario(), episode_quality() (+21 more)

### Community 13 - "SegmentConditions"
Cohesion: 0.15
Nodes (15): _copy_approach(), _copy_ground(), _ground_segments_for_spec(), GroundControlConfig, _GroundPresetSpec, _install_approach_scenarios(), _matrix_draft(), Черновик под шифр матрицы на базе откалиброванного пресета. Словари… (+7 more)

### Community 14 - "test_ics_connector.py"
Cohesion: 0.11
Nodes (18): Разбор телеметрии стенда с совместимостью вперёд. Асимметрия намеренная (JSON-…, _connector(), _FakeSocket, _full_payload(), Транспорт стенда: разбор телеметрии и отправка команд. На проводе чистый JSON…, Подставить ноль значило бы выдумать телеметрию, по которой считается управление., Стенд делает UTF8.GetString() → JsonConvert. Любые байты перед JSON сломали бы…, Windows отдаёт WSAECONNRESET на UDP, если получатель закрыл порт. Ронять цикл… (+10 more)

### Community 15 - "test_run_matrix.py"
Cohesion: 0.10
Nodes (22): ground_cases(), resolve_matrix_run(), compose_matrix_scenario(), _install_through_scenarios(), matrix_battery(), Собрать Б.4 из первой строки и заранее определённой пары законов., Собрать сценарий из конкретных строк APPROACH/ROLLOUT/TAXI.…, Одна строка каталога → минимальный сценарий нужного участка или сквозной пары. (+14 more)

### Community 16 - "AircraftProfile"
Cohesion: 0.10
Nodes (10): AircraftProfile, clamp(), Преобразовать воздушные команды ICD в нормированные DataRef X-Plane., Преобразовать нормированные команды пробега в DataRef X-Plane., Расширение реестра будущим профилем МС-21 без правки XPlaneSim., Проводка и масштабы конкретного планера X-Plane., Общая идентичность ЛА и необязательная привязка к X-Plane. Профиль нужен и…, Command refs retained under the historical public name. (+2 more)

### Community 17 - "ICSSim"
Cohesion: 0.07
Nodes (22): ICSOutputs, _clamp(), ICSSim, ControlsState, FailureMode, StartMode, Обмен со стендом заказчика: телеметрия внутрь, команды наружу. Управление…, Принимает ли стенд наши команды. До включения любой `step` уходит вхолостую. (+14 more)

### Community 18 - "ApproachController"
Cohesion: 0.16
Nodes (20): ApproachConfig, Параметры воздушного контура. Значения по умолчанию — настроенные на стенде.…, ApproachController, ApproachResult, clamp(), ApproachLimits, ApproachTelemetry, Заход по ILS с выравниванием. Телеметрию получает параметром, не читает сам.… (+12 more)

### Community 19 - "Telemetry"
Cohesion: 0.06
Nodes (25): Такт манёвра ухода. → True, когда набор устойчив (пора отдать управление…, Набор устойчив: есть и вертикальная скорость вверх, и прирост радиовысоты над…, Результат проверки допусков захода на одном такте. `landing_allowed` — все ли…, ToleranceReport, FlightSegment, Кадр «связи со стендом нет». Нули, а не None: контур проверяет `valid` первым., Невалидные ICS-сигналы, которые воздушный закон читает безусловно., Приборная скорость (kt → м/с). Отсечки реверса заданы по ней, а не по путевой. (+17 more)

### Community 20 - "gain_scheduler.py"
Cohesion: 0.15
Nodes (15): int64, ActorOutput, _init_log_std(), layer_init(), _mlp_head(), phase_labels_from_groundspeed_kts(), ArrayLike, NDArray (+7 more)

### Community 21 - "XPlaneSim"
Cohesion: 0.12
Nodes (4): _destination(), ControlsState, StartMode, XPlaneSim

### Community 22 - "test_weather.py"
Cohesion: 0.18
Nodes (13): compose_wind(), decompose_wind(), (скорость, откуда) → (crosswind, headwind) относительно курса ВПП. crosswind >…, (crosswind, headwind) → (скорость, откуда, °). Обратна `decompose_wind`., Тесты погоды: разбор ветра, шкала скользкости и чтение условий из пакета стенда., Для пробега существенна боковая составляющая, а не «скорость ветра» сама по…, Все семь кодов из фактических пакетов закрыты явно., test_crosswind_from_right_is_perpendicular() (+5 more)

### Community 23 - "PIDController"
Cohesion: 0.11
Nodes (28): PIDController, test_ground_pids_use_working_ics_numerics_and_explicit_integrator_limits(), _legacy_reference(), Опциональная численность PID (шаг 5): каждый флаг проверяется на том дефекте,…, Если применено ровно то, что выдал PID, коррекции быть не должно., Уставка прыгает, объект стоит на месте — D-составляющая не должна реагировать.…, Выход ИЗ насыщения должен разрешаться всегда, иначе регулятор залипнет. kp…, Если насыщает уже пропорциональная часть, интегрировать нельзя вообще — и это… (+20 more)

### Community 24 - "evaluate.py"
Cohesion: 0.08
Nodes (31): compare_policies(), DefaultGainsPolicy, load_npgs_policy(), main(), NPGSPolicy, Policy, PresetPolicy, ndarray (+23 more)

### Community 25 - "RolloutEnv"
Cohesion: 0.20
Nodes (7): ndarray, Копия команды такта — для расчёта джерка на следующем такте. Копируется…, Окно истории → тензор `(history_len, OBS_DIM)` (последовательность кадров для…, Состояние для поведенческих проверок Shield. Курс здесь — отклонение от…, RolloutEnv, _snapshot_command(), RuntimeState

### Community 26 - "test_xplane_backend.py"
Cohesion: 0.09
Nodes (18): SensorNoise, test_xplane_ignores_failures_outside_rollout_contract(), DatagramSocket, MockXPlaneConnector, ScriptedXPlaneConnector, test_commands_failures_and_close_release_overrides(), test_exact_taxi_row_starts_xplane_and_controller_in_taxi_at_15_knots(), test_failed_approach_setup_releases_overrides_and_pause() (+10 more)

### Community 27 - "test_evaluate.py"
Cohesion: 0.10
Nodes (47): admit_checkpoint(), evaluate_tz(), Диагностика эпизода + сценарий → список вердиктов по пунктам ТЗ разд. 5., Итог эпизода: FAIL, если провален хоть один применимый критерий., Пропускать ли чекпоинт дальше. Отсутствующая/нечисловая метрика = отказ.…, verdict_of(), _battery(), _by_name() (+39 more)

### Community 28 - "test_ppo.py"
Cohesion: 0.15
Nodes (22): build_npgs(), NPGSConfig, Any, Гиперпараметры архитектуры NPGS (замораживаются вместе с весами при поставке)., PPOConfig, Any, Оффлайн-прогон цикла PPO на поданной среде (без стенда) — для тестов/отладки., smoke_train() (+14 more)

### Community 29 - "IcsEngagement"
Cohesion: 0.05
Nodes (23): ControlModeState, IcsEngagement, Автомат включения. `step(inputs)` вызывается каждый такт до формирования…, Полный сброс — новый эпизод начинается с невключённого состояния., Сообщить автомату, что кадр **фактически ушёл** на стенд. Вызывается…, Подхватить уже включённый извне пробег: шлём `ControlMode = Rollout`.…, Войти в пробег самостоятельно: шлём `ControlMode = Rollout`. Это же — передача…, Перейти `Approach → Landing` без нового рукопожатия. Закон остаётся воздушным. (+15 more)

### Community 30 - "XPlaneConnectX"
Cohesion: 0.09
Nodes (11): XPlaneConnectX class initialization. Args: ip (str, optional): IP address where…, Starts a recording of the subscribed DataRefs into self.recorded_data. Data is…, Gets the current value of a DataRef. This is only intended for one-time use.…, Permanently subscribe to a list of DataRefs with a certain frequency. This is…, Writes a value to the specified DataRef provided that the DataRef is writable.…, Sends simulator commands to the simulator. These are not commands for the…, Sets the global position of airplanes as well as their attitude. Note that this…, Gets the global position of the ego aircraft. If frequently needed, consider… (+3 more)

### Community 31 - "runway_profiles.py"
Cohesion: 0.19
Nodes (11): find_earth_nav_dat(), get_runway_profile(), ILSStation, parse_ils_station(), Path, Профили ВПП и разрешение ILS из установленной базы X-Plane., Точка на продолжении оси; положительное расстояние — до порога., Найти LOC (тип 4) без хардкода частоты. (+3 more)

### Community 32 - "test_splits.py"
Cohesion: 0.07
Nodes (53): _as_dict(), contract_for(), Any, Контракт воспроизводимости эпизода (шаг 6). Заимствовано из…, Сколько раз прогнать сценарий, чтобы результат приёмки что-то значил., Худшая реплика по заданной метрике. Приёмка смотрит именно на худшую, а не на…, Источники случайности на стороне стенда, активные при данных условиях. Мы…, Что в эпизоде детерминировано, что нет, и сколько реплик из-за этого нужно. (+45 more)

### Community 33 - "Graphify Pipeline"
Cohesion: 0.08
Nodes (29): Folder Watcher, URL Ingestion, Extra Graph Exports, MCP Graph Server, Confidence Audit Trail, Deterministic Node IDs, Semantic Extraction Contract, Cross-Repository Graph Merge (+21 more)

### Community 34 - "XPlaneConnector"
Cohesion: 0.09
Nodes (9): DataRefSample, Неблокирующий UDP-клиент нативного протокола X-Plane 12., Discard pre-reload values so readiness cannot use stale telemetry., Одна подписка, один поток приёма и явное освобождение ресурсов., Send basic controls to the ego aircraft. There are hundreds of DataRefs that…, Разобрать пакет; публично для детерминированных mock-тестов., Совместимое read-only представление старого XPlaneConnectX., Совместимость с прежним клиентом. (+1 more)

### Community 35 - "ControllingSystem"
Cohesion: 0.07
Nodes (29): ControllingSystem, FailureMode, Связать сценарий с контуром; PID активируются после определения участка., Обновить параметры геометрического наведения латерального канала. Имя сохранено…, Веса влияния каналов (актор, §6): множители к выходам каналов. 1.0 = классика., Привести модель отказов к тому, что сообщает борт (`ICSInputs.Fault*`). Отказы…, Такт управления. → True, если управление окончено (или телеметрия невалидна).…, Три блока: speed controller → guidance → allocator. (+21 more)

### Community 36 - "scenario.py"
Cohesion: 0.11
Nodes (21): compose_scenario(), match_conditions(), FailureMode, WeatherState, Собрать сценарий из независимых источников участков., scenario_distance(), select_scenario(), weather_distance() (+13 more)

### Community 37 - "test_ics_engagement.py"
Cohesion: 0.10
Nodes (47): _Clock, _engine(), _pump(), Автомат включения управления на стенде. Два раздельных предмета проверки: *…, По ICD стенд должен два секунды ПОЛУЧАТЬ ModeAIReady=1. Если считать одно лишь…, Обратная защита: 30 кадров можно выпалить за 0.1 с — время тоже обязано пройти., Срыв предусловия обнуляет и время, и счётчик кадров., Требование ICD — непрерывность: пропуск готовности рвёт серию. (+39 more)

### Community 38 - "test_tolerance.py"
Cohesion: 0.18
Nodes (20): evaluate_approach_tolerances(), _glideslope_tolerance_deg(), ApproachLimits, ApproachTelemetry, FailureMode, Допуск по глиссаде с учётом отказа (ТЗ 5.1.2.1–5.1.2.3), самый мягкий из…, Диагностическая градация приборной скорости по огибающей механизации., Проверить допуски захода по текущему такту. Команды не трогает. `result` —… (+12 more)

### Community 39 - "FakeConnector"
Cohesion: 0.11
Nodes (19): FakeConnector, make_ics_inputs(), Статический стенд: всегда один и тот же кадр, отправленное — в `sent_outputs`., Полный пакет стенда: нули по умолчанию + заданные поля., Неизвестный код — не повод предполагать сухую полосу., Погоду задаёт Заказчик; наш `WeatherState` — это прочитанный кадр, а не задание., До рукопожатия заявлять каналы нельзя: стенд ещё не разрешил нам ими управлять., Стенд отдаёт узлы, футы, футы/мин и градусы/с — граница пересчёта проходит… (+11 more)

### Community 40 - "pid_controller.py"
Cohesion: 0.12
Nodes (26): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+18 more)

### Community 41 - "scenarios.py"
Cohesion: 0.08
Nodes (32): Профили преобразования команд ИСМПУ в органы управления X-Plane., Настройки воздушного участка: заход по ILS, выравнивание, управление скоростью.…, Глобальные константы контура управления (перенесены из main.ipynb)., Константы интерфейса стенда заказчика (ПИВ / ICS). Единый источник правды по…, Приёмочные пороги из ТЗ (раздел 5). Единый источник истины для reward-шейпинга…, Геометрия целевой ВПП и высоты установки ЛА. Смена целевой полосы = правка…, Единая профильная модель сценариев всего интервала полёта. `Scenario` —…, Канонические участки управляемого интервала полёта. (+24 more)

### Community 42 - "NPGS"
Cohesion: 0.18
Nodes (12): floating, NPGS, float32, Tensor, Neural PID Gain Scheduler: общий энкодер + головы актора (абс. gain'ы) + голова…, → (mean (B,17), value (B,), phase_logits (B,n_phases))., 17 сырых выходов → [абс. gains×15, w_lon, w_lat] (layout `REGULATOR_ORDER` +…, Один шаг актора. `action` (…,17) — абс. gain'ы для среды; `raw` (…,17) — сэмпл… (+4 more)

### Community 43 - "ICSInputs"
Cohesion: 0.14
Nodes (24): ControlResult, ICSInputs, ICSOutputs, Неизвестные поля исходного JSON; они доступны аудиту, но не закону управления., airborne_control_mode(), airborne_flare_mode(), deactivate(), live_main() (+16 more)

### Community 44 - "test_gain_scheduler.py"
Cohesion: 0.11
Nodes (19): action_high(), action_low(), decode(), ArrayLike, float32, NDArray, Применение абсолютных коэффициентов PID, выданных NPGS. Действие: вектор…, Плоский вектор действия → `GainCommand` (абсолютные gain'ы). (+11 more)

### Community 45 - "3. Этапы реализации"
Cohesion: 0.09
Nodes (21): 1. Подтверждённые проблемы и целевое состояние, 2. Ключевые интерфейсы, 3. Этапы реализации, 4. Тестирование и критерии готовности, 5. Зафиксированные допущения, 6.1. Один dashboard вместо двух, 6.2. Единый источник данных, 6.3. Представления (+13 more)

### Community 46 - "ScenarioGenerator"
Cohesion: 0.19
Nodes (7): Один случайный сценарий. `difficulty=None` → случайная сложность., ScenarioGenerator, AdmissionResult, _check(), Criterion, Один пункт ТЗ: предел, измеренное значение, вердикт и его причина., Строит вердикт. Неприменимо → SKIP; применимо, но данных нет → FAIL.

### Community 47 - "EngagementInputs"
Cohesion: 0.14
Nodes (10): EngagementInputs, EngagementState, Enum, Автомат включения управления на стенде заказчика. Стенд принимает наши команды…, Передать управление в руление (`ControlMode 3 → 4`). → удался ли переход.…, Сколько уже держится выдержка. 0.0, если отсчёт не идёт (для диагностики)., Почему включение ещё не произошло — для диагностики при таймауте прогрева.…, Слепок для логов и отчётов приёмки. (+2 more)

### Community 48 - "RunRecorder"
Cohesion: 0.16
Nodes (12): default_runs_root(), gains_snapshot(), Path, Единый CSV-регистратор прогонов ICS и X-Plane., Единый каталог прогонов, не зависящий от cwd процесса/Jupyter., Один раз сохранить накопленные кадры и итоговые артефакты прогона., RunRecorder, test_recorder_keeps_all_known_ics_fields_and_unknown_raw_fields() (+4 more)

### Community 49 - "_Clock"
Cohesion: 0.16
Nodes (17): _air(), _Clock, _pump(), После касания режим меняется на пробег — но не раньше: смена режима на глиссаде…, Ниже 80 футов потеря `AgentIsActive` не повод бросать органы: до земли секунды., Окно только удерживает подтверждение. Само оно включения не даёт., Воздушное включение — это фронт `Off → Approach` после выдержки, а не сразу…, 2.2 с — подтверждённое на стенде значение; наземные 2.0 для захода недостаточны. (+9 more)

### Community 50 - "test_go_around.py"
Cohesion: 0.15
Nodes (23): _armed_controller(), _drive(), _frame(), Уход на второй круг (fallback в воздухе): условия срабатывания и передача…, На пробеге ухода нет — segment guard (козление удерживает защёлка сегмента,…, Если реверс уже включён — взлёт невозможен, ухода нет., Устойчивый набор (прирост высоты + положительная верт. скорость) завершает…, После установившегося набора цикл снимает заявку каналов (ControlMode=Off,… (+15 more)

### Community 51 - "Neural PID Gain Scheduler Architecture"
Cohesion: 0.19
Nodes (19): Hybrid Neural PID Controller, Neural PID Gain Scheduler, PPO Training Loop, Preset-Anchored Deterministic Shield, SFT Behavioral-Cloning Warm Start, Absolute-Gain Action Space, Classical PID as the Plant, Deterministic Deployment Runtime (+11 more)

### Community 52 - "test_approach_criteria.py"
Cohesion: 0.10
Nodes (18): ApproachController, angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, Отдельный монитор критерия А.1.1 (не участвует в go-around)., Захватывает А.1.1 после входа в допуск и завершает оценку на 300 ft. (+10 more)

### Community 53 - "._approach_step"
Cohesion: 0.09
Nodes (17): above_decision_height(), at_lateral_alignment_gate(), ils_blocker(), in_terminal_window(), Последние футы перед касанием, где прерывать заход опаснее, чем доработать.…, ВС выше высоты решения ухода на второй круг (30 м по ТЗ 5.1.1.2). → уход…, Полоса подхода к гейту совмещения с осью ± 5 м: `(30 м, 30 м + band]`. Только в…, Почему нельзя продолжать заход по этому кадру. `None` — можно. Закон читает… (+9 more)

### Community 54 - ".value"
Cohesion: 0.25
Nodes (6): _jsonable(), controller_pids(), _jsonable(), pid_operating_points(), Value/setpoint pairs in the native units used by every regulator., Зафиксировать снимок кадра в памяти без файлового I/O.

### Community 55 - "RunwayTracker"
Cohesion: 0.13
Nodes (12): Решить прямую геодезическую задачу на сферической Земле., Геодезическое guidance в истинной системе направлений., Guidance по курсу ВПП и измеренному отклонению — без собственной геодезии.…, Возвращает отклонение от осевой линии в метрах. >0 - правее оси, <0 - левее., Геодезическое наведение на ось ВПП с упреждением по скорости., RunwayTracker, GainSpace, test_guidance_on_centerline_small_heading_error() (+4 more)

### Community 56 - "RomanLogImporter"
Cohesion: 0.19
Nodes (10): _number(), Path, Импорт и проверка внешних CSV-прогонов roman_aviacia_ics., Потоково нормализует основной и authority CSV Романа., RomanLogImporter, verify_manifest(), fixture, roman_csv() (+2 more)

### Community 57 - "working_ics/approach_criteria.py"
Cohesion: 0.21
Nodes (7): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, ICSInputs, Evaluate the A.1.1 approach segment and stop at a radio-altitude floor.

### Community 58 - ".from_dict"
Cohesion: 0.25
Nodes (6): Any, Serialize only the canonical profile- and matrix-aware schema v3., test_battery_covers_key_cases_and_roundtrips(), test_generator_samples_are_valid_and_serializable(), test_preset_roundtrips_through_dict(), test_external_profile_controls_survive_scenario_v2_roundtrip()

### Community 59 - "fakes.py"
Cohesion: 0.09
Nodes (23): ControlModeState, decode_airborne(), decode_outputs(), engaged_inputs(), flight_sim(), _integrate_throttle(), KinematicBench, Фейковый стенд для тестов: `ICSInputs` вместо реального UDP. Единственный… (+15 more)

### Community 60 - "gain_space_for"
Cohesion: 0.13
Nodes (20): gain_space_for(), _profile_name(), Профильное пространство абсолютных PID-коэффициентов NPGS., _regulator_config(), Shield — детерминированный защитный контур между актором и классическим PID.…, Канонический порядок регуляторов, размерности действия и **контракт обучаемого…, Один регулятор, коэффициенты которого (kp/ki/kd) разрешено настраивать сети., RegulatorSpec (+12 more)

### Community 61 - "test_control_parity.py"
Cohesion: 0.13
Nodes (14): Генератор эталонной кривой скорости (Колокол Гаусса)., Начать профиль с фактической скорости текущего участка., То же без лишнего round-trip м/с → узлы → м/с на касании., Возвращает идеальную скорость (м/с) для текущей точки пути., ReferenceTrajectory, TrajectoryState, Тесты паритета после выноса контура из main.ipynb в пакет ismpu. Полный паритет…, test_equally_slow_law_endpoints() (+6 more)

### Community 62 - "Project Dependencies"
Cohesion: 0.18
Nodes (13): Autonomous Landing Controller, Repository Guidance for Codex, Autonomous Landing Controller, Repository Guidance for Claude Code, Neural Landing Implementation Plan, Unified Scenario System, Optional Gymnasium, NumPy (+5 more)

### Community 63 - "test_full_flight.py"
Cohesion: 0.06
Nodes (46): IntFlag, ControlValid, FlightPhase, Биты `ControlValidMask`: какие каналы несёт команда. **Один бит на одно…, Фаза полёта, сообщаемая стендом (`ICSInputs.FlightPhase`)., initial_segment(), is_airborne(), FlightSegment (+38 more)

### Community 64 - "GuidanceState"
Cohesion: 0.29
Nodes (3): GuidanceState, Совместимость с прежним атрибутом; новый термин явно указывает ось., Совместимость со старым словарным API.

### Community 66 - "DashboardState"
Cohesion: 0.18
Nodes (9): DashboardState, _handler_factory(), Path, Thread-safe live state or an immutable CSV replay., configured_controller(), test_capture_export_and_replay_common_run(), test_dashboard_http_api_is_local_and_monitor_only(), test_monitor_only_and_npgs_tuning_locks() (+1 more)

### Community 67 - "heading_deviation_deg"
Cohesion: 0.19
Nodes (12): heading_deviation_deg(), Отклонение курса ВС от направления ВПП — приёмочная величина ТЗ 5.1.3.3 /…, Телеметрия ВС на оси ВПП, смещённого вбок на `offset_m` и с заданным курсом.…, ТЗ 5.1.3.3 нормирует курс «от направления ВПП». Смещение от оси на него не…, На стенде курс ВПП приходит телеметрией; конфиг — только значение по умолчанию., Таблица из находки: раньше оба случая давали противоположный результат., _telemetry_at(), test_heading_deviation_ignores_lateral_offset() (+4 more)

### Community 68 - "test_working_ics_dashboard.py"
Cohesion: 0.35
Nodes (10): ClearWeatherILSController, DashboardState, _controller(), _inputs(), Characterization tests for the bench-validated ``working_ics`` dashboard., _record(), test_dashboard_records_four_airborne_views_and_diagnostics(), test_gain_updates_are_immediate_validated_and_share_pitch_with_flare() (+2 more)

### Community 70 - "agent/pretrain.py"
Cohesion: 0.16
Nodes (13): _phase_labels(), pretrain_sft(), PretrainConfig, Tensor, SFT (behavioral cloning) — предобучение NPGS предсказывать эталонные…, BC-обучение `net` на `dataset` (регрессия mean → target_z). → история по эпохам., Датасет BC: окна наблюдений, постоянные (на прогон) целевые `target_z` и вес…, SFTDataset (+5 more)

### Community 71 - "Unified Profile-Aware Scenario System"
Cohesion: 0.22
Nodes (9): Technical-Specification Acceptance Gates, Bench-Validated ILS Approach Channel, Forward-Only Flight Segment Supervisor, Tolerance-Gated Go-Around, Longitudinal and Lateral Ground Channels, PID Run Matrix, Unified Profile-Aware Scenario System, Legacy Scenario Preset Model (+1 more)

### Community 72 - "Interactive PID Dashboard"
Cohesion: 0.25
Nodes (9): Nine-View PID Dashboard, Run Recording Artifacts, buildTabs, draw, Gain Tuning and Snapshot Export, Interactive PID Dashboard, refresh, render (+1 more)

### Community 73 - "MatrixRun"
Cohesion: 0.06
Nodes (19): cases_for_segment(), ground_runs(), MatrixCase, MatrixCondition, MatrixRun, normalize_code(), _number(), Any (+11 more)

### Community 74 - "DashboardState"
Cohesion: 0.21
Nodes (4): DashboardServer, DashboardState, Any, ICSInputs

### Community 75 - "FailureMode"
Cohesion: 0.11
Nodes (18): FailureMode, Enum, _hash_unit(), is_signature_holdout(), PartitionedScenarioProvider, Детерминированное разбиение сценариев на обучение и holdout (шаг 6). Схема…, SHA-256 от идентификатора → число в [0, 1). Стабильно между запусками и…, Устойчивая комбинация условий, а не имя или целое семейство отказов. (+10 more)

### Community 76 - "ICSInterface.cs"
Cohesion: 0.36
Nodes (7): External.Systems.ICS, ControlModeState, GearState, ICSInputs, ICSOutputs, ReverseEngineType, UInt64

### Community 77 - "compute_reward"
Cohesion: 0.16
Nodes (13): compute_reward(), TypedDict, Считает компоненты и суммарный reward. Все компоненты ≥ 0; reward = −Σ…, Допуск по оси ВПП для текущей фазы: пробег ±3 м, руление ±1 м (ТЗ 5.1.3.1)., RewardComponents, RewardWeights, xte_limit_for(), Перелёт по скорости к концу ВПП опаснее недолёта — симметричным модулем не… (+5 more)

### Community 78 - "runtime/pretrain.py"
Cohesion: 0.20
Nodes (15): build_capture_stack(), build_scenarios(), PretrainRunConfig, Оркестрация SFT-подогрева NPGS (план Stage B): захват классических прогонов на…, (env, net) поверх выбранного backend; env без Shield (чистая классика)., Полный SFT: захват на стенде → BC → чекпоинт. → (net, dataset, history)., Оффлайн SFT на поданной среде (без стенда) — для тестов/отладки. → (net,…, Список сценариев для захвата: отобранные пресеты × повторные прогоны. (+7 more)

### Community 79 - "PPOTrainer"
Cohesion: 0.27
Nodes (7): PPOTrainer, Tensor, Собирает rollout из среды и обновляет NPGS многокомпонентным PPO-loss., Шагает средой `rollout_len` тактов (сброс по завершению эпизода). → статистика., Хук L_shield (§11): барьер, отталкивающий выход от края уровня-1 Shield. По…, PPOMetrics, ScenarioProvider

### Community 80 - "ICS PID Monitor"
Cohesion: 0.29
Nodes (7): buildControls, draw, formatTime, Four-Loop PID Tuning, ICS PID Monitor, Live and Historical Timeline, refresh

### Community 81 - "ics_connector.py"
Cohesion: 0.08
Nodes (19): IntEnum, GearState, ICSBenchConnector, main(), UDP-мост к стенду заказчика (порт 3030) — транспорт пути поставки. `ICSInputs`…, Отправка best-effort со счётчиком ошибок и разрежённым логом. Windows отдаёт…, → True если отправлено. Исключение наружу не выпускается., Мост к стенду: JSON поверх UDP, адрес стенда определяется из входящего пакета. (+11 more)

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
Cohesion: 0.15
Nodes (11): EpisodeObjective, Накопитель по эпизоду: собирает потактовые отсчёты → сводные компоненты.…, _make_box(), Минимальная замена gym.spaces.Box, когда gymnasium не установлен., _SimpleBox, Фиксированный приёмочный набор (детерминированный, без RNG)., Отсутствие данных даёт None, а не 0 — приёмка обязана трактовать это как FAIL., p95 темпа не ловится одиночным выбросом — в отличие от максимума. (+3 more)

### Community 86 - "RuntimeError"
Cohesion: 0.17
Nodes (7): _finite_or_none(), GainUpdateRequest, Валидировать HTTP-запрос и передать запись control-потоку., Применяется только control-потоком в начале такта., Terminates the recording and returns a dictionary of lists that contain the…, Synchronize measurements from multiple sensors to a common frequency.…, RuntimeError

### Community 87 - "ConditionMatch"
Cohesion: 0.17
Nodes (7): ConditionMatch, Сверка ожидаемых условий с фактической телеметрией backend., Погода остаётся отчётной; неверный отказ делает прогон недопустимым., Совместимое имя для прежних потребителей допуска к приёмке., GoAroundManeuver, Начать уход: зафиксировать состояние манёвра и высоту входа., Состояние идущего ухода на второй круг. Пока он активен, заход не ведётся.

### Community 88 - ".from_crosswind"
Cohesion: 0.29
Nodes (5): Any, Собирает ветер из компонент относительно курса ВПП. `crosswind_kts` > 0 — ветер…, Сериализация в примитивы (для логирования/воспроизводимости сценариев)., test_scenario_roundtrip_with_weather_and_failures(), test_weatherstate_from_crosswind()

### Community 89 - "envelope.py"
Cohesion: 0.10
Nodes (25): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+17 more)

### Community 90 - "LongitudinalChannel"
Cohesion: 0.20
Nodes (6): CompletionRule, LongitudinalChannel, Блок 1: скорость → симметричная база тормозов и реверса., Сбросить PID и привязать начало профиля к фактической скорости касания/старта., PidMap, VelocityLaw

### Community 91 - "test_action_contract.py"
Cohesion: 0.14
Nodes (17): _controller(), Контракт обучаемого слоя (Этап 4): что именно сеть имеет право менять. Аргумент…, Полный слепок настраиваемого состояния контура — всё, что действие могло бы…, Действие сети меняет только kp/ki/kd и веса каналов — всё остальное…, Действие = коэффициенты пресета → не сдвигается ни одно поле контура (аналог…, Даже гротескное действие не может расширить пределы выхода регулятора. Границы…, Пустое обоснование = контракт непредъявим по ТЗ., Машиночитаемое утверждение «сеть не является регулятором». (+9 more)

### Community 92 - "base_gains_from_pids"
Cohesion: 0.17
Nodes (16): apply_gains_to_pids(), base_gains_from_pids(), PidMap, Снимок (kp, ki, kd) регуляторов — пресет-якорь для Shield и т.п., Записывает эффективные gain'ы обратно в регуляторы (перед control_step)., apply_corrections(), preset_action(), float64 (+8 more)

### Community 93 - "test_rollout_env.py"
Cohesion: 0.15
Nodes (18): ObservationBuilder, Строит нормированный вектор наблюдения одного кадра., excess(), graded(), Чистый hinge: превышение допуска, нормированное на допуск. Внутри допуска = 0., Штраф с гейтом ТЗ: мягкий линейный наклон внутри допуска + резкий рост за…, Тесты Этапа 2: Observation/Action/reward/RolloutEnv + инвариант identity ==…, Без аннотаций типов @dataclass не видит полей, и тогда любые два экземпляра… (+10 more)

### Community 95 - "reward.py"
Cohesion: 0.11
Nodes (20): _command_jerk(), _component(), _effort_saturated(), _ground_steering(), ObjectiveWeights, _p95(), Objective — единое определение «хорошего пробега» (§11 + приёмка ТЗ разд. 5).…, Упёрлась ли команда в границу **со стороны усилия**. Важное различие: нулевая… (+12 more)

### Community 99 - "_WarmUpSim"
Cohesion: 0.18
Nodes (7): ObserverEstimate, Оценки PINN-обсервера (§12). Заглушка нулями до Этапа 7., Стенд, включающий управление только после N тактов прогрева. Само рукопожатие…, Такты рукопожатия — не шаги эпизода: в это время ВС нами не управлялось. Иначе…, test_env_reports_engagement_state_in_info(), test_warm_up_runs_before_the_episode_and_is_not_counted(), _WarmUpSim

### Community 110 - "protocol.py"
Cohesion: 0.25
Nodes (6): ControlModeState, GearState, ICSOutputs, Any, IntEnum, ReverseEngineType

### Community 111 - "Q: Реализовать этап 0: baseline, golden replay и dashboard characterization"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Реализовать этап 0: baseline, golden replay и dashboard characterization, Source Nodes

### Community 112 - "Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md)., Source Nodes

### Community 113 - "build_sim"
Cohesion: 0.20
Nodes (9): ICSBenchConnector, get_aircraft_profile(), build_sim(), Any, Path, Создать backend; для ICS геодезия включается только явным ``runway_profile``., AircraftProfile, RunwayProfile (+1 more)

### Community 114 - "normalization.py"
Cohesion: 0.19
Nodes (12): clip_unit(), linear(), log_norm(), Фиксированная нормализация Observation Space — единый контракт train ↔ deploy.…, Лог-нормировка неотрицательной величины (видимость): log1p(x)/log1p(scale)., Отображает [lo, hi] → [-1, 1] (для PID output по его границам)., Сериализуемый слепок контракта нормировки (сохраняется вместе с весами).…, snapshot() (+4 more)

### Community 115 - "test_ics_sim.py"
Cohesion: 0.07
Nodes (30): engaged_sim(), (sim, connector) с завершённым рукопожатием: стенд подтвердил `AgentIsActive =…, Тесты стенда (`ICSSim`), подбора сценария и генератора — без реального стенда., Разделение органов из таблицы Заказчика: тиллер — на рулении, педальный пост —…, Заявить канал, который не формируешь, — взять ответственность за неуправляемый…, 31 — единственная маска, с которой заход реально прошёл на стенде. Проверяется…, Один бит на одно командное поле `ICSOutputs` — иначе заявка попадает не в тот…, Базовый контур на стенде: `control_step` сам читает телеметрию и сам отправляет. (+22 more)

### Community 116 - "Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)., Source Nodes

### Community 117 - "gui/dashboard.py"
Cohesion: 0.27
Nodes (4): DashboardServer, main(), Unified local dashboard for the three airborne and five ground PIDs., ViewSpec

### Community 123 - "static_sim"
Cohesion: 0.20
Nodes (10): (sim, connector) с неизменным кадром у порога ВПП. Скорость задаётся в **м/с**.…, static_sim(), test_default_preset_leaves_all_actuators_healthy(), test_runtime_uses_explicit_matrix_run_id_without_telemetry_guessing(), `break_control` взводится в конце КАЖДОГО нормального пробега (достигнута…, Тормоз на 0 = «торможение не требуется», а не «авторитет исчерпан». Иначе флаг…, test_break_control_is_cleared_when_a_scenario_is_applied(), test_env_preset_action_parity_matches_classical_control_step() (+2 more)

### Community 125 - ".begin_flight"
Cohesion: 0.21
Nodes (10): approach_blocker(), ApproachRefused, Воздушный участок начинать нельзя — с названной причиной. Отдельное исключение,…, Можно ли вообще судить об участке по этому кадру. Кадр без пакета стенда…, Почему нельзя вести заход по этому кадру. `None` — можно. Пока проверка одна,…, segment_is_decidable(), FlightSegment, Пересобрать stateful PID и уведомить backend до первого такта участка. (+2 more)

### Community 126 - ".compute"
Cohesion: 0.20
Nodes (4): → (интеграл только с утечкой, интеграл с утечкой и приращением). Оба уже зажаты., Такт регулятора. `measurement` обязателен при `derivative_on_measurement=True`., Back-calculation: подтянуть интегратор к фактически применённой команде. No-op…, Вес апериодического фильтра D-составляющей за такт `dt`.

### Community 127 - "import_workbook"
Cohesion: 0.33
Nodes (9): import_workbook(), main(), Any, Path, Одноразовый импорт исходной Excel-матрицы в runtime-каталог JSON., Прочитать книгу целиком; функция не используется production runtime., _scalar(), write_catalog() (+1 more)

### Community 128 - ".from_ics"
Cohesion: 0.22
Nodes (7): WeatherState, Фактические погодные условия со стенда (ветер, сцепление, осадки, видимость)., `ICSInputs` → `WeatherState`. Единственный источник фактической погоды. Стенд…, `Visibility` в футах. Без пересчёта 16000 футов читались бы как «ясно» вместо…, test_visibility_is_converted_from_feet(), Стенд шлёт узлы и **футы**; в WeatherState видимость — в метрах., test_from_ics_converts_units()

### Community 129 - "telemetry"
Cohesion: 0.09
Nodes (23): on_ground(), Готовый кадр `Telemetry` для прямых вызовов `control_step(dt, telemetry,…, Кадр «ВС на полосе»: обжаты все стойки, курс/координаты у порога UUEE 06R., telemetry(), Пресет — стартовое предположение; фактическую конфигурацию сообщает борт., Отказ может быть снят — накапливающий учёт держал бы орган мёртвым до конца…, Кадр без пакета стенда: пустой `faults` значит «сообщать некому», а не «всё…, Единичный таймаут — не повод вернуть рулю авторитет, которого у него нет. (+15 more)

### Community 130 - "HandshakeBench"
Cohesion: 0.14
Nodes (11): HandshakeBench, Стенд, включающий управление только после корректного рукопожатия. Ждёт…, Стенд включается по полученной готовности, а не по нашему представлению о ней., test_the_airborne_handshake_is_actually_transmitted_before_approach(), _cold_sim(), Сквозной прогрев: маска нулевая, пока стенд не подтвердил `AgentIsActive = 1`., Темп задаётся часами, а не sleep. Со сломанным (или подменённым) sleep наивный…, Молча продолжить нельзя: дальше мы бы «управляли» в пустоту. (+3 more)

### Community 131 - "control.py"
Cohesion: 0.43
Nodes (4): apply_ground_control(), build_pids(), Сборка классического контура из неизменяемой конфигурации., Фабрики stateful-объектов; config-модули хранят только данные.

### Community 133 - ".enter_segment"
Cohesion: 0.25
Nodes (4): FailureMode, FlightSegment, Применить только дельту условий при переходе между участками., Снять один отказ, не переинициализируя отказ, продолжающийся на новом участке.

### Community 135 - "Q: Приступай к выполнению этапа 2 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 2 плана docs/plan.md, Source Nodes

### Community 136 - "_faults_from_inputs"
Cohesion: 0.40
Nodes (4): ICSInputs, _faults_from_inputs(), Отказы, о которых сообщает борт — **единственный** источник истины об отказах.…, Сигналы отказов со стенда → наши `FailureMode`. Отказы шасси…

### Community 138 - ".load"
Cohesion: 0.25
Nodes (6): device, Веса + конфиг + слепок нормировки (включая gain-пространство) одним артефактом., PathLike, test_checkpoint_rejects_another_profile(), test_legacy_checkpoint_requires_explicit_profile_and_matching_space(), test_save_load_roundtrip()

### Community 142 - ".__init__"
Cohesion: 0.29
Nodes (5): AircraftProfile, Path, RunwayProfile, WeatherState, XPlaneConnector

### Community 153 - "runway_condition_from_bench"
Cohesion: 0.25
Nodes (8): Код состояния ВПП со стенда → наша шкала. Неизвестный код трактуется как `ICY`,…, runway_condition_from_bench(), Коды из фактических пакетов переводятся в свою шкалу скользкости., test_runway_condition_codes_are_remapped_not_passed_through(), Коды стенда не упорядочены по скользкости: WET RUBBER=14 близок к WET=2. Подать…, Предположить сухую полосу — разрешить максимальное торможение там, где оно…, test_bench_codes_map_to_a_monotone_slipperiness_scale(), test_unknown_bench_code_is_treated_as_slippery()

### Community 154 - "RolloutBuffer"
Cohesion: 0.29
Nodes (5): device, Плоский буфер одного env: obs-окна, сырые действия, logp/value/reward/done., RolloutBuffer, test_gae_matches_manual_computation(), test_gae_zeroes_bootstrap_after_done()

### Community 155 - "weather.py"
Cohesion: 0.38
Nodes (5): Генератор сценариев обучения (domain randomization). Сэмплирует `Scenario` из…, Enum, Погодные условия эпизода: описание, шкала сцепления и разбор ветра. Модуль **не…, Состояние ВПП как **монотонная шкала скользкости** 0…15 (0 — сухо, 15 — лёд со…, RunwayCondition

### Community 158 - "Q: Приступай к выполнению этапа 4 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 4 плана docs/plan.md, Source Nodes

### Community 162 - "roll_limit_deg"
Cohesion: 0.50
Nodes (4): Предел крена по высоте: чем ниже, тем меньше запас до касания законцовкой.…, roll_limit_deg(), Чем ниже, тем меньше запас до касания законцовкой; настроенный предел не…, test_roll_limit_tightens_towards_the_ground()

### Community 163 - "ControlArchitecture"
Cohesion: 0.50
Nodes (3): ControlArchitecture, Фиксированный порядок слоёв и роль обучаемого компонента., test_contract_rejects_direct_actuator_authority()

## Ambiguous Edges - Review These
- `Unified Profile-Aware Scenario System` → `Legacy Scenario Preset Model`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to
- `Dual-Backend SimInterface` → `ICS-Only Backend Guidance`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **64 isolated node(s):** `Answer`, `Outcome`, `Source Nodes`, `ismpu`, `Answer` (+59 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **56 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `ControllingSystem` (3× useful, score=2.975679177) _(code changed — re-verify)_
- `ICSSim` (2× useful, score=1.997834471) _(code changed — re-verify)_
- `LateralChannel` (2× useful, score=1.976186083)
- `ObservationBuilder` (2× useful, score=1.95615762)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Unified Profile-Aware Scenario System` and `Legacy Scenario Preset Model`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Dual-Backend SimInterface` and `ICS-Only Backend Guidance`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `ControllingSystem` connect `ControllingSystem` to `telemetry`, `train.py`, `control.py`, `test_refactoring_contracts.py`, `Scenario`, `ControlProfile`, `test_pretrain.py`, `SegmentConditions`, `test_run_matrix.py`, `Telemetry`, `PIDController`, `evaluate.py`, `RolloutEnv`, `test_xplane_backend.py`, `test_evaluate.py`, `test_ppo.py`, `FakeConnector`, `test_control_step_is_unchanged_when_tracking_is_off`, `scenarios.py`, `test_gain_scheduler.py`, `ScenarioGenerator`, `RunRecorder`, `_Clock`, `test_go_around.py`, `test_approach_criteria.py`, `._approach_step`, `fakes.py`, `test_control_parity.py`, `test_full_flight.py`, `DashboardState`, `runtime/pretrain.py`, `ics_connector.py`, `EpisodeObjective`, `ConditionMatch`, `LongitudinalChannel`, `test_action_contract.py`, `base_gains_from_pids`, `test_rollout_env.py`, `reward.py`, `_WarmUpSim`, `test_ics_sim.py`, `static_sim`, `.begin_flight`?**
  _High betweenness centrality (0.171) - this node is a cross-community bridge._
- **Why does `Telemetry` connect `Telemetry` to `.from_ics`, `telemetry`, `HandshakeBench`, `test_icd_units.py`, `test_refactoring_contracts.py`, `Scenario`, `ControlsState`, `ControlProfile`, `_faults_from_inputs`, `failures.py`, `LateralChannel`, `.enter_segment`, `SegmentConditions`, `ICSSim`, `ApproachController`, `XPlaneSim`, `test_xplane_backend.py`, `IcsEngagement`, `ControllingSystem`, `test_tolerance.py`, `FakeConnector`, `scenarios.py`, `EngagementInputs`, `RunRecorder`, `_Clock`, `test_go_around.py`, `test_approach_criteria.py`, `._approach_step`, `fakes.py`, `test_control_parity.py`, `test_full_flight.py`, `heading_deviation_deg`, `ics_connector.py`, `test_working_ics_golden.py`, `ConditionMatch`, `envelope.py`, `LongitudinalChannel`, `test_rollout_env.py`, `_WarmUpSim`, `test_ics_sim.py`, `.begin_flight`?**
  _High betweenness centrality (0.129) - this node is a cross-community bridge._
- **Why does `ICSSim` connect `ICSSim` to `telemetry`, `HandshakeBench`, `test_refactoring_contracts.py`, `Scenario`, `Telemetry`, `evaluate.py`, `test_ppo.py`, `IcsEngagement`, `runway_profiles.py`, `ControllingSystem`, `FakeConnector`, `scenarios.py`, `ScenarioGenerator`, `EngagementInputs`, `_Clock`, `test_go_around.py`, `fakes.py`, `test_full_flight.py`, `ics_connector.py`, `test_working_ics_golden.py`, `ConditionMatch`, `test_rollout_env.py`, `_WarmUpSim`, `build_sim`, `test_ics_sim.py`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Are the 31 inferred relationships involving `ControllingSystem` (e.g. with `ApproachSetup` and `ConditionMatch`) actually correct?**
  _`ControllingSystem` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `Telemetry` (e.g. with `ApproachSetup` and `ConditionMatch`) actually correct?**
  _`Telemetry` has 46 INFERRED edges - model-reasoned connections that need verification._