# Graph Report - GOSNIIASProject  (2026-08-15)

## Corpus Check
- 137 files · ~137,387 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2520 nodes · 6048 edges · 163 communities (113 shown, 50 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 575 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `da300d65`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- SpecialSituation
- test_splits.py
- compute_reward
- weather.py
- Shield
- test_refactoring_contracts.py
- SimInterface
- test_approach_channel.py
- ControllingSystem
- ScriptedFlightBench
- GroundControlAllocator
- LateralChannel
- test_pretrain.py
- Scenario
- test_ics_connector.py
- test_run_matrix.py
- AircraftProfile
- ._fill_ground
- ApproachChannel
- Telemetry
- test_gain_scheduler.py
- XPlaneSim
- test_weather.py
- PIDController
- FailureMode
- RolloutEnv
- test_xplane_backend.py
- test_evaluate.py
- test_ppo.py
- IcsEngagement
- XPlaneConnectX
- fakes.py
- WeatherState
- Graphify Pipeline
- XPlaneConnector
- telemetry
- GainSpace
- test_ics_engagement.py
- test_diagnostic_tools.py
- test_ics_sim.py
- pid_controller.py
- scenarios.py
- NPGS
- ICSInputs
- shield.py
- 3. Этапы реализации
- ScenarioGenerator
- ControlModeState
- RunRecorder
- test_full_flight.py
- test_go_around.py
- Neural PID Gain Scheduler Architecture
- test_approach_criteria.py
- test_tolerance.py
- gui/dashboard.py
- RunwayTracker
- RomanLogImporter
- working_ics/approach_criteria.py
- parse_ils_station
- .send_outputs
- gain_space_for
- ReferenceTrajectory
- Project Dependencies
- .from_ics
- GuidanceState
- ICSInputs
- DashboardServer
- heading_deviation_deg
- test_working_ics_dashboard.py
- ICSOutputs
- _descent_frames
- Unified Profile-Aware Scenario System
- Interactive PID Dashboard
- RuntimeError
- ClearWeatherILSController
- splits.py
- ICSInterface.cs
- .enter_segment
- EpisodeObjective
- ShutdownReport
- ICS PID Monitor
- VlaydRolloutBridge
- ICS UDP JSON Protocol
- X-Plane Dashboard and Runtime Guide
- ApproachConfig
- ControlsState
- DashboardState
- _Clock
- FrictionProfile
- envelope.py
- ICSInputs
- test_action_contract.py
- roll_limit_deg
- _WarmUpSim
- test_ground_controller.py
- reward.py
- conftest.py
- agent/__init__.py
- config/__init__.py
- .teleport_approach
- control/__init__.py
- envs/__init__.py
- gui/__init__.py
- ismpu/__init__.py
- io/__init__.py
- runtime/__init__.py
- tools/__init__.py
- utils/__init__.py
- ismpu
- FlightPhase
- ._should_go_around
- Q: Реализовать этап 0: baseline, golden replay и dashboard characterization
- Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md).
- test_default_config_carries_the_tuned_bench_gains
- .build
- engaged_sim
- test_rollout_env.py
- str
- IntEnum
- ControlModeState
- ICSInputs
- ICSOutputs
- socket
- test_control_parity.py
- .read_telemetry
- ApproachRefused
- .compute
- .summary
- _engaged_airborne_sim
- .invalid
- HandshakeBench
- control.py
- _cold_sim
- .blocking_reason
- DatagramSocket
- Q: Приступай к выполнению этапа 2 плана docs/plan.md
- _faults_from_inputs
- pid.py
- GoAroundManeuver
- _legacy_reference
- RegulatorSpec
- .pids
- .reset
- test_control_step_is_unchanged_when_tracking_is_off
- ApproachChannel
- ApproachConfig
- ConditionMatch
- FailureState
- ApproachLimits
- ApproachTelemetry
- PidMap
- FailureMode
- PidMap
- FailureMode
- Scenario
- StartMode
- Scenario
- Scenario
- PIDController
- ReferenceTrajectory
- RewardWeights
- TypedDict
- VelocityLaw

