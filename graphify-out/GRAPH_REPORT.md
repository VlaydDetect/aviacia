# Graph Report - GOSNIIASProject  (2026-08-16)

## Corpus Check
- 146 files · ~170,099 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2740 nodes · 6388 edges · 166 communities (113 shown, 53 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 547 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9e6742fc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_tolerance.py
- GainCommand
- RolloutEnv
- channels.py
- Shield
- test_refactoring_contracts.py
- SimInterface
- airborne_inputs
- scenarios.py
- GainSpace
- ground_allocator.py
- LateralChannel
- test_pretrain.py
- ControlsState
- test_ics_connector.py
- scenario_for_matrix_run
- AircraftProfile
- ICSSim
- control/approach.py
- Telemetry
- gain_scheduler.py
- XPlaneSim
- WeatherState
- PIDController
- Policy
- .step
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
- Scenario
- test_ics_engagement.py
- run_reader.py
- test_ics_sim.py
- pid_controller.py
- xplane_sim.py
- NPGS
- ICSOutputs
- test_gain_scheduler.py
- 3. Этапы реализации
- ScenarioGenerator
- ics_engagement.py
- Path
- test_full_flight.py
- system.py
- Neural PID Gain Scheduler Architecture
- test_approach_criteria.py
- flight.py
- run_artifacts.py
- RunwayTracker
- RomanLogImporter
- working_ics/approach_criteria.py
- test_profiled_scenarios.py
- ScriptedFlightBench
- gain_space_for
- ReferenceTrajectory
- Project Dependencies
- .from_ics
- test_control_parity.py
- ICSInputs
- DashboardState
- test_rollout_env.py
- test_working_ics_dashboard.py
- ICSOutputs
- agent/pretrain.py
- Unified Profile-Aware Scenario System
- Interactive PID Dashboard
- MatrixRun
- DashboardState
- evaluate.py
- ICSInterface.cs
- compute_reward
- test_run_matrix.py
- RunReader
- ICS PID Monitor
- fakes.py
- ICS UDP JSON Protocol
- X-Plane Dashboard and Runtime Guide
- test_working_ics_golden.py
- EpisodeObjective
- rollout_env.py
- ConditionMatch
- run_report.py
- test_approach_channel.py
- LongitudinalChannel
- shield.py
- static_sim
- graded
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
- protocol.py
- Q: Реализовать этап 0: baseline, golden replay и dashboard characterization
- Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md).
- ICSBenchConnector
- normalization.py
- engaged_sim
- Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md).
- LandingFlapConfiguration
- IntEnum
- ControlModeState
- ICSInputs
- ICSOutputs
- socket
- FailureState
- .from_json
- DatagramSocket
- .compute
- DashboardServer
- WeatherState
- Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md).
- HandshakeBench
- control.py
- ApproachLimits
- .enter_segment
- ApproachTelemetry
- Q: Приступай к выполнению этапа 2 плана docs/plan.md
- ICSInputs
- ._commit_landing_mode
- ShutdownReport
- ApproachConfig
- .control_step
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
- Scenario
- FrictionProfile
- Q: Приступай к выполнению этапа 4 плана docs/plan.md
- ReferenceTrajectory
- RewardWeights
- TypedDict
- ApproachSetup
- ICSInputs
- Scenario
- RunRecorder
- parametrize
- TouchdownSetup

## God Nodes (most connected - your core abstractions)
1. `ControllingSystem` - 188 edges
2. `Telemetry` - 128 edges
3. `ControlsState` - 92 edges
4. `ICSSim` - 78 edges
5. `Scenario` - 71 edges
6. `XPlaneSim` - 56 edges
7. `PIDController` - 52 edges
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
- `_Clock` --uses--> `ControllingSystem`  [INFERRED]
  tests/test_full_flight.py → ismpu/control/system.py

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

## Communities (166 total, 53 thin omitted)

### Community 0 - "test_tolerance.py"
Cohesion: 0.07
Nodes (49): lateral_limit_m(), lateral_load_situation(), lateral_situation(), normal_load_situation(), IntEnum, Критерии критичности особых ситуаций МС-21 (Приложение 1 к ТЗ). Таблица АП-25…, Классификация скорости касания относительно VAPP и VВПП пред., Классификация нормальной перегрузки посадочного удара. `heavy` — взлётный вес. (+41 more)

