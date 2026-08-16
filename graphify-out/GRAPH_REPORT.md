# Graph Report - GOSNIIASProject  (2026-08-16)

## Corpus Check
- 149 files · ~174,598 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2818 nodes · 6562 edges · 169 communities (114 shown, 55 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 541 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ac65c0c8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_tolerance.py
- GainCommand
- RolloutEnv
- test_weather.py
- Shield
- json_config.py
- SimInterface
- airborne_inputs
- scenarios.py
- GainSpace
- GroundControlAllocator
- LateralChannel
- test_pretrain.py
- ControlsState
- test_ics_connector.py
- test_run_matrix.py
- AircraftProfile
- .enter_segment
- ApproachController
- Telemetry
- gain_scheduler.py
- XPlaneSim
- worst_replica
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
- ControllingSystem
- test_full_flight.py
- test_ics_engagement.py
- RunSample
- ICSSim
- pid_controller.py
- run_reader.py
- NPGS
- ICSInputs
- test_gain_scheduler.py
- 3. Этапы реализации
- ScenarioGenerator
- EngagementInputs
- Path
- _Clock
- test_go_around.py
- Neural PID Gain Scheduler Architecture
- test_approach_criteria.py
- ._approach_step
- run_artifacts.py
- RunwayTracker
- RomanLogImporter
- working_ics/approach_criteria.py
- test_dashboard.py
- fakes.py
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
- _signal_valid
- Unified Profile-Aware Scenario System
- Interactive PID Dashboard
- MatrixRun
- DashboardState
- FailureMode
- ICSInterface.cs
- heading_deviation_deg
- runtime/pretrain.py
- RunReader
- ICS PID Monitor
- ics_connector.py
- ICS UDP JSON Protocol
- X-Plane Dashboard and Runtime Guide
- test_working_ics_golden.py
- EpisodeObjective
- CompletionRule
- .reset
- import_workbook
- test_approach_channel.py
- LongitudinalChannel
- test_action_contract.py
- static_sim
- .summary
- main
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
- ICSBenchConnector
- normalization.py
- test_ics_sim.py
- Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md).
- VlaydRolloutBridge
- IntEnum
- ControlModeState
- ICSInputs
- ICSOutputs
- socket
- .act_numpy
- .from_json
- GuidanceState
- .compute
- CSVLogger
- WeatherState
- Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md).
- Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md).
- regulators.py
- ApproachLimits
- .enter_segment
- ApproachTelemetry
- Q: Приступай к выполнению этапа 2 плана docs/plan.md
- ICSInputs
- Criterion
- ShutdownReport
- ApproachConfig
- .activate_segment
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
- _faults_from_inputs
- test_matches_the_colleague_implementation_command_for_command
- Scenario
- Path
- Q: Приступай к выполнению этапа 4 плана docs/plan.md
- ReferenceTrajectory
- RewardWeights
- TypedDict
- Scenario
- SimInterface
- ApproachSetup
- ICSInputs
- Scenario
- RunRecorder
- TouchdownSetup

## God Nodes (most connected - your core abstractions)
1. `ControllingSystem` - 175 edges
2. `Telemetry` - 123 edges
3. `ControlsState` - 92 edges
4. `ICSSim` - 76 edges
5. `Scenario` - 71 edges
6. `PIDController` - 54 edges
7. `XPlaneSim` - 54 edges
8. `RolloutEnv` - 52 edges
9. `GainSpace` - 47 edges
10. `Shield` - 45 edges

## Surprising Connections (you probably didn't know these)
- `Autonomous Landing Controller` --semantically_similar_to--> `Autonomous Landing Controller`  [INFERRED] [semantically similar]
  CLAUDE.md → AGENTS.md
- `Profile-Aware Flight Scenarios` --semantically_similar_to--> `Unified Scenario System`  [INFERRED] [semantically similar]
  docs/XPLANE_DASHBOARD.md → implementation_plan.md
- `Acceptance and Evaluation Harness` --semantically_similar_to--> `Technical-Specification Acceptance Gates`  [INFERRED] [semantically similar]
  implementation_plan.md → AGENTS.md
- `X-Plane Resettable Runtime` --semantically_similar_to--> `X-Plane Training and Evaluation Backend`  [INFERRED] [semantically similar]
  docs/XPLANE_DASHBOARD.md → implementation_plan.md
- `test_pid_anti_windup_clamp()` --calls--> `PIDController`  [EXTRACTED]
  tests/test_control_parity.py → ismpu/control/pid.py

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
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/tolerance.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/ground_allocator.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach_criteria.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/flight.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`

## Hyperedges (group relationships)
- **Graphify Extraction and Build Flow** — _codex_skills_graphify_skill_structural_extraction, _codex_skills_graphify_skill_semantic_extraction, _codex_skills_graphify_references_extraction_spec_semantic_extraction_contract, _codex_skills_graphify_references_update_build_merge [EXTRACTED 1.00]
- **Hybrid Neural Landing Control** — implementation_plan_classical_pid_plant, implementation_plan_npgs, implementation_plan_deterministic_shield, implementation_plan_ppo_multicomponent_loss, implementation_plan_pinn_observer [EXTRACTED 1.00]
- **PID Dashboard Ecosystem** — docs_xplane_dashboard_pid_dashboard, ismpu_gui_dashboard_pid_dashboard, ismpu_working_ics_ics_dashboard_ics_pid_monitor [INFERRED 0.85]

## Communities (169 total, 55 thin omitted)

### Community 0 - "test_tolerance.py"
Cohesion: 0.06
Nodes (59): lateral_limit_m(), lateral_load_situation(), lateral_situation(), normal_load_situation(), IntEnum, Критерии критичности особых ситуаций МС-21 (Приложение 1 к ТЗ). Таблица АП-25…, Классификация скорости касания относительно VAPP и VВПП пред., Классификация нормальной перегрузки посадочного удара. `heavy` — взлётный вес. (+51 more)

### Community 1 - "GainCommand"
Cohesion: 0.13
Nodes (11): _clip(), GainCommand, GainMap, RegulatorKey, Что сделал Shield за такт: активированные правила, штрафы, fallback., Уровни 1–2. Возвращает `(effective_gains, safe_command, report)`.…, Уровень 3. Правит небезопасные команды и возвращает `(command, report)`., Выход актора: абсолютные коэффициенты PID + веса каналов. `gains[reg] =… (+3 more)

