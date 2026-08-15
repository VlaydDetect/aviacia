# Graph Report - GOSNIIASProject  (2026-08-15)

## Corpus Check
- 134 files · ~135,002 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2420 nodes · 5960 edges · 123 communities (98 shown, 25 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 519 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2ed8fea0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- SpecialSituation
- test_splits.py
- reward.py
- weather.py
- Shield
- json_config.py
- SimInterface
- test_approach_channel.py
- ControllingSystem
- ICSInputs
- test_refactoring_contracts.py
- LongitudinalChannel
- NPGS
- scenarios.py
- ICSOutputs
- Scenario
- AircraftProfile
- ICSSim
- ApproachChannel
- Telemetry
- test_gain_scheduler.py
- XPlaneSim
- test_weather.py
- PIDController
- evaluate.py
- RolloutEnv
- WeatherState
- test_evaluate.py
- test_ppo.py
- IcsEngagement
- XPlaneConnectX
- rollout_env.py
- gain_scheduler.py
- Graphify Pipeline
- XPlaneConnector
- static_sim
- GainSpace
- test_ics_engagement.py
- test_diagnostic_tools.py
- test_ics_sim.py
- pid_controller.py
- system.py
- .act_numpy
- runner.py
- channels.py
- test_run_matrix.py
- ScenarioGenerator
- EngagementInputs
- RunRecorder
- test_full_flight.py
- _frame
- Neural PID Gain Scheduler Architecture
- test_approach_criteria.py
- test_tolerance.py
- gui/dashboard.py
- RunwayTracker
- RomanLogImporter
- ICSInputs
- parse_ils_station
- .send_outputs
- gain_space_for
- ReferenceTrajectory
- Project Dependencies
- admit_checkpoint
- LateralChannel
- ICSInputs
- test_dashboard.py
- test_rollout_env.py
- test_working_ics_dashboard.py
- ICSOutputs
- _descent_frames
- Unified Profile-Aware Scenario System
- Interactive PID Dashboard
- RuntimeError
- ClearWeatherILSController
- protocol.py
- ICSInterface.cs
- .enter_segment
- EpisodeObjective
- loop.py
- ICS PID Monitor
- .guidance
- ICS UDP JSON Protocol
- X-Plane Dashboard and Runtime Guide
- .from_json
- ControlsState
- DashboardState
- sim_interface.py
- .from_crosswind
- control/approach.py
- ICSInputs
- Criterion
- roll_limit_deg
- _WarmUpSim
- PresetPolicy
- test_zero_bound_is_not_counted_as_saturation
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
- EngagementState
- ._should_go_around
- Q: Реализовать этап 0: baseline, golden replay и dashboard characterization
- Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md).
- test_approach_limits_take_the_conservative_weight_row
- test_confirmation_latches_through_a_dropped_packet
- TypedDict
- tolerance.py
- str
- IntEnum
- ControlModeState
- ICSInputs
- ICSOutputs
- socket

## God Nodes (most connected - your core abstractions)
1. `ControllingSystem` - 168 edges
2. `ControlsState` - 121 edges
3. `Telemetry` - 115 edges
4. `ICSSim` - 81 edges
5. `RunwayTracker` - 58 edges
6. `WeatherState` - 57 edges
7. `XPlaneSim` - 56 edges
8. `AircraftProfile` - 55 edges
9. `RolloutEnv` - 55 edges
10. `PIDController` - 54 edges

## Surprising Connections (you probably didn't know these)
- `Autonomous Landing Controller` --semantically_similar_to--> `Autonomous Landing Controller`  [INFERRED] [semantically similar]
  CLAUDE.md → AGENTS.md
- `Profile-Aware Flight Scenarios` --semantically_similar_to--> `Unified Scenario System`  [INFERRED] [semantically similar]
  docs/XPLANE_DASHBOARD.md → implementation_plan.md
- `Acceptance and Evaluation Harness` --semantically_similar_to--> `Technical-Specification Acceptance Gates`  [INFERRED] [semantically similar]
  implementation_plan.md → AGENTS.md
- `X-Plane Resettable Runtime` --semantically_similar_to--> `X-Plane Training and Evaluation Backend`  [INFERRED] [semantically similar]
  docs/XPLANE_DASHBOARD.md → implementation_plan.md
- `_WarmUpSim` --uses--> `ControlsState`  [INFERRED]
  tests/test_rollout_env.py → ismpu/control/channels.py

## Import Cycles
- 3-file cycle: `ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/control/channels.py`
- 3-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 3-file cycle: `ismpu/config/scenarios.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 3-file cycle: `ismpu/config/aircraft_profiles.py -> ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/config/aircraft_profiles.py`
- 4-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 4-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/tolerance.py -> ismpu/control/approach.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/aircraft_profiles.py -> ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py -> ismpu/config/aircraft_profiles.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/flight.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach_criteria.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/tolerance.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`

## Hyperedges (group relationships)
- **Graphify Extraction and Build Flow** — _codex_skills_graphify_skill_structural_extraction, _codex_skills_graphify_skill_semantic_extraction, _codex_skills_graphify_references_extraction_spec_semantic_extraction_contract, _codex_skills_graphify_references_update_build_merge [EXTRACTED 1.00]
- **Hybrid Neural Landing Control** — implementation_plan_classical_pid_plant, implementation_plan_npgs, implementation_plan_deterministic_shield, implementation_plan_ppo_multicomponent_loss, implementation_plan_pinn_observer [EXTRACTED 1.00]
- **PID Dashboard Ecosystem** — docs_xplane_dashboard_pid_dashboard, ismpu_gui_dashboard_pid_dashboard, ismpu_working_ics_ics_dashboard_ics_pid_monitor [INFERRED 0.85]

## Communities (123 total, 25 thin omitted)

