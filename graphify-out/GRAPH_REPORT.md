# Graph Report - GOSNIIASProject  (2026-08-15)

## Corpus Check
- 138 files · ~138,233 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2559 nodes · 5989 edges · 157 communities (108 shown, 49 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 534 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `070282e8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_tolerance.py
- split_scenarios
- train.py
- test_icd_units.py
- GainSpace
- json_config.py
- SimInterface
- ControlsState
- ApproachConfig
- ScriptedFlightBench
- ground_allocator.py
- LateralChannel
- test_pretrain.py
- scenarios.py
- test_ics_connector.py
- test_run_matrix.py
- AircraftProfile
- ICSSim
- ApproachController
- Telemetry
- test_gain_scheduler.py
- XPlaneSim
- weather.py
- PIDController
- evaluate.py
- RolloutEnv
- test_xplane_backend.py
- test_evaluate.py
- test_ppo.py
- IcsEngagement
- XPlaneConnectX
- fakes.py
- test_splits.py
- Graphify Pipeline
- XPlaneConnector
- ControllingSystem
- Scenario
- test_ics_engagement.py
- test_diagnostic_tools.py
- FakeConnector
- pid_controller.py
- system.py
- NPGS
- ICSInputs
- action.py
- 3. Этапы реализации
- ScenarioGenerator
- EngagementInputs
- RunRecorder
- _Clock
- test_go_around.py
- Neural PID Gain Scheduler Architecture
- test_approach_criteria.py
- ._approach_step
- gui/dashboard.py
- RunwayTracker
- RomanLogImporter
- working_ics/approach_criteria.py
- test_refactoring_contracts.py
- .send_outputs
- gain_space_for
- ReferenceTrajectory
- Project Dependencies
- test_full_flight.py
- GuidanceState
- ICSInputs
- test_dashboard.py
- test_rollout_env.py
- test_working_ics_dashboard.py
- ICSOutputs
- admit_checkpoint
- Unified Profile-Aware Scenario System
- Interactive PID Dashboard
- FailureMode
- DashboardState
- splits.py
- ICSInterface.cs
- LandingFlapConfiguration
- PretrainRunConfig
- VlaydRolloutBridge
- ICS PID Monitor
- ics_connector.py
- ICS UDP JSON Protocol
- X-Plane Dashboard and Runtime Guide
- config/approach.py
- .neutralize_airborne
- DashboardState
- test_profiled_scenarios.py
- FrictionProfile
- test_approach_channel.py
- .guidance
- test_action_contract.py
- PresetPolicy
- rollout_env.py
- SimInterface
- reward.py
- conftest.py
- agent/__init__.py
- config/__init__.py
- Criterion
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
- ToleranceReport
- Q: Реализовать этап 0: baseline, golden replay и dashboard characterization
- Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md).
- decode_outputs
- normalization.py
- test_ics_sim.py
- Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md).
- str
- IntEnum
- ControlModeState
- ICSInputs
- ICSOutputs
- socket
- test_control_parity.py
- EngagementInputs
- .begin_flight
- .compute
- .rudder_cmd
- .point_on_centerline
- on_ground
- HandshakeBench
- regulators.py
- ApproachLimits
- .as_dict
- ApproachTelemetry
- Q: Приступай к выполнению этапа 2 плана docs/plan.md
- _faults_from_inputs
- IcsEngagement
- ICSInputs
- ApproachConfig
- SimInterface
- SimInterface
- Path
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
- Scenario
- ReferenceTrajectory
- RewardWeights
- TypedDict

## God Nodes (most connected - your core abstractions)
1. `ControllingSystem` - 179 edges
2. `Telemetry` - 121 edges
3. `ControlsState` - 97 edges
4. `ICSSim` - 78 edges
5. `PIDController` - 62 edges
6. `Scenario` - 57 edges
7. `RolloutEnv` - 55 edges
8. `XPlaneSim` - 49 edges
9. `NPGS` - 49 edges
10. `FailureMode` - 48 edges

## Surprising Connections (you probably didn't know these)
- `Autonomous Landing Controller` --semantically_similar_to--> `Autonomous Landing Controller`  [INFERRED] [semantically similar]
  CLAUDE.md → AGENTS.md
- `Profile-Aware Flight Scenarios` --semantically_similar_to--> `Unified Scenario System`  [INFERRED] [semantically similar]
  docs/XPLANE_DASHBOARD.md → implementation_plan.md
- `Acceptance and Evaluation Harness` --semantically_similar_to--> `Technical-Specification Acceptance Gates`  [INFERRED] [semantically similar]
  implementation_plan.md → AGENTS.md
- `X-Plane Resettable Runtime` --semantically_similar_to--> `X-Plane Training and Evaluation Backend`  [INFERRED] [semantically similar]
  docs/XPLANE_DASHBOARD.md → implementation_plan.md
- `_Clock` --uses--> `ControlValid`  [INFERRED]
  tests/test_full_flight.py → ismpu/config/ics.py

## Import Cycles
- 3-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 3-file cycle: `ismpu/config/scenarios.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 3-file cycle: `ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/control/channels.py`
- 3-file cycle: `ismpu/config/aircraft_profiles.py -> ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/config/aircraft_profiles.py`
- 4-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 4-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/tolerance.py -> ismpu/control/approach.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach_criteria.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/flight.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/ground_allocator.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/tolerance.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/aircraft_profiles.py -> ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py -> ismpu/config/aircraft_profiles.py`

## Hyperedges (group relationships)
- **Graphify Extraction and Build Flow** — _codex_skills_graphify_skill_structural_extraction, _codex_skills_graphify_skill_semantic_extraction, _codex_skills_graphify_references_extraction_spec_semantic_extraction_contract, _codex_skills_graphify_references_update_build_merge [EXTRACTED 1.00]
- **Hybrid Neural Landing Control** — implementation_plan_classical_pid_plant, implementation_plan_npgs, implementation_plan_deterministic_shield, implementation_plan_ppo_multicomponent_loss, implementation_plan_pinn_observer [EXTRACTED 1.00]
- **PID Dashboard Ecosystem** — docs_xplane_dashboard_pid_dashboard, ismpu_gui_dashboard_pid_dashboard, ismpu_working_ics_ics_dashboard_ics_pid_monitor [INFERRED 0.85]

## Communities (157 total, 49 thin omitted)

### Community 0 - "test_tolerance.py"
Cohesion: 0.07
Nodes (46): lateral_limit_m(), lateral_load_situation(), lateral_situation(), normal_load_situation(), IntEnum, Критерии критичности особых ситуаций МС-21 (Приложение 1 к ТЗ). Таблица АП-25…, Классификация скорости касания относительно VAPP и VВПП пред., Классификация нормальной перегрузки посадочного удара. `heavy` — взлётный вес. (+38 more)

### Community 1 - "split_scenarios"
Cohesion: 0.18
Nodes (15): assert_no_leakage(), Разбивает набор сценариев. Детерминировано и устойчиво к добавлению новых…, Проверяет, что holdout не пересекается с обучением по идентификаторам. Дешёвая…, split_scenarios(), SplitResult, Ради этого хеш и выбран вместо shuffle(seed): иначе новый сценарий менял бы…, _scenario(), test_adding_scenarios_does_not_reshuffle_existing_assignments() (+7 more)

### Community 2 - "train.py"
Cohesion: 0.10
Nodes (21): PPOTrainer, Tensor, Собирает rollout из среды и обновляет NPGS многокомпонентным PPO-loss., Шагает средой `rollout_len` тактов (сброс по завершению эпизода). → статистика., Хук L_shield (§11): барьер, отталкивающий выход от края уровня-1 Shield. По…, build_ics_stack(), build_training_stack(), CSVLogger (+13 more)

### Community 3 - "test_icd_units.py"
Cohesion: 0.11
Nodes (17): Сверка каждого сигнала стенда с документами Заказчика. Два независимых…, 1 фут/мин = 0.3048/60 м/с. Приближение здесь копится на всём заходе., Нумерация фаз из doc-комментария `FlightPhase` в ICSInterface.cs., −26.5…55.0° — фактическое положение РУД во входной телеметрии, не команда., Наши константы обязаны совпадать с таблицей управляющих сигналов Заказчика., Тиллер задаётся ходом в миллиметрах. Отдельным тестом, потому что ошибка была…, 0–45 мм командует, 0–36.73 мм отчитывается. Подмена недодаёт ~18 % хода., В перечне управляющих сигналов абсолютного положения РУД нет — только скорость.… (+9 more)

### Community 4 - "GainSpace"
Cohesion: 0.05
Nodes (54): GainKey, ActorOutput, TypedDict, Тензоры одного прохода актора, до преобразования в NumPy., GainSpace, Any, ArrayLike, float64 (+46 more)

### Community 5 - "json_config.py"
Cohesion: 0.17
Nodes (27): approach_control_from_dict(), approach_control_to_dict(), _copy_approach(), dump_scenario(), _finite_tree(), ground_control_from_dict(), ground_control_to_dict(), _legacy_ground() (+19 more)

### Community 6 - "SimInterface"
Cohesion: 0.10
Nodes (5): BaseException, StartMode, Минимальный lifecycle, одинаковый для стенда и X-Plane., SimInterface, Protocol

### Community 7 - "ControlsState"
Cohesion: 0.08
Nodes (46): ControlsState, Разделяемая по тактам структура команд — и наземных, и воздушных. Аннотации…, _descent_frames(), _our_channel(), Страховка от самообмана: сценарий обязан пройти выравнивание, иначе паритет его…, Угол сноса не должен превращаться в ошибку курса на локализаторе., Стенд иногда сбрасывает Valid при сохранении пригодного численного значения., Отклонение планки курса задаёт доворот в сторону оси, а не от неё. (+38 more)

### Community 9 - "ScriptedFlightBench"
Cohesion: 0.33
Nodes (4): flight_sim(), Стенд, проигрывающий заход и касание **по сценарию**, а не по нашим командам.…, (sim, bench) на сценарном заходе. Рукопожатие ещё не выполнено., ScriptedFlightBench

### Community 10 - "ground_allocator.py"
Cohesion: 0.13
Nodes (17): LongitudinalDiagnostics, FailureManager, FailureState, Эффективности исполнительных органов. Аннотации типов обязательны: без них…, Проецирует набор дискретных отказов в эффективности исполнительных органов., Привести состояние ровно к набору `modes` (то, что сообщил стенд). Пересборка с…, ActuatorFeedback, ActuatorVector (+9 more)

### Community 11 - "LateralChannel"
Cohesion: 0.23
Nodes (7): GuidanceState, LateralChannel, LateralDiagnostics, Блок 2: runway guidance → единый нормированный yaw-запрос., Guidance по тому, что даёт стенд. → словарь guidance или None, если данных нет.…, Единый GuidanceState текущего кадра для control/observation/reward., RunwayTracker

### Community 12 - "test_pretrain.py"
Cohesion: 0.09
Nodes (46): _phase_labels(), pretrain_sft(), PretrainConfig, float32, GainMap, NDArray, Tensor, SFT (behavioral cloning) — предобучение NPGS предсказывать эталонные… (+38 more)

### Community 13 - "scenarios.py"
Cohesion: 0.11
Nodes (28): AircraftControlSet, ApproachSetup, ConditionMatch, _copy_approach(), _copy_ground(), _ground_segments_for_spec(), GroundControlConfig, _GroundPresetSpec (+20 more)

### Community 14 - "test_ics_connector.py"
Cohesion: 0.11
Nodes (18): Разбор телеметрии стенда с совместимостью вперёд. Асимметрия намеренная (JSON-…, _connector(), _FakeSocket, _full_payload(), Транспорт стенда: разбор телеметрии и отправка команд. На проводе чистый JSON…, Подставить ноль значило бы выдумать телеметрию, по которой считается управление., Стенд делает UTF8.GetString() → JsonConvert. Любые байты перед JSON сломали бы…, Windows отдаёт WSAECONNRESET на UDP, если получатель закрыл порт. Ронять цикл… (+10 more)

### Community 15 - "test_run_matrix.py"
Cohesion: 0.12
Nodes (13): compose_matrix_scenario(), _install_through_scenarios(), matrix_battery(), Сценарий по имени либо шифру матрицы, без различия раскладки А/B., Объединить случай листа А и случай листа Б в один полный сценарий. Аргументы…, Собрать штатные сквозные случаи Б.4 из реальных источников листов А и Б., resolve_scenario(), Матрица прогонов и её связь с единым реестром сценариев. (+5 more)

### Community 16 - "AircraftProfile"
Cohesion: 0.10
Nodes (10): _profile_name(), AircraftProfile, clamp(), Преобразовать воздушные команды ICD в нормированные DataRef X-Plane., Преобразовать нормированные команды пробега в DataRef X-Plane., Проводка и масштабы конкретного планера X-Plane., Общая идентичность ЛА и необязательная привязка к X-Plane. Профиль нужен и…, Command refs retained under the historical public name. (+2 more)

### Community 17 - "ICSSim"
Cohesion: 0.06
Nodes (26): ConditionMatch, ICSOutputs, _clamp(), ICSSim, ControlsState, FailureMode, FlightSegment, Scenario (+18 more)

### Community 18 - "ApproachController"
Cohesion: 0.10
Nodes (29): ApproachConfig, Параметры воздушного контура. Значения по умолчанию — настроенные на стенде.…, angle_error_deg(), ApproachController, ApproachResult, clamp(), ApproachLimits, ApproachTelemetry (+21 more)

### Community 19 - "Telemetry"
Cohesion: 0.08
Nodes (16): Такт манёвра ухода. → True, когда набор устойчив (пора отдать управление…, Набор устойчив: есть и вертикальная скорость вверх, и прирост радиовысоты над…, Невалидные ICS-сигналы, которые воздушный закон читает безусловно., Приборная скорость (kt → м/с). Отсечки реверса заданы по ней, а не по путевой., Радиовысота **в футах** — единицы стенда. Порог воздушного включения (400…, Объявлены ли валидными **оба** канала ILS (курсовой и глиссадный). `None` —…, Боковое отклонение от оси, измеренное стендом. Позволяет не считать геодезию…, Обжатие ВСЕХ стоек. Диагностический сигнал; условие включения проверяет сам… (+8 more)

### Community 20 - "test_gain_scheduler.py"
Cohesion: 0.09
Nodes (23): int64, build_npgs(), _init_log_std(), layer_init(), _mlp_head(), NPGSConfig, phase_labels_from_groundspeed_kts(), Any (+15 more)

### Community 21 - "XPlaneSim"
Cohesion: 0.07
Nodes (15): ApproachSetup, _destination(), AircraftProfile, ControlsState, FailureMode, FlightSegment, RunwayProfile, Scenario (+7 more)

### Community 22 - "weather.py"
Cohesion: 0.10
Nodes (27): compose_wind(), decompose_wind(), Enum, Погодные условия эпизода: описание, шкала сцепления и разбор ветра. Модуль **не…, `ICSInputs` → `WeatherState`. Единственный источник фактической погоды. Стенд…, (скорость, откуда) → (crosswind, headwind) относительно курса ВПП. crosswind >…, (crosswind, headwind) → (скорость, откуда, °). Обратна `decompose_wind`., Состояние ВПП как **монотонная шкала скользкости** 0…15 (0 — сухо, 15 — лёд со… (+19 more)

### Community 23 - "PIDController"
Cohesion: 0.09
Nodes (31): PIDController, Сброс внутренних состояний (используется при выключении системы)., test_ground_pids_use_working_ics_numerics_and_explicit_integrator_limits(), _legacy_reference(), Опциональная численность PID (шаг 5): каждый флаг проверяется на том дефекте,…, Если применено ровно то, что выдал PID, коррекции быть не должно., Уставка прыгает, объект стоит на месте — D-составляющая не должна реагировать.…, Выход ИЗ насыщения должен разрешаться всегда, иначе регулятор залипнет. kp… (+23 more)

### Community 24 - "evaluate.py"
Cohesion: 0.08
Nodes (27): AdmissionResult, compare_policies(), DefaultGainsPolicy, load_npgs_policy(), main(), NPGSPolicy, Policy, ndarray (+19 more)

### Community 25 - "RolloutEnv"
Cohesion: 0.09
Nodes (24): preset_action(), float64, 17-мерное действие, точно воспроизводящее коэффициенты пресета (веса = 1).…, ndarray, Копия команды такта — для расчёта джерка на следующем такте. Копируется…, Окно истории → тензор `(history_len, OBS_DIM)` (последовательность кадров для…, Состояние для поведенческих проверок Shield. Курс здесь — отклонение от…, RolloutEnv (+16 more)

### Community 26 - "test_xplane_backend.py"
Cohesion: 0.09
Nodes (16): SensorNoise, DatagramSocket, MockXPlaneConnector, ScriptedXPlaneConnector, test_commands_failures_and_close_release_overrides(), test_failed_approach_setup_releases_overrides_and_pause(), test_ignored_xplane_failure_participates_in_segment_delta_and_is_cleared(), test_missing_or_stale_required_data_makes_xplane_telemetry_invalid() (+8 more)

### Community 27 - "test_evaluate.py"
Cohesion: 0.16
Nodes (27): evaluate_tz(), Диагностика эпизода + сценарий → список вердиктов по пунктам ТЗ разд. 5., _by_name(), _diagnostics(), Тесты приёмки по ТЗ (Этап 5): вердикты по пунктам, правило «нет данных = FAIL»,…, Эпизод не дошёл до руления → допуск ±1 м неприменим. Это SKIP, а не тихий…, Пустой эпизод — это отсутствие данных, а не неприменимость требования., При отказе NWS руль мёртв, ось держится дифференциальным торможением → ±5 м… (+19 more)

### Community 28 - "test_ppo.py"
Cohesion: 0.11
Nodes (25): PPOConfig, Any, device, PPO-тренер + многокомпонентный loss для NPGS (план §11). `L = L_ppo +…, Плоский буфер одного env: obs-окна, сырые действия, logp/value/reward/done., RolloutBuffer, Оффлайн-прогон цикла PPO на поданной среде (без стенда) — для тестов/отладки., smoke_train() (+17 more)

### Community 29 - "IcsEngagement"
Cohesion: 0.06
Nodes (22): ControlModeState, IcsEngagement, Автомат включения. `step(inputs)` вызывается каждый такт до формирования…, Полный сброс — новый эпизод начинается с невключённого состояния., Сообщить автомату, что кадр **фактически ушёл** на стенд. Вызывается…, Подхватить уже включённый извне пробег: шлём `ControlMode = Rollout`.…, Войти в пробег самостоятельно: шлём `ControlMode = Rollout`. Это же — передача…, Перейти `Approach → Landing` без нового рукопожатия. Закон остаётся воздушным. (+14 more)

### Community 30 - "XPlaneConnectX"
Cohesion: 0.08
Nodes (12): XPlaneConnectX class initialization. Args: ip (str, optional): IP address where…, Starts a recording of the subscribed DataRefs into self.recorded_data. Data is…, Synchronize measurements from multiple sensors to a common frequency.…, Gets the current value of a DataRef. This is only intended for one-time use.…, Permanently subscribe to a list of DataRefs with a certain frequency. This is…, Writes a value to the specified DataRef provided that the DataRef is writable.…, Sends simulator commands to the simulator. These are not commands for the…, Sets the global position of airplanes as well as their attitude. Note that this… (+4 more)

### Community 31 - "fakes.py"
Cohesion: 0.10
Nodes (23): ICSBenchConnector, get_aircraft_profile(), find_earth_nav_dat(), get_runway_profile(), ILSStation, parse_ils_station(), Path, Профили ВПП и разрешение ILS из установленной базы X-Plane. (+15 more)

### Community 32 - "test_splits.py"
Cohesion: 0.11
Nodes (27): _as_dict(), contract_for(), Any, Контракт воспроизводимости эпизода (шаг 6). Заимствовано из…, Сколько раз прогнать сценарий, чтобы результат приёмки что-то значил., Худшая реплика по заданной метрике. Приёмка смотрит именно на худшую, а не на…, Источники случайности на стороне стенда, активные при данных условиях. Мы…, Что в эпизоде детерминировано, что нет, и сколько реплик из-за этого нужно. (+19 more)

### Community 33 - "Graphify Pipeline"
Cohesion: 0.08
Nodes (29): Folder Watcher, URL Ingestion, Extra Graph Exports, MCP Graph Server, Confidence Audit Trail, Deterministic Node IDs, Semantic Extraction Contract, Cross-Repository Graph Merge (+21 more)

### Community 34 - "XPlaneConnector"
Cohesion: 0.09
Nodes (9): DataRefSample, Неблокирующий UDP-клиент нативного протокола X-Plane 12., Discard pre-reload values so readiness cannot use stale telemetry., Одна подписка, один поток приёма и явное освобождение ресурсов., Send basic controls to the ego aircraft. There are hundreds of DataRefs that…, Разобрать пакет; публично для детерминированных mock-тестов., Совместимое read-only представление старого XPlaneConnectX., Совместимость с прежним клиентом. (+1 more)

### Community 35 - "ControllingSystem"
Cohesion: 0.05
Nodes (44): ControllingSystem, FailureMode, Связать сценарий с контуром; PID активируются после определения участка., Обновить параметры геометрического наведения латерального канала. Имя сохранено…, Веса влияния каналов (актор, §6): множители к выходам каналов. 1.0 = классика., Прервать заход с названной причиной. → True (управлять больше нечем)., Реверс убран: команды обратной тяги нулевые. В воздухе реверс не выдаётся…, Три блока: speed controller → guidance → allocator. (+36 more)

### Community 36 - "Scenario"
Cohesion: 0.17
Nodes (14): match_conditions(), _profile_name(), FlightSegment, WeatherState, Полный профильный сценарий APPROACH → ROLLOUT → TAXI., Условия пробега для report/eval-кода, работающего только на земле., Scenario, scenario_distance() (+6 more)

### Community 37 - "test_ics_engagement.py"
Cohesion: 0.10
Nodes (46): _Clock, _engine(), _pump(), Автомат включения управления на стенде. Два раздельных предмета проверки: *…, По ICD стенд должен два секунды ПОЛУЧАТЬ ModeAIReady=1. Если считать одно лишь…, Обратная защита: 30 кадров можно выпалить за 0.1 с — время тоже обязано пройти., Срыв предусловия обнуляет и время, и счётчик кадров., Требование ICD — непрерывность: пропуск готовности рвёт серию. (+38 more)

### Community 38 - "test_diagnostic_tools.py"
Cohesion: 0.20
Nodes (19): build_altitude_sweep(), command_for_pulse(), Безопасные elevator/altitude authority sweep без дублирования ICS runner., Чистое преобразование, пригодное и для dry-run, и для ICSSim., safety_reason(), SweepLimits, SweepPulse, validate_pulse() (+11 more)

### Community 39 - "FakeConnector"
Cohesion: 0.10
Nodes (22): FakeConnector, make_ics_inputs(), Статический стенд: всегда один и тот же кадр, отправленное — в `sent_outputs`., Полный пакет стенда: нули по умолчанию + заданные поля., Стенд шлёт узлы, футы, фут/мин и град/с — граница пересчёта в СИ проходит в…, `Visibility` в футах. Без пересчёта 16000 футов читались бы как «ясно» вместо…, test_telemetry_conversions_match_the_documented_input_units(), test_visibility_is_converted_from_feet() (+14 more)

### Community 40 - "pid_controller.py"
Cohesion: 0.09
Nodes (24): Exact package port of the ICS approach contour validated in ``aviacia_v2``. The…, clamp(), ClearWeatherILSController, ControllerConfig, ControlResult, PID, PIDConfig, Path (+16 more)

### Community 41 - "system.py"
Cohesion: 0.08
Nodes (32): Профили преобразования команд ИСМПУ в органы управления X-Plane., Расширение реестра будущим профилем МС-21 без правки XPlaneSim., register_aircraft_profile(), Глобальные константы контура управления (перенесены из main.ipynb)., Константы интерфейса стенда заказчика (ПИВ / ICS). Единый источник правды по…, Приёмочные пороги из ТЗ (раздел 5). Единый источник истины для reward-шейпинга…, Каналы управления и общий вектор команд. `ControlsState` — разделяемая по…, Участки полёта и переходы между ними. Управление ведётся на всём интервале — от… (+24 more)

### Community 42 - "NPGS"
Cohesion: 0.13
Nodes (15): floating, NPGS, float32, NDArray, Tensor, Neural PID Gain Scheduler: общий энкодер + головы актора (абс. gain'ы) + голова…, → (mean (B,17), value (B,), phase_logits (B,n_phases))., 17 сырых выходов → [абс. gains×15, w_lon, w_lat] (layout `REGULATOR_ORDER` +… (+7 more)

### Community 43 - "ICSInputs"
Cohesion: 0.13
Nodes (29): ControlResult, Касание: обжата **любая основная** стойка. Носовая не участвует — она…, ICSInputs, ICSOutputs, Неизвестные поля исходного JSON; они доступны аудиту, но не закону управления., airborne_control_mode(), airborne_flare_mode(), deactivate() (+21 more)

### Community 44 - "action.py"
Cohesion: 0.27
Nodes (11): action_high(), action_low(), float32, NDArray, Применение абсолютных коэффициентов PID, выданных NPGS. Действие: вектор…, reference_action(), GainSpace, SimInterface (+3 more)

### Community 45 - "3. Этапы реализации"
Cohesion: 0.09
Nodes (21): 1. Подтверждённые проблемы и целевое состояние, 2. Ключевые интерфейсы, 3. Этапы реализации, 4. Тестирование и критерии готовности, 5. Зафиксированные допущения, 6.1. Один dashboard вместо двух, 6.2. Единый источник данных, 6.3. Представления (+13 more)

### Community 46 - "ScenarioGenerator"
Cohesion: 0.11
Nodes (15): FlightSegment, Enum, str, Канонические участки управляемого интервала полёта., Участок, для которого выбираются закон управления и условия сценария., Генератор сценариев обучения (domain randomization). Сэмплирует `Scenario` из…, Один случайный сценарий. `difficulty=None` → случайная сложность., Фиксированный приёмочный набор (детерминированный, без RNG). (+7 more)

### Community 47 - "EngagementInputs"
Cohesion: 0.17
Nodes (11): FlightPhase, Фаза полёта, сообщаемая стендом (`ICSInputs.FlightPhase`)., Типизированные backend-расширения общего SI-кадра., TelemetryExtensions, EngagementInputs, EngagementState, Enum, Автомат включения управления на стенде заказчика. Стенд принимает наши команды… (+3 more)

### Community 48 - "RunRecorder"
Cohesion: 0.16
Nodes (11): default_runs_root(), gains_snapshot(), Path, Единый CSV-регистратор прогонов ICS и X-Plane., Единый каталог прогонов, не зависящий от cwd процесса/Jupyter., Один раз сохранить накопленные кадры и итоговые артефакты прогона., RunRecorder, test_recorder_keeps_all_known_ics_fields_and_unknown_raw_fields() (+3 more)

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
Cohesion: 0.09
Nodes (17): above_decision_height(), at_lateral_alignment_gate(), ils_blocker(), in_terminal_window(), Последние футы перед касанием, где прерывать заход опаснее, чем доработать.…, ВС выше высоты решения ухода на второй круг (30 м по ТЗ 5.1.1.2). → уход…, Полоса подхода к гейту совмещения с осью ± 5 м: `(30 м, 30 м + band]`. Только в…, Почему нельзя продолжать заход по этому кадру. `None` — можно. Закон читает… (+9 more)

### Community 54 - "gui/dashboard.py"
Cohesion: 0.24
Nodes (8): _jsonable(), Unified local dashboard for the three airborne and five ground PIDs., ViewSpec, controller_pids(), _jsonable(), pid_operating_points(), Value/setpoint pairs in the native units used by every regulator., Зафиксировать снимок кадра в памяти без файлового I/O.

### Community 55 - "RunwayTracker"
Cohesion: 0.16
Nodes (9): Возвращает отклонение от осевой линии в метрах. >0 - правее оси, <0 - левее., Геодезическое наведение на ось ВПП с упреждением по скорости., RunwayTracker, GainSpace, test_guidance_on_centerline_small_heading_error(), test_xte_sign_left_is_negative(), test_xte_sign_right_is_positive(), test_xte_zero_at_runway_start() (+1 more)

### Community 56 - "RomanLogImporter"
Cohesion: 0.19
Nodes (10): _number(), Path, Импорт и проверка внешних CSV-прогонов roman_aviacia_ics., Потоково нормализует основной и authority CSV Романа., RomanLogImporter, verify_manifest(), fixture, roman_csv() (+2 more)

### Community 57 - "working_ics/approach_criteria.py"
Cohesion: 0.21
Nodes (7): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, ICSInputs, Evaluate the A.1.1 approach segment and stop at a radio-altitude floor.

### Community 58 - "test_refactoring_contracts.py"
Cohesion: 0.12
Nodes (11): Any, Serialize only the canonical profile-aware schema v2., test_battery_covers_key_cases_and_roundtrips(), test_generator_samples_are_valid_and_serializable(), test_preset_roundtrips_through_dict(), DatagramSocket, test_legacy_subscription_starts_at_zero_and_retries_with_diagnostics(), test_production_cli_uses_the_unified_runtime_without_working_ics() (+3 more)

### Community 59 - ".send_outputs"
Cohesion: 0.33
Nodes (5): _integrate_throttle(), Ход рычага РУД за такт: интеграл команды-скорости, зажатый физическим…, Доля обратной тяги по фактическому углу РУД: 0 в положительном секторе, 1 на…, Замедление считается по **фактическому** углу РУД, а не по команде. Тягой…, _reverse_fraction()

### Community 60 - "gain_space_for"
Cohesion: 0.42
Nodes (8): gain_space_for(), Профильные пространства абсолютных PID-коэффициентов NPGS., test_every_profile_preset_gain_is_inside_its_band(), test_normalization_endpoints_and_nonpositive_guard(), test_profile_spaces_have_stable_17_action_contract_and_independent_identity(), test_snapshot_is_serializable_profile_bound_and_exactly_checked(), test_transform_roundtrip_and_default_bias(), _vector()

### Community 61 - "ReferenceTrajectory"
Cohesion: 0.11
Nodes (14): CompletionRule, LongitudinalChannel, Блок 1: скорость → симметричная база тормозов и реверса., Сбросить PID и привязать начало профиля к фактической скорости касания/старта., Генератор эталонной кривой скорости (Колокол Гаусса)., Начать профиль с фактической скорости текущего участка., То же без лишнего round-trip м/с → узлы → м/с на касании., Возвращает идеальную скорость (м/с) для текущей точки пути. (+6 more)

### Community 62 - "Project Dependencies"
Cohesion: 0.18
Nodes (13): Autonomous Landing Controller, Repository Guidance for Codex, Autonomous Landing Controller, Repository Guidance for Claude Code, Neural Landing Implementation Plan, Unified Scenario System, Optional Gymnasium, NumPy (+5 more)

### Community 63 - "test_full_flight.py"
Cohesion: 0.07
Nodes (47): IntFlag, ControlValid, Биты `ControlValidMask`: какие каналы несёт команда. **Один бит на одно…, initial_segment(), is_airborne(), FlightSegment, Сообщает ли стенд, что ВС в воздухе и достаточно высоко для приёма захода.…, С какого участка начинать. Пробег — ответ по умолчанию (см. модуль). (+39 more)

### Community 64 - "GuidanceState"
Cohesion: 0.29
Nodes (3): GuidanceState, Совместимость с прежним атрибутом; новый термин явно указывает ось., Совместимость со старым словарным API.

### Community 66 - "test_dashboard.py"
Cohesion: 0.21
Nodes (6): DashboardServer, main(), configured_controller(), test_capture_export_and_replay_common_run(), test_dashboard_http_api_is_local_and_monitor_only(), test_monitor_only_and_npgs_tuning_locks()

### Community 67 - "test_rollout_env.py"
Cohesion: 0.09
Nodes (32): compute_reward(), excess(), graded(), Считает компоненты и суммарный reward. Все компоненты ≥ 0; reward = −Σ…, Чистый hinge: превышение допуска, нормированное на допуск. Внутри допуска = 0., Штраф с гейтом ТЗ: мягкий линейный наклон внутри допуска + резкий рост за…, Допуск по оси ВПП для текущей фазы: пробег ±3 м, руление ±1 м (ТЗ 5.1.3.1)., xte_limit_for() (+24 more)

### Community 68 - "test_working_ics_dashboard.py"
Cohesion: 0.35
Nodes (10): ClearWeatherILSController, DashboardState, _controller(), _inputs(), Characterization tests for the bench-validated ``working_ics`` dashboard., _record(), test_dashboard_records_four_airborne_views_and_diagnostics(), test_gain_updates_are_immediate_validated_and_share_pitch_with_flare() (+2 more)

### Community 70 - "admit_checkpoint"
Cohesion: 0.16
Nodes (18): admit_checkpoint(), Пропускать ли чекпоинт дальше. Отсутствующая/нечисловая метрика = отказ.…, _battery(), Отсутствующая метрика = отказ, а не «нет данных — значит нет проблемы»., Формально в допуске, но авторитет исчерпан — режим держится на грани., Если сеть не бьёт классику, она не окупается — выпускать её нечего., Канал не двигался за эпизод → p95 = None. Это не дефект., Отрицательный результат должен быть виден в отчёте, а не спрятан. (+10 more)

### Community 71 - "Unified Profile-Aware Scenario System"
Cohesion: 0.22
Nodes (9): Technical-Specification Acceptance Gates, Bench-Validated ILS Approach Channel, Forward-Only Flight Segment Supervisor, Tolerance-Gated Go-Around, Longitudinal and Lateral Ground Channels, PID Run Matrix, Unified Profile-Aware Scenario System, Legacy Scenario Preset Model (+1 more)

### Community 72 - "Interactive PID Dashboard"
Cohesion: 0.25
Nodes (9): Nine-View PID Dashboard, Run Recording Artifacts, buildTabs, draw, Gain Tuning and Snapshot Export, Interactive PID Dashboard, refresh, render (+1 more)

### Community 73 - "FailureMode"
Cohesion: 0.17
Nodes (12): cases_for_segment(), _kts(), MatrixCase, MatrixCondition, Матрица прогонов для настройки базовых ПИД-регуляторов. Машиночитаемая форма…, Один шифр матрицы — вариант отказа/режима, под который настраивается набор…, Шифры одного участка: `approach` / `rollout` / `taxi` / `through`., Матрица задаёт ветер в м/с, телеметрия приходит в узлах. (+4 more)

### Community 74 - "DashboardState"
Cohesion: 0.19
Nodes (4): DashboardServer, DashboardState, Any, ICSInputs

### Community 75 - "splits.py"
Cohesion: 0.09
Nodes (25): has_holdout_failure(), _hash_unit(), holdout_reason(), is_marked_holdout(), is_signature_holdout(), PartitionedScenarioProvider, Детерминированное разбиение сценариев на обучение и holdout (шаг 6). Схема…, SHA-256 от идентификатора → число в [0, 1). Стабильно между запусками и… (+17 more)

### Community 76 - "ICSInterface.cs"
Cohesion: 0.36
Nodes (7): External.Systems.ICS, ControlModeState, GearState, ICSInputs, ICSOutputs, ReverseEngineType, UInt64

### Community 77 - "LandingFlapConfiguration"
Cohesion: 0.26
Nodes (13): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+5 more)

### Community 78 - "PretrainRunConfig"
Cohesion: 0.25
Nodes (11): ground_cases(), Шифры, у которых настраиваются коэффициенты **пробега** (пригодны для SFT).…, build_scenarios(), matrix_preset_names(), PretrainRunConfig, Имена наземных пресетов матрицы прогонов (пригодных для SFT) в порядке матрицы.…, Список сценариев для захвата: отобранные пресеты × повторные прогоны., Пресеты для захвата по конфигурации, с явным отчётом о том, что отброшено. (+3 more)

### Community 79 - "VlaydRolloutBridge"
Cohesion: 0.25
Nodes (7): ICSInputs, socket, Hand the validated airborne session to Vlayd's existing rollout loop. The…, Keep Vlayd's engagement latch synchronized during the approach., Run Vlayd's rollout until taxi speed, then send its taxi handoff., VlaydRolloutBridge, test_rollout_bridge_preserves_engagement_and_switches_without_off()

### Community 80 - "ICS PID Monitor"
Cohesion: 0.29
Nodes (7): buildControls, draw, formatTime, Four-Loop PID Tuning, ICS PID Monitor, Live and Historical Timeline, refresh

### Community 81 - "ics_connector.py"
Cohesion: 0.11
Nodes (14): IntEnum, ControlModeState, GearState, ICSBenchConnector, main(), UDP-мост к стенду заказчика (порт 3030) — транспорт пути поставки. `ICSInputs`…, Отправка best-effort со счётчиком ошибок и разрежённым логом. Windows отдаёт…, → True если отправлено. Исключение наружу не выпускается. (+6 more)

### Community 82 - "ICS UDP JSON Protocol"
Cohesion: 0.33
Nodes (6): Fourteen-Bit ControlValidMask Layout, Dual-Backend SimInterface, Two-Factor ICS Engagement Handshake, ICS UDP JSON Protocol, Telemetry SI Unit Boundary, ICS-Only Backend Guidance

### Community 83 - "X-Plane Dashboard and Runtime Guide"
Cohesion: 0.60
Nodes (6): Aircraft-Profile Checkpoint Isolation, Live A330 Acceptance Checklist, Profile-Aware Flight Scenarios, X-Plane Dashboard and Runtime Guide, X-Plane Resettable Runtime, X-Plane Training and Evaluation Backend

### Community 84 - "config/approach.py"
Cohesion: 0.22
Nodes (7): _pid_from_colleague(), Настройки воздушного участка: заход по ILS, выравнивание, управление скоростью.…, Загрузка настроек из JSON коллеги (`config/ics_clear_weather_pid.json`). Секции…, `PIDConfig` коллеги → аргументы нашего `PIDController`. Предел интегратора у…, Path, Наши умолчания и его файл — одно и то же. Разойдутся — расхождение должно быть…, test_config_from_the_colleague_json_matches_our_defaults()

### Community 85 - ".neutralize_airborne"
Cohesion: 0.33
Nodes (3): Обнуляет все органы управления. Отправку делает вызывающий через `ICSSim.step`.…, Сброс к нейтральным командам — новый эпизод начинается с чистого состояния.…, Обнулить только воздушные команды. Нужно, когда воздушный канал не может…

### Community 86 - "DashboardState"
Cohesion: 0.12
Nodes (11): DashboardState, _finite_or_none(), GainUpdateRequest, _handler_factory(), Path, Валидировать HTTP-запрос и передать запись control-потоку., Применяется только control-потоком в начале такта., Thread-safe live state or an immutable CSV replay. (+3 more)

### Community 87 - "test_profiled_scenarios.py"
Cohesion: 0.28
Nodes (6): compose_scenario(), Собрать сценарий из независимых источников участков., Contracts of the unified aircraft-profiled scenario model., test_composition_keeps_repeated_failures_as_one_set_member(), test_composition_selects_each_phase_and_preserves_provenance(), test_external_profile_controls_survive_scenario_v2_roundtrip()

### Community 88 - "FrictionProfile"
Cohesion: 0.13
Nodes (8): FrictionProfile, Any, Собирает ветер из компонент относительно курса ВПП. `crosswind_kts` > 0 — ветер…, Сериализация в примитивы (для логирования/воспроизводимости сценариев)., Ступенчатый профиль сцепления по дистанции пробега., test_scenario_roundtrip_with_weather_and_failures(), test_weather_roundtrips_through_dict(), test_weatherstate_from_crosswind()

### Community 89 - "test_approach_channel.py"
Cohesion: 0.08
Nodes (33): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+25 more)