### Community 2 - "RolloutEnv"
Cohesion: 0.10
Nodes (22): PPOTrainer, Tensor, Собирает rollout из среды и обновляет NPGS многокомпонентным PPO-loss., Шагает средой `rollout_len` тактов (сброс по завершению эпизода). → статистика., Хук L_shield (§11): барьер, отталкивающий выход от края уровня-1 Shield. По…, ndarray, Окно истории → тензор `(history_len, OBS_DIM)` (последовательность кадров для…, Состояние для поведенческих проверок Shield. Курс здесь — отклонение от… (+14 more)

### Community 3 - "test_weather.py"
Cohesion: 0.06
Nodes (36): Фактические погодные условия со стенда (ветер, сцепление, осадки, видимость)., compose_wind(), decompose_wind(), Any, Enum, `ICSInputs` → `WeatherState`. Единственный источник фактической погоды. Стенд…, Собирает ветер из компонент относительно курса ВПП. `crosswind_kts` > 0 — ветер…, Сериализация в примитивы (для логирования/воспроизводимости сценариев). (+28 more)

### Community 4 - "Shield"
Cohesion: 0.14
Nodes (26): Shield — детерминированный защитный контур между актором и классическим PID.…, Наблюдаемое состояние для поведенческих проверок уровня 3., Границы и веса штрафов Shield (все — настраиваемые, а не свойства сети)., Защитный контур. Детерминирован; хранит состояние прошлого такта для rate-…, Bind the guard to the same aircraft-specific space as the actor., Построение из словаря коэффициентов (напр. пресета сценария)., RuntimeState, Shield (+18 more)

### Community 5 - "json_config.py"
Cohesion: 0.10
Nodes (45): approach_control_from_dict(), approach_control_to_dict(), _copy_approach(), dump_scenario(), _finite_tree(), ground_control_from_dict(), ground_control_to_dict(), _legacy_ground() (+37 more)

### Community 6 - "SimInterface"
Cohesion: 0.11
Nodes (5): BaseException, StartMode, Минимальный lifecycle, одинаковый для стенда и X-Plane., SimInterface, Protocol

### Community 7 - "airborne_inputs"
Cohesion: 0.10
Nodes (38): airborne_inputs(), Кадр «ВС на глиссаде»: стойки не обжаты, ILS валиден, скорость и высота…, _descent_frames(), _our_channel(), Страховка от самообмана: сценарий обязан пройти выравнивание, иначе паритет его…, Угол сноса не должен превращаться в ошибку курса на локализаторе., Стенд иногда сбрасывает Valid при сохранении пригодного численного значения., Отклонение планки курса задаёт доворот в сторону оси, а не от неё. (+30 more)

### Community 8 - "scenarios.py"
Cohesion: 0.07
Nodes (47): compose_scenario(), ControlProfile, _copy_approach(), _copy_ground(), _ground_segments_for_spec(), GroundControlConfig, _GroundPresetSpec, _install_approach_scenarios() (+39 more)

### Community 9 - "GainSpace"
Cohesion: 0.18
Nodes (9): GainKey, GainSpace, Any, ArrayLike, float64, GainMap, NDArray, RegulatorKey (+1 more)

### Community 10 - "GroundControlAllocator"
Cohesion: 0.14
Nodes (13): FailureManager, FailureState, Эффективности исполнительных органов. Аннотации типов обязательны: без них…, Проецирует набор дискретных отказов в эффективности исполнительных органов., Привести состояние ровно к набору `modes` (то, что сообщил стенд). Пересборка с…, ActuatorFeedback, ActuatorVector, _clamp() (+5 more)

### Community 11 - "LateralChannel"
Cohesion: 0.23
Nodes (7): GuidanceState, LateralChannel, LateralDiagnostics, Блок 2: runway guidance → единый нормированный yaw-запрос., Guidance по тому, что даёт стенд. → словарь guidance или None, если данных нет.…, Единый GuidanceState текущего кадра для control/observation/reward., RunwayTracker

### Community 12 - "test_pretrain.py"
Cohesion: 0.14
Nodes (24): capture_dataset(), capture_scenario(), episode_quality(), In-process захват классических траекторий для SFT-датасета (план Stage B).…, Захват набора сценариев → (объединённый `SFTDataset`, отчёты по каждому…, Сводка эпизода + сценарий → (вес доверия к метке, именованные причины…, Один классический прогон сценария → (`SFTDataset` с весом, отчёт о качестве)., Оффлайн SFT на поданной среде (без стенда) — для тестов/отладки. → (net,… (+16 more)

### Community 13 - "ControlsState"
Cohesion: 0.13
Nodes (26): ControlsState, Обнуляет все органы управления. Отправку делает вызывающий через `ICSSim.step`.…, Разделяемая по тактам структура команд — и наземных, и воздушных. Аннотации…, Сброс к нейтральным командам — новый эпизод начинается с чистого состояния.…, Обнулить только воздушные команды. Нужно, когда воздушный канал не может…, Копия команды такта — для расчёта джерка на следующем такте. Копируется…, _snapshot_command(), build_altitude_sweep() (+18 more)

### Community 14 - "test_ics_connector.py"
Cohesion: 0.11
Nodes (20): GearState, Разбор телеметрии стенда с совместимостью вперёд. Асимметрия намеренная (JSON-…, _connector(), _FakeSocket, _full_payload(), Транспорт стенда: разбор телеметрии и отправка команд. На проводе чистый JSON…, Подставить ноль значило бы выдумать телеметрию, по которой считается управление., Стенд делает UTF8.GetString() → JsonConvert. Любые байты перед JSON сломали бы… (+12 more)

### Community 15 - "test_run_matrix.py"
Cohesion: 0.12
Nodes (17): compose_matrix_scenario(), _install_through_scenarios(), matrix_battery(), Собрать Б.4 из первой строки и заранее определённой пары законов., Собрать сценарий из конкретных строк APPROACH/ROLLOUT/TAXI.…, Одна строка каталога → минимальный сценарий нужного участка или сквозной пары., scenario_for_matrix_run(), Матрица прогонов и её связь с единым реестром сценариев. (+9 more)

### Community 16 - "AircraftProfile"
Cohesion: 0.09
Nodes (12): _profile_name(), AircraftProfile, clamp(), Преобразовать воздушные команды ICD в нормированные DataRef X-Plane., Преобразовать нормированные команды пробега в DataRef X-Plane., Расширение реестра будущим профилем МС-21 без правки XPlaneSim., Проводка и масштабы конкретного планера X-Plane., Общая идентичность ЛА и необязательная привязка к X-Plane. Профиль нужен и… (+4 more)

### Community 17 - ".enter_segment"
Cohesion: 0.08
Nodes (18): ConditionMatch, ControlsState, EngagementInputs, _clamp(), FlightSegment, Scenario, Начало эпизода: сброс рукопожатия и первый кадр со стенда. Средой распоряжается…, Сверить ожидаемые условия; стендовые условия никогда не изменяются кодом. (+10 more)

### Community 18 - "ApproachController"
Cohesion: 0.13
Nodes (23): ApproachConfig, Параметры воздушного контура. Значения по умолчанию — настроенные на стенде.…, ApproachController, ApproachResult, clamp(), ApproachLimits, ApproachTelemetry, Заход по ILS с выравниванием. Телеметрию получает параметром, не читает сам.… (+15 more)

### Community 19 - "Telemetry"
Cohesion: 0.04
Nodes (68): Профили преобразования команд ИСМПУ в органы управления X-Plane., Настройки воздушного участка: заход по ILS, выравнивание, управление скоростью.…, Глобальные константы контура управления (перенесены из main.ipynb)., Константы интерфейса стенда заказчика (ПИВ / ICS). Единый источник правды по…, Приёмочные пороги из ТЗ (раздел 5). Единый источник истины для reward-шейпинга…, FlightSegment, Enum, str (+60 more)

### Community 20 - "gain_scheduler.py"
Cohesion: 0.13
Nodes (18): int64, ActorOutput, build_npgs(), _init_log_std(), layer_init(), _mlp_head(), phase_labels_from_groundspeed_kts(), ArrayLike (+10 more)

### Community 22 - "worst_replica"
Cohesion: 0.29
Nodes (6): _as_dict(), Any, Худшая реплика по заданной метрике. Приёмка смотрит именно на худшую, а не на…, worst_replica(), ТЗ задаёт пределы как границы — усреднение прятало бы единичный выход за допуск., test_worst_replica_is_taken_not_the_average()

### Community 23 - "PIDController"
Cohesion: 0.09
Nodes (32): PIDController, Сброс внутренних состояний (используется при выключении системы)., test_ground_pids_use_working_ics_numerics_and_explicit_integrator_limits(), _legacy_reference(), Опциональная численность PID (шаг 5): каждый флаг проверяется на том дефекте,…, Если применено ровно то, что выдал PID, коррекции быть не должно., Уставка прыгает, объект стоит на месте — D-составляющая не должна реагировать.…, Выход ИЗ насыщения должен разрешаться всегда, иначе регулятор залипнет. kp… (+24 more)

### Community 24 - "evaluate.py"
Cohesion: 0.08
Nodes (33): compare_policies(), DefaultGainsPolicy, load_npgs_policy(), main(), NPGSPolicy, Policy, PresetPolicy, ndarray (+25 more)

### Community 25 - "DashboardState"
Cohesion: 0.11
Nodes (9): DashboardState, _finite(), GainChange, _handler_factory(), _jsonable(), Path, HTTP читает только immutable recorder objects; controller меняет control-thread., Вызывается runtime ровно в начале control tick. (+1 more)

### Community 26 - "test_xplane_backend.py"
Cohesion: 0.10
Nodes (14): Неблокирующий UDP-клиент нативного протокола X-Plane 12., test_xplane_ignores_failures_outside_rollout_contract(), MockXPlaneConnector, ScriptedXPlaneConnector, test_commands_failures_and_close_release_overrides(), test_exact_taxi_row_starts_xplane_and_controller_in_taxi_at_15_knots(), test_failed_approach_setup_releases_overrides_and_pause(), test_ignored_xplane_failure_participates_in_segment_delta_and_is_cleared() (+6 more)

### Community 27 - "test_evaluate.py"
Cohesion: 0.10
Nodes (47): admit_checkpoint(), evaluate_tz(), Диагностика эпизода + сценарий → список вердиктов по пунктам ТЗ разд. 5., Итог эпизода: FAIL, если провален хоть один применимый критерий., Пропускать ли чекпоинт дальше. Отсутствующая/нечисловая метрика = отказ.…, verdict_of(), _battery(), _by_name() (+39 more)

### Community 28 - "test_ppo.py"
Cohesion: 0.13
Nodes (24): NPGSConfig, Гиперпараметры архитектуры NPGS (замораживаются вместе с весами при поставке)., PPOConfig, Any, device, PPO-тренер + многокомпонентный loss для NPGS (план §11). `L = L_ppo +…, Плоский буфер одного env: obs-окна, сырые действия, logp/value/reward/done., RolloutBuffer (+16 more)

### Community 29 - "IcsEngagement"
Cohesion: 0.05
Nodes (23): ControlModeState, IcsEngagement, Автомат включения. `step(inputs)` вызывается каждый такт до формирования…, Полный сброс — новый эпизод начинается с невключённого состояния., Сообщить автомату, что кадр **фактически ушёл** на стенд. Вызывается…, Подхватить уже включённый извне пробег: шлём `ControlMode = Rollout`.…, Войти в пробег самостоятельно: шлём `ControlMode = Rollout`. Это же — передача…, Перейти `Approach → Landing` без нового рукопожатия. Закон остаётся воздушным. (+15 more)

### Community 30 - "XPlaneConnectX"
Cohesion: 0.08
Nodes (14): XPlaneConnectX class initialization. Args: ip (str, optional): IP address where…, Starts a recording of the subscribed DataRefs into self.recorded_data. Data is…, Terminates the recording and returns a dictionary of lists that contain the…, Synchronize measurements from multiple sensors to a common frequency.…, Gets the current value of a DataRef. This is only intended for one-time use.…, Permanently subscribe to a list of DataRefs with a certain frequency. This is…, Writes a value to the specified DataRef provided that the DataRef is writable.…, Sends simulator commands to the simulator. These are not commands for the… (+6 more)

### Community 31 - "RunRecorder"
Cohesion: 0.15
Nodes (9): Exception, Append-only writer; ошибка диска помечает прогон, но не выходит в control-loop., Атомарный incremental slice для dashboard, без чтения controller., Сохранить полный effective config; канонические config-файлы не затрагиваются., RunEvent, RunRecorder, test_raw_packet_files_keep_exact_udp_json_and_only_observed_tx(), test_recorder_pins_selected_matrix_rows_and_catalog_hash() (+1 more)

### Community 32 - "test_splits.py"
Cohesion: 0.10
Nodes (41): contract_for(), Сколько раз прогнать сценарий, чтобы результат приёмки что-то значил., Источники случайности на стороне стенда, активные при данных условиях. Мы…, Строит контракт воспроизводимости для сценария., required_replicas(), stochastic_sources(), assert_no_leakage(), has_holdout_failure() (+33 more)

### Community 33 - "Graphify Pipeline"
Cohesion: 0.08
Nodes (29): Folder Watcher, URL Ingestion, Extra Graph Exports, MCP Graph Server, Confidence Audit Trail, Deterministic Node IDs, Semantic Extraction Contract, Cross-Repository Graph Merge (+21 more)

### Community 34 - "XPlaneConnector"
Cohesion: 0.06
Nodes (13): DataRefSample, Discard pre-reload values so readiness cannot use stale telemetry., Одна подписка, один поток приёма и явное освобождение ресурсов., Send basic controls to the ego aircraft. There are hundreds of DataRefs that…, Разобрать пакет; публично для детерминированных mock-тестов., Совместимое read-only представление старого XPlaneConnectX., Совместимость с прежним клиентом., XPlaneConnector (+5 more)

### Community 35 - "ControllingSystem"
Cohesion: 0.06
Nodes (38): ControllingSystem, FailureMode, Связать сценарий с контуром; PID активируются после определения участка., Обновить параметры геометрического наведения латерального канала. Имя сохранено…, Веса влияния каналов (актор, §6): множители к выходам каналов. 1.0 = классика., Такт манёвра ухода. → True, когда набор устойчив (пора отдать управление…, Набор устойчив: есть и вертикальная скорость вверх, и прирост радиовысоты над…, Оркестратор классического контура поверх стенда (`envs.ics_sim.ICSSim`).… (+30 more)

### Community 36 - "test_full_flight.py"
Cohesion: 0.09
Nodes (26): IntFlag, ControlValid, Биты `ControlValidMask`: какие каналы несёт команда. **Один бит на одно…, _engaged_airborne_sim(), parametrize, Управление на всём интервале полёта: заход → касание → пробег → руление.…, «Козление» после касания снимает обжатие на секунду — назад в заход…, Таблицы захода МС-21 к чистому крылу неприменимы — вести по ним нельзя.… (+18 more)

### Community 37 - "test_ics_engagement.py"
Cohesion: 0.10
Nodes (47): _Clock, _engine(), _pump(), Автомат включения управления на стенде. Два раздельных предмета проверки: *…, По ICD стенд должен два секунды ПОЛУЧАТЬ ModeAIReady=1. Если считать одно лишь…, Обратная защита: 30 кадров можно выпалить за 0.1 с — время тоже обязано пройти., Срыв предусловия обнуляет и время, и счётчик кадров., Требование ICD — непрерывность: пропуск готовности рвёт серию. (+39 more)

### Community 38 - "RunSample"
Cohesion: 0.12
Nodes (12): Один такт: вход, команда и диагностика имеют общий ``tick_id``., RunSample, _apply_recorded_gains(), _equal(), _number(), _parse_cell(), ControllingSystem, Типизированный поток новых и legacy-строк с синтетическими ID для старых CSV. (+4 more)

### Community 39 - "ICSSim"
Cohesion: 0.06
Nodes (37): ICSSim, FailureMode, SimInterface, Обмен со стендом заказчика: телеметрия внутрь, команды наружу. Управление…, Принимает ли стенд наши команды. До включения любой `step` уходит вхолостую., Войти в пробег самостоятельно (`ControlMode 0 → 3`)., На стенде отказы приходят телеметрией, а не инжектируются нами., Снять управление: пустая маска и `ControlMode = Off` несколько кадров подряд.… (+29 more)

### Community 40 - "pid_controller.py"
Cohesion: 0.12
Nodes (26): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+18 more)

### Community 41 - "run_reader.py"
Cohesion: 0.07
Nodes (31): AircraftProfile, IcsEngagement, Профильное пространство абсолютных PID-коэффициентов NPGS., _regulator_config(), SFT (behavioral cloning) — предобучение NPGS предсказывать эталонные…, get_aircraft_profile(), find_earth_nav_dat(), get_runway_profile() (+23 more)

### Community 42 - "NPGS"
Cohesion: 0.13
Nodes (18): NPGS, Tensor, Neural PID Gain Scheduler: общий энкодер + головы актора (абс. gain'ы) + голова…, → (mean (B,17), value (B,), phase_logits (B,n_phases))., 17 сырых выходов → [абс. gains×15, w_lon, w_lat] (layout `REGULATOR_ORDER` +…, Один шаг актора. `action` (…,17) — абс. gain'ы для среды; `raw` (…,17) — сэмпл…, Пересчёт на апдейте PPO. → (logp, entropy, value, mean, phase_logits)., pretrain_sft() (+10 more)

### Community 43 - "ICSInputs"
Cohesion: 0.15
Nodes (23): ControlResult, ICSInputs, ICSOutputs, Неизвестные поля исходного JSON; они доступны аудиту, но не закону управления., airborne_control_mode(), airborne_flare_mode(), deactivate(), live_main() (+15 more)

### Community 44 - "test_gain_scheduler.py"
Cohesion: 0.10
Nodes (20): device, Веса + конфиг + слепок нормировки (включая gain-пространство) одним артефактом., action_high(), action_low(), float32, NDArray, Применение абсолютных коэффициентов PID, выданных NPGS. Действие: вектор…, reference_action() (+12 more)

### Community 45 - "3. Этапы реализации"
Cohesion: 0.09
Nodes (21): 1. Подтверждённые проблемы и целевое состояние, 2. Ключевые интерфейсы, 3. Этапы реализации, 4. Тестирование и критерии готовности, 5. Зафиксированные допущения, 6.1. Один dashboard вместо двух, 6.2. Единый источник данных, 6.3. Представления (+13 more)

### Community 46 - "ScenarioGenerator"
Cohesion: 0.21
Nodes (7): Один случайный сценарий. `difficulty=None` → случайная сложность., ScenarioGenerator, AdmissionResult, test_generator_embeds_control_config(), test_generator_high_difficulty_produces_failures(), test_generator_is_deterministic_for_same_seed(), test_generator_zero_difficulty_has_no_failures()

### Community 47 - "EngagementInputs"
Cohesion: 0.14
Nodes (10): EngagementInputs, EngagementState, Enum, Автомат включения управления на стенде заказчика. Стенд принимает наши команды…, Передать управление в руление (`ControlMode 3 → 4`). → удался ли переход.…, Сколько уже держится выдержка. 0.0, если отсчёт не идёт (для диагностики)., Почему включение ещё не произошло — для диагностики при таймауте прогрева.…, Слепок для логов и отчётов приёмки. (+2 more)

### Community 49 - "_Clock"
Cohesion: 0.16
Nodes (17): _air(), _Clock, _pump(), После касания режим меняется на пробег — но не раньше: смена режима на глиссаде…, Ниже 80 футов потеря `AgentIsActive` не повод бросать органы: до земли секунды., Окно только удерживает подтверждение. Само оно включения не даёт., Воздушное включение — это фронт `Off → Approach` после выдержки, а не сразу…, 2.2 с — подтверждённое на стенде значение; наземные 2.0 для захода недостаточны. (+9 more)

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
Cohesion: 0.06
Nodes (23): above_decision_height(), at_lateral_alignment_gate(), ils_blocker(), in_terminal_window(), Последние футы перед касанием, где прерывать заход опаснее, чем доработать.…, ВС выше высоты решения ухода на второй круг (30 м по ТЗ 5.1.1.2). → уход…, Полоса подхода к гейту совмещения с осью ± 5 м: `(30 м, 30 м + band]`. Только в…, Почему нельзя продолжать заход по этому кадру. `None` — можно. Закон читает… (+15 more)

### Community 54 - "run_artifacts.py"
Cohesion: 0.18
Nodes (17): controller_pids(), _csv_value(), default_runs_root(), _effective_configs(), gains_snapshot(), _git_state(), _jsonable(), _matrix_rows() (+9 more)

### Community 55 - "RunwayTracker"
Cohesion: 0.09
Nodes (15): Точка на продолжении оси; положительное расстояние — до порога., Решить прямую геодезическую задачу на сферической Земле., Геодезическое guidance в истинной системе направлений., Guidance по курсу ВПП и измеренному отклонению — без собственной геодезии.…, Возвращает отклонение от осевой линии в метрах. >0 - правее оси, <0 - левее., Геодезическое наведение на ось ВПП с упреждением по скорости., RunwayTracker, KinematicBench (+7 more)

### Community 56 - "RomanLogImporter"
Cohesion: 0.20
Nodes (9): _number(), Path, Потоково нормализует основной и authority CSV Романа., RomanLogImporter, verify_manifest(), fixture, roman_csv(), test_manifest_reports_missing_and_changed_sources() (+1 more)

### Community 57 - "working_ics/approach_criteria.py"
Cohesion: 0.21
Nodes (7): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, ICSInputs, Evaluate the A.1.1 approach segment and stop at a radio-altitude floor.

### Community 58 - "test_dashboard.py"
Cohesion: 0.20
Nodes (13): _live(), _post(), parametrize, test_active_pid_is_editable_in_classical_and_shadow(), test_gain_change_is_queued_bumpless_and_records_full_event(), test_http_api_is_incremental_pending_and_loopback_only(), test_incremental_snapshot_uses_recorder_objects_and_stays_small_when_idle(), test_live_and_replay_use_the_same_dashboard_snapshot() (+5 more)

### Community 59 - "fakes.py"
Cohesion: 0.14
Nodes (14): decode_airborne(), decode_outputs(), flight_sim(), _integrate_throttle(), Фейковый стенд для тестов: `ICSInputs` вместо реального UDP. Единственный…, Отправленные команды в нормированном виде — для сравнения траекторий.…, `ICSOutputs` → (brake_l, brake_r, thr_l_rate, thr_r_rate, steer), всё…, Ход рычага РУД за такт: интеграл команды-скорости, зажатый физическим… (+6 more)

### Community 60 - "gain_space_for"
Cohesion: 0.17
Nodes (15): gain_space_for(), float32, GainMap, NDArray, Абсолютные коэффициенты пресета → `target_z` (17,): gains через `inv_gain`,…, target_z_from_gains(), GainSpace, Профильные пространства абсолютных PID-коэффициентов NPGS. (+7 more)

### Community 61 - "test_control_parity.py"
Cohesion: 0.10
Nodes (19): Enum, Генератор эталонной кривой скорости (Колокол Гаусса)., Начать профиль с фактической скорости текущего участка., То же без лишнего round-trip м/с → узлы → м/с на касании., Возвращает идеальную скорость (м/с) для текущей точки пути., ReferenceTrajectory, TrajectoryState, VelocityLaw (+11 more)

### Community 62 - "Project Dependencies"
Cohesion: 0.18
Nodes (13): Autonomous Landing Controller, Repository Guidance for Codex, Autonomous Landing Controller, Repository Guidance for Claude Code, Neural Landing Implementation Plan, Unified Scenario System, Optional Gymnasium, NumPy (+5 more)

### Community 63 - "test_ground_controller.py"
Cohesion: 0.08
Nodes (36): initial_segment(), is_airborne(), FlightSegment, Сообщает ли стенд, что ВС в воздухе и достаточно высоко для приёма захода.…, С какого участка начинать. Пробег — ответ по умолчанию (см. модуль)., `ICSInputs` → `Telemetry`: поля в СИ + «сырой» пакет для property. Стенд отдаёт…, parametrize, engaged_inputs() (+28 more)

### Community 64 - ".invalid"
Cohesion: 0.20
Nodes (9): Кадр «связи со стендом нет». Нули, а не None: контур проверяет `valid` первым., Стенд при обрыве связи отдаёт НУЛИ с valid=False, а не None. Проверка «поле is…, test_control_step_stops_on_invalid_frame_even_with_numeric_fields(), Первый `read_telemetry` может вернуться по таймауту — это не «мы на полосе».…, test_the_segment_is_not_decided_by_a_frame_without_a_bench_packet(), Единичный таймаут — не повод вернуть рулю авторитет, которого у него нет., Без кадра о конфигурации борта неизвестно ничего — безопасен только штатный…, test_lost_packet_does_not_repair_a_failed_actuator() (+1 more)

### Community 66 - "dashboard_core.py"
Cohesion: 0.10
Nodes (15): _allocator_stage(), DashboardServer, DashboardSnapshot, _first_present(), _gain_ranges(), _gains_from_manifest(), _gains_from_samples(), _load_updates() (+7 more)

### Community 67 - "test_rollout_env.py"
Cohesion: 0.17
Nodes (14): ObservationBuilder, Строит нормированный вектор наблюдения одного кадра., Тесты Этапа 2: Observation/Action/reward/RolloutEnv + инвариант identity ==…, Без аннотаций типов @dataclass не видит полей, и тогда любые два экземпляра…, Свежий экземпляр обязан нести все поля в собственном `__dict__`. Без аннотаций…, `break_control` взводится в конце КАЖДОГО нормального пробега (достигнута…, _ready_controller(), test_break_control_is_cleared_when_a_scenario_is_applied() (+6 more)

### Community 68 - "test_working_ics_dashboard.py"
Cohesion: 0.35
Nodes (10): ClearWeatherILSController, DashboardState, _controller(), _inputs(), Characterization tests for the bench-validated ``working_ics`` dashboard., _record(), test_dashboard_records_four_airborne_views_and_diagnostics(), test_gain_updates_are_immediate_validated_and_share_pitch_with_flare() (+2 more)

### Community 70 - "_signal_valid"
Cohesion: 0.14
Nodes (7): Невалидные ICS-сигналы, которые воздушный закон читает безусловно., Приборная скорость (kt → м/с). Отсечки реверса заданы по ней, а не по путевой., Радиовысота **в футах** — единицы стенда. Порог воздушного включения (400…, Объявлены ли валидными **оба** канала ILS (курсовой и глиссадный). `None` —…, Боковое отклонение от оси, измеренное стендом. Позволяет не считать геодезию…, Validity-флаг стенда плюс конечное числовое значение., _signal_valid()

### Community 71 - "Unified Profile-Aware Scenario System"
Cohesion: 0.22
Nodes (9): Technical-Specification Acceptance Gates, Bench-Validated ILS Approach Channel, Forward-Only Flight Segment Supervisor, Tolerance-Gated Go-Around, Longitudinal and Lateral Ground Channels, PID Run Matrix, Unified Profile-Aware Scenario System, Legacy Scenario Preset Model (+1 more)

### Community 72 - "Interactive PID Dashboard"
Cohesion: 0.25
Nodes (9): Nine-View PID Dashboard, Run Recording Artifacts, buildTabs, draw, Gain Tuning and Snapshot Export, Interactive PID Dashboard, refresh, render (+1 more)

### Community 73 - "MatrixRun"
Cohesion: 0.04
Nodes (23): cases_for_segment(), ground_runs(), MatrixCase, MatrixCondition, MatrixRun, _number(), Any, FailureMode (+15 more)

### Community 74 - "DashboardState"
Cohesion: 0.21
Nodes (4): DashboardServer, DashboardState, Any, ICSInputs

### Community 75 - "FailureMode"
Cohesion: 0.11
Nodes (18): FailureMode, Enum, _hash_unit(), is_signature_holdout(), PartitionedScenarioProvider, Детерминированное разбиение сценариев на обучение и holdout (шаг 6). Схема…, SHA-256 от идентификатора → число в [0, 1). Стабильно между запусками и…, Устойчивая комбинация условий, а не имя или целое семейство отказов. (+10 more)

### Community 76 - "ICSInterface.cs"
Cohesion: 0.36
Nodes (7): External.Systems.ICS, ControlModeState, GearState, ICSInputs, ICSOutputs, ReverseEngineType, UInt64

### Community 77 - "heading_deviation_deg"
Cohesion: 0.19
Nodes (12): heading_deviation_deg(), Отклонение курса ВС от направления ВПП — приёмочная величина ТЗ 5.1.3.3 /…, Телеметрия ВС на оси ВПП, смещённого вбок на `offset_m` и с заданным курсом.…, ТЗ 5.1.3.3 нормирует курс «от направления ВПП». Смещение от оси на него не…, На стенде курс ВПП приходит телеметрией; конфиг — только значение по умолчанию., Таблица из находки: раньше оба случая давали противоположный результат., _telemetry_at(), test_heading_deviation_ignores_lateral_offset() (+4 more)

### Community 78 - "runtime/pretrain.py"
Cohesion: 0.16
Nodes (19): ground_cases(), build_sim(), Any, Path, Создать backend; для ICS геодезия включается только явным ``runway_profile``., build_capture_stack(), build_scenarios(), matrix_preset_names() (+11 more)

### Community 79 - "RunReader"
Cohesion: 0.15
Nodes (23): normalize_code(), resolve_matrix_run(), runs_for_code(), _gain_patch(), main(), promote_candidate(), PromotionError, Path (+15 more)

### Community 80 - "ICS PID Monitor"
Cohesion: 0.29
Nodes (7): buildControls, draw, formatTime, Four-Loop PID Tuning, ICS PID Monitor, Live and Historical Timeline, refresh

### Community 81 - "ics_connector.py"
Cohesion: 0.09
Nodes (18): IntEnum, FlightPhase, Фаза полёта, сообщаемая стендом (`ICSInputs.FlightPhase`)., Типизированные backend-расширения общего SI-кадра., TelemetryExtensions, ControlModeState, ICSBenchConnector, main() (+10 more)

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

### Community 86 - "CompletionRule"
Cohesion: 0.15
Nodes (14): CompletionRule, Как активный наземный сценарий заканчивает управление., ObserverEstimate, Оценки PINN-обсервера (§12). Заглушка нулями до Этапа 7., RewardWeights, EpisodeInfo, _make_box(), GainSpace (+6 more)

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
Cohesion: 0.13
Nodes (16): ControlArchitecture, Фиксированный порядок слоёв и роль обучаемого компонента., Проверяет контракт обучаемого слоя. Нарушение → `ValueError` на старте…, validate_action_contract(), Контракт обучаемого слоя (Этап 4): что именно сеть имеет право менять. Аргумент…, Пустое обоснование = контракт непредъявим по ТЗ., Машиночитаемое утверждение «сеть не является регулятором»., Список запретов должен совпадать с реальными полями команд, иначе он… (+8 more)

### Community 92 - "static_sim"
Cohesion: 0.10
Nodes (34): apply_gains_to_pids(), base_gains_from_pids(), PidMap, Снимок (kp, ki, kd) регуляторов — пресет-якорь для Shield и т.п., Записывает эффективные gain'ы обратно в регуляторы (перед control_step)., apply_corrections(), decode(), preset_action() (+26 more)

### Community 93 - ".summary"
Cohesion: 0.13
Nodes (13): _component(), excess(), graded(), _p95(), 95-й перцентиль. Устойчивее максимума к одиночному выбросу телеметрии., Сырые измерения эпизода. `None` там, где данных не было — приёмка обязана…, Компоненты `{raw, weight, weighted}` + `total_loss`/`reward` + диагностика., Чистый hinge: превышение допуска, нормированное на допуск. Внутри допуска = 0. (+5 more)

### Community 94 - "main"
Cohesion: 0.18
Nodes (14): cli(), _lost_engagement(), main(), ControllingSystem, Снял ли стенд активность посреди прогона. → пора останавливаться. Без этой…, Точка входа: подключиться к стенду, выбрать пресет и провести полёт.…, Единственная production CLI-точка для ICS и явного тестового X-Plane backend., Прогоняет один полёт на уже настроенном контуре. (+6 more)

### Community 95 - "reward.py"
Cohesion: 0.09
Nodes (27): _command_jerk(), compute_reward(), _effort_saturated(), _ground_steering(), ObjectiveWeights, TypedDict, Objective — единое определение «хорошего пробега» (§11 + приёмка ТЗ разд. 5).…, Упёрлась ли команда в границу **со стороны усилия**. Важное различие: нулевая… (+19 more)

### Community 99 - "_WarmUpSim"
Cohesion: 0.29
Nodes (4): Стенд, включающий управление только после N тактов прогрева. Само рукопожатие…, Такты рукопожатия — не шаги эпизода: в это время ВС нами не управлялось. Иначе…, test_warm_up_runs_before_the_episode_and_is_not_counted(), _WarmUpSim

### Community 110 - "protocol.py"
Cohesion: 0.25
Nodes (6): ControlModeState, GearState, ICSOutputs, Any, IntEnum, ReverseEngineType

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
Cohesion: 0.05
Nodes (41): engaged_sim(), (sim, connector) с завершённым рукопожатием: стенд подтвердил `AgentIsActive =…, Регресс: расширение структуры не должно протащить руль высоты в маску пробега., test_ground_frame_still_declares_only_the_ground_channels(), _cold_sim(), Тесты стенда (`ICSSim`), подбора сценария и генератора — без реального стенда., Разделение органов из таблицы Заказчика: тиллер — на рулении, педальный пост —…, Заявить канал, который не формируешь, — взять ответственность за неуправляемый… (+33 more)

### Community 116 - "Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)., Source Nodes

### Community 117 - "VlaydRolloutBridge"
Cohesion: 0.33
Nodes (6): ICSInputs, Hand the validated airborne session to Vlayd's existing rollout loop. The…, Keep Vlayd's engagement latch synchronized during the approach., Run Vlayd's rollout until taxi speed, then send its taxi handoff., VlaydRolloutBridge, test_rollout_bridge_preserves_engagement_and_switches_without_off()

### Community 123 - ".act_numpy"
Cohesion: 0.25
Nodes (5): floating, Any, float32, obs (T,56) np → (action_17 np, raw_17 np, logp float, value float)., no_grad

### Community 124 - ".from_json"
Cohesion: 0.29
Nodes (6): _pid_from_colleague(), Загрузка настроек из JSON коллеги (`config/ics_clear_weather_pid.json`). Секции…, `PIDConfig` коллеги → аргументы нашего `PIDController`. Предел интегратора у…, Path, Наши умолчания и его файл — одно и то же. Разойдутся — расхождение должно быть…, test_config_from_the_colleague_json_matches_our_defaults()

### Community 125 - "GuidanceState"
Cohesion: 0.29
Nodes (3): GuidanceState, Совместимость с прежним атрибутом; новый термин явно указывает ось., Совместимость со старым словарным API.

### Community 126 - ".compute"
Cohesion: 0.18
Nodes (5): → (интеграл только с утечкой, интеграл с утечкой и приращением). Оба уже зажаты., Такт регулятора. `measurement` обязателен при `derivative_on_measurement=True`., Back-calculation: подтянуть интегратор к фактически применённой команде. No-op…, Сменить коэффициенты без сброса D-history и с компенсацией интегратором.…, Вес апериодического фильтра D-составляющей за такт `dt`.

### Community 129 - "Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md)., Source Nodes

### Community 130 - "Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md)., Source Nodes

### Community 131 - "regulators.py"
Cohesion: 0.15
Nodes (10): Канонический порядок регуляторов, размерности действия и **контракт обучаемого…, Один регулятор, коэффициенты которого (kp/ki/kd) разрешено настраивать сети., RegulatorSpec, PIDDiagnostics, Пропорционально-интегрально-дифференциальный регулятор. Класс сохраняет прежнюю…, Типизированный снимок последнего такта регулятора., apply_ground_control(), build_pids() (+2 more)

### Community 133 - ".enter_segment"
Cohesion: 0.25
Nodes (4): FailureMode, FlightSegment, Применить только дельту условий при переходе между участками., Снять один отказ, не переинициализируя отказ, продолжающийся на новом участке.

### Community 135 - "Q: Приступай к выполнению этапа 2 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 2 плана docs/plan.md, Source Nodes

### Community 137 - "Criterion"
Cohesion: 0.40
Nodes (4): _check(), Criterion, Один пункт ТЗ: предел, измеренное значение, вердикт и его причина., Строит вердикт. Неприменимо → SKIP; применимо, но данных нет → FAIL.

### Community 140 - ".activate_segment"
Cohesion: 0.09
Nodes (17): ApproachConfig, ApproachController, approach_blocker(), ApproachRefused, Воздушный участок начинать нельзя — с названной причиной. Отдельное исключение,…, Можно ли вообще судить об участке по этому кадру. Кадр без пакета стенда…, Почему нельзя вести заход по этому кадру. `None` — можно. Пока проверка одна,…, segment_is_decidable() (+9 more)

### Community 142 - ".__init__"
Cohesion: 0.29
Nodes (5): AircraftProfile, Path, RunwayProfile, WeatherState, XPlaneConnector

### Community 154 - "_faults_from_inputs"
Cohesion: 0.50
Nodes (3): _faults_from_inputs(), Отказы, о которых сообщает борт — **единственный** источник истины об отказах.…, Сигналы отказов со стенда → наши `FailureMode`. Отказы шасси…

### Community 155 - "test_matches_the_colleague_implementation_command_for_command"
Cohesion: 0.50
Nodes (4): _colleague_controller(), Оригинальный контур коллеги, настроенный тем же файлом. `None`, если…, Перенос обязан совпадать с подтверждённым на стенде оригиналом, а не «вести…, test_matches_the_colleague_implementation_command_for_command()

### Community 158 - "Q: Приступай к выполнению этапа 4 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 4 плана docs/plan.md, Source Nodes

## Ambiguous Edges - Review These
- `Unified Profile-Aware Scenario System` → `Legacy Scenario Preset Model`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to
- `Dual-Backend SimInterface` → `ICS-Only Backend Guidance`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **70 isolated node(s):** `Answer`, `Outcome`, `Source Nodes`, `ismpu`, `Answer` (+65 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **55 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `ControllingSystem` (3× useful, score=2.936484458)
- `ICSSim` (2× useful, score=1.971519619)
- `LateralChannel` (2× useful, score=1.950156376)
- `ObservationBuilder` (2× useful, score=1.930391722)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Unified Profile-Aware Scenario System` and `Legacy Scenario Preset Model`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Dual-Backend SimInterface` and `ICS-Only Backend Guidance`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `ControllingSystem` connect `ControllingSystem` to `RolloutEnv`, `regulators.py`, `json_config.py`, `scenarios.py`, `Criterion`, `.activate_segment`, `test_pretrain.py`, `test_run_matrix.py`, `Telemetry`, `PIDController`, `evaluate.py`, `test_xplane_backend.py`, `test_evaluate.py`, `test_ppo.py`, `XPlaneConnector`, `test_full_flight.py`, `ICSSim`, `NPGS`, `test_gain_scheduler.py`, `ScenarioGenerator`, `_Clock`, `test_go_around.py`, `test_approach_criteria.py`, `._approach_step`, `test_dashboard.py`, `fakes.py`, `gain_space_for`, `test_control_parity.py`, `test_ground_controller.py`, `.invalid`, `test_rollout_env.py`, `MatrixRun`, `runtime/pretrain.py`, `CompletionRule`, `LongitudinalChannel`, `test_action_contract.py`, `static_sim`, `reward.py`, `_WarmUpSim`, `test_ics_sim.py`, `VlaydRolloutBridge`, `CSVLogger`?**
  _High betweenness centrality (0.151) - this node is a cross-community bridge._
- **Why does `Telemetry` connect `Telemetry` to `test_tolerance.py`, `test_weather.py`, `json_config.py`, `.enter_segment`, `scenarios.py`, `GroundControlAllocator`, `LateralChannel`, `.activate_segment`, `ControlsState`, `.enter_segment`, `ApproachController`, `XPlaneSim`, `_faults_from_inputs`, `ControllingSystem`, `test_full_flight.py`, `ICSSim`, `ICSInputs`, `_Clock`, `test_go_around.py`, `test_approach_criteria.py`, `._approach_step`, `RunwayTracker`, `fakes.py`, `test_control_parity.py`, `test_ground_controller.py`, `.invalid`, `test_rollout_env.py`, `_signal_valid`, `MatrixRun`, `heading_deviation_deg`, `ics_connector.py`, `test_working_ics_golden.py`, `.reset`, `test_approach_channel.py`, `LongitudinalChannel`, `_WarmUpSim`, `test_ics_sim.py`, `VlaydRolloutBridge`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._
- **Why does `ControlsState` connect `ControlsState` to `GainCommand`, `RolloutEnv`, `Shield`, `airborne_inputs`, `GroundControlAllocator`, `.activate_segment`, `.rudder_cmd`, `AircraftProfile`, `Telemetry`, `PIDController`, `test_xplane_backend.py`, `test_matches_the_colleague_implementation_command_for_command`, `ICSSim`, `run_reader.py`, `ICSInputs`, `test_control_parity.py`, `test_rollout_env.py`, `test_working_ics_golden.py`, `EpisodeObjective`, `CompletionRule`, `test_approach_channel.py`, `test_action_contract.py`, `reward.py`, `_WarmUpSim`, `test_ics_sim.py`, `VlaydRolloutBridge`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `ControllingSystem` (e.g. with `ApproachSetup` and `ConditionMatch`) actually correct?**
  _`ControllingSystem` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `Telemetry` (e.g. with `ApproachSetup` and `ConditionMatch`) actually correct?**
  _`Telemetry` has 46 INFERRED edges - model-reasoned connections that need verification._