## God Nodes (most connected - your core abstractions)
1. `ControllingSystem` - 184 edges
2. `ControlsState` - 123 edges
3. `Telemetry` - 115 edges
4. `ICSSim` - 75 edges
5. `PIDController` - 70 edges
6. `Scenario` - 65 edges
7. `FailureMode` - 63 edges
8. `RolloutEnv` - 57 edges
9. `AircraftProfile` - 55 edges
10. `XPlaneSim` - 52 edges

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
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/flight.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/ground_allocator.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach_criteria.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/tolerance.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`

## Hyperedges (group relationships)
- **Graphify Extraction and Build Flow** — _codex_skills_graphify_skill_structural_extraction, _codex_skills_graphify_skill_semantic_extraction, _codex_skills_graphify_references_extraction_spec_semantic_extraction_contract, _codex_skills_graphify_references_update_build_merge [EXTRACTED 1.00]
- **Hybrid Neural Landing Control** — implementation_plan_classical_pid_plant, implementation_plan_npgs, implementation_plan_deterministic_shield, implementation_plan_ppo_multicomponent_loss, implementation_plan_pinn_observer [EXTRACTED 1.00]
- **PID Dashboard Ecosystem** — docs_xplane_dashboard_pid_dashboard, ismpu_gui_dashboard_pid_dashboard, ismpu_working_ics_ics_dashboard_ics_pid_monitor [INFERRED 0.85]

## Communities (163 total, 50 thin omitted)

### Community 0 - "SpecialSituation"
Cohesion: 0.09
Nodes (26): lateral_limit_m(), lateral_load_situation(), lateral_situation(), normal_load_situation(), IntEnum, Критерии критичности особых ситуаций МС-21 (Приложение 1 к ТЗ). Таблица АП-25…, Классификация скорости касания относительно VAPP и VВПП пред., Классификация нормальной перегрузки посадочного удара. `heavy` — взлётный вес. (+18 more)

### Community 1 - "test_splits.py"
Cohesion: 0.13
Nodes (31): assert_no_leakage(), has_holdout_failure(), holdout_reason(), is_marked_holdout(), Помечен ли сценарий как holdout своим именем., Затрагивает ли сценарий зарезервированное семейство отказов., Почему сценарий в holdout, или `None` если он обучающий. Причина всегда…, Разбивает набор сценариев. Детерминировано и устойчиво к добавлению новых… (+23 more)

### Community 2 - "compute_reward"
Cohesion: 0.15
Nodes (13): compute_reward(), TypedDict, Считает компоненты и суммарный reward. Все компоненты ≥ 0; reward = −Σ…, Допуск по оси ВПП для текущей фазы: пробег ±3 м, руление ±1 м (ТЗ 5.1.3.1)., RewardComponents, xte_limit_for(), Перелёт по скорости к концу ВПП опаснее недолёта — симметричным модулем не…, Тормоз на 0 = «торможение не требуется», а не «авторитет исчерпан». Иначе флаг… (+5 more)

### Community 3 - "weather.py"
Cohesion: 0.06
Nodes (39): cases_for_segment(), _kts(), MatrixCase, MatrixCondition, Матрица прогонов для настройки базовых ПИД-регуляторов. Машиночитаемая форма…, Один шифр матрицы — вариант отказа/режима, под который настраивается набор…, Шифры одного участка: `approach` / `rollout` / `taxi` / `through`., Матрица задаёт ветер в м/с, телеметрия приходит в узлах. (+31 more)

### Community 4 - "Shield"
Cohesion: 0.08
Nodes (36): _clip(), GainCommand, GainMap, RegulatorKey, Наблюдаемое состояние для поведенческих проверок уровня 3., Что сделал Shield за такт: активированные правила, штрафы, fallback., Границы и веса штрафов Shield (все — настраиваемые, а не свойства сети)., Защитный контур. Детерминирован; хранит состояние прошлого такта для rate-… (+28 more)

### Community 5 - "test_refactoring_contracts.py"
Cohesion: 0.12
Nodes (38): approach_control_from_dict(), approach_control_to_dict(), _copy_approach(), dump_scenario(), _finite_tree(), ground_control_from_dict(), ground_control_to_dict(), _legacy_ground() (+30 more)

### Community 6 - "SimInterface"
Cohesion: 0.11
Nodes (5): BaseException, StartMode, Минимальный lifecycle, одинаковый для стенда и X-Plane., SimInterface, Protocol

### Community 7 - "test_approach_channel.py"
Cohesion: 0.13
Nodes (33): angle_error_deg(), Разность курсов, приведённая к (-180, 180]., airborne_inputs(), Кадр «ВС на глиссаде»: стойки не обжаты, ILS валиден, скорость и высота…, _our_channel(), Воздушный канал: заход по ILS, выравнивание, скоростной канал. Главный тест…, Угол сноса не должен превращаться в ошибку курса на локализаторе., Стенд иногда сбрасывает Valid при сохранении пригодного численного значения. (+25 more)

### Community 8 - "ControllingSystem"
Cohesion: 0.07
Nodes (22): ControllingSystem, ApproachConfig, SimInterface, Связать сценарий с контуром; PID активируются после определения участка., Пересобрать воздушный канал под заданные настройки. → новый канал. Именно…, Обновить параметры геометрического наведения латерального канала. Имя сохранено…, Веса влияния каналов (актор, §6): множители к выходам каналов. 1.0 = классика., Привести модель отказов к тому, что сообщает борт (`ICSInputs.Fault*`). Отказы… (+14 more)

### Community 9 - "ScriptedFlightBench"
Cohesion: 0.33
Nodes (4): Стенд, проигрывающий заход и касание **по сценарию**, а не по нашим командам.…, ScriptedFlightBench, Сквозной прогон: рукопожатие в воздухе → заход → касание → пробег → руление.…, test_a_whole_flight_runs_from_approach_to_taxi()

### Community 10 - "GroundControlAllocator"
Cohesion: 0.13
Nodes (15): FailureManager, FailureState, Эффективности исполнительных органов. Аннотации типов обязательны: без них…, Проецирует набор дискретных отказов в эффективности исполнительных органов., Привести состояние ровно к набору `modes` (то, что сообщил стенд). Пересборка с…, ActuatorFeedback, ActuatorVector, AllocationDiagnostics (+7 more)

### Community 11 - "LateralChannel"
Cohesion: 0.23
Nodes (7): GuidanceState, LateralChannel, LateralDiagnostics, Блок 2: runway guidance → единый нормированный yaw-запрос., Guidance по тому, что даёт стенд. → словарь guidance или None, если данных нет.…, Единый GuidanceState текущего кадра для control/observation/reward., RunwayTracker

### Community 12 - "test_pretrain.py"
Cohesion: 0.09
Nodes (40): NPGSConfig, Any, Гиперпараметры архитектуры NPGS (замораживаются вместе с весами при поставке)., _phase_labels(), pretrain_sft(), PretrainConfig, Tensor, BC-обучение `net` на `dataset` (регрессия mean → target_z). → история по эпохам. (+32 more)

### Community 13 - "Scenario"
Cohesion: 0.09
Nodes (19): _copy_approach(), _copy_ground(), _ground_segments_for_spec(), _GroundPresetSpec, _install_approach_scenarios(), _matrix_draft(), _profile_name(), ApproachConfig (+11 more)

### Community 14 - "test_ics_connector.py"
Cohesion: 0.08
Nodes (24): IntEnum, GearState, Разбор телеметрии стенда с совместимостью вперёд. Асимметрия намеренная (JSON-…, Отправка best-effort со счётчиком ошибок и разрежённым логом. Windows отдаёт…, → True если отправлено. Исключение наружу не выпускается., ResilientSender, ReverseEngineType, _connector() (+16 more)

### Community 15 - "test_run_matrix.py"
Cohesion: 0.06
Nodes (34): compose_matrix_scenario(), compose_scenario(), _install_through_scenarios(), matrix_battery(), Сценарий по имени либо шифру матрицы, без различия раскладки А/B., Собрать сценарий из независимых источников участков., Объединить случай листа А и случай листа Б в один полный сценарий. Аргументы…, Собрать штатные сквозные случаи Б.4 из реальных источников листов А и Б. (+26 more)

### Community 16 - "AircraftProfile"
Cohesion: 0.09
Nodes (12): AircraftProfile, clamp(), Преобразовать воздушные команды ICD в нормированные DataRef X-Plane., Преобразовать нормированные команды пробега в DataRef X-Plane., Расширение реестра будущим профилем МС-21 без правки XPlaneSim., Проводка и масштабы конкретного планера X-Plane., Общая идентичность ЛА и необязательная привязка к X-Plane. Профиль нужен и…, Command refs retained under the historical public name. (+4 more)

### Community 17 - "._fill_ground"
Cohesion: 0.18
Nodes (9): ICSOutputs, _clamp(), Желаемый уровень реверса [-1, 0] → скорость перемещения РУД (°/с). Тягой (в том…, Снять управление: пустая маска и `ControlMode = Off` несколько кадров подряд.…, `ControlsState` → `ICSOutputs` (единицы ICD), **по текущему участку полёта**.…, Воздушный участок: перегрузка, элероны и скорости РУД. Флаги фаз (`ModeFlare*`,…, Пробег и руление: тормоза, путевое управление, реверс. Путевой орган **зависит…, Фактический угол РУД из последнего кадра стенда; 0 при отсутствии кадра.… (+1 more)

### Community 18 - "ApproachChannel"
Cohesion: 0.15
Nodes (20): ApproachLimits, ApproachTelemetry, ApproachChannel, ApproachResult, clamp(), ApproachConfig, Заход по ILS с выравниванием. Телеметрию получает параметром, не читает сам.…, Сброс регуляторов и всей памяти профиля — новый заход начинается с чистого… (+12 more)

### Community 19 - "Telemetry"
Cohesion: 0.07
Nodes (19): Такт манёвра ухода. → True, когда набор устойчив (пора отдать управление…, Набор устойчив: есть и вертикальная скорость вверх, и прирост радиовысоты над…, Невалидные ICS-сигналы, которые воздушный закон читает безусловно., Приборная скорость (kt → м/с). Отсечки реверса заданы по ней, а не по путевой., Радиовысота **в футах** — единицы стенда. Порог воздушного включения (400…, Объявлены ли валидными **оба** канала ILS (курсовой и глиссадный). `None` —…, Посадочная конфигурация механизации; `None` — положение не посадочное. `None`…, Касание: обжата **любая основная** стойка. Носовая не участвует — она… (+11 more)

### Community 20 - "test_gain_scheduler.py"
Cohesion: 0.08
Nodes (26): int64, build_npgs(), phase_labels_from_groundspeed_kts(), device, Веса + конфиг + слепок нормировки (включая gain-пространство) одним артефактом., action_high(), action_low(), float32 (+18 more)

### Community 21 - "XPlaneSim"
Cohesion: 0.17
Nodes (4): ApproachData, Backend-независимый срез сигналов для захода и ухода на второй круг., XPlaneDiagnostics, XPlaneSim

### Community 22 - "test_weather.py"
Cohesion: 0.12
Nodes (19): compose_wind(), decompose_wind(), Собирает ветер из компонент относительно курса ВПП. `crosswind_kts` > 0 — ветер…, (скорость, откуда) → (crosswind, headwind) относительно курса ВПП. crosswind >…, (crosswind, headwind) → (скорость, откуда, °). Обратна `decompose_wind`., test_scenario_roundtrip_with_weather_and_failures(), Тесты погоды: разбор ветра, шкала скользкости и чтение условий из пакета стенда., Для пробега существенна боковая составляющая, а не «скорость ветра» сама по… (+11 more)

### Community 23 - "PIDController"
Cohesion: 0.13
Nodes (24): PIDController, Опциональная численность PID (шаг 5): каждый флаг проверяется на том дефекте,…, Если применено ровно то, что выдал PID, коррекции быть не должно., Уставка прыгает, объект стоит на месте — D-составляющая не должна реагировать.…, Выход ИЗ насыщения должен разрешаться всегда, иначе регулятор залипнет. kp…, Если насыщает уже пропорциональная часть, интегрировать нельзя вообще — и это…, Точная утечка = решение dI/dt = e − I/τ при постоянной e, а не приращение e·dt., При мёртвом актуаторе применяется 0 вместо выхода PID — интегратор это… (+16 more)

### Community 24 - "FailureMode"
Cohesion: 0.06
Nodes (36): FailureMode, Enum, Модель отказов бортового оборудования. `FailureState` хранит мультипликативные…, На стенде отказы приходят телеметрией, а не инжектируются нами., AdmissionResult, _check(), compare_policies(), Criterion (+28 more)

### Community 25 - "RolloutEnv"
Cohesion: 0.13
Nodes (11): Tensor, Шагает средой `rollout_len` тактов (сброс по завершению эпизода). → статистика., Хук L_shield (§11): барьер, отталкивающий выход от края уровня-1 Shield. По…, ndarray, Окно истории → тензор `(history_len, OBS_DIM)` (последовательность кадров для…, Состояние для поведенческих проверок Shield. Курс здесь — отклонение от…, RolloutEnv, PPOMetrics (+3 more)

### Community 26 - "test_xplane_backend.py"
Cohesion: 0.11
Nodes (14): Ожидаемые физические условия одного участка., SegmentConditions, test_xplane_ignores_failures_outside_rollout_contract(), MockXPlaneConnector, ScriptedXPlaneConnector, test_commands_failures_and_close_release_overrides(), test_failed_approach_setup_releases_overrides_and_pause(), test_ignored_xplane_failure_participates_in_segment_delta_and_is_cleared() (+6 more)

### Community 27 - "test_evaluate.py"
Cohesion: 0.09
Nodes (51): admit_checkpoint(), evaluate_tz(), Диагностика эпизода + сценарий → список вердиктов по пунктам ТЗ разд. 5., Итог эпизода: FAIL, если провален хоть один применимый критерий., Один эпизод под заданной политикой → objective + вердикты ТЗ., Пропускать ли чекпоинт дальше. Отсутствующая/нечисловая метрика = отказ.…, run_episode(), verdict_of() (+43 more)

### Community 28 - "test_ppo.py"
Cohesion: 0.07
Nodes (41): PPOConfig, PPOTrainer, Any, device, PPO-тренер + многокомпонентный loss для NPGS (план §11). `L = L_ppo +…, Собирает rollout из среды и обновляет NPGS многокомпонентным PPO-loss., Плоский буфер одного env: obs-окна, сырые действия, logp/value/reward/done., RolloutBuffer (+33 more)