### Community 90 - ".guidance"
Cohesion: 0.25
Nodes (3): Решить прямую геодезическую задачу на сферической Земле., Геодезическое guidance в истинной системе направлений., Guidance по курсу ВПП и измеренному отклонению — без собственной геодезии.…

### Community 91 - "test_action_contract.py"
Cohesion: 0.08
Nodes (35): ControlArchitecture, Фиксированный порядок слоёв и роль обучаемого компонента., Проверяет контракт обучаемого слоя. Нарушение → `ValueError` на старте…, validate_action_contract(), apply_corrections(), decode(), ArrayLike, GainMap (+27 more)

### Community 92 - "PresetPolicy"
Cohesion: 0.29
Nodes (5): PresetPolicy, Baseline 2 («оракул»): коэффициенты пресета сценария = классика, под которую он…, _scripted_env(), test_compare_policies_flags_which_baseline_each_policy_beats(), test_run_episode_produces_criteria_and_diagnostics()

### Community 93 - "rollout_env.py"
Cohesion: 0.16
Nodes (17): Профильное пространство абсолютных PID-коэффициентов NPGS., ObservationBuilder, ObserverEstimate, Observation Space — сборка и нормировка вектора состояния (§5). Собирает один…, Оценки PINN-обсервера (§12). Заглушка нулями до Этапа 7., Строит нормированный вектор наблюдения одного кадра., RewardWeights, EpisodeInfo (+9 more)

