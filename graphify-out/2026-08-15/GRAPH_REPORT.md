# Graph Report - GOSNIIASProject  (2026-08-15)

## Corpus Check
- 134 files · ~135,002 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2344 nodes · 6076 edges · 119 communities (102 shown, 17 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 641 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f4a9df3f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- tolerance.py
- test_splits.py
- reward.py
- weather.py
- Shield
- test_refactoring_contracts.py
- Scenario
- test_approach_channel.py
- ControllingSystem
- ScriptedFlightBench
- airborne_inputs
- system.py
- test_pretrain.py
- scenarios.py
- ics_connector.py
- test_ics_sim.py
- AircraftProfile
- ICSSim
- ApproachChannel
- Telemetry
- test_gain_scheduler.py
- XPlaneSim
- observation.py
- PIDController
- evaluate.py
- train.py
- test_xplane_backend.py
- test_evaluate.py
- test_ppo.py
- IcsEngagement
- XPlaneConnectX
- test_rollout_env.py
- test_weather.py
- Graphify Pipeline
- XPlaneConnector
- RolloutEnv
- GainSpace
- test_ics_engagement.py
- test_diagnostic_tools.py
- FakeConnector
- ICSInputs
- ics_sim.py
- NPGS
- runner.py
- test_action_contract.py
- runtime/pretrain.py
- ScenarioGenerator
- ControlModeState
- telemetry
- test_full_flight.py
- test_go_around.py
- Neural PID Gain Scheduler Architecture
- ApproachCriteriaMonitor
- test_tolerance.py
- DashboardState
- RunwayTracker
- RomanLogImporter
- working_ics/approach_criteria.py
- runway_profiles.py
- fakes.py
- gain_space_for
- test_control_parity.py
- Project Dependencies
- engaged_sim
- runway_tracker.py
- on_ground
- Converts
- heading_deviation_deg
- DatagramSocket
- ._fill_ground
- .compute
- Unified Profile-Aware Scenario System
- Interactive PID Dashboard
- control.py
- DashboardState
- protocol.py
- ICSInterface.cs
- scenario_signature
- test_working_ics_port.py
- DashboardServer
- ICS PID Monitor
- DatagramSocket
- ICS UDP JSON Protocol
- X-Plane Dashboard and Runtime Guide
- .from_json
- ControlsState
- ._header
- xplane_connector.py
- .from_crosswind
- approach_limits
- _faults_from_inputs
- Criterion
- roll_limit_deg
- FrictionProfile
- PresetPolicy
- HandshakeBench
- conftest.py
- agent/__init__.py
- config/__init__.py
- RegulatorSpec
- control/__init__.py
- envs/__init__.py
- gui/__init__.py
- ismpu/__init__.py
- io/__init__.py
- runtime/__init__.py
- tools/__init__.py
- utils/__init__.py
- ismpu
- _cold_sim
- .from_ics
- Q: Реализовать этап 0: baseline, golden replay и dashboard characterization
- Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md).
- stochastic_sources
- touchdown_speed_situation
- test_localizer_deflection_turns_the_aircraft_back_to_the_centreline
- _glideslope_tolerance_deg
- .reset
- .current_dref_values

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
- `DatagramSocket` --uses--> `FlightSegment`  [INFERRED]
  tests/test_refactoring_contracts.py → ismpu/config/segments.py

## Import Cycles
- 3-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 3-file cycle: `ismpu/config/scenarios.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 3-file cycle: `ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/control/channels.py`
- 3-file cycle: `ismpu/config/aircraft_profiles.py -> ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/config/aircraft_profiles.py`
- 4-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 4-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/tolerance.py -> ismpu/control/approach.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/tolerance.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/flight.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach_criteria.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/aircraft_profiles.py -> ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py -> ismpu/config/aircraft_profiles.py`

## Hyperedges (group relationships)
- **Graphify Extraction and Build Flow** — _codex_skills_graphify_skill_structural_extraction, _codex_skills_graphify_skill_semantic_extraction, _codex_skills_graphify_references_extraction_spec_semantic_extraction_contract, _codex_skills_graphify_references_update_build_merge [EXTRACTED 1.00]
- **Hybrid Neural Landing Control** — implementation_plan_classical_pid_plant, implementation_plan_npgs, implementation_plan_deterministic_shield, implementation_plan_ppo_multicomponent_loss, implementation_plan_pinn_observer [EXTRACTED 1.00]
- **PID Dashboard Ecosystem** — docs_xplane_dashboard_pid_dashboard, ismpu_gui_dashboard_pid_dashboard, ismpu_working_ics_ics_dashboard_ics_pid_monitor [INFERRED 0.85]

## Communities (119 total, 17 thin omitted)

### Community 0 - "tolerance.py"
Cohesion: 0.11
Nodes (23): lateral_limit_m(), lateral_load_situation(), lateral_situation(), normal_load_situation(), IntEnum, Критерии критичности особых ситуаций МС-21 (Приложение 1 к ТЗ). Таблица АП-25…, Классификация нормальной перегрузки посадочного удара. `heavy` — взлётный вес., Классификация боковой составляющей перегрузки касания. (+15 more)

### Community 1 - "test_splits.py"
Cohesion: 0.09
Nodes (40): assert_no_leakage(), has_holdout_failure(), _hash_unit(), holdout_reason(), is_marked_holdout(), Детерминированное разбиение сценариев на обучение и holdout (шаг 6). Схема…, SHA-256 от идентификатора → число в [0, 1). Стабильно между запусками и…, Помечен ли сценарий как holdout своим именем. (+32 more)

### Community 2 - "reward.py"
Cohesion: 0.06
Nodes (41): _command_jerk(), _component(), compute_reward(), _effort_saturated(), excess(), graded(), ObjectiveWeights, _p95() (+33 more)