### Community 29 - "IcsEngagement"
Cohesion: 0.06
Nodes (21): IcsEngagement, ControlModeState, Автомат включения. `step(inputs)` вызывается каждый такт до формирования…, Полный сброс — новый эпизод начинается с невключённого состояния., Сообщить автомату, что кадр **фактически ушёл** на стенд. Вызывается…, Подхватить уже включённый извне пробег: шлём `ControlMode = Rollout`.…, Войти в пробег самостоятельно: шлём `ControlMode = Rollout`. Это же — передача…, Войти в заход самостоятельно: шлём `ControlMode = Approach`. Обычно вызывать не… (+13 more)

### Community 30 - "XPlaneConnectX"
Cohesion: 0.08
Nodes (13): XPlaneConnectX class initialization. Args: ip (str, optional): IP address where…, Starts a recording of the subscribed DataRefs into self.recorded_data. Data is…, Terminates the recording and returns a dictionary of lists that contain the…, Synchronize measurements from multiple sensors to a common frequency.…, Gets the current value of a DataRef. This is only intended for one-time use.…, Permanently subscribe to a list of DataRefs with a certain frequency. This is…, Writes a value to the specified DataRef provided that the DataRef is writable.…, Sends simulator commands to the simulator. These are not commands for the… (+5 more)

### Community 31 - "fakes.py"
Cohesion: 0.08
Nodes (25): ICSBenchConnector, IcsEngagement, get_aircraft_profile(), Профили преобразования команд ИСМПУ в органы управления X-Plane., Константы интерфейса стенда заказчика (ПИВ / ICS). Единый источник правды по…, _destination(), get_runway_profile(), Профили ВПП и разрешение ILS из установленной базы X-Plane. (+17 more)

### Community 32 - "WeatherState"
Cohesion: 0.11
Nodes (22): _as_dict(), contract_for(), Any, Контракт воспроизводимости эпизода (шаг 6). Заимствовано из…, Сколько раз прогнать сценарий, чтобы результат приёмки что-то значил., Худшая реплика по заданной метрике. Приёмка смотрит именно на худшую, а не на…, Источники случайности на стороне стенда, активные при данных условиях. Мы…, Что в эпизоде детерминировано, что нет, и сколько реплик из-за этого нужно. (+14 more)

### Community 33 - "Graphify Pipeline"
Cohesion: 0.08
Nodes (29): Folder Watcher, URL Ingestion, Extra Graph Exports, MCP Graph Server, Confidence Audit Trail, Deterministic Node IDs, Semantic Extraction Contract, Cross-Repository Graph Merge (+21 more)