### Community 1 - "GainCommand"
Cohesion: 0.13
Nodes (11): _clip(), GainCommand, GainMap, RegulatorKey, Что сделал Shield за такт: активированные правила, штрафы, fallback., Уровни 1–2. Возвращает `(effective_gains, safe_command, report)`.…, Уровень 3. Правит небезопасные команды и возвращает `(command, report)`., Выход актора: абсолютные коэффициенты PID + веса каналов. `gains[reg] =… (+3 more)

### Community 2 - "RolloutEnv"
Cohesion: 0.09
Nodes (24): PPOTrainer, Tensor, Собирает rollout из среды и обновляет NPGS многокомпонентным PPO-loss., Шагает средой `rollout_len` тактов (сброс по завершению эпизода). → статистика., Хук L_shield (§11): барьер, отталкивающий выход от края уровня-1 Shield. По…, build_sim(), Any, Path (+16 more)

### Community 3 - "channels.py"
Cohesion: 0.05
Nodes (53): Геометрия целевой ВПП и высоты установки ЛА. Смена целевой полосы = правка…, Каналы управления и общий вектор команд. `ControlsState` — разделяемая по…, Слежение за осью ВПП: геодезия, cross-track error, guidance с look-ahead.…, Observation Space — сборка и нормировка вектора состояния (§5). Собирает один…, compose_wind(), decompose_wind(), Enum, Погодные условия эпизода: описание, шкала сцепления и разбор ветра. Модуль **не… (+45 more)

### Community 4 - "Shield"
Cohesion: 0.14
Nodes (25): Наблюдаемое состояние для поведенческих проверок уровня 3., Границы и веса штрафов Shield (все — настраиваемые, а не свойства сети)., Защитный контур. Детерминирован; хранит состояние прошлого такта для rate-…, Bind the guard to the same aircraft-specific space as the actor., Построение из словаря коэффициентов (напр. пресета сценария)., RuntimeState, Shield, ShieldConfig (+17 more)

### Community 5 - "test_refactoring_contracts.py"
Cohesion: 0.13
Nodes (39): approach_control_from_dict(), approach_control_to_dict(), _copy_approach(), dump_scenario(), _finite_tree(), ground_control_from_dict(), ground_control_to_dict(), _legacy_ground() (+31 more)

### Community 6 - "SimInterface"
Cohesion: 0.11
Nodes (5): BaseException, StartMode, Минимальный lifecycle, одинаковый для стенда и X-Plane., SimInterface, Protocol

### Community 7 - "airborne_inputs"
Cohesion: 0.08
Nodes (42): airborne_inputs(), Кадр «ВС на глиссаде»: стойки не обжаты, ILS валиден, скорость и высота…, _colleague_controller(), _descent_frames(), _our_channel(), Страховка от самообмана: сценарий обязан пройти выравнивание, иначе паритет его…, Угол сноса не должен превращаться в ошибку курса на локализаторе., Стенд иногда сбрасывает Valid при сохранении пригодного численного значения. (+34 more)

### Community 8 - "scenarios.py"
Cohesion: 0.12
Nodes (21): ControlProfile, _copy_approach(), _copy_ground(), _ground_segments_for_spec(), _GroundPresetSpec, _install_approach_scenarios(), _materialize_override(), _matrix_draft() (+13 more)

### Community 9 - "GainSpace"
Cohesion: 0.18
Nodes (9): GainKey, GainSpace, Any, ArrayLike, float64, GainMap, NDArray, RegulatorKey (+1 more)

### Community 10 - "ground_allocator.py"
Cohesion: 0.16
Nodes (13): LongitudinalDiagnostics, Сбросить PID и привязать начало профиля к фактической скорости касания/старта., ActuatorFeedback, ActuatorVector, AllocationDiagnostics, _clamp(), GroundControlAllocator, FlightSegment (+5 more)

### Community 11 - "LateralChannel"
Cohesion: 0.23
Nodes (7): GuidanceState, LateralChannel, LateralDiagnostics, Блок 2: runway guidance → единый нормированный yaw-запрос., Guidance по тому, что даёт стенд. → словарь guidance или None, если данных нет.…, Единый GuidanceState текущего кадра для control/observation/reward., RunwayTracker

### Community 12 - "test_pretrain.py"
Cohesion: 0.12
Nodes (29): float32, GainMap, NDArray, Абсолютные коэффициенты пресета → `target_z` (17,): gains через `inv_gain`,…, target_z_from_gains(), capture_dataset(), capture_scenario(), episode_quality() (+21 more)

### Community 13 - "ControlsState"
Cohesion: 0.15
Nodes (24): ControlsState, Обнуляет все органы управления. Отправку делает вызывающий через `ICSSim.step`.…, Разделяемая по тактам структура команд — и наземных, и воздушных. Аннотации…, Сброс к нейтральным командам — новый эпизод начинается с чистого состояния.…, Обнулить только воздушные команды. Нужно, когда воздушный канал не может…, build_altitude_sweep(), command_for_pulse(), Безопасные elevator/altitude authority sweep без дублирования ICS runner. (+16 more)

### Community 14 - "test_ics_connector.py"
Cohesion: 0.09
Nodes (23): GearState, Разбор телеметрии стенда с совместимостью вперёд. Асимметрия намеренная (JSON-…, Отправка best-effort со счётчиком ошибок и разрежённым логом. Windows отдаёт…, → True если отправлено. Исключение наружу не выпускается., ResilientSender, _connector(), _FakeSocket, _full_payload() (+15 more)

### Community 15 - "scenario_for_matrix_run"
Cohesion: 0.18
Nodes (13): resolve_matrix_run(), compose_matrix_scenario(), _install_through_scenarios(), Собрать Б.4 из первой строки и заранее определённой пары законов., Собрать сценарий из конкретных строк APPROACH/ROLLOUT/TAXI.…, Одна строка каталога → минимальный сценарий нужного участка или сквозной пары., scenario_for_matrix_run(), test_compose_matrix_scenario_combines_air_and_ground_control_and_failures() (+5 more)

### Community 16 - "AircraftProfile"
Cohesion: 0.10
Nodes (10): AircraftProfile, clamp(), Преобразовать воздушные команды ICD в нормированные DataRef X-Plane., Преобразовать нормированные команды пробега в DataRef X-Plane., Расширение реестра будущим профилем МС-21 без правки XPlaneSim., Проводка и масштабы конкретного планера X-Plane., Общая идентичность ЛА и необязательная привязка к X-Plane. Профиль нужен и…, Command refs retained under the historical public name. (+2 more)

### Community 17 - "ICSSim"
Cohesion: 0.07
Nodes (24): ConditionMatch, ControlsState, EngagementInputs, ICSSim, FailureMode, FlightSegment, Scenario, SimInterface (+16 more)

### Community 18 - "control/approach.py"
Cohesion: 0.11
Nodes (28): ApproachConfig, Параметры воздушного контура. Значения по умолчанию — настроенные на стенде.…, angle_error_deg(), ApproachController, ApproachResult, clamp(), ApproachLimits, ApproachTelemetry (+20 more)

### Community 19 - "Telemetry"
Cohesion: 0.05
Nodes (29): Такт манёвра ухода. → True, когда набор устойчив (пора отдать управление…, Набор устойчив: есть и вертикальная скорость вверх, и прирост радиовысоты над…, Невалидные ICS-сигналы, которые воздушный закон читает безусловно., Приборная скорость (kt → м/с). Отсечки реверса заданы по ней, а не по путевой., Радиовысота **в футах** — единицы стенда. Порог воздушного включения (400…, Объявлены ли валидными **оба** канала ILS (курсовой и глиссадный). `None` —…, Посадочная конфигурация механизации; `None` — положение не посадочное. `None`…, Боковое отклонение от оси, измеренное стендом. Позволяет не считать геодезию… (+21 more)

### Community 20 - "gain_scheduler.py"
Cohesion: 0.12
Nodes (19): int64, ActorOutput, build_npgs(), _init_log_std(), layer_init(), _mlp_head(), phase_labels_from_groundspeed_kts(), ArrayLike (+11 more)

### Community 21 - "XPlaneSim"
Cohesion: 0.11
Nodes (5): _destination(), XPlaneDiagnostics, ControlsState, StartMode, XPlaneSim

### Community 22 - "WeatherState"
Cohesion: 0.10
Nodes (26): FlightSegment, Enum, str, Участок, для которого выбираются закон управления и условия сценария., _as_dict(), contract_for(), Any, Контракт воспроизводимости эпизода (шаг 6). Заимствовано из… (+18 more)

### Community 23 - "PIDController"
Cohesion: 0.08
Nodes (34): PIDController, PIDDiagnostics, Пропорционально-интегрально-дифференциальный регулятор. Класс сохраняет прежнюю…, Типизированный снимок последнего такта регулятора., Сброс внутренних состояний (используется при выключении системы)., test_ground_pids_use_working_ics_numerics_and_explicit_integrator_limits(), _legacy_reference(), Опциональная численность PID (шаг 5): каждый флаг проверяется на том дефекте,… (+26 more)

### Community 24 - "Policy"
Cohesion: 0.09
Nodes (22): compare_policies(), DefaultGainsPolicy, main(), Policy, PresetPolicy, ndarray, Прогон набора сценариев под одной политикой → сводка по политике., Сравнение политик на одном наборе сценариев (обязательный шаг приёмки).… (+14 more)

### Community 25 - ".step"
Cohesion: 0.20
Nodes (6): ndarray, Копия команды такта — для расчёта джерка на следующем такте. Копируется…, Окно истории → тензор `(history_len, OBS_DIM)` (последовательность кадров для…, Состояние для поведенческих проверок Shield. Курс здесь — отклонение от…, _snapshot_command(), RuntimeState

### Community 26 - "test_xplane_backend.py"
Cohesion: 0.09
Nodes (16): test_xplane_ignores_failures_outside_rollout_contract(), DatagramSocket, MockXPlaneConnector, ScriptedXPlaneConnector, test_commands_failures_and_close_release_overrides(), test_exact_taxi_row_starts_xplane_and_controller_in_taxi_at_15_knots(), test_failed_approach_setup_releases_overrides_and_pause(), test_ignored_xplane_failure_participates_in_segment_delta_and_is_cleared() (+8 more)

### Community 27 - "test_evaluate.py"
Cohesion: 0.09
Nodes (51): admit_checkpoint(), evaluate_tz(), Диагностика эпизода + сценарий → список вердиктов по пунктам ТЗ разд. 5., Итог эпизода: FAIL, если провален хоть один применимый критерий., Один эпизод под заданной политикой → objective + вердикты ТЗ., Пропускать ли чекпоинт дальше. Отсутствующая/нечисловая метрика = отказ.…, run_episode(), verdict_of() (+43 more)

### Community 28 - "test_ppo.py"
Cohesion: 0.11
Nodes (25): NPGSConfig, Any, Гиперпараметры архитектуры NPGS (замораживаются вместе с весами при поставке)., PPOConfig, Any, device, PPO-тренер + многокомпонентный loss для NPGS (план §11). `L = L_ppo +…, Плоский буфер одного env: obs-окна, сырые действия, logp/value/reward/done. (+17 more)