### Community 3 - "weather.py"
Cohesion: 0.09
Nodes (25): Enum, Погодные условия эпизода: описание, шкала сцепления и разбор ветра. Модуль **не…, Состояние ВПП как **монотонная шкала скользкости** 0…15 (0 — сухо, 15 — лёд со…, Код состояния ВПП со стенда → наша шкала. Неизвестный код трактуется как `ICY`,…, runway_condition_from_bench(), RunwayCondition, Сверка каждого сигнала стенда с документами Заказчика. Два независимых…, 1 фут/мин = 0.3048/60 м/с. Приближение здесь копится на всём заходе. (+17 more)

### Community 4 - "Shield"
Cohesion: 0.07
Nodes (41): apply_gains_to_pids(), _clip(), GainCommand, GainMap, PidMap, RegulatorKey, Shield — детерминированный защитный контур между актором и классическим PID.…, Наблюдаемое состояние для поведенческих проверок уровня 3. (+33 more)

### Community 5 - "test_refactoring_contracts.py"
Cohesion: 0.13
Nodes (36): ApproachConfig, Настройки воздушного участка: заход по ILS, выравнивание, управление скоростью.…, Параметры воздушного контура. Значения по умолчанию — настроенные на стенде.…, approach_control_from_dict(), approach_control_to_dict(), _copy_approach(), dump_scenario(), _finite_tree() (+28 more)

### Community 6 - "Scenario"
Cohesion: 0.06
Nodes (22): BaseException, _profile_name(), Полный профильный сценарий APPROACH → ROLLOUT → TAXI., Условия пробега для report/eval-кода, работающего только на земле., Scenario, FailureMode, Enum, Модель отказов бортового оборудования. `FailureState` хранит мультипликативные… (+14 more)

### Community 7 - "test_approach_channel.py"
Cohesion: 0.09
Nodes (41): _colleague_controller(), _descent_frames(), _our_channel(), Воздушный канал: заход по ILS, выравнивание, скоростной канал. Главный тест…, Страховка от самообмана: сценарий обязан пройти выравнивание, иначе паритет его…, Угол сноса не должен превращаться в ошибку курса на локализаторе., Стенд иногда сбрасывает Valid при сохранении пригодного численного значения., Крен парируется элеронами с обратным знаком — это проводка стенда, а не… (+33 more)

### Community 8 - "ControllingSystem"
Cohesion: 0.05
Nodes (29): ControllingSystem, Связать сценарий с контуром; PID активируются после определения участка., Пересобрать воздушный канал под заданные настройки. → новый канал. Именно…, Обновить параметры геометрического наведения латерального канала. Имя сохранено…, Веса влияния каналов (актор, §6): множители к выходам каналов. 1.0 = классика., Привести модель отказов к тому, что сообщает борт (`ICSInputs.Fault*`). Отказы…, Такт управления. → True, если управление окончено (или телеметрия невалидна).…, Прервать заход с названной причиной. → True (управлять больше нечем). (+21 more)

### Community 9 - "ScriptedFlightBench"
Cohesion: 0.18
Nodes (8): flight_sim(), KinematicBench, Стенд, проигрывающий заход и касание **по сценарию**, а не по нашим командам.…, (sim, bench) на сценарном заходе. Рукопожатие ещё не выполнено., Мини-модель стенда: замедление ~ команде тормоза/реверса, ход вдоль осевой ВПП.…, ScriptedFlightBench, Сквозной прогон: рукопожатие в воздухе → заход → касание → пробег → руление.…, test_a_whole_flight_runs_from_approach_to_taxi()

### Community 10 - "airborne_inputs"
Cohesion: 0.13
Nodes (19): `ICSInputs` → `Telemetry`: поля в СИ + «сырой» пакет для property. Стенд отдаёт…, airborne_inputs(), Кадр «ВС на глиссаде»: стойки не обжаты, ILS валиден, скорость и высота…, Носовая стойка обжимается позже основных — ждать её значит пропустить начало…, «Козление» после касания снимает обжатие на секунду — назад в заход…, Таблицы захода МС-21 к чистому крылу неприменимы — вести по ним нельзя.…, Нулевое отклонение при снятой валидности неотличимо от «точно на оси»., Ниже 80 футов до земли секунды — бросать органы там хуже, чем доработать. (+11 more)

### Community 11 - "system.py"
Cohesion: 0.07
Nodes (31): Приёмочные пороги из ТЗ (раздел 5). Единый источник истины для reward-шейпинга…, LateralChannel, Каналы управления и общий вектор команд. `ControlsState` — разделяемая по…, Удержание оси ВПП. Телеметрию получает параметром, не читает сам., approach_blocker(), ApproachRefused, at_lateral_alignment_gate(), ils_blocker() (+23 more)

### Community 12 - "test_pretrain.py"
Cohesion: 0.10
Nodes (39): _phase_labels(), pretrain_sft(), PretrainConfig, float32, GainMap, NDArray, Tensor, SFT (behavioral cloning) — предобучение NPGS предсказывать эталонные… (+31 more)

### Community 13 - "scenarios.py"
Cohesion: 0.06
Nodes (46): MatrixCase, Один шифр матрицы — вариант отказа/режима, под который настраивается набор…, AircraftControlSet, compose_matrix_scenario(), ConditionMatch, _copy_approach(), _copy_ground(), _ground_segments_for_spec() (+38 more)

### Community 14 - "ics_connector.py"
Cohesion: 0.07
Nodes (32): GearState, ICSBenchConnector, ICSInputs, ICSOutputs, main(), IntEnum, UDP-мост к стенду заказчика (порт 3030) — транспорт пути поставки. `ICSInputs`…, Разбор телеметрии стенда с совместимостью вперёд. Асимметрия намеренная (JSON-… (+24 more)

### Community 15 - "test_ics_sim.py"
Cohesion: 0.07
Nodes (32): compose_scenario(), Any, Serialize only the canonical profile-aware schema v2., Собрать сценарий из независимых источников участков., select_for_telemetry(), select_scenario(), Тесты стенда (`ICSSim`), подбора сценария и генератора — без реального стенда., Заявить канал, который не формируешь, — взять ответственность за неуправляемый… (+24 more)

### Community 16 - "AircraftProfile"
Cohesion: 0.09
Nodes (11): AircraftProfile, clamp(), Преобразовать воздушные команды ICD в нормированные DataRef X-Plane., Преобразовать нормированные команды пробега в DataRef X-Plane., Расширение реестра будущим профилем МС-21 без правки XPlaneSim., Проводка и масштабы конкретного планера X-Plane., Общая идентичность ЛА и необязательная привязка к X-Plane. Профиль нужен и…, Command refs retained under the historical public name. (+3 more)

### Community 17 - "ICSSim"
Cohesion: 0.12
Nodes (9): ICSSim, Обмен со стендом заказчика: телеметрия внутрь, команды наружу. Управление…, Принимает ли стенд наши команды. До включения любой `step` уходит вхолостую., Гонит стимул рукопожатия, пока стенд не подтвердит включение (`AgentIsActive =…, Войти в пробег самостоятельно (`ControlMode 0 → 3`)., Передать управление в руление (`3 → 4`) — по решению вызывающего, что пробег…, Признаки для автомата включения. `agent_is_active` — подтверждение стенда:…, На стенде отказы приходят телеметрией, а не инжектируются нами. (+1 more)

### Community 18 - "ApproachChannel"
Cohesion: 0.15
Nodes (19): ApproachChannel, ApproachResult, clamp(), ApproachLimits, ApproachTelemetry, Заход по ILS с выравниванием. Телеметрию получает параметром, не читает сам.…, Сброс регуляторов и всей памяти профиля — новый заход начинается с чистого…, Такт воздушного управления: пишет команды в `state`, возвращает диагностику.… (+11 more)

### Community 19 - "Telemetry"
Cohesion: 0.05
Nodes (20): above_decision_height(), ВС выше высоты решения ухода на второй круг (30 м по ТЗ 5.1.1.2). → уход…, Нужно ли уходить на второй круг по этому такту. → причина или `None`. Только…, Начать уход: зафиксировать состояние манёвра и высоту входа., Такт манёвра ухода. → True, когда набор устойчив (пора отдать управление…, Набор устойчив: есть и вертикальная скорость вверх, и прирост радиовысоты над…, Кадр «связи со стендом нет». Нули, а не None: контур проверяет `valid` первым., Приборная скорость (kt → м/с). Отсечки реверса заданы по ней, а не по путевой. (+12 more)

### Community 20 - "test_gain_scheduler.py"
Cohesion: 0.07
Nodes (26): int64, ActorOutput, build_npgs(), _init_log_std(), layer_init(), _mlp_head(), phase_labels_from_groundspeed_kts(), ArrayLike (+18 more)

### Community 21 - "XPlaneSim"
Cohesion: 0.11
Nodes (6): StartMode, Применить только дельту условий при переходе между участками., Снять один отказ, не переинициализируя отказ, продолжающийся на новом участке., XPlaneSim, RuntimeError, test_reload_renews_subscriptions_and_sensor_dropout_is_applied()

### Community 22 - "observation.py"
Cohesion: 0.19
Nodes (13): clip_unit(), linear(), log_norm(), Фиксированная нормализация Observation Space — единый контракт train ↔ deploy.…, Лог-нормировка неотрицательной величины (видимость): log1p(x)/log1p(scale)., Отображает [lo, hi] → [-1, 1] (для PID output по его границам)., Сериализуемый слепок контракта нормировки (сохраняется вместе с весами).…, snapshot() (+5 more)

### Community 23 - "PIDController"
Cohesion: 0.08
Nodes (33): Регуляторы канала по именам — для логов и приёмки, не для…, PIDController, Сброс внутренних состояний (используется при выключении системы)., _legacy_reference(), Опциональная численность PID (шаг 5): каждый флаг проверяется на том дефекте,…, При `steering_eff = 0` применяется 0 вместо выхода PID — интегратор обязан это…, Если применено ровно то, что выдал PID, коррекции быть не должно., Сквозная проверка: NWS-отказ обнуляет руль, интегратор курсового PID не должен… (+25 more)

### Community 24 - "evaluate.py"
Cohesion: 0.08
Nodes (32): _as_dict(), contract_for(), Any, Контракт воспроизводимости эпизода (шаг 6). Заимствовано из…, Сколько раз прогнать сценарий, чтобы результат приёмки что-то значил., Худшая реплика по заданной метрике. Приёмка смотрит именно на худшую, а не на…, Что в эпизоде детерминировано, что нет, и сколько реплик из-за этого нужно., Даст ли повторный прогон с тем же сидом ту же траекторию. (+24 more)

### Community 25 - "train.py"
Cohesion: 0.09
Nodes (25): PPOTrainer, Tensor, Собирает rollout из среды и обновляет NPGS многокомпонентным PPO-loss., Шагает средой `rollout_len` тактов (сброс по завершению эпизода). → статистика., Хук L_shield (§11): барьер, отталкивающий выход от края уровня-1 Shield. По…, build_sim(), Any, Path (+17 more)

### Community 26 - "test_xplane_backend.py"
Cohesion: 0.12
Nodes (11): test_xplane_ignores_failures_outside_rollout_contract(), MockXPlaneConnector, test_commands_failures_and_close_release_overrides(), test_failed_approach_setup_releases_overrides_and_pause(), test_ignored_xplane_failure_participates_in_segment_delta_and_is_cleared(), test_missing_or_stale_required_data_makes_xplane_telemetry_invalid(), test_profile_rejects_unknown_aircraft_and_clamps_commands(), test_scripted_xplane_full_approach_rollout_taxi_chain() (+3 more)

### Community 27 - "test_evaluate.py"
Cohesion: 0.10
Nodes (49): admit_checkpoint(), evaluate_tz(), Диагностика эпизода + сценарий → список вердиктов по пунктам ТЗ разд. 5., Итог эпизода: FAIL, если провален хоть один применимый критерий., Пропускать ли чекпоинт дальше. Отсутствующая/нечисловая метрика = отказ.…, Markdown-отчёт приёмки. Отрицательные результаты не скрываются — они и есть…, render_report(), verdict_of() (+41 more)

### Community 28 - "test_ppo.py"
Cohesion: 0.11
Nodes (25): NPGSConfig, Any, Гиперпараметры архитектуры NPGS (замораживаются вместе с весами при поставке)., PPOConfig, Any, device, PPO-тренер + многокомпонентный loss для NPGS (план §11). `L = L_ppo +…, Плоский буфер одного env: obs-окна, сырые действия, logp/value/reward/done. (+17 more)

### Community 29 - "IcsEngagement"
Cohesion: 0.05
Nodes (24): IcsEngagement, ControlModeState, Автомат включения. `step(inputs)` вызывается каждый такт до формирования…, Полный сброс — новый эпизод начинается с невключённого состояния., Сообщить автомату, что кадр **фактически ушёл** на стенд. Вызывается…, Подхватить уже включённый извне пробег: шлём `ControlMode = Rollout`.…, Войти в пробег самостоятельно: шлём `ControlMode = Rollout`. Это же — передача…, Войти в заход самостоятельно: шлём `ControlMode = Approach`. Обычно вызывать не… (+16 more)

### Community 30 - "XPlaneConnectX"
Cohesion: 0.08
Nodes (13): XPlaneConnectX class initialization. Args: ip (str, optional): IP address where…, Starts a recording of the subscribed DataRefs into self.recorded_data. Data is…, Terminates the recording and returns a dictionary of lists that contain the…, Synchronize measurements from multiple sensors to a common frequency.…, Gets the current value of a DataRef. This is only intended for one-time use.…, Permanently subscribe to a list of DataRefs with a certain frequency. This is…, Writes a value to the specified DataRef provided that the DataRef is writable.…, Sends simulator commands to the simulator. These are not commands for the… (+5 more)

### Community 31 - "test_rollout_env.py"
Cohesion: 0.10
Nodes (33): action_high(), action_low(), float32, NDArray, Применение абсолютных коэффициентов PID, выданных NPGS. Действие: вектор…, reference_action(), ObservationBuilder, ObserverEstimate (+25 more)

### Community 32 - "test_weather.py"
Cohesion: 0.14
Nodes (16): compose_wind(), decompose_wind(), (скорость, откуда) → (crosswind, headwind) относительно курса ВПП. crosswind >…, (crosswind, headwind) → (скорость, откуда, °). Обратна `decompose_wind`., Тесты погоды: разбор ветра, шкала скользкости и чтение условий из пакета стенда., Для пробега существенна боковая составляющая, а не «скорость ветра» сама по…, Коды стенда не упорядочены по скользкости: ICE=2 стоит между WET=1 и FLOODED=3.…, ICD перечисляет ровно семь состояний — незакрытый код молча стал бы «льдом». (+8 more)

### Community 33 - "Graphify Pipeline"
Cohesion: 0.08
Nodes (29): Folder Watcher, URL Ingestion, Extra Graph Exports, MCP Graph Server, Confidence Audit Trail, Deterministic Node IDs, Semantic Extraction Contract, Cross-Repository Graph Merge (+21 more)

### Community 34 - "XPlaneConnector"
Cohesion: 0.12
Nodes (5): Discard pre-reload values so readiness cannot use stale telemetry., Одна подписка, один поток приёма и явное освобождение ресурсов., Send basic controls to the ego aircraft. There are hundreds of DataRefs that…, Совместимость с прежним клиентом., XPlaneConnector

### Community 35 - "RolloutEnv"
Cohesion: 0.09
Nodes (35): base_gains_from_pids(), Снимок (kp, ki, kd) регуляторов — пресет-якорь для Shield и т.п., apply_corrections(), decode(), preset_action(), ArrayLike, float64, GainMap (+27 more)

### Community 36 - "GainSpace"
Cohesion: 0.18
Nodes (9): GainKey, GainSpace, Any, ArrayLike, float64, GainMap, NDArray, RegulatorKey (+1 more)

### Community 37 - "test_ics_engagement.py"
Cohesion: 0.10
Nodes (46): _Clock, _engine(), _pump(), Автомат включения управления на стенде. Два раздельных предмета проверки: *…, По ICD стенд должен два секунды ПОЛУЧАТЬ ModeAIReady=1. Если считать одно лишь…, Обратная защита: 30 кадров можно выпалить за 0.1 с — время тоже обязано пройти., Срыв предусловия обнуляет и время, и счётчик кадров., Требование ICD — непрерывность: пропуск готовности рвёт серию. (+38 more)

### Community 38 - "test_diagnostic_tools.py"
Cohesion: 0.20
Nodes (19): build_altitude_sweep(), command_for_pulse(), Безопасные elevator/altitude authority sweep без дублирования ICS runner., Чистое преобразование, пригодное и для dry-run, и для ICSSim., safety_reason(), SweepLimits, SweepPulse, validate_pulse() (+11 more)

### Community 39 - "FakeConnector"
Cohesion: 0.12
Nodes (17): FakeConnector, make_ics_inputs(), Полный пакет стенда: нули по умолчанию + заданные поля., Статический стенд: всегда один и тот же кадр, отправленное — в `sent_outputs`., Погоду задаёт Заказчик; наш `WeatherState` — это прочитанный кадр, а не задание., До рукопожатия заявлять каналы нельзя: стенд ещё не разрешил нам ими управлять., Стенд отдаёт узлы, футы, футы/мин и градусы/с — граница пересчёта проходит…, Неизвестный код — не повод предполагать сухую полосу. (+9 more)

### Community 40 - "ICSInputs"
Cohesion: 0.14
Nodes (23): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+15 more)

### Community 41 - "ics_sim.py"
Cohesion: 0.08
Nodes (34): get_aircraft_profile(), Профили преобразования команд ИСМПУ в органы управления X-Plane., Глобальные константы контура управления (перенесены из main.ipynb)., alpha_prot_deg(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+26 more)

### Community 42 - "NPGS"
Cohesion: 0.16
Nodes (13): floating, NPGS, float32, NDArray, Tensor, Neural PID Gain Scheduler: общий энкодер + головы актора (абс. gain'ы) + голова…, → (mean (B,17), value (B,), phase_logits (B,n_phases))., 17 сырых выходов → [абс. gains×15, w_lon, w_lat] (layout `REGULATOR_ORDER` +… (+5 more)

### Community 43 - "runner.py"
Cohesion: 0.19
Nodes (21): ICSOutputs, airborne_control_mode(), airborne_flare_mode(), deactivate(), live_main(), main(), main_gear_contact(), make_airborne_output() (+13 more)

### Community 44 - "test_action_contract.py"
Cohesion: 0.13
Nodes (17): ControlArchitecture, Канонический порядок регуляторов, размерности действия и **контракт обучаемого…, Фиксированный порядок слоёв и роль обучаемого компонента., Проверяет контракт обучаемого слоя. Нарушение → `ValueError` на старте…, validate_action_contract(), Контракт обучаемого слоя (Этап 4): что именно сеть имеет право менять. Аргумент…, Пустое обоснование = контракт непредъявим по ТЗ., Машиночитаемое утверждение «сеть не является регулятором». (+9 more)

### Community 45 - "runtime/pretrain.py"
Cohesion: 0.21
Nodes (16): ground_cases(), Шифры, у которых настраиваются коэффициенты **пробега** (пригодны для SFT).…, build_capture_stack(), build_scenarios(), matrix_preset_names(), PretrainRunConfig, Оркестрация SFT-подогрева NPGS (план Stage B): захват классических прогонов на…, Имена наземных пресетов матрицы прогонов (пригодных для SFT) в порядке матрицы.… (+8 more)

### Community 46 - "ScenarioGenerator"
Cohesion: 0.15
Nodes (8): Один случайный сценарий. `difficulty=None` → случайная сложность., Фиксированный приёмочный набор (детерминированный, без RNG)., ScenarioGenerator, AdmissionResult, test_generator_embeds_control_config(), test_generator_high_difficulty_produces_failures(), test_generator_is_deterministic_for_same_seed(), test_generator_zero_difficulty_has_no_failures()

### Community 47 - "ControlModeState"
Cohesion: 0.27
Nodes (8): ControlModeState, EngagementInputs, EngagementState, Enum, Автомат включения управления на стенде заказчика. Стенд принимает наши команды…, Передать управление в руление (`ControlMode 3 → 4`). → удался ли переход.…, Состояние **исходящего стимула** (что мы шлём стенду), а не факта включения.…, Признаки со стенда, от которых зависит рукопожатие. `agent_is_active` —…

### Community 48 - "telemetry"
Cohesion: 0.13
Nodes (15): default_runs_root(), _jsonable(), Path, Один раз сохранить накопленные кадры и итоговые артефакты прогона., Единый каталог прогонов, не зависящий от cwd процесса/Jupyter., RunRecorder, Готовый кадр `Telemetry` для прямых вызовов `control_step(dt, telemetry,…, telemetry() (+7 more)

### Community 49 - "test_full_flight.py"
Cohesion: 0.10
Nodes (34): IntFlag, ControlValid, Биты `ControlValidMask`: какие каналы несёт команда. **Один бит на одно…, initial_segment(), is_airborne(), Сообщает ли стенд, что ВС в воздухе и достаточно высоко для приёма захода.…, С какого участка начинать. Пробег — ответ по умолчанию (см. модуль)., _air() (+26 more)

### Community 50 - "test_go_around.py"
Cohesion: 0.19
Nodes (19): _armed_controller(), _drive(), _frame(), Уход на второй круг (fallback в воздухе): условия срабатывания и передача…, После установившегося набора цикл снимает заявку каналов (ControlMode=Off,…, Контур на заходе: `begin_flight` по кадру в воздухе выше 400 футов., Устойчивое превышение курсового допуска выше высоты решения → уход на второй…, Один-два кадра за допуском ухода не вызывают — нужен устойчивый выход (дебаунс). (+11 more)

### Community 51 - "Neural PID Gain Scheduler Architecture"
Cohesion: 0.19
Nodes (19): Hybrid Neural PID Controller, Neural PID Gain Scheduler, PPO Training Loop, Preset-Anchored Deterministic Shield, SFT Behavioral-Cloning Warm Start, Absolute-Gain Action Space, Classical PID as the Plant, Deterministic Deployment Runtime (+11 more)

### Community 52 - "ApproachCriteriaMonitor"
Cohesion: 0.10
Nodes (18): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, Отдельный монитор критерия А.1.1 (не участвует в go-around)., Захватывает А.1.1 после входа в допуск и завершает оценку на 300 ft., Деградация команд по эффективности актуаторов — **только наземные органы**.… (+10 more)

### Community 53 - "test_tolerance.py"
Cohesion: 0.21
Nodes (17): evaluate_approach_tolerances(), ApproachLimits, Проверить допуски захода по текущему такту. Команды не трогает. `result` —…, Допуски захода: классификаторы критичности (Приложение 1) и рантайм-монитор.…, 0.6° вне штатного допуска 0.5°, но в пределах допуска при отказе шасси (0.7°)., Ось ± 5 м проверяется только у гейта; выше него боковое отклонение не…, Zпред = 0.5·B − 0.5·Zш: класс A (60 м) → 25.7 м, класс В (42 м) → 16.7 м., Норма ≤ Zпред−5 м; у предела на скорости → СС; за пределом на скорости → АС. (+9 more)

### Community 54 - "DashboardState"
Cohesion: 0.09
Nodes (21): DashboardState, _finite_or_none(), GainUpdateRequest, _handler_factory(), main(), Path, Unified local dashboard for the three airborne and five ground PIDs., Валидировать HTTP-запрос и передать запись control-потоку. (+13 more)

### Community 55 - "RunwayTracker"
Cohesion: 0.16
Nodes (8): Решить прямую геодезическую задачу на сферической Земле., Guidance по курсу ВПП и измеренному отклонению — без собственной геодезии.…, Возвращает отклонение от осевой линии в метрах. >0 - правее оси, <0 - левее., Геодезическое наведение на ось ВПП с упреждением по скорости., RunwayTracker, test_xte_sign_left_is_negative(), test_xte_sign_right_is_positive(), test_runway_profile_delegates_geometry_to_tracker()

### Community 56 - "RomanLogImporter"
Cohesion: 0.19
Nodes (10): _number(), Path, Импорт и проверка внешних CSV-прогонов roman_aviacia_ics., Потоково нормализует основной и authority CSV Романа., RomanLogImporter, verify_manifest(), fixture, roman_csv() (+2 more)

### Community 57 - "working_ics/approach_criteria.py"
Cohesion: 0.21
Nodes (7): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, ICSInputs, Evaluate the A.1.1 approach segment and stop at a radio-altitude floor.

### Community 58 - "runway_profiles.py"
Cohesion: 0.22
Nodes (10): find_earth_nav_dat(), get_runway_profile(), ILSStation, parse_ils_station(), Path, Профили ВПП и разрешение ILS из установленной базы X-Plane., Точка на продолжении оси; положительное расстояние — до порога., Найти LOC (тип 4) без хардкода частоты. (+2 more)

### Community 59 - "fakes.py"
Cohesion: 0.14
Nodes (14): decode_airborne(), decode_outputs(), _integrate_throttle(), Фейковый стенд для тестов: `ICSInputs` вместо реального UDP. Единственный…, Отправленные команды в нормированном виде — для сравнения траекторий.…, `ICSOutputs` → (brake_l, brake_r, thr_l_rate, thr_r_rate, steer), всё…, Ход рычага РУД за такт: интеграл команды-скорости, зажатый физическим…, Доля обратной тяги по фактическому углу РУД: 0 в положительном секторе, 1 на… (+6 more)

### Community 60 - "gain_space_for"
Cohesion: 0.20
Nodes (13): gain_space_for(), _profile_name(), Профильное пространство абсолютных PID-коэффициентов NPGS., _regulator_config(), Профильные пространства абсолютных PID-коэффициентов NPGS., test_every_profile_preset_gain_is_inside_its_band(), test_gain_space_can_be_built_from_external_scenario_registry(), test_normalization_endpoints_and_nonpositive_guard() (+5 more)

### Community 61 - "test_control_parity.py"
Cohesion: 0.09
Nodes (20): LongitudinalChannel, Управление скоростью по эталонной кривой. Телеметрию получает параметром, не…, Генератор эталонной кривой скорости (Колокол Гаусса)., Возвращает идеальную скорость (м/с) для текущей точки пути., ReferenceTrajectory, TrajectoryState, Тесты паритета после выноса контура из main.ipynb в пакет ismpu. Полный паритет…, Стенд при обрыве связи отдаёт НУЛИ с valid=False, а не None. Проверка «поле is… (+12 more)

### Community 62 - "Project Dependencies"
Cohesion: 0.18
Nodes (13): Autonomous Landing Controller, Repository Guidance for Codex, Autonomous Landing Controller, Repository Guidance for Claude Code, Neural Landing Implementation Plan, Unified Scenario System, Optional Gymnasium, NumPy (+5 more)

### Community 63 - "engaged_sim"
Cohesion: 0.12
Nodes (16): engaged_sim(), (sim, connector) с завершённым рукопожатием: стенд подтвердил `AgentIsActive =…, Регресс: расширение структуры не должно протащить руль высоты в маску пробега., test_ground_frame_still_declares_only_the_ground_channels(), Разделение органов из таблицы Заказчика: тиллер — на рулении, педальный пост —…, Базовый контур на стенде: `control_step` сам читает телеметрию и сам отправляет., На стенде каждый лишний `read_telemetry` — лишний приём UDP. Кадр, вернувшийся…, Замолчать нельзя: последнее отклонение осталось бы приложенным до сторожа на… (+8 more)

### Community 64 - "runway_tracker.py"
Cohesion: 0.18
Nodes (5): Guidance по тому, что даёт стенд. → словарь guidance или None, если данных нет.…, Единый GuidanceState текущего кадра для control/observation/reward., GuidanceState, Слежение за осью ВПП: геодезия, cross-track error, guidance с look-ahead.…, Совместимость со старым словарным API.

### Community 65 - "on_ground"
Cohesion: 0.13
Nodes (14): engaged_inputs(), on_ground(), ICSInputs, Кадр «ВС на полосе»: обжаты все стойки, курс/координаты у порога UUEE 06R., Кадр стенда, который уже принял управление: `AgentIsActive = 1`, идёт пробег., В такте касания команда обязана быть уже наземной, а не последней командой…, test_the_first_ground_tick_is_computed_by_the_ground_channels(), Пресет — стартовое предположение; фактическую конфигурацию сообщает борт. (+6 more)

### Community 66 - "Converts"
Cohesion: 0.16
Nodes (11): cases_for_segment(), _kts(), MatrixCondition, Матрица прогонов для настройки базовых ПИД-регуляторов. Машиночитаемая форма…, Шифры одного участка: `approach` / `rollout` / `taxi` / `through`., Матрица задаёт ветер в м/с, телеметрия приходит в узлах., Условие прогона из справочника матрицы (П.1–П.5 для захода, У.1–У.8 для ВПП).…, Геометрия целевой ВПП и высоты установки ЛА. Смена целевой полосы = правка… (+3 more)

### Community 67 - "heading_deviation_deg"
Cohesion: 0.19
Nodes (12): heading_deviation_deg(), Отклонение курса ВС от направления ВПП — приёмочная величина ТЗ 5.1.3.3 /…, Телеметрия ВС на оси ВПП, смещённого вбок на `offset_m` и с заданным курсом.…, ТЗ 5.1.3.3 нормирует курс «от направления ВПП». Смещение от оси на него не…, На стенде курс ВПП приходит телеметрией; конфиг — только значение по умолчанию., Таблица из находки: раньше оба случая давали противоположный результат., _telemetry_at(), test_heading_deviation_ignores_lateral_offset() (+4 more)

### Community 69 - "._fill_ground"
Cohesion: 0.21
Nodes (8): _clamp(), ICSOutputs, Желаемый уровень реверса [-1, 0] → скорость перемещения РУД (°/с). Тягой (в том…, `ControlsState` → `ICSOutputs` (единицы ICD), **по текущему участку полёта**.…, Воздушный участок: перегрузка, элероны и скорости РУД. Флаги фаз (`ModeFlare*`,…, Пробег и руление: тормоза, путевое управление, реверс. Путевой орган **зависит…, Фактический угол РУД из последнего кадра стенда; 0 при отсутствии кадра.…, _throttle_rate()

### Community 70 - ".compute"
Cohesion: 0.20
Nodes (4): → (интеграл только с утечкой, интеграл с утечкой и приращением). Оба уже зажаты., Такт регулятора. `measurement` обязателен при `derivative_on_measurement=True`., Back-calculation: подтянуть интегратор к фактически применённой команде. No-op…, Вес апериодического фильтра D-составляющей за такт `dt`.

### Community 71 - "Unified Profile-Aware Scenario System"
Cohesion: 0.22
Nodes (9): Technical-Specification Acceptance Gates, Bench-Validated ILS Approach Channel, Forward-Only Flight Segment Supervisor, Tolerance-Gated Go-Around, Longitudinal and Lateral Ground Channels, PID Run Matrix, Unified Profile-Aware Scenario System, Legacy Scenario Preset Model (+1 more)

### Community 72 - "Interactive PID Dashboard"
Cohesion: 0.25
Nodes (9): Nine-View PID Dashboard, Run Recording Artifacts, buildTabs, draw, Gain Tuning and Snapshot Export, Interactive PID Dashboard, refresh, render (+1 more)

### Community 73 - "control.py"
Cohesion: 0.43
Nodes (4): apply_ground_control(), build_pids(), Сборка классического контура из неизменяемой конфигурации., Фабрики stateful-объектов; config-модули хранят только данные.

### Community 74 - "DashboardState"
Cohesion: 0.19
Nodes (4): DashboardServer, DashboardState, Any, ICSInputs

### Community 75 - "protocol.py"
Cohesion: 0.32
Nodes (5): ControlModeState, GearState, Any, IntEnum, ReverseEngineType

### Community 76 - "ICSInterface.cs"
Cohesion: 0.36
Nodes (7): External.Systems.ICS, ControlModeState, GearState, ICSInputs, ICSOutputs, ReverseEngineType, UInt64

### Community 77 - "scenario_signature"
Cohesion: 0.20
Nodes (8): is_signature_holdout(), PartitionedScenarioProvider, Устойчивая комбинация условий, а не имя или целое семейство отказов., Каноническая дискретизация условий для train/eval split., Фильтр над единым sampler с непересекающимися train/eval signatures., scenario_signature(), ScenarioSignature, test_signature_holdout_is_stable_and_not_failure_family_based()

### Community 78 - "test_working_ics_port.py"
Cohesion: 0.15
Nodes (12): Path, ICSInputs, socket, Hand the validated airborne session to Vlayd's existing rollout loop. The…, Keep Vlayd's engagement latch synchronized during the approach., Run Vlayd's rollout until taxi speed, then send its taxi handoff., VlaydRolloutBridge, test_flare_mode_bit_clears_at_20ft_while_landing_mode_remains_active() (+4 more)

### Community 79 - "DashboardServer"
Cohesion: 0.20
Nodes (7): DashboardServer, _lost_engagement(), main(), Снял ли стенд активность посреди прогона. → пора останавливаться. Без этой…, Точка входа: подключиться к стенду, выбрать пресет и провести полёт.…, Прогоняет один полёт на уже настроенном контуре., run()

### Community 80 - "ICS PID Monitor"
Cohesion: 0.29
Nodes (7): buildControls, draw, formatTime, Four-Loop PID Tuning, ICS PID Monitor, Live and Historical Timeline, refresh

### Community 81 - "DatagramSocket"
Cohesion: 0.29
Nodes (3): DatagramSocket, test_legacy_subscription_starts_at_zero_and_retries_with_diagnostics(), test_xplane_used_wire_packets_match_confirmed_original()

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
Cohesion: 0.12
Nodes (15): ControlsState, PidMap, Финальные пределы наземных команд — после дифференциального микса. Воздушные…, Обнуляет все органы управления. Отправку делает вызывающий через `ICSSim.step`.…, Разделяемая по тактам структура команд — и наземных, и воздушных. Аннотации…, Сброс к нейтральным командам — новый эпизод начинается с чистого состояния.…, Обнулить только воздушные команды. Нужно, когда воздушный канал не может…, Копия команды такта — для расчёта джерка на следующем такте. Копируется… (+7 more)

### Community 87 - "xplane_connector.py"
Cohesion: 0.33
Nodes (3): DataRefSample, Неблокирующий UDP-клиент нативного протокола X-Plane 12., Разобрать пакет; публично для детерминированных mock-тестов.

### Community 88 - ".from_crosswind"
Cohesion: 0.22
Nodes (5): Any, Собирает ветер из компонент относительно курса ВПП. `crosswind_kts` > 0 — ветер…, Сериализация в примитивы (для логирования/воспроизводимости сценариев)., test_weather_roundtrips_through_dict(), test_weatherstate_from_crosswind()

### Community 89 - "approach_limits"
Cohesion: 0.25
Nodes (8): approach_limits(), ApproachLimits, _ceiling_weight_index(), Индекс ближайшей строки таблицы **не ниже** заданной массы (консервативная…, Полный набор ограничений захода для массы, конфигурации и числа Маха., Границы диапазона для конкретной массы, конфигурации и числа Маха., Между строками таблицы берётся ближайшая сверху, а не интерполяция., test_approach_limits_take_the_conservative_weight_row()

### Community 90 - "_faults_from_inputs"
Cohesion: 0.40
Nodes (4): _faults_from_inputs(), ICSInputs, Отказы, о которых сообщает борт — **единственный** источник истины об отказах.…, Сигналы отказов со стенда → наши `FailureMode`. Отказы шасси…

### Community 91 - "Criterion"
Cohesion: 0.40
Nodes (4): _check(), Criterion, Один пункт ТЗ: предел, измеренное значение, вердикт и его причина., Строит вердикт. Неприменимо → SKIP; применимо, но данных нет → FAIL.

### Community 92 - "roll_limit_deg"
Cohesion: 0.50
Nodes (4): Предел крена по высоте: чем ниже, тем меньше запас до касания законцовкой.…, roll_limit_deg(), Чем ниже, тем меньше запас до касания законцовкой; настроенный предел не…, test_roll_limit_tightens_towards_the_ground()

### Community 93 - "FrictionProfile"
Cohesion: 0.25
Nodes (3): FrictionProfile, Ступенчатый профиль сцепления по дистанции пробега., ScriptedXPlaneConnector

### Community 94 - "PresetPolicy"
Cohesion: 0.13
Nodes (11): DefaultGainsPolicy, main(), PresetPolicy, Пишет `evaluation.json` + `report.md`. → пути записанных файлов., Полная приёмка на стенде: приёмочный набор × 4 политики → отчёт + гейт допуска.…, Baseline 1: DEFAULT-коэффициенты во всех сценариях (что выдаёт «холодная» сеть)., Baseline 2 («оракул»): коэффициенты пресета сценария = классика, под которую он…, write_report() (+3 more)

### Community 95 - "HandshakeBench"
Cohesion: 0.29
Nodes (4): HandshakeBench, Стенд, включающий управление только после корректного рукопожатия. Ждёт…, Стенд включается по полученной готовности, а не по нашему представлению о ней., test_the_airborne_handshake_is_actually_transmitted_before_approach()

### Community 109 - "_cold_sim"
Cohesion: 0.29
Nodes (7): _cold_sim(), Сквозной прогрев: маска нулевая, пока стенд не подтвердил `AgentIsActive = 1`., Темп задаётся часами, а не sleep. Со сломанным (или подменённым) sleep наивный…, Молча продолжить нельзя: дальше мы бы «управляли» в пустоту., test_cold_ground_start_engages_only_after_the_bench_confirms(), test_warm_up_paces_itself_and_does_not_flood_the_bench(), test_warm_up_timeout_raises_with_a_diagnosis()

### Community 110 - ".from_ics"
Cohesion: 0.33
Nodes (5): `ICSInputs` → `WeatherState`. Единственный источник фактической погоды. Стенд…, `Visibility` в футах. Без пересчёта 16000 футов читались бы как «ясно» вместо…, test_visibility_is_converted_from_feet(), Стенд шлёт узлы и **футы**; в WeatherState видимость — в метрах., test_from_ics_converts_units()

### Community 111 - "Q: Реализовать этап 0: baseline, golden replay и dashboard characterization"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Реализовать этап 0: baseline, golden replay и dashboard characterization, Source Nodes

### Community 112 - "Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md)., Source Nodes

### Community 113 - "stochastic_sources"
Cohesion: 0.40
Nodes (5): Источники случайности на стороне стенда, активные при данных условиях. Мы…, stochastic_sources(), Иначе реплики требовались бы даже в штиль — приёмка утроилась бы без причины., test_a_breath_of_wind_is_not_treated_as_stochastic(), test_each_stochastic_source_is_named_separately()

### Community 114 - "touchdown_speed_situation"
Cohesion: 0.50
Nodes (4): Классификация скорости касания относительно VAPP и VВПП пред., touchdown_speed_situation(), Норма 0.96·VAPP…VAPP+10; слишком медленно/быстро — СС; ≥ VВПП пред (194) — АС., test_touchdown_speed_situation_bands()

### Community 115 - "test_localizer_deflection_turns_the_aircraft_back_to_the_centreline"
Cohesion: 0.50
Nodes (4): angle_error_deg(), Разность курсов, приведённая к (-180, 180]., Отклонение планки курса задаёт доворот в сторону оси, а не от неё., test_localizer_deflection_turns_the_aircraft_back_to_the_centreline()

### Community 116 - "_glideslope_tolerance_deg"
Cohesion: 0.67
Nodes (3): _glideslope_tolerance_deg(), ApproachTelemetry, Допуск по глиссаде с учётом отказа (ТЗ 5.1.2.1–5.1.2.3), самый мягкий из…

## Ambiguous Edges - Review These
- `Unified Profile-Aware Scenario System` → `Legacy Scenario Preset Model`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to
- `Dual-Backend SimInterface` → `ICS-Only Backend Guidance`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **37 isolated node(s):** `Answer`, `Outcome`, `Source Nodes`, `Answer`, `Outcome` (+32 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Unified Profile-Aware Scenario System` and `Legacy Scenario Preset Model`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Dual-Backend SimInterface` and `ICS-Only Backend Guidance`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `ControllingSystem` connect `ControllingSystem` to `tolerance.py`, `reward.py`, `test_refactoring_contracts.py`, `Scenario`, `ScriptedFlightBench`, `airborne_inputs`, `system.py`, `test_pretrain.py`, `scenarios.py`, `test_ics_sim.py`, `Telemetry`, `PIDController`, `evaluate.py`, `train.py`, `test_xplane_backend.py`, `test_evaluate.py`, `test_ppo.py`, `test_rollout_env.py`, `RolloutEnv`, `test_action_contract.py`, `runtime/pretrain.py`, `ScenarioGenerator`, `telemetry`, `test_full_flight.py`, `test_go_around.py`, `ApproachCriteriaMonitor`, `DashboardState`, `RunwayTracker`, `fakes.py`, `test_control_parity.py`, `engaged_sim`, `on_ground`, `DatagramSocket`, `control.py`, `test_working_ics_port.py`, `DashboardServer`, `DatagramSocket`, `ControlsState`, `Criterion`, `FrictionProfile`, `PresetPolicy`?**
  _High betweenness centrality (0.153) - this node is a cross-community bridge._
- **Why does `Telemetry` connect `Telemetry` to `tolerance.py`, `weather.py`, `test_refactoring_contracts.py`, `Scenario`, `test_approach_channel.py`, `ControllingSystem`, `ScriptedFlightBench`, `airborne_inputs`, `system.py`, `scenarios.py`, `ics_connector.py`, `test_ics_sim.py`, `AircraftProfile`, `ICSSim`, `ApproachChannel`, `XPlaneSim`, `IcsEngagement`, `test_rollout_env.py`, `test_diagnostic_tools.py`, `FakeConnector`, `ics_sim.py`, `ControlModeState`, `telemetry`, `test_full_flight.py`, `test_go_around.py`, `ApproachCriteriaMonitor`, `test_tolerance.py`, `fakes.py`, `test_control_parity.py`, `Converts`, `heading_deviation_deg`, `test_working_ics_port.py`, `ControlsState`, `._header`, `_faults_from_inputs`, `HandshakeBench`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Why does `ControlsState` connect `ControlsState` to `reward.py`, `Shield`, `Scenario`, `test_approach_channel.py`, `ControllingSystem`, `system.py`, `test_ics_sim.py`, `AircraftProfile`, `ICSSim`, `ApproachChannel`, `Telemetry`, `XPlaneSim`, `PIDController`, `test_xplane_backend.py`, `test_rollout_env.py`, `RolloutEnv`, `test_diagnostic_tools.py`, `FakeConnector`, `ics_sim.py`, `test_action_contract.py`, `ApproachCriteriaMonitor`, `RunwayTracker`, `test_control_parity.py`, `engaged_sim`, `runway_tracker.py`, `Converts`, `DatagramSocket`, `._fill_ground`, `test_working_ics_port.py`, `FrictionProfile`, `_cold_sim`, `test_localizer_deflection_turns_the_aircraft_back_to_the_centreline`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `ControllingSystem` (e.g. with `AircraftControlSet` and `ApproachSetup`) actually correct?**
  _`ControllingSystem` has 43 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `ControlsState` (e.g. with `GainCommand` and `RuntimeState`) actually correct?**
  _`ControlsState` has 40 INFERRED edges - model-reasoned connections that need verification._