### Community 95 - "reward.py"
Cohesion: 0.08
Nodes (29): _command_jerk(), _component(), _effort_saturated(), EpisodeObjective, _ground_steering(), ObjectiveWeights, _p95(), TypedDict (+21 more)

### Community 99 - "Criterion"
Cohesion: 0.29
Nodes (6): _check(), Criterion, Один пункт ТЗ: предел, измеренное значение, вердикт и его причина., Строит вердикт. Неприменимо → SKIP; применимо, но данных нет → FAIL., Итог эпизода: FAIL, если провален хоть один применимый критерий., verdict_of()

### Community 111 - "Q: Реализовать этап 0: baseline, golden replay и dashboard characterization"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Реализовать этап 0: baseline, golden replay и dashboard characterization, Source Nodes

### Community 112 - "Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md)., Source Nodes

### Community 113 - "decode_outputs"
Cohesion: 0.29
Nodes (6): decode_outputs(), Отправленные команды в нормированном виде — для сравнения траекторий.…, `ICSOutputs` → (brake_l, brake_r, thr_l_rate, thr_r_rate, steer), всё…, NWS_FAIL отключает стойку/педаль, но оставляет руль и дифференциальные органы., test_control_step_emits_five_bounded_commands(), test_nws_fail_preset_injects_failure()