### Community 34 - "XPlaneConnector"
Cohesion: 0.07
Nodes (11): DataRefSample, Discard pre-reload values so readiness cannot use stale telemetry., Одна подписка, один поток приёма и явное освобождение ресурсов., Send basic controls to the ego aircraft. There are hundreds of DataRefs that…, Разобрать пакет; публично для детерминированных mock-тестов., Совместимое read-only представление старого XPlaneConnectX., Совместимость с прежним клиентом., XPlaneConnector (+3 more)

### Community 35 - "telemetry"
Cohesion: 0.07
Nodes (32): decode_outputs(), on_ground(), Готовый кадр `Telemetry` для прямых вызовов `control_step(dt, telemetry,…, Отправленные команды в нормированном виде — для сравнения траекторий.…, `ICSOutputs` → (brake_l, brake_r, thr_l_rate, thr_r_rate, steer), всё…, Кадр «ВС на полосе»: обжаты все стойки, курс/координаты у порога UUEE 06R., telemetry(), NWS_FAIL отключает стойку/педаль, но оставляет руль и дифференциальные органы. (+24 more)

### Community 36 - "GainSpace"
Cohesion: 0.18
Nodes (9): GainKey, GainSpace, Any, ArrayLike, float64, GainMap, NDArray, RegulatorKey (+1 more)

### Community 37 - "test_ics_engagement.py"
Cohesion: 0.15
Nodes (29): _engine(), Автомат включения управления на стенде. Два раздельных предмета проверки: *…, По ICD стенд должен два секунды ПОЛУЧАТЬ ModeAIReady=1. Если считать одно лишь…, Что бы мы ни слали, включены мы только когда стенд ответил AgentIsActive = 1., Единичный потерянный пакет не должен «выключать» нас на такт., Валидный кадр с AgentIsActive = 0 — стенд снял активацию, значит и мы больше не…, `ControlMode` нет во входной структуре, поэтому подхват опирается на фазу…, Обжатие стоек на пробеге истинно всегда — если переходить по нему, пробег был… (+21 more)

### Community 38 - "test_diagnostic_tools.py"
Cohesion: 0.20
Nodes (19): build_altitude_sweep(), command_for_pulse(), Безопасные elevator/altitude authority sweep без дублирования ICS runner., Чистое преобразование, пригодное и для dry-run, и для ICSSim., safety_reason(), SweepLimits, SweepPulse, validate_pulse() (+11 more)

### Community 39 - "test_ics_sim.py"
Cohesion: 0.06
Nodes (37): select_for_telemetry(), ICSSim, SimInterface, Обмен со стендом заказчика: телеметрия внутрь, команды наружу. Управление…, Принимает ли стенд наши команды. До включения любой `step` уходит вхолостую., Войти в пробег самостоятельно (`ControlMode 0 → 3`)., ShutdownReport, FakeConnector (+29 more)

### Community 40 - "pid_controller.py"
Cohesion: 0.10
Nodes (29): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+21 more)

### Community 41 - "scenarios.py"
Cohesion: 0.06
Nodes (45): Настройки воздушного участка: заход по ILS, выравнивание, управление скоростью.…, Глобальные константы контура управления (перенесены из main.ipynb)., Приёмочные пороги из ТЗ (раздел 5). Единый источник истины для reward-шейпинга…, ConditionMatch, match_conditions(), WeatherState, Единая профильная модель сценариев всего интервала полёта. `Scenario` —…, Сверка ожидаемых условий с фактической телеметрией backend. (+37 more)

### Community 42 - "NPGS"
Cohesion: 0.16
Nodes (13): floating, NPGS, float32, NDArray, Tensor, Neural PID Gain Scheduler: общий энкодер + головы актора (абс. gain'ы) + голова…, → (mean (B,17), value (B,), phase_logits (B,n_phases))., 17 сырых выходов → [абс. gains×15, w_lon, w_lat] (layout `REGULATOR_ORDER` +… (+5 more)

### Community 43 - "ICSInputs"
Cohesion: 0.12
Nodes (31): ControlResult, ICSInputs, ICSOutputs, Неизвестные поля исходного JSON; они доступны аудиту, но не закону управления., airborne_control_mode(), airborne_flare_mode(), deactivate(), live_main() (+23 more)

### Community 44 - "shield.py"
Cohesion: 0.07
Nodes (52): float32, GainMap, NDArray, Абсолютные коэффициенты пресета → `target_z` (17,): gains через `inv_gain`,…, target_z_from_gains(), apply_gains_to_pids(), base_gains_from_pids(), PidMap (+44 more)

### Community 45 - "3. Этапы реализации"
Cohesion: 0.09
Nodes (21): 1. Подтверждённые проблемы и целевое состояние, 2. Ключевые интерфейсы, 3. Этапы реализации, 4. Тестирование и критерии готовности, 5. Зафиксированные допущения, 6.1. Один dashboard вместо двух, 6.2. Единый источник данных, 6.3. Представления (+13 more)

### Community 46 - "ScenarioGenerator"
Cohesion: 0.13
Nodes (12): Any, Serialize only the canonical profile-aware schema v2., Один случайный сценарий. `difficulty=None` → случайная сложность., ScenarioGenerator, test_battery_covers_key_cases_and_roundtrips(), test_generator_embeds_control_config(), test_generator_high_difficulty_produces_failures(), test_generator_is_deterministic_for_same_seed() (+4 more)

### Community 47 - "ControlModeState"
Cohesion: 0.27
Nodes (8): ControlModeState, EngagementInputs, EngagementState, Enum, Автомат включения управления на стенде заказчика. Стенд принимает наши команды…, Передать управление в руление (`ControlMode 3 → 4`). → удался ли переход.…, Состояние **исходящего стимула** (что мы шлём стенду), а не факта включения.…, Признаки со стенда, от которых зависит рукопожатие. `agent_is_active` —…

### Community 48 - "RunRecorder"
Cohesion: 0.15
Nodes (11): default_runs_root(), gains_snapshot(), Path, Единый CSV-регистратор прогонов ICS и X-Plane., Единый каталог прогонов, не зависящий от cwd процесса/Jupyter., Один раз сохранить накопленные кадры и итоговые артефакты прогона., RunRecorder, test_recorder_keeps_all_known_ics_fields_and_unknown_raw_fields() (+3 more)

### Community 49 - "test_full_flight.py"
Cohesion: 0.11
Nodes (28): initial_segment(), is_airborne(), FlightSegment, Сообщает ли стенд, что ВС в воздухе и достаточно высоко для приёма захода.…, С какого участка начинать. Пробег — ответ по умолчанию (см. модуль)., _air(), _Clock, _pump() (+20 more)

### Community 50 - "test_go_around.py"
Cohesion: 0.17
Nodes (21): _armed_controller(), _drive(), _frame(), Уход на второй круг (fallback в воздухе): условия срабатывания и передача…, Если реверс уже включён — взлёт невозможен, ухода нет., Устойчивый набор (прирост высоты + положительная верт. скорость) завершает…, После установившегося набора цикл снимает заявку каналов (ControlMode=Off,…, Контур на заходе: `begin_flight` по кадру в воздухе выше 400 футов. (+13 more)

### Community 51 - "Neural PID Gain Scheduler Architecture"
Cohesion: 0.19
Nodes (19): Hybrid Neural PID Controller, Neural PID Gain Scheduler, PPO Training Loop, Preset-Anchored Deterministic Shield, SFT Behavioral-Cloning Warm Start, Absolute-Gain Action Space, Classical PID as the Plant, Deterministic Deployment Runtime (+11 more)

### Community 52 - "test_approach_criteria.py"
Cohesion: 0.19
Nodes (12): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, Отдельный монитор критерия А.1.1 (не участвует в go-around)., Захватывает А.1.1 после входа в допуск и завершает оценку на 300 ft., frame() (+4 more)

### Community 53 - "test_tolerance.py"
Cohesion: 0.17
Nodes (21): evaluate_approach_tolerances(), _glideslope_tolerance_deg(), ApproachLimits, ApproachTelemetry, Монитор допусков захода в реальном времени + классификация особой ситуации.…, Результат проверки допусков захода на одном такте. `landing_allowed` — все ли…, Допуск по глиссаде с учётом отказа (ТЗ 5.1.2.1–5.1.2.3), самый мягкий из…, Диагностическая градация приборной скорости по огибающей механизации. (+13 more)

### Community 54 - "gui/dashboard.py"
Cohesion: 0.14
Nodes (12): _finite_or_none(), GainUpdateRequest, _jsonable(), Unified local dashboard for the three airborne and five ground PIDs., Валидировать HTTP-запрос и передать запись control-потоку., Применяется только control-потоком в начале такта., ViewSpec, controller_pids() (+4 more)

### Community 55 - "RunwayTracker"
Cohesion: 0.15
Nodes (7): Точка на продолжении оси; положительное расстояние — до порога., Решить прямую геодезическую задачу на сферической Земле., Возвращает отклонение от осевой линии в метрах. >0 - правее оси, <0 - левее., Геодезическое наведение на ось ВПП с упреждением по скорости., RunwayTracker, GainSpace, test_runway_profile_delegates_geometry_to_tracker()

### Community 56 - "RomanLogImporter"
Cohesion: 0.19
Nodes (10): _number(), Path, Импорт и проверка внешних CSV-прогонов roman_aviacia_ics., Потоково нормализует основной и authority CSV Романа., RomanLogImporter, verify_manifest(), fixture, roman_csv() (+2 more)

### Community 57 - "working_ics/approach_criteria.py"
Cohesion: 0.21
Nodes (7): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, ICSInputs, Evaluate the A.1.1 approach segment and stop at a radio-altitude floor.

### Community 58 - "parse_ils_station"
Cohesion: 0.43
Nodes (6): find_earth_nav_dat(), ILSStation, parse_ils_station(), Path, Найти LOC (тип 4) без хардкода частоты., test_earth_nav_parser_finds_requested_localizer()

### Community 59 - ".send_outputs"
Cohesion: 0.33
Nodes (5): _integrate_throttle(), Ход рычага РУД за такт: интеграл команды-скорости, зажатый физическим…, Доля обратной тяги по фактическому углу РУД: 0 в положительном секторе, 1 на…, Замедление считается по **фактическому** углу РУД, а не по команде. Тягой…, _reverse_fraction()

### Community 60 - "gain_space_for"
Cohesion: 0.09
Nodes (30): ActorOutput, _init_log_std(), layer_init(), _mlp_head(), ArrayLike, TypedDict, Neural PID Gain Scheduler (NPGS) — актор + критик (план §10; выход — АБСОЛЮТНЫЕ…, Per-output log_std: gain-слоты `log(frac)−log(s_i)` (равномерный мульт. шаг),… (+22 more)

### Community 61 - "ReferenceTrajectory"
Cohesion: 0.13
Nodes (12): LongitudinalChannel, LongitudinalDiagnostics, Блок 1: скорость → симметричная база тормозов и реверса., Сбросить PID и привязать начало профиля к фактической скорости касания/старта., Генератор эталонной кривой скорости (Колокол Гаусса)., Начать профиль с фактической скорости текущего участка., То же без лишнего round-trip м/с → узлы → м/с на касании., Возвращает идеальную скорость (м/с) для текущей точки пути. (+4 more)

### Community 62 - "Project Dependencies"
Cohesion: 0.18
Nodes (13): Autonomous Landing Controller, Repository Guidance for Codex, Autonomous Landing Controller, Repository Guidance for Claude Code, Neural Landing Implementation Plan, Unified Scenario System, Optional Gymnasium, NumPy (+5 more)

### Community 63 - ".from_ics"
Cohesion: 0.10
Nodes (19): `ICSInputs` → `Telemetry`: поля в СИ + «сырой» пакет для property. Стенд отдаёт…, engaged_inputs(), Кадр стенда, который уже принял управление: `AgentIsActive = 1`, идёт пробег., Носовая стойка обжимается позже основных — ждать её значит пропустить начало…, «Козление» после касания снимает обжатие на секунду — назад в заход…, В такте касания команда обязана быть уже наземной, а не последней командой…, Таблицы захода МС-21 к чистому крылу неприменимы — вести по ним нельзя.…, Нулевое отклонение при снятой валидности неотличимо от «точно на оси». (+11 more)

### Community 64 - "GuidanceState"
Cohesion: 0.18
Nodes (5): GuidanceState, Геодезическое guidance в истинной системе направлений., Guidance по курсу ВПП и измеренному отклонению — без собственной геодезии.…, Совместимость с прежним атрибутом; новый термин явно указывает ось., Совместимость со старым словарным API.

### Community 67 - "heading_deviation_deg"
Cohesion: 0.19
Nodes (12): heading_deviation_deg(), Отклонение курса ВС от направления ВПП — приёмочная величина ТЗ 5.1.3.3 /…, Телеметрия ВС на оси ВПП, смещённого вбок на `offset_m` и с заданным курсом.…, ТЗ 5.1.3.3 нормирует курс «от направления ВПП». Смещение от оси на него не…, На стенде курс ВПП приходит телеметрией; конфиг — только значение по умолчанию., Таблица из находки: раньше оба случая давали противоположный результат., _telemetry_at(), test_heading_deviation_ignores_lateral_offset() (+4 more)

### Community 68 - "test_working_ics_dashboard.py"
Cohesion: 0.35
Nodes (10): ClearWeatherILSController, DashboardState, _controller(), _inputs(), Characterization tests for the bench-validated ``working_ics`` dashboard., _record(), test_dashboard_records_four_airborne_views_and_diagnostics(), test_gain_updates_are_immediate_validated_and_share_pitch_with_flare() (+2 more)

### Community 70 - "_descent_frames"
Cohesion: 0.17
Nodes (12): _colleague_controller(), _descent_frames(), Страховка от самообмана: сценарий обязан пройти выравнивание, иначе паритет его…, `ElevatorCmd` — перегрузка в g, и предел ±0.5 действует и на глиссаде, и в…, Контура парирования сноса нет — наземный контур обязан принимать ВС со сносом., Оригинальный контур коллеги, настроенный тем же файлом. `None`, если…, Сценарий снижения: высота падает, планка курса и глиссады «дышит», тангаж…, Перенос обязан совпадать с подтверждённым на стенде оригиналом, а не «вести… (+4 more)

### Community 71 - "Unified Profile-Aware Scenario System"
Cohesion: 0.22
Nodes (9): Technical-Specification Acceptance Gates, Bench-Validated ILS Approach Channel, Forward-Only Flight Segment Supervisor, Tolerance-Gated Go-Around, Longitudinal and Lateral Ground Channels, PID Run Matrix, Unified Profile-Aware Scenario System, Legacy Scenario Preset Model (+1 more)

### Community 72 - "Interactive PID Dashboard"
Cohesion: 0.25
Nodes (9): Nine-View PID Dashboard, Run Recording Artifacts, buildTabs, draw, Gain Tuning and Snapshot Export, Interactive PID Dashboard, refresh, render (+1 more)

### Community 74 - "ClearWeatherILSController"
Cohesion: 0.14
Nodes (7): DashboardServer, DashboardState, Any, ICSInputs, ClearWeatherILSController, test_roundout_commands_a_material_pitch_increase_before_touchdown(), test_terminal_pitch_hold_starts_before_last_five_feet_guidance_cutoff()

### Community 75 - "splits.py"
Cohesion: 0.11
Nodes (16): _hash_unit(), is_signature_holdout(), PartitionedScenarioProvider, Детерминированное разбиение сценариев на обучение и holdout (шаг 6). Схема…, SHA-256 от идентификатора → число в [0, 1). Стабильно между запусками и…, Устойчивая комбинация условий, а не имя или целое семейство отказов., Каноническая дискретизация условий для train/eval split., Фильтр над единым sampler с непересекающимися train/eval signatures. (+8 more)

### Community 76 - "ICSInterface.cs"
Cohesion: 0.36
Nodes (7): External.Systems.ICS, ControlModeState, GearState, ICSInputs, ICSOutputs, ReverseEngineType, UInt64

### Community 77 - ".enter_segment"
Cohesion: 0.20
Nodes (5): FailureMode, FlightSegment, Scenario, Применить только дельту условий при переходе между участками., Снять один отказ, не переинициализируя отказ, продолжающийся на новом участке.

### Community 78 - "EpisodeObjective"
Cohesion: 0.20
Nodes (8): EpisodeObjective, Накопитель по эпизоду: собирает потактовые отсчёты → сводные компоненты.…, Фиксированный приёмочный набор (детерминированный, без RNG)., Отсутствие данных даёт None, а не 0 — приёмка обязана трактовать это как FAIL., p95 темпа не ловится одиночным выбросом — в отличие от максимума., test_episode_objective_p95_rate_is_robust_to_a_single_spike(), test_episode_objective_reports_none_for_unobserved_phases(), test_episode_objective_separates_rollout_and_taxi_phases()

### Community 80 - "ICS PID Monitor"
Cohesion: 0.29
Nodes (7): buildControls, draw, formatTime, Four-Loop PID Tuning, ICS PID Monitor, Live and Historical Timeline, refresh

### Community 81 - "VlaydRolloutBridge"
Cohesion: 0.13
Nodes (12): ICSBenchConnector, main(), Мост к стенду: JSON поверх UDP, адрес стенда определяется из входящего пакета., Приём телеметрии стенда. Адрес отправителя определяется автоматически., Отправка управления на стенд. → отправлено ли (исключение наружу не…, Диагностический приём телеметрии. Управление отсюда **не выдаётся**. Прежняя…, ICSInputs, socket (+4 more)

### Community 82 - "ICS UDP JSON Protocol"
Cohesion: 0.33
Nodes (6): Fourteen-Bit ControlValidMask Layout, Dual-Backend SimInterface, Two-Factor ICS Engagement Handshake, ICS UDP JSON Protocol, Telemetry SI Unit Boundary, ICS-Only Backend Guidance

### Community 83 - "X-Plane Dashboard and Runtime Guide"
Cohesion: 0.60
Nodes (6): Aircraft-Profile Checkpoint Isolation, Live A330 Acceptance Checklist, Profile-Aware Flight Scenarios, X-Plane Dashboard and Runtime Guide, X-Plane Resettable Runtime, X-Plane Training and Evaluation Backend

### Community 84 - "ApproachConfig"
Cohesion: 0.25
Nodes (7): ApproachConfig, _pid_from_colleague(), Загрузка настроек из JSON коллеги (`config/ics_clear_weather_pid.json`). Секции…, `PIDConfig` коллеги → аргументы нашего `PIDController`. Предел интегратора у…, Параметры воздушного контура. Значения по умолчанию — настроенные на стенде.…, Наши умолчания и его файл — одно и то же. Разойдутся — расхождение должно быть…, test_config_from_the_colleague_json_matches_our_defaults()

### Community 85 - "ControlsState"
Cohesion: 0.15
Nodes (11): ControlsState, Обнуляет все органы управления. Отправку делает вызывающий через `ICSSim.step`.…, Совместимое имя старого API; колёсные органы оно больше не обозначает., Разделяемая по тактам структура команд — и наземных, и воздушных. Аннотации…, Сброс к нейтральным командам — новый эпизод начинается с чистого состояния.…, Обнулить только воздушные команды. Нужно, когда воздушный канал не может…, Копия команды такта — для расчёта джерка на следующем такте. Копируется…, _snapshot_command() (+3 more)

### Community 86 - "DashboardState"
Cohesion: 0.18
Nodes (9): DashboardState, _handler_factory(), Path, Thread-safe live state or an immutable CSV replay., configured_controller(), test_capture_export_and_replay_common_run(), test_dashboard_http_api_is_local_and_monitor_only(), test_monitor_only_and_npgs_tuning_locks() (+1 more)

### Community 87 - "_Clock"
Cohesion: 0.13
Nodes (17): _Clock, _pump(), Обратная защита: 30 кадров можно выпалить за 0.1 с — время тоже обязано пройти., Срыв предусловия обнуляет и время, и счётчик кадров., Требование ICD — непрерывность: пропуск готовности рвёт серию., Неудачная отправка (сокет вернул False) выдержку не продвигает., Порог задан в узлах. 1.5 узла — стимул идёт; 2.9 узла — нет. Пересчёт…, Прямой тест главного дефекта: наша выдержка 2 с сама по себе включения не даёт. (+9 more)

### Community 88 - "FrictionProfile"
Cohesion: 0.18
Nodes (5): FrictionProfile, Any, Сериализация в примитивы (для логирования/воспроизводимости сценариев)., Ступенчатый профиль сцепления по дистанции пробега., test_weather_roundtrips_through_dict()

### Community 89 - "envelope.py"
Cohesion: 0.12
Nodes (23): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+15 more)

### Community 91 - "test_action_contract.py"
Cohesion: 0.13
Nodes (16): ControlArchitecture, Фиксированный порядок слоёв и роль обучаемого компонента., Проверяет контракт обучаемого слоя. Нарушение → `ValueError` на старте…, validate_action_contract(), Контракт обучаемого слоя (Этап 4): что именно сеть имеет право менять. Аргумент…, Пустое обоснование = контракт непредъявим по ТЗ., Машиночитаемое утверждение «сеть не является регулятором»., Список запретов должен совпадать с реальными полями команд, иначе он… (+8 more)

### Community 92 - "roll_limit_deg"
Cohesion: 0.50
Nodes (4): Предел крена по высоте: чем ниже, тем меньше запас до касания законцовкой.…, roll_limit_deg(), Чем ниже, тем меньше запас до касания законцовкой; настроенный предел не…, test_roll_limit_tightens_towards_the_ground()

### Community 93 - "_WarmUpSim"
Cohesion: 0.13
Nodes (13): ObserverEstimate, Оценки PINN-обсервера (§12). Заглушка нулями до Этапа 7., RewardWeights, EpisodeInfo, _make_box(), TypedDict, Минимальная замена gym.spaces.Box, когда gymnasium не установлен., _SimpleBox (+5 more)

### Community 94 - "test_ground_controller.py"
Cohesion: 0.16
Nodes (17): _lost_engagement(), SimInterface, Снял ли стенд активность посреди прогона. → пора останавливаться. Без этой…, Прогоняет один полёт на уже настроенном контуре., run(), RunResult, _direct_ground_frame(), Контракты наземного контура этапа 2. (+9 more)

### Community 95 - "reward.py"
Cohesion: 0.13
Nodes (18): _command_jerk(), _effort_saturated(), _ground_steering(), ObjectiveWeights, _p95(), Objective — единое определение «хорошего пробега» (§11 + приёмка ТЗ разд. 5).…, Упёрлась ли команда в границу **со стороны усилия**. Важное различие: нулевая…, Доля из 5 команд, исчерпавших авторитет (упёршихся в ненулевую границу PID).… (+10 more)

### Community 109 - "FlightPhase"
Cohesion: 0.67
Nodes (3): FlightPhase, IntEnum, Фаза полёта, сообщаемая стендом (`ICSInputs.FlightPhase`).

### Community 110 - "._should_go_around"
Cohesion: 0.40
Nodes (3): Реверс убран: команды обратной тяги нулевые. В воздухе реверс не выдаётся…, Нужно ли уходить на второй круг по этому такту. → причина или `None`. Только…, ToleranceReport

### Community 111 - "Q: Реализовать этап 0: baseline, golden replay и dashboard characterization"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Реализовать этап 0: baseline, golden replay и dashboard characterization, Source Nodes

### Community 112 - "Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md)., Source Nodes

### Community 114 - ".build"
Cohesion: 0.13
Nodes (13): clip_unit(), linear(), log_norm(), Лог-нормировка неотрицательной величины (видимость): log1p(x)/log1p(scale)., Отображает [lo, hi] → [-1, 1] (для PID output по его границам)., symmetric(), WeatherState, Фактические погодные условия со стенда (ветер, сцепление, осадки, видимость). (+5 more)

### Community 115 - "engaged_sim"
Cohesion: 0.12
Nodes (16): engaged_sim(), (sim, connector) с завершённым рукопожатием: стенд подтвердил `AgentIsActive =…, Регресс: расширение структуры не должно протащить руль высоты в маску пробега., test_ground_frame_still_declares_only_the_ground_channels(), Разделение органов из таблицы Заказчика: тиллер — на рулении, педальный пост —…, Базовый контур на стенде: `control_step` сам читает телеметрию и сам отправляет., На стенде каждый лишний `read_telemetry` — лишний приём UDP. Кадр, вернувшийся…, Замолчать нельзя: последнее отклонение осталось бы приложенным до сторожа на… (+8 more)