### Community 29 - "IcsEngagement"
Cohesion: 0.05
Nodes (29): ControlModeState, EngagementInputs, IcsEngagement, Автомат включения. `step(inputs)` вызывается каждый такт до формирования…, Полный сброс — новый эпизод начинается с невключённого состояния., Сообщить автомату, что кадр **фактически ушёл** на стенд. Вызывается…, Подхватить уже включённый извне пробег: шлём `ControlMode = Rollout`.…, Войти в пробег самостоятельно: шлём `ControlMode = Rollout`. Это же — передача… (+21 more)

### Community 30 - "XPlaneConnectX"
Cohesion: 0.08
Nodes (14): XPlaneConnectX class initialization. Args: ip (str, optional): IP address where…, Starts a recording of the subscribed DataRefs into self.recorded_data. Data is…, Terminates the recording and returns a dictionary of lists that contain the…, Synchronize measurements from multiple sensors to a common frequency.…, Gets the current value of a DataRef. This is only intended for one-time use.…, Permanently subscribe to a list of DataRefs with a certain frequency. This is…, Writes a value to the specified DataRef provided that the DataRef is writable.…, Sends simulator commands to the simulator. These are not commands for the… (+6 more)

### Community 31 - "RunRecorder"
Cohesion: 0.17
Nodes (5): Exception, Подключить best-effort аудит сырых успешно принятых/отправленных UDP payload., Append-only writer; ошибка диска помечает прогон, но не выходит в control-loop., RunEvent, RunRecorder

### Community 32 - "test_splits.py"
Cohesion: 0.10
Nodes (39): Сколько раз прогнать сценарий, чтобы результат приёмки что-то значил., required_replicas(), assert_no_leakage(), has_holdout_failure(), _hash_unit(), holdout_reason(), is_marked_holdout(), SHA-256 от идентификатора → число в [0, 1). Стабильно между запусками и… (+31 more)

### Community 33 - "Graphify Pipeline"
Cohesion: 0.08
Nodes (29): Folder Watcher, URL Ingestion, Extra Graph Exports, MCP Graph Server, Confidence Audit Trail, Deterministic Node IDs, Semantic Extraction Contract, Cross-Repository Graph Merge (+21 more)