### Community 114 - "normalization.py"
Cohesion: 0.15
Nodes (14): clip_unit(), linear(), log_norm(), Фиксированная нормализация Observation Space — единый контракт train ↔ deploy.…, Лог-нормировка неотрицательной величины (видимость): log1p(x)/log1p(scale)., Отображает [lo, hi] → [-1, 1] (для PID output по его границам)., Сериализуемый слепок контракта нормировки (сохраняется вместе с весами).…, snapshot() (+6 more)

### Community 115 - "test_ics_sim.py"
Cohesion: 0.05
Nodes (45): select_for_telemetry(), engaged_sim(), (sim, connector) с завершённым рукопожатием: стенд подтвердил `AgentIsActive =…, Регресс: расширение структуры не должно протащить руль высоты в маску пробега., test_ground_frame_still_declares_only_the_ground_channels(), _cold_sim(), Тесты стенда (`ICSSim`), подбора сценария и генератора — без реального стенда., Разделение органов из таблицы Заказчика: тиллер — на рулении, педальный пост —… (+37 more)

### Community 116 - "Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)., Source Nodes

### Community 123 - "test_control_parity.py"
Cohesion: 0.22
Nodes (8): Тесты паритета после выноса контура из main.ipynb в пакет ismpu. Полный паритет…, test_control_step_stops_and_sends_nothing_on_missing_telemetry(), test_default_preset_leaves_all_actuators_healthy(), test_pid_anti_windup_clamp(), test_pid_filtered_derivative(), test_pid_output_clamped_to_bounds(), test_pid_proportional_and_integral_accumulation(), test_pid_zero_dt_returns_zero()

### Community 125 - ".begin_flight"
Cohesion: 0.12
Nodes (13): approach_blocker(), ApproachRefused, Воздушный участок начинать нельзя — с названной причиной. Отдельное исключение,…, Можно ли вообще судить об участке по этому кадру. Кадр без пакета стенда…, Почему нельзя вести заход по этому кадру. `None` — можно. Пока проверка одна,…, segment_is_decidable(), FlightSegment, Пересобрать stateful PID и уведомить backend до первого такта участка. (+5 more)

### Community 126 - ".compute"
Cohesion: 0.20
Nodes (4): → (интеграл только с утечкой, интеграл с утечкой и приращением). Оба уже зажаты., Такт регулятора. `measurement` обязателен при `derivative_on_measurement=True`., Back-calculation: подтянуть интегратор к фактически применённой команде. No-op…, Вес апериодического фильтра D-составляющей за такт `dt`.

### Community 129 - "on_ground"
Cohesion: 0.15
Nodes (12): Кадр «связи со стендом нет». Нули, а не None: контур проверяет `valid` первым., on_ground(), Кадр «ВС на полосе»: обжаты все стойки, курс/координаты у порога UUEE 06R., Стенд при обрыве связи отдаёт НУЛИ с valid=False, а не None. Проверка «поле is…, test_control_step_stops_on_invalid_frame_even_with_numeric_fields(), Пресет — стартовое предположение; фактическую конфигурацию сообщает борт., Отказ может быть снят — накапливающий учёт держал бы орган мёртвым до конца…, Единичный таймаут — не повод вернуть рулю авторитет, которого у него нет. (+4 more)

### Community 130 - "HandshakeBench"
Cohesion: 0.25
Nodes (4): HandshakeBench, KinematicBench, Стенд, включающий управление только после корректного рукопожатия. Ждёт…, Мини-модель стенда: замедление ~ команде тормоза/реверса, ход вдоль осевой ВПП.…

### Community 131 - "regulators.py"
Cohesion: 0.15
Nodes (10): Канонический порядок регуляторов, размерности действия и **контракт обучаемого…, Один регулятор, коэффициенты которого (kp/ki/kd) разрешено настраивать сети., RegulatorSpec, PIDDiagnostics, Пропорционально-интегрально-дифференциальный регулятор. Класс сохраняет прежнюю…, Типизированный снимок последнего такта регулятора., apply_ground_control(), build_pids() (+2 more)

### Community 133 - ".as_dict"
Cohesion: 0.33
Nodes (3): Сколько уже держится выдержка. 0.0, если отсчёт не идёт (для диагностики)., Почему включение ещё не произошло — для диагностики при таймауте прогрева.…, Слепок для логов и отчётов приёмки.

### Community 135 - "Q: Приступай к выполнению этапа 2 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 2 плана docs/plan.md, Source Nodes

### Community 136 - "_faults_from_inputs"
Cohesion: 0.40
Nodes (4): _faults_from_inputs(), ICSInputs, Отказы, о которых сообщает борт — **единственный** источник истины об отказах.…, Сигналы отказов со стенда → наши `FailureMode`. Отказы шасси…

## Ambiguous Edges - Review These
- `Unified Profile-Aware Scenario System` → `Legacy Scenario Preset Model`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to
- `Dual-Backend SimInterface` → `ICS-Only Backend Guidance`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **61 isolated node(s):** `Answer`, `Outcome`, `Source Nodes`, `ismpu`, `Answer` (+56 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **49 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `LateralChannel` (2× useful, score=1.976957493)
- `RunRecorder` (2× useful, score=1.976957493)
- `ControllingSystem` (2× useful, score=1.976489101) _(code changed — re-verify)_
- `ObservationBuilder` (2× useful, score=1.956921212)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Unified Profile-Aware Scenario System` and `Legacy Scenario Preset Model`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Dual-Backend SimInterface` and `ICS-Only Backend Guidance`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `ControllingSystem` connect `ControllingSystem` to `on_ground`, `train.py`, `regulators.py`, `json_config.py`, `SimInterface`, `test_pretrain.py`, `scenarios.py`, `test_run_matrix.py`, `ApproachController`, `Telemetry`, `PIDController`, `evaluate.py`, `RolloutEnv`, `test_xplane_backend.py`, `test_evaluate.py`, `test_ppo.py`, `Scenario`, `FakeConnector`, `pid_controller.py`, `system.py`, `action.py`, `RunRecorder`, `_Clock`, `test_go_around.py`, `test_approach_criteria.py`, `._approach_step`, `test_refactoring_contracts.py`, `ReferenceTrajectory`, `test_full_flight.py`, `test_dashboard.py`, `test_rollout_env.py`, `PretrainRunConfig`, `VlaydRolloutBridge`, `DashboardState`, `test_action_contract.py`, `PresetPolicy`, `rollout_env.py`, `reward.py`, `Criterion`, `decode_outputs`, `test_ics_sim.py`, `test_control_parity.py`, `.begin_flight`?**
  _High betweenness centrality (0.168) - this node is a cross-community bridge._
- **Why does `Telemetry` connect `Telemetry` to `test_tolerance.py`, `on_ground`, `HandshakeBench`, `test_icd_units.py`, `json_config.py`, `SimInterface`, `ControlsState`, `_faults_from_inputs`, `ScriptedFlightBench`, `ground_allocator.py`, `LateralChannel`, `scenarios.py`, `ICSSim`, `ApproachController`, `XPlaneSim`, `RolloutEnv`, `test_xplane_backend.py`, `IcsEngagement`, `fakes.py`, `ControllingSystem`, `Scenario`, `test_diagnostic_tools.py`, `FakeConnector`, `pid_controller.py`, `system.py`, `ICSInputs`, `EngagementInputs`, `RunRecorder`, `_Clock`, `test_go_around.py`, `test_approach_criteria.py`, `._approach_step`, `ReferenceTrajectory`, `test_full_flight.py`, `test_rollout_env.py`, `VlaydRolloutBridge`, `test_approach_channel.py`, `rollout_env.py`, `normalization.py`, `test_ics_sim.py`, `test_control_parity.py`, `.begin_flight`?**
  _High betweenness centrality (0.131) - this node is a cross-community bridge._
- **Why does `ControlsState` connect `ControlsState` to `GainSpace`, `ground_allocator.py`, `scenarios.py`, `AircraftProfile`, `ApproachController`, `Telemetry`, `PIDController`, `RolloutEnv`, `test_xplane_backend.py`, `test_diagnostic_tools.py`, `FakeConnector`, `pid_controller.py`, `system.py`, `ICSInputs`, `ReferenceTrajectory`, `test_rollout_env.py`, `VlaydRolloutBridge`, `.neutralize_airborne`, `test_approach_channel.py`, `test_action_contract.py`, `rollout_env.py`, `reward.py`, `test_ics_sim.py`, `.rudder_cmd`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `ControllingSystem` (e.g. with `AircraftControlSet` and `ApproachSetup`) actually correct?**
  _`ControllingSystem` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `Telemetry` (e.g. with `AircraftControlSet` and `ApproachSetup`) actually correct?**
  _`Telemetry` has 46 INFERRED edges - model-reasoned connections that need verification._