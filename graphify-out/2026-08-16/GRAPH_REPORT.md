# Graph Report - GOSNIIASProject  (2026-08-16)

## Corpus Check
- 156 files · ~182,878 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2977 nodes · 6887 edges · 198 communities (130 shown, 68 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 481 edges (avg confidence: 0.61)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `716d4f4e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- criticality.py
- GainCommand
- .step
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
- ics_connector.py
- test_run_matrix.py
- AircraftProfile
- ics_sim.py
- ApproachController
- system.py
- weather.py
- XPlaneSim
- segments.py
- PIDController
- evaluate.py
- DashboardState
- .from_preset
- test_evaluate.py
- RolloutEnv
- IcsEngagement
- XPlaneConnectX
- RunRecorder
- test_splits.py
- Graphify Pipeline
- XPlaneConnector
- telemetry
- test_full_flight.py
- test_ics_engagement.py
- run_reader.py
- sft.py
- pid_controller.py
- fakes.py
- NPGS
- ICSInputs
- test_gain_scheduler.py
- 3. Этапы реализации
- ScenarioGenerator
- test_profiled_scenarios.py
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
- runtime/pretrain.py
- gain_space_for
- test_control_parity.py
- Project Dependencies
- ControllingSystem
- PidGainRegressor
- ICSInputs
- dashboard_core.py
- test_tolerance.py
- test_working_ics_dashboard.py
- ICSOutputs
- Telemetry
- Unified Profile-Aware Scenario System
- Interactive PID Dashboard
- run_matrix.py
- DashboardState
- splits.py
- ICSInterface.cs
- test_rollout_env.py
- PretrainRunConfig
- promote_candidate.py
- ICS PID Monitor
- rollout_bridge.py
- ICS UDP JSON Protocol
- X-Plane Dashboard and Runtime Guide
- test_working_ics_golden.py
- EpisodeObjective
- run_report.py
- scenarios.py
- import_workbook
- test_approach_channel.py
- LongitudinalDiagnostics
- shield.py
- static_sim
- ICSSim
- xplane_sim.py
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
- test_sft_regressors.py
- .from_json
- GuidanceState
- .compute
- RunReader
- WeatherState
- Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md).
- Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md).
- pid.py
- RolloutBuffer
- gain_scheduler.py
- EngagementInputs
- Q: Приступай к выполнению этапа 2 плана docs/plan.md
- ICSInputs
- verdict_of
- compute_reward
- ApproachConfig
- FailureMode
- .rudder_cmd
- LandingFlapConfiguration
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
- Normalization
- runway_profiles.py
- Scenario
- Path
- Q: Приступай к выполнению этапа 4 плана docs/plan.md
- ReferenceTrajectory
- RewardWeights
- TypedDict
- Scenario
- protocol.py
- aircraft_profiles.py
- decode
- DashboardServer
- Q: Приступай к выполнению этапа 8 плана [plan.md](docs/plan.md).
- ApproachSetup
- .airborne_commands
- ICSInputs
- apply_gains_to_pids
- Scenario
- ConditionMatch
- .from_ics
- ._should_go_around
- TouchdownSetup
- ApproachController
- ControllingSystem
- render_report
- ApproachLimits
- Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md).
- ApproachTelemetry
- FlightSegment
- NPGS
- AircraftProfile
- Any
- ApproachConfig
- FailureMode
- FlightSegment
- WeatherState
- StartMode
- ndarray
- ControllingSystem
- Path
- PretrainConfig
- SimInterface
- RunRecorder

## God Nodes (most connected - your core abstractions)
1. `ControllingSystem` - 160 edges
2. `ControlsState` - 92 edges
3. `Telemetry` - 87 edges
4. `Scenario` - 70 edges
5. `ICSSim` - 70 edges
6. `XPlaneSim` - 54 edges
7. `PIDController` - 50 edges
8. `GainSpace` - 47 edges
9. `airborne_inputs()` - 46 edges
10. `RolloutEnv` - 44 edges

## Surprising Connections (you probably didn't know these)
- `Autonomous Landing Controller` --semantically_similar_to--> `Autonomous Landing Controller`  [INFERRED] [semantically similar]
  CLAUDE.md → AGENTS.md
- `Profile-Aware Flight Scenarios` --semantically_similar_to--> `Unified Scenario System`  [INFERRED] [semantically similar]
  docs/XPLANE_DASHBOARD.md → implementation_plan.md
- `Acceptance and Evaluation Harness` --semantically_similar_to--> `Technical-Specification Acceptance Gates`  [INFERRED] [semantically similar]
  implementation_plan.md → AGENTS.md
- `X-Plane Resettable Runtime` --semantically_similar_to--> `X-Plane Training and Evaluation Backend`  [INFERRED] [semantically similar]
  docs/XPLANE_DASHBOARD.md → implementation_plan.md
- `_Clock` --uses--> `ControllingSystem`  [INFERRED]
  tests/test_full_flight.py → ismpu/control/system.py

## Import Cycles
- 3-file cycle: `ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/control/channels.py`
- 3-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 3-file cycle: `ismpu/config/scenarios.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
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

## Communities (198 total, 68 thin omitted)

### Community 0 - "criticality.py"
Cohesion: 0.09
Nodes (26): lateral_limit_m(), lateral_load_situation(), lateral_situation(), normal_load_situation(), IntEnum, Критерии критичности особых ситуаций МС-21 (Приложение 1 к ТЗ). Таблица АП-25…, Классификация скорости касания относительно VAPP и VВПП пред., Классификация нормальной перегрузки посадочного удара. `heavy` — взлётный вес. (+18 more)

### Community 1 - "GainCommand"
Cohesion: 0.19
Nodes (8): _clip(), GainCommand, GainMap, Что сделал Shield за такт: активированные правила, штрафы, fallback., Уровни 1–2. Возвращает `(effective_gains, safe_command, report)`.…, Выход актора: абсолютные коэффициенты PID + веса каналов. `gains[reg] =…, ShieldReport, ShieldReportSnapshot

### Community 2 - ".step"
Cohesion: 0.20
Nodes (6): ndarray, Копия команды такта — для расчёта джерка на следующем такте. Копируется…, Окно истории → тензор `(history_len, OBS_DIM)` (последовательность кадров для…, Состояние для поведенческих проверок Shield. Курс здесь — отклонение от…, _snapshot_command(), RuntimeState

### Community 3 - "test_weather.py"
Cohesion: 0.10
Nodes (21): compose_wind(), decompose_wind(), Any, Собирает ветер из компонент относительно курса ВПП. `crosswind_kts` > 0 — ветер…, Сериализация в примитивы (для логирования/воспроизводимости сценариев)., (скорость, откуда) → (crosswind, headwind) относительно курса ВПП. crosswind >…, (crosswind, headwind) → (скорость, откуда, °). Обратна `decompose_wind`., Тесты погоды: разбор ветра, шкала скользкости и чтение условий из пакета стенда. (+13 more)

### Community 4 - "Shield"
Cohesion: 0.13
Nodes (26): Наблюдаемое состояние для поведенческих проверок уровня 3., Границы и веса штрафов Shield (все — настраиваемые, а не свойства сети)., Защитный контур. Детерминирован; хранит состояние прошлого такта для rate-…, Bind the guard to the same aircraft-specific space as the actor., Уровень 3. Правит небезопасные команды и возвращает `(command, report)`., Построение из словаря коэффициентов (напр. пресета сценария)., RuntimeState, Shield (+18 more)

### Community 5 - "json_config.py"
Cohesion: 0.11
Nodes (38): approach_control_from_dict(), approach_control_to_dict(), _copy_approach(), dump_scenario(), _finite_tree(), ground_control_from_dict(), ground_control_to_dict(), _legacy_ground() (+30 more)

### Community 6 - "SimInterface"
Cohesion: 0.11
Nodes (5): BaseException, Минимальный lifecycle, одинаковый для стенда и X-Plane., SimInterface, Protocol, StartMode

### Community 7 - "airborne_inputs"
Cohesion: 0.08
Nodes (43): airborne_inputs(), Кадр «ВС на глиссаде»: стойки не обжаты, ILS валиден, скорость и высота…, _colleague_controller(), _descent_frames(), _our_channel(), Страховка от самообмана: сценарий обязан пройти выравнивание, иначе паритет его…, Угол сноса не должен превращаться в ошибку курса на локализаторе., Стенд иногда сбрасывает Valid при сохранении пригодного численного значения. (+35 more)

### Community 8 - "Scenario"
Cohesion: 0.17
Nodes (17): AircraftProfile, FailureMode, FlightSegment, match_conditions(), _profile_name(), Полный профильный сценарий APPROACH → ROLLOUT → TAXI., Условия пробега для report/eval-кода, работающего только на земле., Scenario (+9 more)

### Community 9 - "GainSpace"
Cohesion: 0.18
Nodes (9): GainKey, GainSpace, Any, ArrayLike, float64, GainMap, NDArray, RegulatorKey (+1 more)

### Community 10 - "ground_allocator.py"
Cohesion: 0.14
Nodes (15): FailureManager, FailureState, Эффективности исполнительных органов. Аннотации типов обязательны: без них…, Проецирует набор дискретных отказов в эффективности исполнительных органов., ActuatorFeedback, ActuatorVector, AllocationDiagnostics, _clamp() (+7 more)

### Community 11 - "LateralChannel"
Cohesion: 0.23
Nodes (7): GuidanceState, LateralChannel, LateralDiagnostics, Блок 2: runway guidance → единый нормированный yaw-запрос., Guidance по тому, что даёт стенд. → словарь guidance или None, если данных нет.…, Единый GuidanceState текущего кадра для control/observation/reward., RunwayTracker

### Community 12 - "test_pretrain.py"
Cohesion: 0.08
Nodes (44): _phase_labels(), pretrain_sft(), PretrainConfig, float32, GainMap, NDArray, Tensor, SFT (behavioral cloning) — предобучение NPGS предсказывать эталонные… (+36 more)

### Community 13 - "ControlsState"
Cohesion: 0.13
Nodes (27): ControlsState, Обнуляет все органы управления. Отправку делает вызывающий через `ICSSim.step`.…, Разделяемая по тактам структура команд — и наземных, и воздушных. Аннотации…, Сброс к нейтральным командам — новый эпизод начинается с чистого состояния.…, Обнулить только воздушные команды. Нужно, когда воздушный канал не может…, build_altitude_sweep(), command_for_pulse(), Безопасные elevator/altitude authority sweep без дублирования ICS runner. (+19 more)

### Community 14 - "ics_connector.py"
Cohesion: 0.07
Nodes (31): GearState, ICSBenchConnector, ICSOutputs, main(), UDP-мост к стенду заказчика (порт 3030) — транспорт пути поставки. `ICSInputs`…, Разбор телеметрии стенда с совместимостью вперёд. Асимметрия намеренная (JSON-…, Отправка best-effort со счётчиком ошибок и разрежённым логом. Windows отдаёт…, → True если отправлено. Исключение наружу не выпускается. (+23 more)

### Community 15 - "test_run_matrix.py"
Cohesion: 0.08
Nodes (31): resolve_matrix_run(), compose_matrix_scenario(), _install_through_scenarios(), matrix_battery(), Перенести накопленные overrides одного шифра на следующее условие этого же…, Собрать Б.4 из первой строки и заранее определённой пары законов., Сценарий по имени либо шифру матрицы, без различия раскладки А/B., Собрать сценарий из конкретных строк APPROACH/ROLLOUT/TAXI.… (+23 more)

### Community 16 - "AircraftProfile"
Cohesion: 0.16
Nodes (3): AircraftProfile, Общая идентичность ЛА и необязательная привязка к X-Plane. Профиль нужен и…, Command refs retained under the historical public name.

### Community 17 - "ics_sim.py"
Cohesion: 0.11
Nodes (20): IntEnum, FlightPhase, Константы интерфейса стенда заказчика (ПИВ / ICS). Единый источник правды по…, Фаза полёта, сообщаемая стендом (`ICSInputs.FlightPhase`)., ils_blocker(), in_terminal_window(), Участки полёта и переходы между ними. Управление ведётся на всём интервале — от…, Последние футы перед касанием, где прерывать заход опаснее, чем доработать.… (+12 more)

### Community 18 - "ApproachController"
Cohesion: 0.10
Nodes (28): ApproachLimits, ApproachTelemetry, ApproachConfig, Параметры воздушного контура. Значения по умолчанию — настроенные на стенде.…, angle_error_deg(), ApproachController, ApproachResult, clamp() (+20 more)

### Community 19 - "system.py"
Cohesion: 0.15
Nodes (14): Глобальные константы контура управления (перенесены из main.ipynb)., Приёмочные пороги из ТЗ (раздел 5). Единый источник истины для reward-шейпинга…, Геометрия целевой ВПП и высоты установки ЛА. Смена целевой полосы = правка…, Каналы управления и общий вектор команд. `ControlsState` — разделяемая по…, Слежение за осью ВПП: геодезия, cross-track error, guidance с look-ahead.…, Оркестратор классического контура управления — на всём интервале полёта.…, CompletionRule, Enum (+6 more)

### Community 20 - "weather.py"
Cohesion: 0.08
Nodes (26): Генератор сценариев обучения (domain randomization). Сэмплирует `Scenario` из…, Enum, Погодные условия эпизода: описание, шкала сцепления и разбор ветра. Модуль **не…, Состояние ВПП как **монотонная шкала скользкости** 0…15 (0 — сухо, 15 — лёд со…, Код состояния ВПП со стенда → наша шкала. Неизвестный код трактуется как `ICY`,…, runway_condition_from_bench(), RunwayCondition, Сверка каждого сигнала стенда с документами Заказчика. Два независимых… (+18 more)

### Community 21 - "XPlaneSim"
Cohesion: 0.07
Nodes (14): _destination(), XPlaneDiagnostics, AircraftProfile, ControlsState, FailureMode, FlightSegment, Path, RunwayProfile (+6 more)

### Community 22 - "segments.py"
Cohesion: 0.09
Nodes (27): FlightSegment, Enum, str, Канонические участки управляемого интервала полёта., Участок, для которого выбираются закон управления и условия сценария., _as_dict(), contract_for(), Any (+19 more)

### Community 23 - "PIDController"
Cohesion: 0.09
Nodes (31): PIDController, Сброс внутренних состояний (используется при выключении системы)., _legacy_reference(), Опциональная численность PID (шаг 5): каждый флаг проверяется на том дефекте,…, Если применено ровно то, что выдал PID, коррекции быть не должно., Уставка прыгает, объект стоит на месте — D-составляющая не должна реагировать.…, Выход ИЗ насыщения должен разрешаться всегда, иначе регулятор залипнет. kp…, Если насыщает уже пропорциональная часть, интегрировать нельзя вообще — и это… (+23 more)

### Community 24 - "evaluate.py"
Cohesion: 0.09
Nodes (27): compare_policies(), DefaultGainsPolicy, load_npgs_policy(), main(), NPGSPolicy, Policy, PresetPolicy, Приёмка по ТЗ (разд. 5) + обязательное сравнение с baseline'ами (Этап 5). Схема… (+19 more)

### Community 25 - "DashboardState"
Cohesion: 0.13
Nodes (7): DashboardState, GainChange, _handler_factory(), _jsonable(), Path, HTTP читает только immutable recorder objects; controller меняет control-thread., Вызывается runtime ровно в начале control tick.

### Community 26 - ".from_preset"
Cohesion: 0.09
Nodes (21): Ожидаемые физические условия одного участка., SegmentConditions, SensorNoise, test_xplane_ignores_failures_outside_rollout_contract(), DatagramSocket, MockXPlaneConnector, ScriptedXPlaneConnector, test_commands_failures_and_close_release_overrides() (+13 more)

### Community 27 - "test_evaluate.py"
Cohesion: 0.16
Nodes (27): evaluate_tz(), Диагностика эпизода + сценарий → список вердиктов по пунктам ТЗ разд. 5., _by_name(), _diagnostics(), Тесты приёмки по ТЗ (Этап 5): вердикты по пунктам, правило «нет данных = FAIL»,…, Эпизод не дошёл до руления → допуск ±1 м неприменим. Это SKIP, а не тихий…, Пустой эпизод — это отсутствие данных, а не неприменимость требования., При отказе NWS руль мёртв, ось держится дифференциальным торможением → ±5 м… (+19 more)

### Community 28 - "RolloutEnv"
Cohesion: 0.09
Nodes (36): NPGSConfig, Гиперпараметры архитектуры NPGS (замораживаются вместе с весами при поставке)., PPOConfig, PPOTrainer, Any, PPO-тренер + многокомпонентный loss для NPGS (план §11). `L = L_ppo +…, Собирает rollout из среды и обновляет NPGS многокомпонентным PPO-loss., RolloutEnv (+28 more)

### Community 29 - "IcsEngagement"
Cohesion: 0.05
Nodes (23): ControlModeState, IcsEngagement, Автомат включения. `step(inputs)` вызывается каждый такт до формирования…, Полный сброс — новый эпизод начинается с невключённого состояния., Сообщить автомату, что кадр **фактически ушёл** на стенд. Вызывается…, Подхватить уже включённый извне пробег: шлём `ControlMode = Rollout`.…, Войти в пробег самостоятельно: шлём `ControlMode = Rollout`. Это же — передача…, Перейти `Approach → Landing` без нового рукопожатия. Закон остаётся воздушным. (+15 more)

### Community 30 - "XPlaneConnectX"
Cohesion: 0.08
Nodes (13): XPlaneConnectX class initialization. Args: ip (str, optional): IP address where…, Starts a recording of the subscribed DataRefs into self.recorded_data. Data is…, Terminates the recording and returns a dictionary of lists that contain the…, Synchronize measurements from multiple sensors to a common frequency.…, Gets the current value of a DataRef. This is only intended for one-time use.…, Permanently subscribe to a list of DataRefs with a certain frequency. This is…, Writes a value to the specified DataRef provided that the DataRef is writable.…, Sends simulator commands to the simulator. These are not commands for the… (+5 more)

### Community 31 - "RunRecorder"
Cohesion: 0.17
Nodes (7): Exception, Подключить best-effort аудит сырых успешно принятых/отправленных UDP payload., Append-only writer; ошибка диска помечает прогон, но не выходит в control-loop., Атомарный incremental slice для dashboard, без чтения controller., Сохранить полный effective config; канонические config-файлы не затрагиваются., RunEvent, RunRecorder

### Community 32 - "test_splits.py"
Cohesion: 0.15
Nodes (26): assert_no_leakage(), has_holdout_failure(), Затрагивает ли сценарий зарезервированное семейство отказов., Разбивает набор сценариев. Детерминировано и устойчиво к добавлению новых…, Проверяет, что holdout не пересекается с обучением по идентификаторам. Дешёвая…, split_scenarios(), Разбиение train/holdout и контракт воспроизводимости (шаг 6). Два свойства,…, Ради этого хеш и выбран вместо shuffle(seed): иначе новый сценарий менял бы… (+18 more)

### Community 33 - "Graphify Pipeline"
Cohesion: 0.08
Nodes (29): Folder Watcher, URL Ingestion, Extra Graph Exports, MCP Graph Server, Confidence Audit Trail, Deterministic Node IDs, Semantic Extraction Contract, Cross-Repository Graph Merge (+21 more)

### Community 34 - "XPlaneConnector"
Cohesion: 0.07
Nodes (10): Discard pre-reload values so readiness cannot use stale telemetry., Одна подписка, один поток приёма и явное освобождение ресурсов., Send basic controls to the ego aircraft. There are hundreds of DataRefs that…, Разобрать пакет; публично для детерминированных mock-тестов., Совместимое read-only представление старого XPlaneConnectX., Совместимость с прежним клиентом., XPlaneConnector, DatagramSocket (+2 more)

### Community 35 - "telemetry"
Cohesion: 0.08
Nodes (28): decode_outputs(), Готовый кадр `Telemetry` для прямых вызовов `control_step(dt, telemetry,…, Отправленные команды в нормированном виде — для сравнения траекторий.…, `ICSOutputs` → (brake_l, brake_r, thr_l_rate, thr_r_rate, steer), всё…, telemetry(), NWS_FAIL отключает стойку/педаль, но оставляет руль и дифференциальные органы., test_control_step_emits_five_bounded_commands(), test_nws_fail_preset_injects_failure() (+20 more)

### Community 36 - "test_full_flight.py"
Cohesion: 0.06
Nodes (48): IntFlag, ControlValid, Биты `ControlValidMask`: какие каналы несёт команда. **Один бит на одно…, initial_segment(), is_airborne(), FlightSegment, Сообщает ли стенд, что ВС в воздухе и достаточно высоко для приёма захода.…, С какого участка начинать. Пробег — ответ по умолчанию (см. модуль). (+40 more)

### Community 37 - "test_ics_engagement.py"
Cohesion: 0.10
Nodes (47): _Clock, _engine(), _pump(), Автомат включения управления на стенде. Два раздельных предмета проверки: *…, По ICD стенд должен два секунды ПОЛУЧАТЬ ModeAIReady=1. Если считать одно лишь…, Обратная защита: 30 кадров можно выпалить за 0.1 с — время тоже обязано пройти., Срыв предусловия обнуляет и время, и счётчик кадров., Требование ICD — непрерывность: пропуск готовности рвёт серию. (+39 more)

### Community 38 - "run_reader.py"
Cohesion: 0.11
Nodes (20): Один такт: вход, команда и диагностика имеют общий ``tick_id``., RunSample, _apply_recorded_gains(), _bool_or_none(), _equal(), main(), _number(), _parse_cell() (+12 more)

### Community 39 - "sft.py"
Cohesion: 0.14
Nodes (23): GuardResult, controller_pids(), Собрать фиксированную CSV-схему без файлового I/O; используется и replay., sample_values(), apply_gain_vector(), controller_gain_vector(), _feature_value(), feature_vector() (+15 more)

### Community 40 - "pid_controller.py"
Cohesion: 0.19
Nodes (11): Exact package port of the ICS approach contour validated in ``aviacia_v2``. The…, clamp(), ClearWeatherILSController, ControllerConfig, ControlResult, PID, PIDConfig, Path (+3 more)

### Community 41 - "fakes.py"
Cohesion: 0.09
Nodes (18): decode_airborne(), flight_sim(), HandshakeBench, _integrate_throttle(), KinematicBench, Фейковый стенд для тестов: `ICSInputs` вместо реального UDP. Единственный…, Ход рычага РУД за такт: интеграл команды-скорости, зажатый физическим…, Доля обратной тяги по фактическому углу РУД: 0 в положительном секторе, 1 на… (+10 more)

### Community 42 - "NPGS"
Cohesion: 0.14
Nodes (13): floating, NPGS, Any, float32, NDArray, Tensor, Neural PID Gain Scheduler: общий энкодер + головы актора (абс. gain'ы) + голова…, → (mean (B,17), value (B,), phase_logits (B,n_phases)). (+5 more)

### Community 43 - "ICSInputs"
Cohesion: 0.13
Nodes (25): ControlResult, ICSInputs, Неизвестные поля исходного JSON; они доступны аудиту, но не закону управления., airborne_control_mode(), airborne_flare_mode(), deactivate(), live_main(), main() (+17 more)

### Community 44 - "test_gain_scheduler.py"
Cohesion: 0.12
Nodes (17): build_npgs(), device, action_high(), action_low(), float32, NDArray, reference_action(), net() (+9 more)

### Community 45 - "3. Этапы реализации"
Cohesion: 0.09
Nodes (21): 1. Подтверждённые проблемы и целевое состояние, 2. Ключевые интерфейсы, 3. Этапы реализации, 4. Тестирование и критерии готовности, 5. Зафиксированные допущения, 6.1. Один dashboard вместо двух, 6.2. Единый источник данных, 6.3. Представления (+13 more)

### Community 46 - "ScenarioGenerator"
Cohesion: 0.16
Nodes (9): Один случайный сценарий. `difficulty=None` → случайная сложность., Фиксированный приёмочный набор (детерминированный, без RNG)., ScenarioGenerator, test_battery_covers_key_cases_and_roundtrips(), test_generator_embeds_control_config(), test_generator_high_difficulty_produces_failures(), test_generator_is_deterministic_for_same_seed(), test_generator_samples_are_valid_and_serializable() (+1 more)

### Community 47 - "test_profiled_scenarios.py"
Cohesion: 0.15
Nodes (10): Any, compose_scenario(), Serialize only the canonical profile- and matrix-aware schema v3., Собрать сценарий из независимых источников участков., test_scenario_roundtrip_with_weather_and_failures(), Contracts of the unified aircraft-profiled scenario model., test_automatic_selection_never_falls_back_to_a_draft_profile_branch(), test_composition_keeps_repeated_failures_as_one_set_member() (+2 more)

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
Cohesion: 0.07
Nodes (26): approach_blocker(), ApproachRefused, at_lateral_alignment_gate(), Полоса подхода к гейту совмещения с осью ± 5 м: `(30 м, 30 м + band]`. Только в…, Окончен ли воздушный участок. Два независимых признака, любой достаточен:…, Воздушный участок начинать нельзя — с названной причиной. Отдельное исключение,…, Можно ли вообще судить об участке по этому кадру. Кадр без пакета стенда…, Почему нельзя вести заход по этому кадру. `None` — можно. Пока проверка одна,… (+18 more)

### Community 54 - "run_artifacts.py"
Cohesion: 0.19
Nodes (16): _csv_value(), default_runs_root(), _effective_configs(), gains_snapshot(), _git_state(), json_sha256(), _jsonable(), _matrix_rows() (+8 more)

### Community 55 - "RunwayTracker"
Cohesion: 0.15
Nodes (8): Решить прямую геодезическую задачу на сферической Земле., Геодезическое guidance в истинной системе направлений., Guidance по курсу ВПП и измеренному отклонению — без собственной геодезии.…, Возвращает отклонение от осевой линии в метрах. >0 - правее оси, <0 - левее., Геодезическое наведение на ось ВПП с упреждением по скорости., RunwayTracker, GainSpace, test_runway_profile_delegates_geometry_to_tracker()

### Community 56 - "RomanLogImporter"
Cohesion: 0.19
Nodes (10): _number(), Path, Импорт и проверка внешних CSV-прогонов roman_aviacia_ics., Потоково нормализует основной и authority CSV Романа., RomanLogImporter, verify_manifest(), fixture, roman_csv() (+2 more)

### Community 57 - "working_ics/approach_criteria.py"
Cohesion: 0.21
Nodes (7): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, ICSInputs, Evaluate the A.1.1 approach segment and stop at a radio-altitude floor.

### Community 58 - "test_dashboard.py"
Cohesion: 0.20
Nodes (13): _live(), _post(), parametrize, test_active_pid_is_editable_in_classical_and_shadow(), test_gain_change_is_queued_bumpless_and_records_full_event(), test_http_api_is_incremental_pending_and_loopback_only(), test_incremental_snapshot_uses_recorder_objects_and_stays_small_when_idle(), test_live_and_replay_use_the_same_dashboard_snapshot() (+5 more)

### Community 59 - "runtime/pretrain.py"
Cohesion: 0.15
Nodes (27): cli(), _condition_key(), _fit_feature_normalization(), load_offline_dataset(), _normalized_mse(), _physical_bounds(), _predict(), ndarray (+19 more)

### Community 60 - "gain_space_for"
Cohesion: 0.24
Nodes (12): gain_space_for(), _profile_name(), Профильное пространство абсолютных PID-коэффициентов NPGS., _regulator_config(), Профильные пространства абсолютных PID-коэффициентов NPGS., test_every_profile_preset_gain_is_inside_its_band(), test_gain_space_can_be_built_from_external_scenario_registry(), test_normalization_endpoints_and_nonpositive_guard() (+4 more)

### Community 61 - "test_control_parity.py"
Cohesion: 0.09
Nodes (20): Генератор эталонной кривой скорости (Колокол Гаусса)., Начать профиль с фактической скорости текущего участка., То же без лишнего round-trip м/с → узлы → м/с на касании., Возвращает идеальную скорость (м/с) для текущей точки пути., ReferenceTrajectory, TrajectoryState, Тесты паритета после выноса контура из main.ipynb в пакет ismpu. Полный паритет…, Стенд при обрыве связи отдаёт НУЛИ с valid=False, а не None. Проверка «поле is… (+12 more)

### Community 62 - "Project Dependencies"
Cohesion: 0.18
Nodes (13): Autonomous Landing Controller, Repository Guidance for Codex, Autonomous Landing Controller, Repository Guidance for Claude Code, Neural Landing Implementation Plan, Unified Scenario System, Optional Gymnasium, NumPy (+5 more)

### Community 63 - "ControllingSystem"
Cohesion: 0.09
Nodes (29): ControllingSystem, Связать сценарий с контуром; PID активируются после определения участка., Обновить параметры геометрического наведения латерального канала. Имя сохранено…, Веса влияния каналов (актор, §6): множители к выходам каналов. 1.0 = классика., Оркестратор классического контура поверх стенда (`envs.ics_sim.ICSSim`).…, Аварийная остановка: обнулить органы и **снять заявку каналов**. Именно…, _lost_engagement(), SimInterface (+21 more)

### Community 64 - "PidGainRegressor"
Cohesion: 0.12
Nodes (15): device, Веса + конфиг + слепок нормировки (включая gain-пространство) одним артефактом., GainGuard, PidGainRegressor, Any, Минимальная SFT-модель абсолютных коэффициентов PID и общий runtime guard., Сохранить веса вместе с полным train↔runtime контрактом., Проверяет prediction и ограничивает скорость изменения до записи в PID. (+7 more)

### Community 66 - "dashboard_core.py"
Cohesion: 0.10
Nodes (14): _allocator_stage(), DashboardServer, DashboardSnapshot, _finite(), _first_present(), _gain_ranges(), _gains_from_manifest(), _gains_from_samples() (+6 more)

### Community 67 - "test_tolerance.py"
Cohesion: 0.15
Nodes (23): evaluate_approach_tolerances(), _glideslope_tolerance_deg(), ApproachLimits, ApproachTelemetry, FailureMode, Монитор допусков захода в реальном времени + классификация особой ситуации.…, Результат проверки допусков захода на одном такте. `landing_allowed` — все ли…, Допуск по глиссаде с учётом отказа (ТЗ 5.1.2.1–5.1.2.3), самый мягкий из… (+15 more)

### Community 68 - "test_working_ics_dashboard.py"
Cohesion: 0.35
Nodes (10): ClearWeatherILSController, DashboardState, _controller(), _inputs(), Characterization tests for the bench-validated ``working_ics`` dashboard., _record(), test_dashboard_records_four_airborne_views_and_diagnostics(), test_gain_updates_are_immediate_validated_and_share_pitch_with_flare() (+2 more)

### Community 70 - "Telemetry"
Cohesion: 0.09
Nodes (14): Кадр «связи со стендом нет». Нули, а не None: контур проверяет `valid` первым., Невалидные ICS-сигналы, которые воздушный закон читает безусловно., Приборная скорость (kt → м/с). Отсечки реверса заданы по ней, а не по путевой., Радиовысота **в футах** — единицы стенда. Порог воздушного включения (400…, Объявлены ли валидными **оба** канала ILS (курсовой и глиссадный). `None` —…, Боковое отклонение от оси, измеренное стендом. Позволяет не считать геодезию…, Обжатие ВСЕХ стоек. Диагностический сигнал; условие включения проверяет сам…, Фаза полёта по `config.ics.FlightPhase` — по ней распознаётся уже идущий пробег. (+6 more)

### Community 71 - "Unified Profile-Aware Scenario System"
Cohesion: 0.22
Nodes (9): Technical-Specification Acceptance Gates, Bench-Validated ILS Approach Channel, Forward-Only Flight Segment Supervisor, Tolerance-Gated Go-Around, Longitudinal and Lateral Ground Channels, PID Run Matrix, Unified Profile-Aware Scenario System, Legacy Scenario Preset Model (+1 more)

### Community 72 - "Interactive PID Dashboard"
Cohesion: 0.25
Nodes (9): Nine-View PID Dashboard, Run Recording Artifacts, buildTabs, draw, Gain Tuning and Snapshot Export, Interactive PID Dashboard, refresh, render (+1 more)

### Community 73 - "run_matrix.py"
Cohesion: 0.05
Nodes (21): cases_for_segment(), ground_runs(), MatrixCase, MatrixCondition, MatrixRun, normalize_code(), _number(), Any (+13 more)

### Community 74 - "DashboardState"
Cohesion: 0.36
Nodes (3): DashboardState, Any, ICSInputs

### Community 75 - "splits.py"
Cohesion: 0.08
Nodes (25): FailureMode, Enum, Привести состояние ровно к набору `modes` (то, что сообщил стенд). Пересборка с…, _hash_unit(), holdout_reason(), is_marked_holdout(), is_signature_holdout(), PartitionedScenarioProvider (+17 more)

### Community 76 - "ICSInterface.cs"
Cohesion: 0.36
Nodes (7): External.Systems.ICS, ControlModeState, GearState, ICSInputs, ICSOutputs, ReverseEngineType, UInt64

### Community 77 - "test_rollout_env.py"
Cohesion: 0.16
Nodes (19): ObservationBuilder, Строит нормированный вектор наблюдения одного кадра., heading_deviation_deg(), Отклонение курса ВС от направления ВПП — приёмочная величина ТЗ 5.1.3.3 /…, Тесты Этапа 2: Observation/Action/reward/RolloutEnv + инвариант identity ==…, Телеметрия ВС на оси ВПП, смещённого вбок на `offset_m` и с заданным курсом.…, ТЗ 5.1.3.3 нормирует курс «от направления ВПП». Смещение от оси на него не…, На стенде курс ВПП приходит телеметрией; конфиг — только значение по умолчанию. (+11 more)

### Community 78 - "PretrainRunConfig"
Cohesion: 0.33
Nodes (9): ground_cases(), build_scenarios(), matrix_preset_names(), PretrainRunConfig, Legacy-каталог accepted presets; активный offline trainer его не вызывает., Legacy-представление наземных строк; dataset строится по run-directory., _selected_presets(), test_sft_accepts_only_accepted_profiles() (+1 more)

### Community 79 - "promote_candidate.py"
Cohesion: 0.38
Nodes (13): _gain_patch(), main(), promote_candidate(), PromotionError, Path, Проверяемое продвижение dashboard candidate в sparse scenario override., Пересчитать matrix/config hashes, а не доверять двум согласованно изменённым…, Проверить run и записать новый scenario JSON; registry исходников не меняется. (+5 more)

### Community 80 - "ICS PID Monitor"
Cohesion: 0.29
Nodes (7): buildControls, draw, formatTime, Four-Loop PID Tuning, ICS PID Monitor, Live and Historical Timeline, refresh

### Community 81 - "rollout_bridge.py"
Cohesion: 0.27
Nodes (6): ICSInputs, socket, Hand the validated airborne session to Vlayd's existing rollout loop. The…, Keep Vlayd's engagement latch synchronized during the approach., Run Vlayd's rollout until taxi speed, then send its taxi handoff., VlaydRolloutBridge

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
Nodes (12): EpisodeObjective, Накопитель по эпизоду: собирает потактовые отсчёты → сводные компоненты.…, _make_box(), GainSpace, SimInterface, Минимальная замена gym.spaces.Box, когда gymnasium не установлен., _SimpleBox, Отсутствие данных даёт None, а не 0 — приёмка обязана трактовать это как FAIL. (+4 more)

### Community 86 - "run_report.py"
Cohesion: 0.19
Nodes (22): _accepted_segments(), aggregate_matrix_results(), _approach_runway_heading_error(), build_run_report(), _handover_ratio(), main(), _matrix_results(), _max_abs() (+14 more)

### Community 87 - "scenarios.py"
Cohesion: 0.12
Nodes (22): ApproachConfig, ControlProfile, _copy_approach(), _copy_ground(), _ground_segments_for_spec(), _GroundPresetSpec, _install_approach_scenarios(), _materialize_override() (+14 more)

### Community 88 - "import_workbook"
Cohesion: 0.33
Nodes (9): import_workbook(), main(), Any, Path, Одноразовый импорт исходной Excel-матрицы в runtime-каталог JSON., Прочитать книгу целиком; функция не используется production runtime., _scalar(), write_catalog() (+1 more)

### Community 89 - "test_approach_channel.py"
Cohesion: 0.08
Nodes (33): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+25 more)

### Community 90 - "LongitudinalDiagnostics"
Cohesion: 0.18
Nodes (7): CompletionRule, LongitudinalChannel, LongitudinalDiagnostics, Блок 1: скорость → симметричная база тормозов и реверса., Сбросить PID и привязать начало профиля к фактической скорости касания/старта., PidMap, VelocityLaw

### Community 91 - "shield.py"
Cohesion: 0.10
Nodes (21): Shield — детерминированный защитный контур между актором и классическим PID.…, ControlArchitecture, Канонический порядок регуляторов, размерности действия и **контракт обучаемого…, Фиксированный порядок слоёв и роль обучаемого компонента., Проверяет контракт обучаемого слоя. Нарушение → `ValueError` на старте…, Один регулятор, коэффициенты которого (kp/ki/kd) разрешено настраивать сети., RegulatorSpec, validate_action_contract() (+13 more)

### Community 92 - "static_sim"
Cohesion: 0.11
Nodes (29): base_gains_from_pids(), Снимок (kp, ki, kd) регуляторов — пресет-якорь для Shield и т.п., apply_corrections(), preset_action(), float64, GainMap, 17-мерное действие, точно воспроизводящее коэффициенты пресета (веса = 1).…, Применяет абсолютные gain'ы к контуру. Возвращает `(effective_gains,… (+21 more)

### Community 93 - "ICSSim"
Cohesion: 0.06
Nodes (24): ConditionMatch, ControlsState, EngagementInputs, ICSSim, FailureMode, FlightSegment, Scenario, SimInterface (+16 more)

### Community 94 - "xplane_sim.py"
Cohesion: 0.10
Nodes (16): Настройки воздушного участка: заход по ILS, выравнивание, управление скоростью.…, Модель отказов бортового оборудования. `FailureState` хранит мультипликативные…, ApproachData, ControlDiagnostics, Enum, str, Общий контракт симулятора и воздушных сигналов. ICS и X-Plane различаются…, Результат безусловного best-effort отключения backend. (+8 more)

### Community 95 - "reward.py"
Cohesion: 0.09
Nodes (27): _command_jerk(), _component(), _effort_saturated(), excess(), graded(), _ground_steering(), ObjectiveWeights, _p95() (+19 more)

### Community 99 - "_WarmUpSim"
Cohesion: 0.15
Nodes (9): ObserverEstimate, Оценки PINN-обсервера (§12). Заглушка нулями до Этапа 7., EpisodeInfo, TypedDict, Стенд, включающий управление только после N тактов прогрева. Само рукопожатие…, Такты рукопожатия — не шаги эпизода: в это время ВС нами не управлялось. Иначе…, test_env_reports_engagement_state_in_info(), test_warm_up_runs_before_the_episode_and_is_not_counted() (+1 more)

### Community 110 - "test_campaign.py"
Cohesion: 0.26
Nodes (15): campaign_phase(), campaign_rows(), campaign_summary(), _config_status(), main(), next_campaign_row(), Path, Порядок и фактический статус кампании из 280 матричных прогонов. (+7 more)

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
Cohesion: 0.03
Nodes (74): engaged_sim(), FakeConnector, make_ics_inputs(), on_ground(), Статический стенд: всегда один и тот же кадр, отправленное — в `sent_outputs`., (sim, connector) с завершённым рукопожатием: стенд подтвердил `AgentIsActive =…, Полный пакет стенда: нули по умолчанию + заданные поля., Кадр «ВС на полосе»: обжаты все стойки, курс/координаты у порога UUEE 06R. (+66 more)

### Community 116 - "Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)., Source Nodes

### Community 117 - "admit_checkpoint"
Cohesion: 0.14
Nodes (19): AdmissionResult, admit_checkpoint(), Пропускать ли чекпоинт дальше. Отсутствующая/нечисловая метрика = отказ.…, _battery(), Отсутствующая метрика = отказ, а не «нет данных — значит нет проблемы»., Формально в допуске, но авторитет исчерпан — режим держится на грани., Если сеть не бьёт классику, она не окупается — выпускать её нечего., Канал не двигался за эпизод → p95 = None. Это не дефект. (+11 more)

### Community 123 - "test_sft_regressors.py"
Cohesion: 0.14
Nodes (16): Dataset, feature_schema_hash(), Стабильный hash порядка признаков; перестановка является сменой контракта., Ленивые непрерывные окна: один прогноз на каждый такт после заполнения истории., WindowDataset, checkpoint_metadata(), Path, _checkpoint() (+8 more)

### Community 124 - ".from_json"
Cohesion: 0.33
Nodes (5): _pid_from_colleague(), Загрузка настроек из JSON коллеги (`config/ics_clear_weather_pid.json`). Секции…, `PIDConfig` коллеги → аргументы нашего `PIDController`. Предел интегратора у…, Наши умолчания и его файл — одно и то же. Разойдутся — расхождение должно быть…, test_config_from_the_colleague_json_matches_our_defaults()

### Community 125 - "GuidanceState"
Cohesion: 0.29
Nodes (3): GuidanceState, Совместимость с прежним атрибутом; новый термин явно указывает ось., Совместимость со старым словарным API.

### Community 126 - ".compute"
Cohesion: 0.18
Nodes (5): → (интеграл только с утечкой, интеграл с утечкой и приращением). Оба уже зажаты., Такт регулятора. `measurement` обязателен при `derivative_on_measurement=True`., Back-calculation: подтянуть интегратор к фактически применённой команде. No-op…, Сменить коэффициенты без сброса D-history и с компенсацией интегратором.…, Вес апериодического фильтра D-составляющей за такт `dt`.

### Community 127 - "RunReader"
Cohesion: 0.16
Nodes (11): _load_updates(), После recorder.finish держать полный run доступным, но только для чтения., Path, Run-directory и любой поддержанный CSV через один streaming API., RunReader, _frame(), _record_ground_run(), test_approach_stream_has_three_pid_states_and_replays_at_1e_12() (+3 more)

### Community 129 - "Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md)., Source Nodes

### Community 130 - "Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md)., Source Nodes

### Community 131 - "pid.py"
Cohesion: 0.21
Nodes (7): PIDDiagnostics, Пропорционально-интегрально-дифференциальный регулятор. Класс сохраняет прежнюю…, Типизированный снимок последнего такта регулятора., apply_ground_control(), build_pids(), Сборка классического контура из неизменяемой конфигурации., Фабрики stateful-объектов; config-модули хранят только данные.

### Community 132 - "RolloutBuffer"
Cohesion: 0.15
Nodes (10): device, Tensor, Шагает средой `rollout_len` тактов (сброс по завершению эпизода). → статистика., Хук L_shield (§11): барьер, отталкивающий выход от края уровня-1 Shield. По…, Плоский буфер одного env: obs-окна, сырые действия, logp/value/reward/done., RolloutBuffer, PPOMetrics, ScenarioProvider (+2 more)

### Community 133 - "gain_scheduler.py"
Cohesion: 0.17
Nodes (14): int64, ActorOutput, _init_log_std(), layer_init(), _mlp_head(), phase_labels_from_groundspeed_kts(), ArrayLike, TypedDict (+6 more)

### Community 134 - "EngagementInputs"
Cohesion: 0.14
Nodes (10): EngagementInputs, EngagementState, Enum, Автомат включения управления на стенде заказчика. Стенд принимает наши команды…, Передать управление в руление (`ControlMode 3 → 4`). → удался ли переход.…, Сколько уже держится выдержка. 0.0, если отсчёт не идёт (для диагностики)., Почему включение ещё не произошло — для диагностики при таймауте прогрева.…, Слепок для логов и отчётов приёмки. (+2 more)

### Community 135 - "Q: Приступай к выполнению этапа 2 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 2 плана docs/plan.md, Source Nodes

### Community 137 - "verdict_of"
Cohesion: 0.18
Nodes (13): _check(), Criterion, evaluate_matrix_run(), _range_check(), Один пункт ТЗ: предел, измеренное значение, вердикт и его причина., Строит вердикт. Неприменимо → SKIP; применимо, но данных нет → FAIL., Проверить несимметричный интервал; отсутствие измерения остаётся отказом., Оценить именно выбранную строку матрицы, не смешивая фазы соседних шифров. (+5 more)

### Community 138 - "compute_reward"
Cohesion: 0.14
Nodes (15): compute_reward(), TypedDict, Считает компоненты и суммарный reward. Все компоненты ≥ 0; reward = −Σ…, Допуск по оси ВПП для текущей фазы: пробег ±3 м, руление ±1 м (ТЗ 5.1.3.1)., RewardComponents, RewardWeights, xte_limit_for(), Перелёт по скорости к концу ВПП опаснее недолёта — симметричным модулем не… (+7 more)

### Community 142 - "LandingFlapConfiguration"
Cohesion: 0.26
Nodes (13): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+5 more)

### Community 154 - "Normalization"
Cohesion: 0.23
Nodes (7): ArrayLike, float32, float64, Normalization, NDArray, Покомпонентная standardization и границы обучающей выборки., no_grad

### Community 155 - "runway_profiles.py"
Cohesion: 0.24
Nodes (10): find_earth_nav_dat(), get_runway_profile(), ILSStation, parse_ils_station(), Path, Профили ВПП и разрешение ILS из установленной базы X-Plane., Точка на продолжении оси; положительное расстояние — до порога., Найти LOC (тип 4) без хардкода частоты. (+2 more)

### Community 158 - "Q: Приступай к выполнению этапа 4 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 4 плана docs/plan.md, Source Nodes

### Community 163 - "protocol.py"
Cohesion: 0.25
Nodes (6): ControlModeState, GearState, ICSOutputs, Any, IntEnum, ReverseEngineType

### Community 164 - "aircraft_profiles.py"
Cohesion: 0.15
Nodes (12): IcsEngagement, get_aircraft_profile(), Профили преобразования команд ИСМПУ в органы управления X-Plane., Расширение реестра будущим профилем МС-21 без правки XPlaneSim., Проводка и масштабы конкретного планера X-Plane., register_aircraft_profile(), XPlaneAircraftBinding, build_sim() (+4 more)

### Community 165 - "decode"
Cohesion: 0.22
Nodes (7): RegulatorKey, Плоский вектор действия (17,) → GainCommand. Layout: [gains×15, w_lon, w_lat]., decode(), ArrayLike, Плоский вектор действия → `GainCommand` (абсолютные gain'ы)., test_action_maps_to_all_five_regulators_independently(), test_reference_action_decodes_to_default_gains()

### Community 167 - "Q: Приступай к выполнению этапа 8 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 8 плана [plan.md](docs/plan.md)., Source Nodes

### Community 169 - ".airborne_commands"
Cohesion: 0.40
Nodes (3): clamp(), Преобразовать воздушные команды ICD в нормированные DataRef X-Plane., Преобразовать нормированные команды пробега в DataRef X-Plane.

### Community 171 - "apply_gains_to_pids"
Cohesion: 0.50
Nodes (4): apply_gains_to_pids(), PidMap, Записывает эффективные gain'ы обратно в регуляторы (перед control_step)., test_gain_bridge_helpers_with_real_pids()

### Community 173 - "ConditionMatch"
Cohesion: 0.25
Nodes (4): ConditionMatch, Сверка ожидаемых условий с фактической телеметрией backend., Погода остаётся отчётной; неверный отказ делает прогон недопустимым., Совместимое имя для прежних потребителей допуска к приёмке.

### Community 174 - ".from_ics"
Cohesion: 0.25
Nodes (6): Фактические погодные условия со стенда (ветер, сцепление, осадки, видимость)., `ICSInputs` → `WeatherState`. Единственный источник фактической погоды. Стенд…, `Visibility` в футах. Без пересчёта 16000 футов читались бы как «ясно» вместо…, test_visibility_is_converted_from_feet(), Стенд шлёт узлы и **футы**; в WeatherState видимость — в метрах., test_from_ics_converts_units()

### Community 175 - "._should_go_around"
Cohesion: 0.29
Nodes (5): above_decision_height(), ВС выше высоты решения ухода на второй круг (30 м по ТЗ 5.1.1.2). → уход…, Реверс убран: команды обратной тяги нулевые. В воздухе реверс не выдаётся…, Нужно ли уходить на второй круг по этому такту. → причина или `None`. Только…, ToleranceReport

### Community 179 - "render_report"
Cohesion: 0.50
Nodes (4): Markdown-отчёт приёмки. Отрицательные результаты не скрываются — они и есть…, Пишет `evaluation.json` + `report.md`. → пути записанных файлов., render_report(), write_report()

### Community 181 - "Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md)., Source Nodes

## Ambiguous Edges - Review These
- `Unified Profile-Aware Scenario System` → `Legacy Scenario Preset Model`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to
- `Dual-Backend SimInterface` → `ICS-Only Backend Guidance`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **76 isolated node(s):** `Answer`, `Outcome`, `Source Nodes`, `ismpu`, `Answer` (+71 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **68 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `loop.py` (2× useful, score=1.984886047) _(code changed — re-verify)_
- `ICSSim` (2× useful, score=1.968852507)
- `LateralChannel` (2× useful, score=1.947518166)
- `ObservationBuilder` (2× useful, score=1.92778025)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Unified Profile-Aware Scenario System` and `Legacy Scenario Preset Model`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Dual-Backend SimInterface` and `ICS-Only Backend Guidance`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `ControllingSystem` connect `ControllingSystem` to `pid.py`, `json_config.py`, `compute_reward`, `test_pretrain.py`, `test_run_matrix.py`, `ApproachController`, `system.py`, `PIDController`, `evaluate.py`, `.from_preset`, `test_evaluate.py`, `RolloutEnv`, `telemetry`, `test_full_flight.py`, `sft.py`, `._should_go_around`, `_Clock`, `test_go_around.py`, `test_approach_criteria.py`, `._approach_step`, `test_dashboard.py`, `test_control_parity.py`, `test_rollout_env.py`, `rollout_bridge.py`, `EpisodeObjective`, `LongitudinalDiagnostics`, `shield.py`, `static_sim`, `reward.py`, `_WarmUpSim`, `test_campaign.py`, `test_ics_sim.py`, `test_sft_regressors.py`, `RunReader`?**
  _High betweenness centrality (0.137) - this node is a cross-community bridge._
- **Why does `Telemetry` connect `Telemetry` to `ground_allocator.py`, `LateralChannel`, `ControlsState`, `ics_connector.py`, `ics_sim.py`, `system.py`, `weather.py`, `XPlaneSim`, `telemetry`, `test_full_flight.py`, `fakes.py`, `ICSInputs`, `.from_ics`, `_Clock`, `test_go_around.py`, `test_approach_criteria.py`, `._approach_step`, `test_control_parity.py`, `test_tolerance.py`, `test_rollout_env.py`, `rollout_bridge.py`, `test_working_ics_golden.py`, `test_approach_channel.py`, `LongitudinalDiagnostics`, `static_sim`, `ICSSim`, `xplane_sim.py`, `_WarmUpSim`, `test_ics_sim.py`, `RunReader`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Why does `Scenario` connect `Scenario` to `.step`, `json_config.py`, `SimInterface`, `GainSpace`, `test_run_matrix.py`, `system.py`, `weather.py`, `XPlaneSim`, `segments.py`, `.from_preset`, `RolloutEnv`, `test_splits.py`, `sft.py`, `ScenarioGenerator`, `test_profiled_scenarios.py`, `gain_space_for`, `promote_candidate.py`, `EpisodeObjective`, `scenarios.py`, `xplane_sim.py`, `_WarmUpSim`, `test_ics_sim.py`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `ControllingSystem` (e.g. with `ApproachConfig` and `EpisodeInfo`) actually correct?**
  _`ControllingSystem` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `ControlsState` (e.g. with `GainCommand` and `RuntimeState`) actually correct?**
  _`ControlsState` has 24 INFERRED edges - model-reasoned connections that need verification._