### Community 34 - "XPlaneConnector"
Cohesion: 0.09
Nodes (8): DataRefSample, Discard pre-reload values so readiness cannot use stale telemetry., Одна подписка, один поток приёма и явное освобождение ресурсов., Send basic controls to the ego aircraft. There are hundreds of DataRefs that…, Разобрать пакет; публично для детерминированных mock-тестов., Совместимое read-only представление старого XPlaneConnectX., Совместимость с прежним клиентом., XPlaneConnector

### Community 35 - "ControllingSystem"
Cohesion: 0.06
Nodes (46): ControllingSystem, FailureMode, Связать сценарий с контуром; PID активируются после определения участка., Обновить параметры геометрического наведения латерального канала. Имя сохранено…, Веса влияния каналов (актор, §6): множители к выходам каналов. 1.0 = классика., Оркестратор классического контура поверх стенда (`envs.ics_sim.ICSSim`).…, Аварийная остановка: обнулить органы и **снять заявку каналов**. Именно…, parametrize (+38 more)

### Community 36 - "Scenario"
Cohesion: 0.13
Nodes (23): match_conditions(), _profile_name(), AircraftProfile, FailureMode, FlightSegment, WeatherState, Ожидаемые физические условия одного участка., Полный профильный сценарий APPROACH → ROLLOUT → TAXI. (+15 more)

### Community 37 - "test_ics_engagement.py"
Cohesion: 0.10
Nodes (47): _Clock, _engine(), _pump(), Автомат включения управления на стенде. Два раздельных предмета проверки: *…, По ICD стенд должен два секунды ПОЛУЧАТЬ ModeAIReady=1. Если считать одно лишь…, Обратная защита: 30 кадров можно выпалить за 0.1 с — время тоже обязано пройти., Срыв предусловия обнуляет и время, и счётчик кадров., Требование ICD — непрерывность: пропуск готовности рвёт серию. (+39 more)

### Community 38 - "run_reader.py"
Cohesion: 0.13
Nodes (17): Один такт: вход, команда и диагностика имеют общий ``tick_id``., RunSample, _apply_recorded_gains(), _bool_or_none(), _equal(), main(), _number(), _parse_cell() (+9 more)

### Community 39 - "test_ics_sim.py"
Cohesion: 0.05
Nodes (48): FakeConnector, make_ics_inputs(), on_ground(), Статический стенд: всегда один и тот же кадр, отправленное — в `sent_outputs`., Полный пакет стенда: нули по умолчанию + заданные поля., Кадр «ВС на полосе»: обжаты все стойки, курс/координаты у порога UUEE 06R., _cold_sim(), Тесты стенда (`ICSSim`), подбора сценария и генератора — без реального стенда. (+40 more)

### Community 40 - "pid_controller.py"
Cohesion: 0.14
Nodes (15): roll_limit_deg(), Exact package port of the ICS approach contour validated in ``aviacia_v2``. The…, angle_error_deg(), clamp(), ClearWeatherILSController, ControllerConfig, ControlResult, PID (+7 more)

### Community 41 - "xplane_sim.py"
Cohesion: 0.12
Nodes (13): AircraftProfile, IcsEngagement, get_aircraft_profile(), Профили преобразования команд ИСМПУ в органы управления X-Plane., Настройки воздушного участка: заход по ILS, выравнивание, управление скоростью.…, get_runway_profile(), Профили ВПП и разрешение ILS из установленной базы X-Plane., Единая фабрика backend: ICS по умолчанию, X-Plane явно. (+5 more)