### Community 0 - "SpecialSituation"
Cohesion: 0.13
Nodes (18): lateral_load_situation(), normal_load_situation(), IntEnum, Критерии критичности особых ситуаций МС-21 (Приложение 1 к ТЗ). Таблица АП-25…, Классификация скорости касания относительно VAPP и VВПП пред., Классификация нормальной перегрузки посадочного удара. `heavy` — взлётный вес., Классификация боковой составляющей перегрузки касания., Степень опасности особой ситуации по АП-25. Упорядочена по возрастанию тяжести:… (+10 more)

### Community 1 - "test_splits.py"
Cohesion: 0.06
Nodes (59): contract_for(), Сколько раз прогнать сценарий, чтобы результат приёмки что-то значил., Источники случайности на стороне стенда, активные при данных условиях. Мы…, Строит контракт воспроизводимости для сценария., required_replicas(), stochastic_sources(), assert_no_leakage(), has_holdout_failure() (+51 more)

### Community 2 - "reward.py"
Cohesion: 0.07
Nodes (34): _command_jerk(), _component(), compute_reward(), excess(), graded(), ObjectiveWeights, _p95(), TypedDict (+26 more)

### Community 3 - "weather.py"
Cohesion: 0.07
Nodes (31): Фактические погодные условия со стенда (ветер, сцепление, осадки, видимость)., Enum, Погодные условия эпизода: описание, шкала сцепления и разбор ветра. Модуль **не…, `ICSInputs` → `WeatherState`. Единственный источник фактической погоды. Стенд…, Состояние ВПП как **монотонная шкала скользкости** 0…15 (0 — сухо, 15 — лёд со…, Код состояния ВПП со стенда → наша шкала. Неизвестный код трактуется как `ICY`,…, runway_condition_from_bench(), RunwayCondition (+23 more)

### Community 4 - "Shield"
Cohesion: 0.08
Nodes (36): _clip(), GainCommand, GainMap, RegulatorKey, Наблюдаемое состояние для поведенческих проверок уровня 3., Что сделал Shield за такт: активированные правила, штрафы, fallback., Границы и веса штрафов Shield (все — настраиваемые, а не свойства сети)., Защитный контур. Детерминирован; хранит состояние прошлого такта для rate-… (+28 more)

### Community 5 - "json_config.py"
Cohesion: 0.15
Nodes (24): ApproachConfig, Настройки воздушного участка: заход по ILS, выравнивание, управление скоростью.…, Параметры воздушного контура. Значения по умолчанию — настроенные на стенде.…, approach_control_from_dict(), _copy_approach(), ground_control_from_dict(), _legacy_ground(), _legacy_matrix_segments() (+16 more)

### Community 6 - "SimInterface"
Cohesion: 0.11
Nodes (5): BaseException, StartMode, Минимальный lifecycle, одинаковый для стенда и X-Plane., SimInterface, Protocol

### Community 7 - "test_approach_channel.py"
Cohesion: 0.14
Nodes (31): airborne_inputs(), Кадр «ВС на глиссаде»: стойки не обжаты, ILS валиден, скорость и высота…, _our_channel(), Воздушный канал: заход по ILS, выравнивание, скоростной канал. Главный тест…, Угол сноса не должен превращаться в ошибку курса на локализаторе., Стенд иногда сбрасывает Valid при сохранении пригодного численного значения., Отклонение планки курса задаёт доворот в сторону оси, а не от неё., Крен парируется элеронами с обратным знаком — это проводка стенда, а не… (+23 more)

### Community 8 - "ControllingSystem"
Cohesion: 0.05
Nodes (42): ControllingSystem, FailureMode, Связать сценарий с контуром; PID активируются после определения участка., Обновить параметры геометрического наведения латерального канала. Имя сохранено…, Веса влияния каналов (актор, §6): множители к выходам каналов. 1.0 = классика., Привести модель отказов к тому, что сообщает борт (`ICSInputs.Fault*`). Отказы…, Такт управления. → True, если управление окончено (или телеметрия невалидна).…, Прервать заход с названной причиной. → True (управлять больше нечем). (+34 more)

### Community 9 - "ICSInputs"
Cohesion: 0.08
Nodes (20): _faults_from_inputs(), Отказы, о которых сообщает борт — **единственный** источник истины об отказах.…, Сигналы отказов со стенда → наши `FailureMode`. Отказы шасси…, ICSInputs, Неизвестные поля исходного JSON; они доступны аудиту, но не закону управления., engaged_inputs(), flight_sim(), kinematic_sim() (+12 more)

### Community 10 - "test_refactoring_contracts.py"
Cohesion: 0.14
Nodes (21): approach_control_to_dict(), dump_scenario(), _finite_tree(), ground_control_to_dict(), load_scenario(), Any, Path, scenario_from_document() (+13 more)

### Community 11 - "LongitudinalChannel"
Cohesion: 0.18
Nodes (6): LongitudinalChannel, Управление скоростью по эталонной кривой. Телеметрию получает параметром, не…, PidMap, PIDController, ReferenceTrajectory, VelocityLaw

### Community 12 - "NPGS"
Cohesion: 0.08
Nodes (54): NPGS, Neural PID Gain Scheduler: общий энкодер + головы актора (абс. gain'ы) + голова…, _phase_labels(), pretrain_sft(), PretrainConfig, float32, GainMap, NDArray (+46 more)

### Community 13 - "scenarios.py"
Cohesion: 0.10
Nodes (27): cases_for_segment(), _kts(), MatrixCase, MatrixCondition, Матрица прогонов для настройки базовых ПИД-регуляторов. Машиночитаемая форма…, Один шифр матрицы — вариант отказа/режима, под который настраивается набор…, Шифры одного участка: `approach` / `rollout` / `taxi` / `through`., Матрица задаёт ветер в м/с, телеметрия приходит в узлах. (+19 more)

### Community 14 - "ICSOutputs"
Cohesion: 0.07
Nodes (30): GearState, ICSBenchConnector, ICSOutputs, main(), Разбор телеметрии стенда с совместимостью вперёд. Асимметрия намеренная (JSON-…, Отправка best-effort со счётчиком ошибок и разрежённым логом. Windows отдаёт…, → True если отправлено. Исключение наружу не выпускается., Мост к стенду: JSON поверх UDP, адрес стенда определяется из входящего пакета. (+22 more)

### Community 15 - "Scenario"
Cohesion: 0.07
Nodes (35): compose_scenario(), match_conditions(), _profile_name(), Полный профильный сценарий APPROACH → ROLLOUT → TAXI., Условия пробега для report/eval-кода, работающего только на земле., Собрать сценарий из независимых источников участков., Scenario, scenario_distance() (+27 more)

### Community 16 - "AircraftProfile"
Cohesion: 0.08
Nodes (14): AircraftProfile, clamp(), Профили преобразования команд ИСМПУ в органы управления X-Plane., Преобразовать воздушные команды ICD в нормированные DataRef X-Plane., Преобразовать нормированные команды пробега в DataRef X-Plane., Расширение реестра будущим профилем МС-21 без правки XPlaneSim., Проводка и масштабы конкретного планера X-Plane., Общая идентичность ЛА и необязательная привязка к X-Plane. Профиль нужен и… (+6 more)

### Community 17 - "ICSSim"
Cohesion: 0.07
Nodes (20): EngagementInputs, _clamp(), ICSSim, FailureMode, StartMode, Обмен со стендом заказчика: телеметрия внутрь, команды наружу. Управление…, Принимает ли стенд наши команды. До включения любой `step` уходит вхолостую., Начало эпизода: сброс рукопожатия и первый кадр со стенда. Средой распоряжается… (+12 more)

### Community 18 - "ApproachChannel"
Cohesion: 0.15
Nodes (19): ApproachChannel, ApproachResult, clamp(), ApproachLimits, ApproachTelemetry, Заход по ILS с выравниванием. Телеметрию получает параметром, не читает сам.…, Сброс регуляторов и всей памяти профиля — новый заход начинается с чистого…, Такт воздушного управления: пишет команды в `state`, возвращает диагностику.… (+11 more)

### Community 19 - "Telemetry"
Cohesion: 0.05
Nodes (34): approach_blocker(), ApproachRefused, Воздушный участок начинать нельзя — с названной причиной. Отдельное исключение,…, Почему нельзя вести заход по этому кадру. `None` — можно. Пока проверка одна,…, GoAroundManeuver, FlightSegment, Пересобрать stateful PID и уведомить backend до первого такта участка., Определить стартовый участок по кадру стенда. → выбранный участок. Вызывается в… (+26 more)

### Community 20 - "test_gain_scheduler.py"
Cohesion: 0.09
Nodes (23): build_npgs(), device, Веса + конфиг + слепок нормировки (включая gain-пространство) одним артефактом., action_high(), action_low(), float32, NDArray, reference_action() (+15 more)

### Community 22 - "test_weather.py"
Cohesion: 0.08
Nodes (29): clip_unit(), linear(), log_norm(), Фиксированная нормализация Observation Space — единый контракт train ↔ deploy.…, Лог-нормировка неотрицательной величины (видимость): log1p(x)/log1p(scale)., Отображает [lo, hi] → [-1, 1] (для PID output по его границам)., Сериализуемый слепок контракта нормировки (сохраняется вместе с весами).…, snapshot() (+21 more)

### Community 23 - "PIDController"
Cohesion: 0.05
Nodes (45): Один регулятор, коэффициенты которого (kp/ki/kd) разрешено настраивать сети., RegulatorSpec, Регуляторы канала по именам — для логов и приёмки, не для…, PIDController, Пропорционально-интегрально-дифференциальный регулятор. Улучшенный PID с leaky-…, → (интеграл только с утечкой, интеграл с утечкой и приращением). Оба уже зажаты., Такт регулятора. `measurement` обязателен при `derivative_on_measurement=True`., Back-calculation: подтянуть интегратор к фактически применённой команде. No-op… (+37 more)

### Community 24 - "evaluate.py"
Cohesion: 0.09
Nodes (28): Худшая реплика по заданной метрике. Приёмка смотрит именно на худшую, а не на…, worst_replica(), compare_policies(), DefaultGainsPolicy, load_npgs_policy(), main(), NPGSPolicy, Policy (+20 more)

### Community 25 - "RolloutEnv"
Cohesion: 0.08
Nodes (25): PPOTrainer, Tensor, Собирает rollout из среды и обновляет NPGS многокомпонентным PPO-loss., Шагает средой `rollout_len` тактов (сброс по завершению эпизода). → статистика., Хук L_shield (§11): барьер, отталкивающий выход от края уровня-1 Shield. По…, ndarray, Scenario, Окно истории → тензор `(history_len, OBS_DIM)` (последовательность кадров для… (+17 more)

### Community 26 - "WeatherState"
Cohesion: 0.08
Nodes (23): get_aircraft_profile(), Ожидаемые физические условия одного участка., SegmentConditions, FrictionProfile, Погодные условия. Поля — ровно то, что сообщает стенд (см. `from_ics`).…, Ступенчатый профиль сцепления по дистанции пробега., WeatherState, test_xplane_ignores_failures_outside_rollout_contract() (+15 more)

### Community 27 - "test_evaluate.py"
Cohesion: 0.15
Nodes (31): evaluate_tz(), Диагностика эпизода + сценарий → список вердиктов по пунктам ТЗ разд. 5., Итог эпизода: FAIL, если провален хоть один применимый критерий., verdict_of(), _by_name(), _diagnostics(), Тесты приёмки по ТЗ (Этап 5): вердикты по пунктам, правило «нет данных = FAIL»,…, Эпизод не дошёл до руления → допуск ±1 м неприменим. Это SKIP, а не тихий… (+23 more)

### Community 28 - "test_ppo.py"
Cohesion: 0.13
Nodes (22): NPGSConfig, Any, Гиперпараметры архитектуры NPGS (замораживаются вместе с весами при поставке)., PPOConfig, Any, device, Плоский буфер одного env: obs-окна, сырые действия, logp/value/reward/done., RolloutBuffer (+14 more)

### Community 29 - "IcsEngagement"
Cohesion: 0.07
Nodes (16): IcsEngagement, Автомат включения. `step(inputs)` вызывается каждый такт до формирования…, Полный сброс — новый эпизод начинается с невключённого состояния., Сообщить автомату, что кадр **фактически ушёл** на стенд. Вызывается…, Войти в заход самостоятельно: шлём `ControlMode = Approach`. Обычно вызывать не…, Выдержка под текущую цель: воздушная длиннее наземной (2.2 с против 2.0)., Уже гоним какой-то режим (Approach/Rollout/Taxi), а не заявку готовности., Признак стенда `AgentIsActive`: интерфейс ICS активен. Необходимое условие. (+8 more)

### Community 30 - "XPlaneConnectX"
Cohesion: 0.08
Nodes (13): XPlaneConnectX class initialization. Args: ip (str, optional): IP address where…, Starts a recording of the subscribed DataRefs into self.recorded_data. Data is…, Terminates the recording and returns a dictionary of lists that contain the…, Synchronize measurements from multiple sensors to a common frequency.…, Gets the current value of a DataRef. This is only intended for one-time use.…, Permanently subscribe to a list of DataRefs with a certain frequency. This is…, Writes a value to the specified DataRef provided that the DataRef is writable.…, Sends simulator commands to the simulator. These are not commands for the… (+5 more)

### Community 31 - "rollout_env.py"
Cohesion: 0.11
Nodes (19): PPO-тренер + многокомпонентный loss для NPGS (план §11). `L = L_ppo +…, Геометрия целевой ВПП и высоты установки ЛА. Смена целевой полосы = правка…, Слежение за осью ВПП: геодезия, cross-track error, guidance с look-ahead.…, Генератор эталонной кривой скорости пробега. Два закона замедления: колокол…, TrajectoryState, ObserverEstimate, Observation Space — сборка и нормировка вектора состояния (§5). Собирает один…, Оценки PINN-обсервера (§12). Заглушка нулями до Этапа 7. (+11 more)

### Community 32 - "gain_scheduler.py"
Cohesion: 0.17
Nodes (14): int64, ActorOutput, _init_log_std(), layer_init(), _mlp_head(), phase_labels_from_groundspeed_kts(), ArrayLike, TypedDict (+6 more)

### Community 33 - "Graphify Pipeline"
Cohesion: 0.08
Nodes (29): Folder Watcher, URL Ingestion, Extra Graph Exports, MCP Graph Server, Confidence Audit Trail, Deterministic Node IDs, Semantic Extraction Contract, Cross-Repository Graph Merge (+21 more)

### Community 34 - "XPlaneConnector"
Cohesion: 0.07
Nodes (12): DataRefSample, Неблокирующий UDP-клиент нативного протокола X-Plane 12., Discard pre-reload values so readiness cannot use stale telemetry., Одна подписка, один поток приёма и явное освобождение ресурсов., Send basic controls to the ego aircraft. There are hundreds of DataRefs that…, Разобрать пакет; публично для детерминированных mock-тестов., Совместимое read-only представление старого XPlaneConnectX., Совместимость с прежним клиентом. (+4 more)

### Community 35 - "static_sim"
Cohesion: 0.12
Nodes (22): preset_action(), float64, GainMap, 17-мерное действие, точно воспроизводящее коэффициенты пресета (веса = 1).…, decode_outputs(), Отправленные команды в нормированном виде — для сравнения траекторий.…, `ICSOutputs` → (brake_l, brake_r, thr_l_rate, thr_r_rate, steer), всё…, (sim, connector) с неизменным кадром у порога ВПП. Скорость задаётся в **м/с**.… (+14 more)

### Community 36 - "GainSpace"
Cohesion: 0.18
Nodes (9): GainKey, GainSpace, Any, ArrayLike, float64, GainMap, NDArray, RegulatorKey (+1 more)

### Community 37 - "test_ics_engagement.py"
Cohesion: 0.11
Nodes (44): _Clock, _engine(), _pump(), Автомат включения управления на стенде. Два раздельных предмета проверки: *…, По ICD стенд должен два секунды ПОЛУЧАТЬ ModeAIReady=1. Если считать одно лишь…, Обратная защита: 30 кадров можно выпалить за 0.1 с — время тоже обязано пройти., Срыв предусловия обнуляет и время, и счётчик кадров., Требование ICD — непрерывность: пропуск готовности рвёт серию. (+36 more)

### Community 38 - "test_diagnostic_tools.py"
Cohesion: 0.20
Nodes (19): build_altitude_sweep(), command_for_pulse(), Безопасные elevator/altitude authority sweep без дублирования ICS runner., Чистое преобразование, пригодное и для dry-run, и для ICSSim., safety_reason(), SweepLimits, SweepPulse, validate_pulse() (+11 more)

### Community 39 - "test_ics_sim.py"
Cohesion: 0.04
Nodes (60): engaged_sim(), FakeConnector, HandshakeBench, make_ics_inputs(), on_ground(), Статический стенд: всегда один и тот же кадр, отправленное — в `sent_outputs`., (sim, connector) с завершённым рукопожатием: стенд подтвердил `AgentIsActive =…, Стенд, включающий управление только после корректного рукопожатия. Ждёт… (+52 more)

### Community 40 - "pid_controller.py"
Cohesion: 0.14
Nodes (21): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+13 more)

### Community 41 - "system.py"
Cohesion: 0.07
Nodes (36): IcsEngagement, IntEnum, Глобальные константы контура управления (перенесены из main.ipynb)., Константы интерфейса стенда заказчика (ПИВ / ICS). Единый источник правды по…, Приёмочные пороги из ТЗ (раздел 5). Единый источник истины для reward-шейпинга…, _destination(), get_runway_profile(), Профили ВПП и разрешение ILS из установленной базы X-Plane. (+28 more)

### Community 42 - ".act_numpy"
Cohesion: 0.15
Nodes (11): floating, float32, NDArray, Tensor, → (mean (B,17), value (B,), phase_logits (B,n_phases))., 17 сырых выходов → [абс. gains×15, w_lon, w_lat] (layout `REGULATOR_ORDER` +…, Один шаг актора. `action` (…,17) — абс. gain'ы для среды; `raw` (…,17) — сэмпл…, Пересчёт на апдейте PPO. → (logp, entropy, value, mean, phase_logits). (+3 more)

### Community 43 - "runner.py"
Cohesion: 0.13
Nodes (28): ControlResult, airborne_control_mode(), airborne_flare_mode(), deactivate(), live_main(), main(), main_gear_contact(), make_airborne_output() (+20 more)

### Community 44 - "channels.py"
Cohesion: 0.07
Nodes (41): apply_gains_to_pids(), base_gains_from_pids(), PidMap, Shield — детерминированный защитный контур между актором и классическим PID.…, Снимок (kp, ki, kd) регуляторов — пресет-якорь для Shield и т.п., Записывает эффективные gain'ы обратно в регуляторы (перед control_step)., ControlArchitecture, Канонический порядок регуляторов, размерности действия и **контракт обучаемого… (+33 more)

### Community 45 - "test_run_matrix.py"
Cohesion: 0.11
Nodes (18): ground_cases(), Шифры, у которых настраиваются коэффициенты **пробега** (пригодны для SFT).…, compose_matrix_scenario(), _install_through_scenarios(), matrix_battery(), Сценарий по имени либо шифру матрицы, без различия раскладки А/B., Объединить случай листа А и случай листа Б в один полный сценарий. Аргументы…, Собрать штатные сквозные случаи Б.4 из реальных источников листов А и Б. (+10 more)

### Community 46 - "ScenarioGenerator"
Cohesion: 0.19
Nodes (7): Один случайный сценарий. `difficulty=None` → случайная сложность., ScenarioGenerator, AdmissionResult, test_generator_embeds_control_config(), test_generator_high_difficulty_produces_failures(), test_generator_is_deterministic_for_same_seed(), test_generator_zero_difficulty_has_no_failures()

### Community 47 - "EngagementInputs"
Cohesion: 0.11
Nodes (11): EngagementInputs, ControlModeState, Подхватить уже включённый извне пробег: шлём `ControlMode = Rollout`.…, Войти в пробег самостоятельно: шлём `ControlMode = Rollout`. Это же — передача…, Передать управление в руление (`ControlMode 3 → 4`). → удался ли переход.…, Продвинуть автомат: снять признак стенда и обновить исходящий стимул.…, Оба условия сразу: прошло время И столько же кадров реально ушло. Время…, Под какой режим гнать стимул. `None` — предусловий нет ни для одного. Воздушный… (+3 more)

### Community 48 - "RunRecorder"
Cohesion: 0.22
Nodes (6): default_runs_root(), Path, Один раз сохранить накопленные кадры и итоговые артефакты прогона., Единый каталог прогонов, не зависящий от cwd процесса/Jupyter., RunRecorder, test_zero_sample_run_has_a_replayable_csv_header()

### Community 49 - "test_full_flight.py"
Cohesion: 0.05
Nodes (63): IntFlag, ControlValid, Биты `ControlValidMask`: какие каналы несёт команда. **Один бит на одно…, initial_segment(), is_airborne(), FlightSegment, Окончен ли воздушный участок. Два независимых признака, любой достаточен:…, Сообщает ли стенд, что ВС в воздухе и достаточно высоко для приёма захода.… (+55 more)

### Community 50 - "_frame"
Cohesion: 0.14
Nodes (20): _armed_controller(), _drive(), _frame(), Если реверс уже включён — взлёт невозможен, ухода нет., Устойчивый набор (прирост высоты + положительная верт. скорость) завершает…, После установившегося набора цикл снимает заявку каналов (ControlMode=Off,…, Контур на заходе: `begin_flight` по кадру в воздухе выше 400 футов., Устойчивое превышение курсового допуска выше высоты решения → уход на второй… (+12 more)

### Community 51 - "Neural PID Gain Scheduler Architecture"
Cohesion: 0.19
Nodes (19): Hybrid Neural PID Controller, Neural PID Gain Scheduler, PPO Training Loop, Preset-Anchored Deterministic Shield, SFT Behavioral-Cloning Warm Start, Absolute-Gain Action Space, Classical PID as the Plant, Deterministic Deployment Runtime (+11 more)

### Community 52 - "test_approach_criteria.py"
Cohesion: 0.09
Nodes (20): ApproachChannel, ApproachConfig, angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, Отдельный монитор критерия А.1.1 (не участвует в go-around). (+12 more)

### Community 53 - "test_tolerance.py"
Cohesion: 0.19
Nodes (20): lateral_limit_m(), lateral_situation(), Zпред — предельное отклонение оси ВС от оси ВПП (внешнее колесо у кромки).…, Классификация бокового увода по Табл. 1. Норма (БС/УУП): |Zбок| ≤ Zпред − 5 м.…, evaluate_approach_tolerances(), Проверить допуски захода по текущему такту. Команды не трогает. `result` —…, Допуски захода: классификаторы критичности (Приложение 1) и рантайм-монитор.…, 0.6° вне штатного допуска 0.5°, но в пределах допуска при отказе шасси (0.7°). (+12 more)

### Community 54 - "gui/dashboard.py"
Cohesion: 0.18
Nodes (12): _finite_or_none(), GainUpdateRequest, Unified local dashboard for the three airborne and five ground PIDs., Валидировать HTTP-запрос и передать запись control-потоку., ViewSpec, controller_pids(), gains_snapshot(), _jsonable() (+4 more)

### Community 55 - "RunwayTracker"
Cohesion: 0.14
Nodes (10): Точка на продолжении оси; положительное расстояние — до порога., Возвращает отклонение от осевой линии в метрах. >0 - правее оси, <0 - левее., Геодезическое наведение на ось ВПП с упреждением по скорости., RunwayTracker, GainSpace, test_guidance_on_centerline_small_heading_error(), test_xte_sign_left_is_negative(), test_xte_sign_right_is_positive() (+2 more)

### Community 56 - "RomanLogImporter"
Cohesion: 0.19
Nodes (10): _number(), Path, Импорт и проверка внешних CSV-прогонов roman_aviacia_ics., Потоково нормализует основной и authority CSV Романа., RomanLogImporter, verify_manifest(), fixture, roman_csv() (+2 more)

### Community 57 - "ICSInputs"
Cohesion: 0.23
Nodes (8): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, ICSInputs, Evaluate the A.1.1 approach segment and stop at a radio-altitude floor., ICSInputs

### Community 58 - "parse_ils_station"
Cohesion: 0.43
Nodes (6): find_earth_nav_dat(), ILSStation, parse_ils_station(), Path, Найти LOC (тип 4) без хардкода частоты., test_earth_nav_parser_finds_requested_localizer()

### Community 59 - ".send_outputs"
Cohesion: 0.33
Nodes (5): _integrate_throttle(), Ход рычага РУД за такт: интеграл команды-скорости, зажатый физическим…, Доля обратной тяги по фактическому углу РУД: 0 в положительном секторе, 1 на…, Замедление считается по **фактическому** углу РУД, а не по команде. Тягой…, _reverse_fraction()

### Community 60 - "gain_space_for"
Cohesion: 0.24
Nodes (12): gain_space_for(), _profile_name(), Профильное пространство абсолютных PID-коэффициентов NPGS., _regulator_config(), Профильные пространства абсолютных PID-коэффициентов NPGS., test_every_profile_preset_gain_is_inside_its_band(), test_gain_space_can_be_built_from_external_scenario_registry(), test_normalization_endpoints_and_nonpositive_guard() (+4 more)

### Community 61 - "ReferenceTrajectory"
Cohesion: 0.29
Nodes (5): Генератор эталонной кривой скорости (Колокол Гаусса)., Возвращает идеальную скорость (м/с) для текущей точки пути., ReferenceTrajectory, test_equally_slow_law_endpoints(), test_gauss_bell_endpoints_and_monotonicity()

### Community 62 - "Project Dependencies"
Cohesion: 0.18
Nodes (13): Autonomous Landing Controller, Repository Guidance for Codex, Autonomous Landing Controller, Repository Guidance for Claude Code, Neural Landing Implementation Plan, Unified Scenario System, Optional Gymnasium, NumPy (+5 more)

### Community 63 - "admit_checkpoint"
Cohesion: 0.18
Nodes (16): admit_checkpoint(), Пропускать ли чекпоинт дальше. Отсутствующая/нечисловая метрика = отказ.…, _battery(), Отсутствующая метрика = отказ, а не «нет данных — значит нет проблемы»., Если сеть не бьёт классику, она не окупается — выпускать её нечего., Канал не двигался за эпизод → p95 = None. Это не дефект., Отрицательный результат должен быть виден в отчёте, а не спрятан., Сводка прогона под одной политикой из списка диагностик. (+8 more)

### Community 64 - "LateralChannel"
Cohesion: 0.18
Nodes (7): LateralChannel, Удержание оси ВПП. Телеметрию получает параметром, не читает сам., Guidance по тому, что даёт стенд. → словарь guidance или None, если данных нет.…, Единый GuidanceState текущего кадра для control/observation/reward., GuidanceState, Совместимость с прежним атрибутом; новый термин явно указывает ось., Совместимость со старым словарным API.

### Community 66 - "test_dashboard.py"
Cohesion: 0.21
Nodes (6): DashboardServer, main(), configured_controller(), test_capture_export_and_replay_common_run(), test_dashboard_http_api_is_local_and_monitor_only(), test_monitor_only_and_npgs_tuning_locks()

### Community 67 - "test_rollout_env.py"
Cohesion: 0.16
Nodes (19): ObservationBuilder, Строит нормированный вектор наблюдения одного кадра., heading_deviation_deg(), Отклонение курса ВС от направления ВПП — приёмочная величина ТЗ 5.1.3.3 /…, Тесты Этапа 2: Observation/Action/reward/RolloutEnv + инвариант identity ==…, Телеметрия ВС на оси ВПП, смещённого вбок на `offset_m` и с заданным курсом.…, ТЗ 5.1.3.3 нормирует курс «от направления ВПП». Смещение от оси на него не…, На стенде курс ВПП приходит телеметрией; конфиг — только значение по умолчанию. (+11 more)

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

### Community 73 - "RuntimeError"
Cohesion: 0.20
Nodes (6): ConditionMatch, FlightSegment, Scenario, Сверить ожидаемые условия; стендовые условия никогда не изменяются кодом., StartMode, RuntimeError

### Community 74 - "ClearWeatherILSController"
Cohesion: 0.15
Nodes (7): DashboardServer, DashboardState, Any, ICSInputs, ClearWeatherILSController, test_roundout_commands_a_material_pitch_increase_before_touchdown(), test_terminal_pitch_hold_starts_before_last_five_feet_guidance_cutoff()

### Community 75 - "protocol.py"
Cohesion: 0.25
Nodes (6): ControlModeState, GearState, ICSOutputs, Any, IntEnum, ReverseEngineType

### Community 76 - "ICSInterface.cs"
Cohesion: 0.36
Nodes (7): External.Systems.ICS, ControlModeState, GearState, ICSInputs, ICSOutputs, ReverseEngineType, UInt64

### Community 77 - ".enter_segment"
Cohesion: 0.20
Nodes (5): FailureMode, FlightSegment, Scenario, Применить только дельту условий при переходе между участками., Снять один отказ, не переинициализируя отказ, продолжающийся на новом участке.

### Community 78 - "EpisodeObjective"
Cohesion: 0.20
Nodes (8): EpisodeObjective, Накопитель по эпизоду: собирает потактовые отсчёты → сводные компоненты.…, Фиксированный приёмочный набор (детерминированный, без RNG)., Отсутствие данных даёт None, а не 0 — приёмка обязана трактовать это как FAIL., p95 темпа не ловится одиночным выбросом — в отличие от максимума., test_episode_objective_p95_rate_is_robust_to_a_single_spike(), test_episode_objective_reports_none_for_unobserved_phases(), test_episode_objective_separates_rollout_and_taxi_phases()

### Community 79 - "loop.py"
Cohesion: 0.14
Nodes (15): build_sim(), Any, Path, Создать backend; для ICS геодезия включается только явным ``runway_profile``., Результат безусловного best-effort отключения backend., RunResult, ShutdownReport, _lost_engagement() (+7 more)

### Community 80 - "ICS PID Monitor"
Cohesion: 0.29
Nodes (7): buildControls, draw, formatTime, Four-Loop PID Tuning, ICS PID Monitor, Live and Historical Timeline, refresh

### Community 81 - ".guidance"
Cohesion: 0.25
Nodes (3): Решить прямую геодезическую задачу на сферической Земле., Геодезическое guidance в истинной системе направлений., Guidance по курсу ВПП и измеренному отклонению — без собственной геодезии.…

### Community 82 - "ICS UDP JSON Protocol"
Cohesion: 0.33
Nodes (6): Fourteen-Bit ControlValidMask Layout, Dual-Backend SimInterface, Two-Factor ICS Engagement Handshake, ICS UDP JSON Protocol, Telemetry SI Unit Boundary, ICS-Only Backend Guidance

### Community 83 - "X-Plane Dashboard and Runtime Guide"
Cohesion: 0.60
Nodes (6): Aircraft-Profile Checkpoint Isolation, Live A330 Acceptance Checklist, Profile-Aware Flight Scenarios, X-Plane Dashboard and Runtime Guide, X-Plane Resettable Runtime, X-Plane Training and Evaluation Backend

### Community 84 - ".from_json"
Cohesion: 0.33
Nodes (5): _pid_from_colleague(), Загрузка настроек из JSON коллеги (`config/ics_clear_weather_pid.json`). Секции…, `PIDConfig` коллеги → аргументы нашего `PIDController`. Предел интегратора у…, Наши умолчания и его файл — одно и то же. Разойдутся — расхождение должно быть…, test_config_from_the_colleague_json_matches_our_defaults()

### Community 85 - "ControlsState"
Cohesion: 0.11
Nodes (15): FailureState, ControlsState, PidMap, Деградация команд по эффективности актуаторов — **только наземные органы**.…, Финальные пределы наземных команд — после дифференциального микса. Воздушные…, Обнуляет все органы управления. Отправку делает вызывающий через `ICSSim.step`.…, Разделяемая по тактам структура команд — и наземных, и воздушных. Аннотации…, Сброс к нейтральным командам — новый эпизод начинается с чистого состояния.… (+7 more)

### Community 86 - "DashboardState"
Cohesion: 0.17
Nodes (6): DashboardState, _handler_factory(), _jsonable(), Path, Применяется только control-потоком в начале такта., Thread-safe live state or an immutable CSV replay.

### Community 87 - "sim_interface.py"
Cohesion: 0.29
Nodes (6): ControlDiagnostics, Enum, Общий контракт симулятора и воздушных сигналов. ICS и X-Plane различаются…, RunStopReason, XPlaneDiagnostics, str

### Community 88 - ".from_crosswind"
Cohesion: 0.29
Nodes (5): Any, Собирает ветер из компонент относительно курса ВПП. `crosswind_kts` > 0 — ветер…, Сериализация в примитивы (для логирования/воспроизводимости сценариев)., test_scenario_roundtrip_with_weather_and_failures(), test_weatherstate_from_crosswind()

### Community 89 - "control/approach.py"
Cohesion: 0.11
Nodes (25): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+17 more)

### Community 91 - "Criterion"
Cohesion: 0.40
Nodes (4): _check(), Criterion, Один пункт ТЗ: предел, измеренное значение, вердикт и его причина., Строит вердикт. Неприменимо → SKIP; применимо, но данных нет → FAIL.

### Community 92 - "roll_limit_deg"
Cohesion: 0.50
Nodes (4): Предел крена по высоте: чем ниже, тем меньше запас до касания законцовкой.…, roll_limit_deg(), Чем ниже, тем меньше запас до касания законцовкой; настроенный предел не…, test_roll_limit_tightens_towards_the_ground()

### Community 93 - "_WarmUpSim"
Cohesion: 0.25
Nodes (5): Стенд, включающий управление только после N тактов прогрева. Само рукопожатие…, Такты рукопожатия — не шаги эпизода: в это время ВС нами не управлялось. Иначе…, test_env_reports_engagement_state_in_info(), test_warm_up_runs_before_the_episode_and_is_not_counted(), _WarmUpSim

### Community 94 - "PresetPolicy"
Cohesion: 0.29
Nodes (5): PresetPolicy, Baseline 2 («оракул»): коэффициенты пресета сценария = классика, под которую он…, _scripted_env(), test_compare_policies_flags_which_baseline_each_policy_beats(), test_run_episode_produces_criteria_and_diagnostics()

### Community 95 - "test_zero_bound_is_not_counted_as_saturation"
Cohesion: 0.29
Nodes (7): _effort_saturated(), Упёрлась ли команда в границу **со стороны усилия**. Важное различие: нулевая…, Доля из 5 команд, исчерпавших авторитет (упёршихся в ненулевую границу PID).…, saturation_fraction(), Тормоз на 0 = «торможение не требуется», а не «авторитет исчерпан». Иначе флаг…, test_saturation_fraction_counts_commands_pegged_at_their_pid_bounds(), test_zero_bound_is_not_counted_as_saturation()

### Community 109 - "EngagementState"
Cohesion: 0.27
Nodes (6): FlightPhase, IntEnum, Фаза полёта, сообщаемая стендом (`ICSInputs.FlightPhase`)., EngagementState, Enum, Состояние **исходящего стимула** (что мы шлём стенду), а не факта включения.…

### Community 110 - "._should_go_around"
Cohesion: 0.40
Nodes (3): Реверс убран: команды обратной тяги нулевые. В воздухе реверс не выдаётся…, Нужно ли уходить на второй круг по этому такту. → причина или `None`. Только…, ToleranceReport

### Community 111 - "Q: Реализовать этап 0: baseline, golden replay и dashboard characterization"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Реализовать этап 0: baseline, golden replay и dashboard characterization, Source Nodes

### Community 112 - "Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md)., Source Nodes

### Community 113 - "test_approach_limits_take_the_conservative_weight_row"
Cohesion: 0.33
Nodes (4): Между строками таблицы берётся ближайшая сверху, а не интерполяция., Умолчания пакета — это настроенные на стенде значения, а не дефолты класса…, test_approach_limits_take_the_conservative_weight_row(), test_default_config_carries_the_tuned_bench_gains()

### Community 116 - "tolerance.py"
Cohesion: 0.20
Nodes (9): _glideslope_tolerance_deg(), ApproachLimits, ApproachTelemetry, Монитор допусков захода в реальном времени + классификация особой ситуации.…, Результат проверки допусков захода на одном такте. `landing_allowed` — все ли…, Допуск по глиссаде с учётом отказа (ТЗ 5.1.2.1–5.1.2.3), самый мягкий из…, Диагностическая градация приборной скорости по огибающей механизации., _speed_situation() (+1 more)

## Ambiguous Edges - Review These
- `Unified Profile-Aware Scenario System` → `Legacy Scenario Preset Model`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to
- `Dual-Backend SimInterface` → `ICS-Only Backend Guidance`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **37 isolated node(s):** `ismpu`, `Answer`, `Outcome`, `Source Nodes`, `Answer` (+32 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `ObservationBuilder` (2× useful, score=1.962059332)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Unified Profile-Aware Scenario System` and `Legacy Scenario Preset Model`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Dual-Backend SimInterface` and `ICS-Only Backend Guidance`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `ControllingSystem` connect `ControllingSystem` to `json_config.py`, `SimInterface`, `ICSInputs`, `test_refactoring_contracts.py`, `LongitudinalChannel`, `NPGS`, `scenarios.py`, `Scenario`, `Telemetry`, `test_gain_scheduler.py`, `PIDController`, `evaluate.py`, `RolloutEnv`, `WeatherState`, `test_evaluate.py`, `test_ppo.py`, `rollout_env.py`, `XPlaneConnector`, `static_sim`, `test_ics_sim.py`, `system.py`, `channels.py`, `test_run_matrix.py`, `ScenarioGenerator`, `test_full_flight.py`, `_frame`, `test_approach_criteria.py`, `RunwayTracker`, `LateralChannel`, `test_dashboard.py`, `test_rollout_env.py`, `loop.py`, `ControlsState`, `Criterion`, `_WarmUpSim`, `PresetPolicy`, `test_zero_bound_is_not_counted_as_saturation`, `._should_go_around`?**
  _High betweenness centrality (0.141) - this node is a cross-community bridge._
- **Why does `Telemetry` connect `Telemetry` to `weather.py`, `json_config.py`, `SimInterface`, `test_approach_channel.py`, `ControllingSystem`, `ICSInputs`, `LongitudinalChannel`, `scenarios.py`, `ICSOutputs`, `Scenario`, `AircraftProfile`, `ICSSim`, `ApproachChannel`, `XPlaneSim`, `WeatherState`, `static_sim`, `test_diagnostic_tools.py`, `test_ics_sim.py`, `system.py`, `channels.py`, `test_full_flight.py`, `_frame`, `test_approach_criteria.py`, `test_tolerance.py`, `LateralChannel`, `test_rollout_env.py`, `RuntimeError`, `.enter_segment`, `loop.py`, `ControlsState`, `sim_interface.py`, `control/approach.py`, `_WarmUpSim`, `._should_go_around`, `tolerance.py`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._
- **Why does `ControlsState` connect `ControlsState` to `reward.py`, `Shield`, `SimInterface`, `test_approach_channel.py`, `ControllingSystem`, `LongitudinalChannel`, `AircraftProfile`, `ICSSim`, `ApproachChannel`, `Telemetry`, `XPlaneSim`, `RolloutEnv`, `WeatherState`, `rollout_env.py`, `test_diagnostic_tools.py`, `test_ics_sim.py`, `system.py`, `runner.py`, `channels.py`, `test_approach_criteria.py`, `RunwayTracker`, `LateralChannel`, `test_rollout_env.py`, `_descent_frames`, `EpisodeObjective`, `loop.py`, `sim_interface.py`, `control/approach.py`, `_WarmUpSim`, `test_zero_bound_is_not_counted_as_saturation`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `ControllingSystem` (e.g. with `AircraftControlSet` and `ApproachSetup`) actually correct?**
  _`ControllingSystem` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Are the 36 inferred relationships involving `ControlsState` (e.g. with `GainCommand` and `RuntimeState`) actually correct?**
  _`ControlsState` has 36 INFERRED edges - model-reasoned connections that need verification._