### Community 116 - "test_rollout_env.py"
Cohesion: 0.19
Nodes (13): ObservationBuilder, Строит нормированный вектор наблюдения одного кадра., Тесты Этапа 2: Observation/Action/reward/RolloutEnv + инвариант identity ==…, Без аннотаций типов @dataclass не видит полей, и тогда любые два экземпляра…, Свежий экземпляр обязан нести все поля в собственном `__dict__`. Без аннотаций…, `break_control` взводится в конце КАЖДОГО нормального пробега (достигнута…, _ready_controller(), test_break_control_is_cleared_when_a_scenario_is_applied() (+5 more)

### Community 123 - "test_control_parity.py"
Cohesion: 0.15
Nodes (12): Тесты паритета после выноса контура из main.ipynb в пакет ismpu. Полный паритет…, test_control_step_stops_and_sends_nothing_on_missing_telemetry(), test_default_preset_leaves_all_actuators_healthy(), test_guidance_on_centerline_small_heading_error(), test_pid_anti_windup_clamp(), test_pid_filtered_derivative(), test_pid_output_clamped_to_bounds(), test_pid_proportional_and_integral_accumulation() (+4 more)

### Community 124 - ".read_telemetry"
Cohesion: 0.18
Nodes (6): EngagementInputs, Начало эпизода: сброс рукопожатия и первый кадр со стенда. Средой распоряжается…, Гонит стимул рукопожатия, пока стенд не подтвердит включение (`AgentIsActive =…, Передать управление в руление (`3 → 4`) — по решению вызывающего, что пробег…, Признаки для автомата включения. `agent_is_active` — подтверждение стенда:…, StartMode

### Community 125 - "ApproachRefused"
Cohesion: 0.22
Nodes (7): ApproachRefused, Воздушный участок начинать нельзя — с названной причиной. Отдельное исключение,…, FlightSegment, Пересобрать stateful PID и уведомить backend до первого такта участка., Определить стартовый участок по кадру стенда. → выбранный участок. Вызывается в…, Досчитать отложенное решение об участке на первом пригодном кадре., Передать управление с захода на пробег (`ControlMode 1 → 3`). Момент — первое…

### Community 126 - ".compute"
Cohesion: 0.20
Nodes (4): → (интеграл только с утечкой, интеграл с утечкой и приращением). Оба уже зажаты., Такт регулятора. `measurement` обязателен при `derivative_on_measurement=True`., Back-calculation: подтянуть интегратор к фактически применённой команде. No-op…, Вес апериодического фильтра D-составляющей за такт `dt`.

### Community 127 - ".summary"
Cohesion: 0.20
Nodes (9): _component(), excess(), graded(), Компоненты `{raw, weight, weighted}` + `total_loss`/`reward` + диагностика., Чистый hinge: превышение допуска, нормированное на допуск. Внутри допуска = 0., Штраф с гейтом ТЗ: мягкий линейный наклон внутри допуска + резкий рост за…, Ровно на пороге ТЗ штраф = наклон внутри полосы; дальше растёт много круче., test_excess_is_zero_inside_the_tolerance() (+1 more)

### Community 128 - "_engaged_airborne_sim"
Cohesion: 0.22
Nodes (9): IntFlag, ControlValid, Биты `ControlValidMask`: какие каналы несёт команда. **Один бит на одно…, _engaged_airborne_sim(), (sim, conn), где стенд уже принял воздушное управление (`ControlMode =…, ТЗ 5.1.5: показатели выдерживания — отчёт, идущий вместе с командой., test_airborne_frame_carries_the_commands_in_icd_units(), test_airborne_frame_declares_only_the_airborne_channels() (+1 more)

### Community 129 - ".invalid"
Cohesion: 0.22
Nodes (7): Кадр «связи со стендом нет». Нули, а не None: контур проверяет `valid` первым., Path, Стенд при обрыве связи отдаёт НУЛИ с valid=False, а не None. Проверка «поле is…, test_control_step_stops_on_invalid_frame_even_with_numeric_fields(), Первый `read_telemetry` может вернуться по таймауту — это не «мы на полосе».…, test_the_segment_is_not_decided_by_a_frame_without_a_bench_packet(), XPlaneConnector

### Community 130 - "HandshakeBench"
Cohesion: 0.25
Nodes (4): HandshakeBench, KinematicBench, Стенд, включающий управление только после корректного рукопожатия. Ждёт…, Мини-модель стенда: замедление ~ команде тормоза/реверса, ход вдоль осевой ВПП.…

### Community 131 - "control.py"
Cohesion: 0.43
Nodes (4): apply_ground_control(), build_pids(), Сборка классического контура из неизменяемой конфигурации., Фабрики stateful-объектов; config-модули хранят только данные.

### Community 132 - "_cold_sim"
Cohesion: 0.29
Nodes (7): _cold_sim(), Сквозной прогрев: маска нулевая, пока стенд не подтвердил `AgentIsActive = 1`., Темп задаётся часами, а не sleep. Со сломанным (или подменённым) sleep наивный…, Молча продолжить нельзя: дальше мы бы «управляли» в пустоту., test_cold_ground_start_engages_only_after_the_bench_confirms(), test_warm_up_paces_itself_and_does_not_flood_the_bench(), test_warm_up_timeout_raises_with_a_diagnosis()

### Community 133 - ".blocking_reason"
Cohesion: 0.33
Nodes (3): Сколько уже держится выдержка. 0.0, если отсчёт не идёт (для диагностики)., Почему включение ещё не произошло — для диагностики при таймауте прогрева.…, Слепок для логов и отчётов приёмки.

### Community 135 - "Q: Приступай к выполнению этапа 2 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 2 плана docs/plan.md, Source Nodes

### Community 136 - "_faults_from_inputs"
Cohesion: 0.40
Nodes (4): ICSInputs, _faults_from_inputs(), Отказы, о которых сообщает борт — **единственный** источник истины об отказах.…, Сигналы отказов со стенда → наши `FailureMode`. Отказы шасси…

### Community 137 - "pid.py"
Cohesion: 0.40
Nodes (3): PIDDiagnostics, Пропорционально-интегрально-дифференциальный регулятор. Класс сохраняет прежнюю…, Типизированный снимок последнего такта регулятора.

### Community 138 - "GoAroundManeuver"
Cohesion: 0.50
Nodes (3): GoAroundManeuver, Начать уход: зафиксировать состояние манёвра и высоту входа., Состояние идущего ухода на второй круг. Пока он активен, заход не ведётся.

### Community 139 - "_legacy_reference"
Cohesion: 0.67
Nodes (3): _legacy_reference(), Независимая реализация ПРЕЖНЕЙ численности — эталон для проверки парити., test_defaults_reproduce_the_legacy_numerics_bit_for_bit()

## Ambiguous Edges - Review These
- `Unified Profile-Aware Scenario System` → `Legacy Scenario Preset Model`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to
- `Dual-Backend SimInterface` → `ICS-Only Backend Guidance`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **58 isolated node(s):** `1. Подтверждённые проблемы и целевое состояние`, `2. Ключевые интерфейсы`, `Этап 0 — Зафиксировать воспроизводимый baseline`, `Этап 1 — Исправить границу телеметрии и ложный XTE`, `Этап 2 — Пересобрать наземный контроллер` (+53 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **50 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `ObservationBuilder` (2× useful, score=1.961919599) _(code changed — re-verify)_

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Unified Profile-Aware Scenario System` and `Legacy Scenario Preset Model`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Dual-Backend SimInterface` and `ICS-Only Backend Guidance`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `ControllingSystem` connect `ControllingSystem` to `_engaged_airborne_sim`, `.invalid`, `compute_reward`, `control.py`, `test_refactoring_contracts.py`, `DatagramSocket`, `ScriptedFlightBench`, `GroundControlAllocator`, `LateralChannel`, `GoAroundManeuver`, `Scenario`, `test_pretrain.py`, `test_run_matrix.py`, `test_control_step_is_unchanged_when_tracking_is_off`, `ApproachChannel`, `Telemetry`, `test_gain_scheduler.py`, `PIDController`, `FailureMode`, `RolloutEnv`, `test_xplane_backend.py`, `test_evaluate.py`, `test_ppo.py`, `XPlaneConnector`, `telemetry`, `test_ics_sim.py`, `scenarios.py`, `shield.py`, `RunRecorder`, `test_full_flight.py`, `test_go_around.py`, `test_approach_criteria.py`, `ReferenceTrajectory`, `.from_ics`, `VlaydRolloutBridge`, `ControlsState`, `DashboardState`, `test_action_contract.py`, `_WarmUpSim`, `test_ground_controller.py`, `reward.py`, `._should_go_around`, `engaged_sim`, `test_rollout_env.py`, `test_control_parity.py`, `ApproachRefused`?**
  _High betweenness centrality (0.163) - this node is a cross-community bridge._
- **Why does `Telemetry` connect `Telemetry` to `.invalid`, `HandshakeBench`, `weather.py`, `test_refactoring_contracts.py`, `test_approach_channel.py`, `ControllingSystem`, `_faults_from_inputs`, `GroundControlAllocator`, `LateralChannel`, `GoAroundManeuver`, `Scenario`, `ScriptedFlightBench`, `AircraftProfile`, `ApproachChannel`, `XPlaneSim`, `FailureMode`, `test_xplane_backend.py`, `fakes.py`, `telemetry`, `test_diagnostic_tools.py`, `test_ics_sim.py`, `scenarios.py`, `RunRecorder`, `test_full_flight.py`, `test_go_around.py`, `test_approach_criteria.py`, `test_tolerance.py`, `ReferenceTrajectory`, `.from_ics`, `heading_deviation_deg`, `.enter_segment`, `VlaydRolloutBridge`, `ControlsState`, `_WarmUpSim`, `test_ground_controller.py`, `._should_go_around`, `.build`, `test_rollout_env.py`, `test_control_parity.py`, `.read_telemetry`, `ApproachRefused`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `ControlsState` connect `ControlsState` to `compute_reward`, `Shield`, `_cold_sim`, `SimInterface`, `test_approach_channel.py`, `ControllingSystem`, `DatagramSocket`, `GroundControlAllocator`, `GoAroundManeuver`, `AircraftProfile`, `._fill_ground`, `ApproachChannel`, `Telemetry`, `XPlaneSim`, `PIDController`, `RolloutEnv`, `test_xplane_backend.py`, `fakes.py`, `test_diagnostic_tools.py`, `test_ics_sim.py`, `scenarios.py`, `ICSInputs`, `shield.py`, `ReferenceTrajectory`, `_descent_frames`, `EpisodeObjective`, `ShutdownReport`, `test_action_contract.py`, `_WarmUpSim`, `reward.py`, `engaged_sim`, `test_rollout_env.py`, `.read_telemetry`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `ControllingSystem` (e.g. with `AircraftControlSet` and `ApproachSetup`) actually correct?**
  _`ControllingSystem` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Are the 41 inferred relationships involving `ControlsState` (e.g. with `GainCommand` and `RuntimeState`) actually correct?**
  _`ControlsState` has 41 INFERRED edges - model-reasoned connections that need verification._