### Community 42 - "NPGS"
Cohesion: 0.15
Nodes (13): floating, NPGS, float32, Tensor, Neural PID Gain Scheduler: общий энкодер + головы актора (абс. gain'ы) + голова…, → (mean (B,17), value (B,), phase_logits (B,n_phases))., 17 сырых выходов → [абс. gains×15, w_lon, w_lat] (layout `REGULATOR_ORDER` +…, Один шаг актора. `action` (…,17) — абс. gain'ы для среды; `raw` (…,17) — сэмпл… (+5 more)

### Community 43 - "ICSOutputs"
Cohesion: 0.15
Nodes (21): ControlResult, ICSOutputs, airborne_flare_mode(), deactivate(), live_main(), main(), main_gear_contact(), make_airborne_output() (+13 more)

### Community 44 - "test_gain_scheduler.py"
Cohesion: 0.10
Nodes (18): device, Веса + конфиг + слепок нормировки (включая gain-пространство) одним артефактом., action_high(), action_low(), float32, NDArray, reference_action(), GainSpace (+10 more)

### Community 45 - "3. Этапы реализации"
Cohesion: 0.09
Nodes (21): 1. Подтверждённые проблемы и целевое состояние, 2. Ключевые интерфейсы, 3. Этапы реализации, 4. Тестирование и критерии готовности, 5. Зафиксированные допущения, 6.1. Один dashboard вместо двух, 6.2. Единый источник данных, 6.3. Представления (+13 more)

### Community 46 - "ScenarioGenerator"
Cohesion: 0.19
Nodes (7): Один случайный сценарий. `difficulty=None` → случайная сложность., ScenarioGenerator, Any, Собирает ветер из компонент относительно курса ВПП. `crosswind_kts` > 0 — ветер…, Сериализация в примитивы (для логирования/воспроизводимости сценариев)., test_scenario_roundtrip_with_weather_and_failures(), test_weatherstate_from_crosswind()

### Community 47 - "ics_engagement.py"
Cohesion: 0.50
Nodes (4): EngagementState, Enum, Автомат включения управления на стенде заказчика. Стенд принимает наши команды…, Состояние **исходящего стимула** (что мы шлём стенду), а не факта включения.…

### Community 49 - "test_full_flight.py"
Cohesion: 0.09
Nodes (34): IntFlag, ControlValid, FlightPhase, Биты `ControlValidMask`: какие каналы несёт команда. **Один бит на одно…, Фаза полёта, сообщаемая стендом (`ICSInputs.FlightPhase`)., _air(), _Clock, _engaged_airborne_sim() (+26 more)

### Community 50 - "system.py"
Cohesion: 0.11
Nodes (28): Глобальные константы контура управления (перенесены из main.ipynb)., Приёмочные пороги из ТЗ (раздел 5). Единый источник истины для reward-шейпинга…, GoAroundManeuver, Оркестратор классического контура управления — на всём интервале полёта.…, Состояние идущего ухода на второй круг. Пока он активен, заход не ведётся., _armed_controller(), _drive(), _frame() (+20 more)

### Community 51 - "Neural PID Gain Scheduler Architecture"
Cohesion: 0.19
Nodes (19): Hybrid Neural PID Controller, Neural PID Gain Scheduler, PPO Training Loop, Preset-Anchored Deterministic Shield, SFT Behavioral-Cloning Warm Start, Absolute-Gain Action Space, Classical PID as the Plant, Deterministic Deployment Runtime (+11 more)

### Community 52 - "test_approach_criteria.py"
Cohesion: 0.19
Nodes (12): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, Отдельный монитор критерия А.1.1 (не участвует в go-around)., Захватывает А.1.1 после входа в допуск и завершает оценку на 300 ft., frame() (+4 more)

### Community 53 - "flight.py"
Cohesion: 0.07
Nodes (30): above_decision_height(), approach_blocker(), ApproachRefused, at_lateral_alignment_gate(), ils_blocker(), in_terminal_window(), Участки полёта и переходы между ними. Управление ведётся на всём интервале — от…, Последние футы перед касанием, где прерывать заход опаснее, чем доработать.… (+22 more)

### Community 54 - "run_artifacts.py"
Cohesion: 0.17
Nodes (18): _jsonable(), controller_pids(), _csv_value(), default_runs_root(), _effective_configs(), gains_snapshot(), _git_state(), _jsonable() (+10 more)

### Community 55 - "RunwayTracker"
Cohesion: 0.07
Nodes (23): find_earth_nav_dat(), ILSStation, parse_ils_station(), Path, Точка на продолжении оси; положительное расстояние — до порога., Найти LOC (тип 4) без хардкода частоты., RunwayProfile, GuidanceState (+15 more)

### Community 56 - "RomanLogImporter"
Cohesion: 0.19
Nodes (10): _number(), Path, Импорт и проверка внешних CSV-прогонов roman_aviacia_ics., Потоково нормализует основной и authority CSV Романа., RomanLogImporter, verify_manifest(), fixture, roman_csv() (+2 more)

### Community 57 - "working_ics/approach_criteria.py"
Cohesion: 0.21
Nodes (7): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, ICSInputs, Evaluate the A.1.1 approach segment and stop at a radio-altitude floor.

### Community 58 - "test_profiled_scenarios.py"
Cohesion: 0.11
Nodes (15): compose_scenario(), Any, Serialize only the canonical profile- and matrix-aware schema v3., Сценарий по имени либо шифру матрицы, без различия раскладки А/B., Собрать сценарий из независимых источников участков., resolve_scenario(), test_battery_covers_key_cases_and_roundtrips(), test_generator_samples_are_valid_and_serializable() (+7 more)

### Community 59 - "ScriptedFlightBench"
Cohesion: 0.12
Nodes (13): flight_sim(), _integrate_throttle(), KinematicBench, Ход рычага РУД за такт: интеграл команды-скорости, зажатый физическим…, Доля обратной тяги по фактическому углу РУД: 0 в положительном секторе, 1 на…, Стенд, проигрывающий заход и касание **по сценарию**, а не по нашим командам.…, (sim, bench) на сценарном заходе. Рукопожатие ещё не выполнено., Мини-модель стенда: замедление ~ команде тормоза/реверса, ход вдоль осевой ВПП.… (+5 more)

### Community 60 - "gain_space_for"
Cohesion: 0.24
Nodes (12): gain_space_for(), _profile_name(), Профильное пространство абсолютных PID-коэффициентов NPGS., _regulator_config(), Профильные пространства абсолютных PID-коэффициентов NPGS., test_every_profile_preset_gain_is_inside_its_band(), test_gain_space_can_be_built_from_external_scenario_registry(), test_normalization_endpoints_and_nonpositive_guard() (+4 more)

### Community 61 - "ReferenceTrajectory"
Cohesion: 0.16
Nodes (11): Enum, Генератор эталонной кривой скорости пробега. Два закона замедления: колокол…, Генератор эталонной кривой скорости (Колокол Гаусса)., Начать профиль с фактической скорости текущего участка., То же без лишнего round-trip м/с → узлы → м/с на касании., Возвращает идеальную скорость (м/с) для текущей точки пути., ReferenceTrajectory, TrajectoryState (+3 more)

### Community 62 - "Project Dependencies"
Cohesion: 0.18
Nodes (13): Autonomous Landing Controller, Repository Guidance for Codex, Autonomous Landing Controller, Repository Guidance for Claude Code, Neural Landing Implementation Plan, Unified Scenario System, Optional Gymnasium, NumPy (+5 more)

### Community 63 - ".from_ics"
Cohesion: 0.08
Nodes (26): initial_segment(), is_airborne(), FlightSegment, Сообщает ли стенд, что ВС в воздухе и достаточно высоко для приёма захода.…, С какого участка начинать. Пробег — ответ по умолчанию (см. модуль)., `ICSInputs` → `Telemetry`: поля в СИ + «сырой» пакет для property. Стенд отдаёт…, engaged_inputs(), Кадр стенда, который уже принял управление: `AgentIsActive = 1`, идёт пробег. (+18 more)

### Community 64 - "test_control_parity.py"
Cohesion: 0.09
Nodes (20): Кадр «связи со стендом нет». Нули, а не None: контур проверяет `valid` первым., decode_outputs(), Отправленные команды в нормированном виде — для сравнения траекторий.…, `ICSOutputs` → (brake_l, brake_r, thr_l_rate, thr_r_rate, steer), всё…, Тесты паритета после выноса контура из main.ipynb в пакет ismpu. Полный паритет…, NWS_FAIL отключает стойку/педаль, но оставляет руль и дифференциальные органы., Стенд при обрыве связи отдаёт НУЛИ с valid=False, а не None. Проверка «поле is…, test_control_step_emits_five_bounded_commands() (+12 more)

### Community 66 - "DashboardState"
Cohesion: 0.09
Nodes (17): DashboardServer, DashboardState, _finite_or_none(), GainUpdateRequest, _handler_factory(), main(), Path, Unified local dashboard for the three airborne and five ground PIDs. (+9 more)

### Community 67 - "test_rollout_env.py"
Cohesion: 0.12
Nodes (23): ObservationBuilder, Строит нормированный вектор наблюдения одного кадра., heading_deviation_deg(), Отклонение курса ВС от направления ВПП — приёмочная величина ТЗ 5.1.3.3 /…, Тесты Этапа 2: Observation/Action/reward/RolloutEnv + инвариант identity ==…, Без аннотаций типов @dataclass не видит полей, и тогда любые два экземпляра…, Свежий экземпляр обязан нести все поля в собственном `__dict__`. Без аннотаций…, Телеметрия ВС на оси ВПП, смещённого вбок на `offset_m` и с заданным курсом.… (+15 more)

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
Cohesion: 0.43
Nodes (3): DashboardState, Any, ICSInputs

### Community 75 - "evaluate.py"
Cohesion: 0.08
Nodes (23): FailureMode, Enum, Модель отказов бортового оборудования. `FailureState` хранит мультипликативные…, Генератор сценариев обучения (domain randomization). Сэмплирует `Scenario` из…, is_signature_holdout(), PartitionedScenarioProvider, Детерминированное разбиение сценариев на обучение и holdout (шаг 6). Схема…, Устойчивая комбинация условий, а не имя или целое семейство отказов. (+15 more)

### Community 76 - "ICSInterface.cs"
Cohesion: 0.36
Nodes (7): External.Systems.ICS, ControlModeState, GearState, ICSInputs, ICSOutputs, ReverseEngineType, UInt64

### Community 77 - "compute_reward"
Cohesion: 0.14
Nodes (14): compute_reward(), TypedDict, Считает компоненты и суммарный reward. Все компоненты ≥ 0; reward = −Σ…, Допуск по оси ВПП для текущей фазы: пробег ±3 м, руление ±1 м (ТЗ 5.1.3.1)., RewardComponents, xte_limit_for(), Перелёт по скорости к концу ВПП опаснее недолёта — симметричным модулем не…, Тормоз на 0 = «торможение не требуется», а не «авторитет исчерпан». Иначе флаг… (+6 more)

### Community 78 - "test_run_matrix.py"
Cohesion: 0.08
Nodes (35): ground_cases(), matrix_battery(), Канонические участки управляемого интервала полёта., build_capture_stack(), build_scenarios(), matrix_preset_names(), PretrainRunConfig, Оркестрация SFT-подогрева NPGS (план Stage B): захват классических прогонов на… (+27 more)

### Community 79 - "RunReader"
Cohesion: 0.20
Nodes (9): Path, Run-directory и любой поддержанный CSV через один streaming API., RunReader, _frame(), _record_ground_run(), test_approach_stream_has_three_pid_states_and_replays_at_1e_12(), test_legacy_adapter_does_not_invent_missing_pid_terms(), test_report_contains_matrix_metrics_and_aggregation_uses_workbook_columns() (+1 more)

### Community 80 - "ICS PID Monitor"
Cohesion: 0.29
Nodes (7): buildControls, draw, formatTime, Four-Loop PID Tuning, ICS PID Monitor, Live and Historical Timeline, refresh

### Community 81 - "fakes.py"
Cohesion: 0.09
Nodes (25): IntEnum, Константы интерфейса стенда заказчика (ПИВ / ICS). Единый источник правды по…, _clamp(), _faults_from_inputs(), Стенд заказчика как источник телеметрии и приёмник команд. Единственный…, Сигналы отказов со стенда → наши `FailureMode`. Отказы шасси…, Желаемый уровень реверса [-1, 0] → скорость перемещения РУД (°/с). Тягой (в том…, Типизированные backend-расширения общего SI-кадра. (+17 more)

### Community 82 - "ICS UDP JSON Protocol"
Cohesion: 0.33
Nodes (6): Fourteen-Bit ControlValidMask Layout, Dual-Backend SimInterface, Two-Factor ICS Engagement Handshake, ICS UDP JSON Protocol, Telemetry SI Unit Boundary, ICS-Only Backend Guidance

### Community 83 - "X-Plane Dashboard and Runtime Guide"
Cohesion: 0.60
Nodes (6): Aircraft-Profile Checkpoint Isolation, Live A330 Acceptance Checklist, Profile-Aware Flight Scenarios, X-Plane Dashboard and Runtime Guide, X-Plane Resettable Runtime, X-Plane Training and Evaluation Backend

### Community 84 - "test_working_ics_golden.py"
Cohesion: 0.24
Nodes (12): Касание: обжата **любая основная** стойка. Носовая не участвует — она…, airborne_control_mode(), _assert_numeric_result(), ICSInputs, Characterization baseline of the bench-validated ``working_ics`` approach., Канонический контур и формирователь пакета совпадают с эталоном до 1e-12., _replay(), _rows() (+4 more)

### Community 85 - "EpisodeObjective"
Cohesion: 0.20
Nodes (8): EpisodeObjective, Накопитель по эпизоду: собирает потактовые отсчёты → сводные компоненты.…, Фиксированный приёмочный набор (детерминированный, без RNG)., Отсутствие данных даёт None, а не 0 — приёмка обязана трактовать это как FAIL., p95 темпа не ловится одиночным выбросом — в отличие от максимума., test_episode_objective_p95_rate_is_robust_to_a_single_spike(), test_episode_objective_reports_none_for_unobserved_phases(), test_episode_objective_separates_rollout_and_taxi_phases()

### Community 86 - "rollout_env.py"
Cohesion: 0.22
Nodes (12): CompletionRule, Как активный наземный сценарий заканчивает управление., ObserverEstimate, Оценки PINN-обсервера (§12). Заглушка нулями до Этапа 7., RewardWeights, EpisodeInfo, _make_box(), TypedDict (+4 more)

### Community 87 - "ConditionMatch"
Cohesion: 0.25
Nodes (4): ConditionMatch, Сверка ожидаемых условий с фактической телеметрией backend., Погода остаётся отчётной; неверный отказ делает прогон недопустимым., Совместимое имя для прежних потребителей допуска к приёмке.

### Community 88 - "run_report.py"
Cohesion: 0.26
Nodes (13): aggregate_matrix_results(), build_run_report(), main(), _matrix_results(), _max_abs(), _metrics(), _number(), _optional() (+5 more)

### Community 89 - "test_approach_channel.py"
Cohesion: 0.09
Nodes (32): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+24 more)

### Community 90 - "LongitudinalChannel"
Cohesion: 0.25
Nodes (5): CompletionRule, LongitudinalChannel, Блок 1: скорость → симметричная база тормозов и реверса., PidMap, VelocityLaw

### Community 91 - "shield.py"
Cohesion: 0.10
Nodes (21): Shield — детерминированный защитный контур между актором и классическим PID.…, ControlArchitecture, Канонический порядок регуляторов, размерности действия и **контракт обучаемого…, Фиксированный порядок слоёв и роль обучаемого компонента., Проверяет контракт обучаемого слоя. Нарушение → `ValueError` на старте…, Один регулятор, коэффициенты которого (kp/ki/kd) разрешено настраивать сети., RegulatorSpec, validate_action_contract() (+13 more)

### Community 92 - "static_sim"
Cohesion: 0.09
Nodes (37): apply_gains_to_pids(), base_gains_from_pids(), PidMap, Снимок (kp, ki, kd) регуляторов — пресет-якорь для Shield и т.п., Записывает эффективные gain'ы обратно в регуляторы (перед control_step)., apply_corrections(), decode(), preset_action() (+29 more)

### Community 93 - "graded"
Cohesion: 0.50
Nodes (4): graded(), Штраф с гейтом ТЗ: мягкий линейный наклон внутри допуска + резкий рост за…, Ровно на пороге ТЗ штраф = наклон внутри полосы; дальше растёт много круче., test_graded_penalty_breaks_exactly_at_the_tz_limit()

### Community 94 - "loop.py"
Cohesion: 0.19
Nodes (13): cli(), _lost_engagement(), main(), Scenario, SimInterface, Управляющий цикл 20 Гц против стенда заказчика — **весь интервал полёта**.…, Снял ли стенд активность посреди прогона. → пора останавливаться. Без этой…, Точка входа: подключиться к стенду, выбрать пресет и провести полёт.… (+5 more)

### Community 95 - "reward.py"
Cohesion: 0.10
Nodes (23): _command_jerk(), _component(), _effort_saturated(), excess(), _ground_steering(), ObjectiveWeights, _p95(), Objective — единое определение «хорошего пробега» (§11 + приёмка ТЗ разд. 5).… (+15 more)

### Community 99 - "_WarmUpSim"
Cohesion: 0.25
Nodes (5): Стенд, включающий управление только после N тактов прогрева. Само рукопожатие…, Такты рукопожатия — не шаги эпизода: в это время ВС нами не управлялось. Иначе…, test_env_reports_engagement_state_in_info(), test_warm_up_runs_before_the_episode_and_is_not_counted(), _WarmUpSim

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
Cohesion: 0.15
Nodes (14): clip_unit(), linear(), log_norm(), Фиксированная нормализация Observation Space — единый контракт train ↔ deploy.…, Лог-нормировка неотрицательной величины (видимость): log1p(x)/log1p(scale)., Отображает [lo, hi] → [-1, 1] (для PID output по его границам)., Сериализуемый слепок контракта нормировки (сохраняется вместе с весами).…, snapshot() (+6 more)

### Community 115 - "engaged_sim"
Cohesion: 0.12
Nodes (16): engaged_sim(), (sim, connector) с завершённым рукопожатием: стенд подтвердил `AgentIsActive =…, Регресс: расширение структуры не должно протащить руль высоты в маску пробега., test_ground_frame_still_declares_only_the_ground_channels(), Разделение органов из таблицы Заказчика: тиллер — на рулении, педальный пост —…, Базовый контур на стенде: `control_step` сам читает телеметрию и сам отправляет., На стенде каждый лишний `read_telemetry` — лишний приём UDP. Кадр, вернувшийся…, Замолчать нельзя: последнее отклонение осталось бы приложенным до сторожа на… (+8 more)

### Community 116 - "Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)., Source Nodes

### Community 117 - "LandingFlapConfiguration"
Cohesion: 0.36
Nodes (10): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+2 more)

### Community 123 - "FailureState"
Cohesion: 0.31
Nodes (5): FailureManager, FailureState, Эффективности исполнительных органов. Аннотации типов обязательны: без них…, Проецирует набор дискретных отказов в эффективности исполнительных органов., Привести состояние ровно к набору `modes` (то, что сообщил стенд). Пересборка с…

### Community 124 - ".from_json"
Cohesion: 0.29
Nodes (6): _pid_from_colleague(), Загрузка настроек из JSON коллеги (`config/ics_clear_weather_pid.json`). Секции…, `PIDConfig` коллеги → аргументы нашего `PIDController`. Предел интегратора у…, Path, Наши умолчания и его файл — одно и то же. Разойдутся — расхождение должно быть…, test_config_from_the_colleague_json_matches_our_defaults()

### Community 125 - "DatagramSocket"
Cohesion: 0.29
Nodes (3): DatagramSocket, test_legacy_subscription_starts_at_zero_and_retries_with_diagnostics(), test_xplane_used_wire_packets_match_confirmed_original()

### Community 126 - ".compute"
Cohesion: 0.20
Nodes (4): → (интеграл только с утечкой, интеграл с утечкой и приращением). Оба уже зажаты., Такт регулятора. `measurement` обязателен при `derivative_on_measurement=True`., Back-calculation: подтянуть интегратор к фактически применённой команде. No-op…, Вес апериодического фильтра D-составляющей за такт `dt`.

### Community 129 - "Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md)., Source Nodes

### Community 130 - "HandshakeBench"
Cohesion: 0.29
Nodes (4): HandshakeBench, Стенд, включающий управление только после корректного рукопожатия. Ждёт…, Стенд включается по полученной готовности, а не по нашему представлению о ней., test_the_airborne_handshake_is_actually_transmitted_before_approach()

### Community 131 - "control.py"
Cohesion: 0.43
Nodes (4): apply_ground_control(), build_pids(), Сборка классического контура из неизменяемой конфигурации., Фабрики stateful-объектов; config-модули хранят только данные.

### Community 133 - ".enter_segment"
Cohesion: 0.25
Nodes (4): FailureMode, FlightSegment, Применить только дельту условий при переходе между участками., Снять один отказ, не переинициализируя отказ, продолжающийся на новом участке.

### Community 135 - "Q: Приступай к выполнению этапа 2 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 2 плана docs/plan.md, Source Nodes

### Community 140 - ".control_step"
Cohesion: 0.12
Nodes (9): ApproachConfig, ApproachController, SimInterface, Пересобрать воздушный канал под заданные настройки. → новый канал. Именно…, Привести модель отказов к тому, что сообщает борт (`ICSInputs.Fault*`). Отказы…, Такт управления. → True, если управление окончено (или телеметрия невалидна).…, Три блока: speed controller → guidance → allocator., Передать управление в руление (`ControlMode 3 → 4`) — пробег окончен.… (+1 more)

### Community 142 - ".__init__"
Cohesion: 0.29
Nodes (5): AircraftProfile, Path, RunwayProfile, WeatherState, XPlaneConnector

### Community 158 - "Q: Приступай к выполнению этапа 4 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 4 плана docs/plan.md, Source Nodes

## Ambiguous Edges - Review These
- `Unified Profile-Aware Scenario System` → `Legacy Scenario Preset Model`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to
- `Dual-Backend SimInterface` → `ICS-Only Backend Guidance`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **67 isolated node(s):** `1. Подтверждённые проблемы и целевое состояние`, `2. Ключевые интерфейсы`, `Этап 0 — Зафиксировать воспроизводимый baseline`, `Этап 1 — Исправить границу телеметрии и ложный XTE`, `Этап 2 — Пересобрать наземный контроллер` (+62 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **53 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `ControllingSystem` (3× useful, score=2.972857199) _(code changed — re-verify)_
- `ICSSim` (2× useful, score=1.99593983) _(code changed — re-verify)_
- `LateralChannel` (2× useful, score=1.974311972)
- `ObservationBuilder` (2× useful, score=1.954302503)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Unified Profile-Aware Scenario System` and `Legacy Scenario Preset Model`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Dual-Backend SimInterface` and `ICS-Only Backend Guidance`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `ControllingSystem` connect `ControllingSystem` to `RolloutEnv`, `control.py`, `test_refactoring_contracts.py`, `scenarios.py`, `._commit_landing_mode`, `.control_step`, `test_pretrain.py`, `Telemetry`, `PIDController`, `Policy`, `test_xplane_backend.py`, `test_evaluate.py`, `test_ppo.py`, `Scenario`, `run_reader.py`, `test_ics_sim.py`, `NPGS`, `test_gain_scheduler.py`, `test_full_flight.py`, `system.py`, `test_approach_criteria.py`, `flight.py`, `ScriptedFlightBench`, `.from_ics`, `test_control_parity.py`, `DashboardState`, `test_rollout_env.py`, `evaluate.py`, `compute_reward`, `test_run_matrix.py`, `RunReader`, `fakes.py`, `rollout_env.py`, `ConditionMatch`, `LongitudinalChannel`, `shield.py`, `static_sim`, `loop.py`, `reward.py`, `_WarmUpSim`, `engaged_sim`, `DatagramSocket`?**
  _High betweenness centrality (0.169) - this node is a cross-community bridge._
- **Why does `Telemetry` connect `Telemetry` to `test_tolerance.py`, `HandshakeBench`, `channels.py`, `test_refactoring_contracts.py`, `.enter_segment`, `scenarios.py`, `._commit_landing_mode`, `ground_allocator.py`, `LateralChannel`, `.control_step`, `ControlsState`, `ICSSim`, `control/approach.py`, `XPlaneSim`, `ControllingSystem`, `Scenario`, `run_reader.py`, `test_ics_sim.py`, `xplane_sim.py`, `ICSOutputs`, `test_full_flight.py`, `system.py`, `test_approach_criteria.py`, `flight.py`, `ScriptedFlightBench`, `.from_ics`, `test_control_parity.py`, `test_rollout_env.py`, `RunReader`, `fakes.py`, `test_working_ics_golden.py`, `ConditionMatch`, `test_approach_channel.py`, `LongitudinalChannel`, `_WarmUpSim`, `normalization.py`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Why does `ControlsState` connect `ControlsState` to `GainCommand`, `RolloutEnv`, `channels.py`, `Shield`, `airborne_inputs`, `ground_allocator.py`, `.control_step`, `.rudder_cmd`, `AircraftProfile`, `Telemetry`, `PIDController`, `.step`, `test_xplane_backend.py`, `test_ics_sim.py`, `xplane_sim.py`, `ICSOutputs`, `ReferenceTrajectory`, `test_rollout_env.py`, `compute_reward`, `test_working_ics_golden.py`, `EpisodeObjective`, `rollout_env.py`, `test_approach_channel.py`, `shield.py`, `reward.py`, `_WarmUpSim`, `engaged_sim`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Are the 33 inferred relationships involving `ControllingSystem` (e.g. with `ApproachSetup` and `ConditionMatch`) actually correct?**
  _`ControllingSystem` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 49 inferred relationships involving `Telemetry` (e.g. with `ApproachSetup` and `ConditionMatch`) actually correct?**
  _`Telemetry` has 49 INFERRED edges - model-reasoned connections that need verification._