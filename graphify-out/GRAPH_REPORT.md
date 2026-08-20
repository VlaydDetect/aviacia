# Graph Report - GOSNIIASProject  (2026-08-20)

## Corpus Check
- 141 files · ~142,681 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2561 nodes · 5355 edges · 249 communities (130 shown, 119 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 292 edges (avg confidence: 0.6)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `66753da5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- RunRecorder
- GainMap
- ndarray
- test_evaluate.py
- ICSBenchConnector
- json_config.py
- SimInterface
- ControlsState
- Scenario
- GainKey
- Telemetry
- test_default_config_carries_the_tuned_bench_gains
- float32
- test_sft_regressors.py
- test_ics_connector.py
- test_run_matrix.py
- AircraftProfile
- airborne_inputs
- control/approach.py
- DashboardServer
- test_icd_units.py
- XPlaneSim
- Any
- PIDController
- ndarray
- DashboardState
- test_xplane_backend.py
- test_ics_sim.py
- Any
- IcsEngagement
- ground_allocator.py
- ._fail
- Telemetry
- Graphify Pipeline
- XPlaneConnector
- ControllingSystem
- test_ground_controller.py
- test_ics_engagement.py
- run_reader.py
- sft.py
- test_diagnostic_tools.py
- fakes.py
- floating
- ICSInputs
- device
- 3. Этапы реализации
- FakeConnector
- test_profiled_scenarios.py
- Path
- test_full_flight.py
- test_go_around.py
- Hybrid Neural PID Controller
- test_approach_criteria.py
- run_artifacts.py
- sim_interface.py
- RunwayTracker
- ICSSim
- ICSInputs
- test_dashboard.py
- pretrain.py
- ._apply
- test_control_parity.py
- Project Dependencies
- RunRecorder
- PidGainRegressor
- ICSInputs
- dashboard_core.py
- test_tolerance.py
- test_working_ics_dashboard.py
- ICSOutputs
- test_campaign.py
- Unified Profile-Aware Scenario System
- Interactive PID Dashboard
- MatrixRun
- test_weather.py
- ics_sim.py
- ICSInterface.cs
- План исправления
- run_pretrain
- .value
- ICS PID Monitor
- run_report.py
- Autonomous Landing Controller
- X-Plane Dashboard and Runtime Guide
- test_working_ics_golden.py
- GainSpace
- promote_candidate.py
- scenarios.py
- import_workbook
- FlightSegment
- LateralChannel
- RunReader
- initial_segment
- .read_telemetry
- ApproachConfig
- Q: Приступай к выполнению этапа 9 плана [plan.md](docs/plan.md). В процессе старайся упрощать код, удалять лишний и неиспользуемый код, а также максимально покрывать его комментариями.
- conftest.py
- agent/__init__.py
- config/__init__.py
- TypedDict
- control/__init__.py
- envs/__init__.py
- gui/__init__.py
- ismpu/__init__.py
- io/__init__.py
- runtime/__init__.py
- tools/__init__.py
- utils/__init__.py
- ismpu
- .enter_segment
- Q: Приступай к выполнению этапа 9 плана docs/plan.md; упрощай код, удаляй лишнее и добавляй комментарии.
- Q: Реализовать этап 0: baseline, golden replay и dashboard characterization
- Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md).
- config/approach.py
- ndarray
- .neutralize_airborne
- Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md).
- evaluate.py
- ._approach_step
- ControlModeState
- ICSInputs
- ICSOutputs
- socket
- IntEnum
- flight.py
- AircraftProfile
- .compute
- .from_csv
- .from_ics
- Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md).
- Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md).
- pid.py
- device
- int64
- WeatherState
- Q: Приступай к выполнению этапа 2 плана docs/plan.md
- ControlsState
- ClearWeatherILSController
- TypedDict
- xplane_sim.py
- FailureMode
- RunwayProfile
- pid_controller.py
- ControlModeState
- ApproachChannel
- Scenario
- WeatherState
- .from_dict
- StartMode
- Enum
- PidMap
- GuidanceState
- PidMap
- weather.py
- Normalization
- .__init__
- Scenario
- Path
- Q: Приступай к выполнению этапа 4 плана docs/plan.md
- runway_profiles.py
- RewardWeights
- TypedDict
- failures.py
- .reset
- RunSample
- RegulatorKey
- test_refactoring_contracts.py
- Q: Приступай к выполнению этапа 8 плана [plan.md](docs/plan.md).
- ApproachLimits
- VlaydRolloutBridge
- ICSInputs
- PidMap
- ApproachTelemetry
- Any
- ArrayLike
- float32
- LongitudinalChannel
- NDArray
- ShutdownReport
- Tensor
- ApproachLimits
- Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md).
- ApproachTelemetry
- Scenario
- NPGS
- TypedDict
- Any
- ApproachConfig
- ArrayLike
- float64
- GainMap
- NDArray
- ndarray
- ControllingSystem
- on_ground
- PretrainConfig
- ToleranceReport
- RegulatorKey
- Tensor
- GainMap
- NDArray
- Tensor
- ics.py
- ArrayLike
- float32
- float64
- GainMap
- NDArray
- _faults_from_inputs
- HandshakeBench
- GainSpace
- SimInterface
- backend_factory.py
- resolve_matrix_run
- Linear
- Normal
- DatagramSocket
- PPOMetrics
- .__init__
- .enter_segment
- RuntimeState
- Q: Добавить runtime-проверки наземных допусков ТЗ в _ground_step
- ScenarioProvider
- Sequential
- SFTDataset
- xplane.md
- segments.py
- fixture
- .set_packet_observer
- ApproachResult
- ControllingSystem
- FailureMode
- Q: Почему прогон runs/20260816T174009.095580Z раскачивает самолёт и не сохраняет паритет с working_ics по логу logs/ics_pid_20260816_104551.csv?
- Q: Проанализировать три неудачных production-прогона против working_ics и составить план исправления
- Q: Почему production-заход терял паритет с working_ics и как это исправлено?
- Q: Каков финальный результат исправления runtime-паритета 2026-08-16?
- Q: Проанализировать run 20260816T213847.114116Z, сравнить управление с working_ics и исправить уход по GLIDESLOPE и неисполняемый go-around.
- Path
- SimInterface
- parametrize
- AircraftProfile
- Any
- Enum
- FailureMode
- str
- RunReader
- FlightSegment
- str
- WeatherState

## God Nodes (most connected - your core abstractions)
1. `ControllingSystem` - 128 edges
2. `Telemetry` - 83 edges
3. `ICSSim` - 72 edges
4. `ControlsState` - 57 edges
5. `XPlaneSim` - 54 edges
6. `airborne_inputs()` - 51 edges
7. `RunRecorder` - 46 edges
8. `PIDController` - 46 edges
9. `Scenario` - 44 edges
10. `IcsEngagement` - 42 edges

## Surprising Connections (you probably didn't know these)
- `Autonomous Landing Controller` --semantically_similar_to--> `Autonomous Landing Controller`  [INFERRED] [semantically similar]
  CLAUDE.md → AGENTS.md
- `test_preset_apply_control_matches_direct_config_apply()` --calls--> `ControllingSystem`  [EXTRACTED]
  tests/test_ics_sim.py → ismpu/control/system.py
- `DatagramSocket` --uses--> `ControllingSystem`  [INFERRED]
  tests/test_refactoring_contracts.py → ismpu/control/system.py
- `test_applying_each_b42_segment_rebuilds_the_relevant_pids()` --calls--> `ControllingSystem`  [EXTRACTED]
  tests/test_run_matrix.py → ismpu/control/system.py
- `test_approach_setup_rebuilds_regulators()` --calls--> `ControllingSystem`  [EXTRACTED]
  tests/test_run_matrix.py → ismpu/control/system.py

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
- **PID Dashboard Ecosystem** — docs_xplane_dashboard_pid_dashboard, ismpu_gui_dashboard_pid_dashboard, ismpu_working_ics_ics_dashboard_ics_pid_monitor [INFERRED 0.85]

## Communities (249 total, 119 thin omitted)

### Community 0 - "RunRecorder"
Cohesion: 0.15
Nodes (16): Скопировать канонический preset и заменить только запрошенные условия запуска., Append-only writer; ошибка диска помечает прогон, но не выходит в control-loop., Дождаться записи всех ранее поставленных элементов и flush файлов., RunRecorder, test_approach_stream_has_three_pid_states_and_replays_at_1e_12(), test_report_exposes_go_around_command_to_feedback_metrics(), test_raw_packet_files_keep_exact_udp_json_and_only_observed_tx(), test_recorder_keeps_all_known_ics_fields_and_unknown_raw_fields() (+8 more)

### Community 3 - "test_evaluate.py"
Cohesion: 0.26
Nodes (21): evaluate_tz(), Преобразовать наземные метрики запуска в вердикты раздела 5 ТЗ., Вернуть ``FAIL``, если провален хотя бы один применимый критерий., verdict_of(), _by_name(), _diagnostics(), Регрессии чистых вердиктов ТЗ: пределы, применимость и отсутствие данных., Вернуть полный штатный набор метрик с запасом до каждого допуска. (+13 more)

### Community 4 - "ICSBenchConnector"
Cohesion: 0.11
Nodes (11): ICSBenchConnector, Отправка best-effort со счётчиком ошибок и разрежённым логом. Windows отдаёт…, → True если отправлено. Исключение наружу не выпускается., Мост к стенду: JSON поверх UDP, адрес стенда определяется из входящего пакета., Приём телеметрии стенда. Адрес отправителя определяется автоматически., Дождаться кадра и отбросить накопившийся UDP backlog, оставив самый свежий.…, Зафиксировать и разобрать один уже принятый UDP payload., Отправка управления на стенд. → отправлено ли (исключение наружу не… (+3 more)

### Community 5 - "json_config.py"
Cohesion: 0.12
Nodes (38): approach_control_from_dict(), approach_control_to_dict(), _copy_approach(), dump_scenario(), _finite_tree(), ground_control_from_dict(), ground_control_to_dict(), _legacy_ground() (+30 more)

### Community 6 - "SimInterface"
Cohesion: 0.10
Nodes (5): BaseException, StartMode, Минимальный lifecycle, одинаковый для стенда и X-Plane., SimInterface, Protocol

### Community 7 - "ControlsState"
Cohesion: 0.09
Nodes (47): angle_error_deg(), Разность курсов, приведённая к (-180, 180]., ControlsState, Разделяемая по тактам структура команд — и наземных, и воздушных. Аннотации…, _colleague_controller(), _descent_frames(), _our_channel(), Воздушный канал: заход по ILS, выравнивание, скоростной канал. Главный тест… (+39 more)

### Community 8 - "Scenario"
Cohesion: 0.11
Nodes (27): AircraftProfile, FailureMode, FlightSegment, _profile_name(), Оценить близость telemetry к preset; несовпадение отказа доминирует над погодой., Выбрать ближайший нематричный preset, не допуская draft без явного флага., Подобрать нематричный preset по валидной telemetry или безопасным defaults., Полный профильный сценарий APPROACH → ROLLOUT → TAXI. (+19 more)

### Community 10 - "Telemetry"
Cohesion: 0.09
Nodes (14): Телеметрия стенда, приведённая к **СИ**. Проверять надо `valid` **до** полей:…, Невалидные ICS-сигналы, которые воздушный закон читает безусловно., Приборная скорость (kt → м/с). Отсечки реверса заданы по ней, а не по путевой., Радиовысота **в футах** — единицы стенда. Порог воздушного включения (400…, Объявлены ли валидными **оба** канала ILS (курсовой и глиссадный). `None` —…, Посадочная конфигурация механизации; `None` — положение не посадочное. `None`…, Боковое отклонение от оси, измеренное стендом. Позволяет не считать геодезию…, Обжатие ВСЕХ стоек. Диагностический сигнал; условие включения проверяет сам… (+6 more)

### Community 13 - "test_sft_regressors.py"
Cohesion: 0.12
Nodes (19): feature_schema_hash(), GainGuard, Минимальная SFT-модель абсолютных коэффициентов PID и общий runtime guard., Стабильный hash порядка признаков; перестановка является сменой контракта., Проверяет prediction и ограничивает скорость изменения до записи в PID., Проверить prediction и ограничить его относительно accepted preset/предыдущего…, checkpoint_metadata(), Path (+11 more)

### Community 14 - "test_ics_connector.py"
Cohesion: 0.09
Nodes (25): GearState, IntEnum, Разбор телеметрии стенда с совместимостью вперёд. Асимметрия намеренная (JSON-…, Дискретное положение стойки в кодировке ICSInputs., Состояние створок реверса; величину задаёт отрицательный throttle rate., ReverseEngineType, _connector(), _FakeSocket (+17 more)

### Community 15 - "test_run_matrix.py"
Cohesion: 0.10
Nodes (21): compose_matrix_scenario(), _install_through_scenarios(), Сценарий по имени либо шифру матрицы, без различия раскладки А/B., Собрать сценарий из конкретных строк APPROACH/ROLLOUT/TAXI.…, Одна строка каталога → минимальный сценарий нужного участка или сквозной пары., Перенести накопленные overrides одного шифра на следующее условие этого же…, Собрать Б.4 из первой строки и заранее определённой пары законов., rebind_matrix_run() (+13 more)

### Community 16 - "AircraftProfile"
Cohesion: 0.12
Nodes (6): AircraftProfile, clamp(), Преобразовать воздушные команды ICD в нормированные DataRef X-Plane., Преобразовать нормированные команды пробега в DataRef X-Plane., Общая идентичность ЛА и необязательная привязка к X-Plane. Профиль нужен и…, Command refs retained under the historical public name.

### Community 17 - "airborne_inputs"
Cohesion: 0.12
Nodes (22): `ICSInputs` → `Telemetry`: поля в СИ + «сырой» пакет для property. Стенд отдаёт…, airborne_inputs(), Кадр «ВС на глиссаде»: стойки не обжаты, ILS валиден, скорость и высота…, Носовая стойка обжимается позже основных — ждать её значит пропустить начало…, «Козление» после касания снимает обжатие на секунду — назад в заход…, В такте касания команда обязана быть уже наземной, а не последней командой…, Таблицы захода МС-21 к чистому крылу неприменимы — вести по ним нельзя.…, Координаты захода не делают безопасным кадр с оставшимся INIT_CLIMB и взлётным… (+14 more)

### Community 18 - "control/approach.py"
Cohesion: 0.06
Nodes (51): ApproachLimits, ApproachTelemetry, alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration (+43 more)

### Community 19 - "DashboardServer"
Cohesion: 0.24
Nodes (5): DashboardServer, Loopback-only HTTP lifecycle вокруг одного ``DashboardState``., Фактически привязанные host/port, включая ephemeral port 0 в тестах., Идемпотентно запустить daemon HTTP thread., Отклонить pending tuning, остановить thread и закрыть listening socket.

### Community 20 - "test_icd_units.py"
Cohesion: 0.10
Nodes (19): Сверка каждого сигнала стенда с документами Заказчика. Два независимых…, Стенд шлёт узлы, футы, фут/мин и град/с — граница пересчёта в СИ проходит в…, 1 фут/мин = 0.3048/60 м/с. Приближение здесь копится на всём заходе., Нумерация фаз из doc-комментария `FlightPhase` в ICSInterface.cs., −26.5…55.0° — фактическое положение РУД во входной телеметрии, не команда., Наши константы обязаны совпадать с таблицей управляющих сигналов Заказчика., Тиллер задаётся ходом в миллиметрах. Отдельным тестом, потому что ошибка была…, 0–45 мм командует, 0–36.73 мм отчитывается. Подмена недодаёт ~18 % хода. (+11 more)

### Community 21 - "XPlaneSim"
Cohesion: 0.14
Nodes (4): Снимок готовности resettable backend для recorder/dashboard., XPlaneDiagnostics, ControlsState, XPlaneSim

### Community 23 - "PIDController"
Cohesion: 0.09
Nodes (31): Регуляторы канала по именам — для логов и приёмки, не для…, PIDController, Сброс внутренних состояний (используется при выключении системы)., Забыть разрыв измерения, сохранив накопленный интеграл и текущий выход., _legacy_reference(), Опциональная численность PID (шаг 5): каждый флаг проверяется на том дефекте,…, Если применено ровно то, что выдал PID, коррекции быть не должно., Уставка прыгает, объект стоит на месте — D-составляющая не должна реагировать.… (+23 more)

### Community 25 - "DashboardState"
Cohesion: 0.15
Nodes (9): _allocator_stage(), DashboardState, _first_present(), HTTP читает только immutable recorder objects; controller меняет control-thread., Стабильный execution id live/replay источника., Вернуть подписи всех девяти панелей в порядке HTML layout., Вернуть только новые recorder updates; смена run_id принудительно сбрасывает…, JSON-ready форма ``snapshot`` для ``GET /api/state``. (+1 more)

### Community 26 - "test_xplane_backend.py"
Cohesion: 0.12
Nodes (14): MockXPlaneConnector, ScriptedXPlaneConnector, test_commands_failures_and_close_release_overrides(), test_exact_taxi_row_starts_xplane_and_controller_in_taxi_at_15_knots(), test_failed_approach_setup_releases_overrides_and_pause(), test_ignored_xplane_failure_participates_in_segment_delta_and_is_cleared(), test_missing_or_stale_required_data_makes_xplane_telemetry_invalid(), test_reload_renews_subscriptions_and_sensor_dropout_is_applied() (+6 more)

### Community 27 - "test_ics_sim.py"
Cohesion: 0.06
Nodes (38): engaged_sim(), (sim, connector) с завершённым рукопожатием: стенд подтвердил `AgentIsActive =…, _cold_sim(), Тесты стенда (`ICSSim`) и подбора сценария — без реального стенда., Разделение органов из таблицы Заказчика: тиллер — на рулении, педальный пост —…, Заявить канал, который не формируешь, — взять ответственность за неуправляемый…, 31 — единственная маска, с которой заход реально прошёл на стенде. Проверяется…, Один бит на одно командное поле `ICSOutputs` — иначе заявка попадает не в тот… (+30 more)

### Community 29 - "IcsEngagement"
Cohesion: 0.05
Nodes (30): ControlModeState, EngagementInputs, IcsEngagement, Автомат включения. `step(inputs)` вызывается каждый такт до формирования…, Полный сброс — новый эпизод начинается с невключённого состояния., Сообщить автомату, что кадр **фактически ушёл** на стенд. Вызывается…, Подхватить уже включённый извне пробег: шлём `ControlMode = Rollout`.…, Войти в пробег самостоятельно: шлём `ControlMode = Rollout`. Это же — передача… (+22 more)

### Community 30 - "ground_allocator.py"
Cohesion: 0.19
Nodes (15): LateralDiagnostics, LongitudinalDiagnostics, FailureState, Эффективности исполнительных органов. Аннотации типов обязательны: без них…, ActuatorFeedback, ActuatorVector, AllocationDiagnostics, _clamp() (+7 more)

### Community 31 - "._fail"
Cohesion: 0.25
Nodes (4): Exception, Поставить запись без блокировки control thread; переполнение инвалидирует run., Сохранить полный effective config; канонические config-файлы не затрагиваются., RunEvent

### Community 32 - "Telemetry"
Cohesion: 0.11
Nodes (17): approach_blocker(), ApproachRefused, Воздушный участок начинать нельзя — с названной причиной. Отдельное исключение,…, Можно ли вообще судить об участке по этому кадру. Кадр без пакета стенда…, Почему нельзя вести заход по этому кадру. `None` — можно. Пока проверка одна,…, segment_is_decidable(), FlightSegment, Telemetry (+9 more)

### Community 33 - "Graphify Pipeline"
Cohesion: 0.08
Nodes (29): Folder Watcher, URL Ingestion, Extra Graph Exports, MCP Graph Server, Confidence Audit Trail, Deterministic Node IDs, Semantic Extraction Contract, Cross-Repository Graph Merge (+21 more)

### Community 34 - "XPlaneConnector"
Cohesion: 0.06
Nodes (23): DataRefSample, Неблокирующий UDP-клиент нативного протокола X-Plane 12., Атомарно снять все свежие значения без раскрытия внутреннего mutable cache., Discard pre-reload values so readiness cannot use stale telemetry., Повторять RREF requests до получения всех значений либо подробного timeout., Отправить один нативный 509-byte DREF packet., Последнее значение DataRef и monotonic timestamp его UDP-пакета., Отправить один нативный CMND packet. (+15 more)

### Community 35 - "ControllingSystem"
Cohesion: 0.07
Nodes (37): ControllingSystem, Связать сценарий с контуром; PID активируются после определения участка., Разорвать D-history после пропуска устаревшей UDP-очереди, не трогая интегралы., Оркестратор классического контура поверх стенда (`envs.ics_sim.ICSSim`).…, Аварийная остановка: обнулить органы и **снять заявку каналов**. Именно…, decode_outputs(), Готовый кадр `Telemetry` для прямых вызовов `control_step(dt, telemetry,…, Отправленные команды в нормированном виде — для сравнения траекторий.… (+29 more)

### Community 36 - "test_ground_controller.py"
Cohesion: 0.11
Nodes (26): _lost_engagement(), SimInterface, Снял ли стенд активность посреди прогона. → пора останавливаться. Без этой…, Компактные перцентили миллисекунд без зависимости в критическом пути., Прогоняет один полёт на уже настроенном контуре., run(), _timing_summary(), parametrize (+18 more)

### Community 37 - "test_ics_engagement.py"
Cohesion: 0.10
Nodes (49): _Clock, _engine(), _pump(), Автомат включения управления на стенде. Два раздельных предмета проверки: *…, По ICD стенд должен два секунды ПОЛУЧАТЬ ModeAIReady=1. Если считать одно лишь…, Обратная защита: 30 кадров можно выпалить за 0.1 с — время тоже обязано пройти., Срыв предусловия обнуляет и время, и счётчик кадров., Требование ICD — непрерывность: пропуск готовности рвёт серию. (+41 more)

### Community 38 - "run_reader.py"
Cohesion: 0.12
Nodes (19): _apply_recorded_gains(), _bool_or_none(), _equal(), main(), _number(), _parse_cell(), ControllingSystem, Единое потоковое чтение run-directory, replay и прежних CSV. (+11 more)

### Community 39 - "sft.py"
Cohesion: 0.13
Nodes (23): GuardResult, Фактически разрешённые gains и причина ограничений/fallback., apply_gain_vector(), controller_gain_vector(), _feature_value(), feature_vector(), gain_vector_from_row(), _number() (+15 more)

### Community 40 - "test_diagnostic_tools.py"
Cohesion: 0.20
Nodes (19): build_altitude_sweep(), command_for_pulse(), Безопасные elevator/altitude authority sweep без дублирования ICS runner., Чистое преобразование, пригодное и для dry-run, и для ICSSim., safety_reason(), SweepLimits, SweepPulse, validate_pulse() (+11 more)

### Community 41 - "fakes.py"
Cohesion: 0.08
Nodes (23): IntEnum, FlightPhase, Фаза полёта, сообщаемая стендом (`ICSInputs.FlightPhase`)., ControlModeState, Режим управления/индикации, передаваемый в каждом ICSOutputs., decode_airborne(), flight_sim(), _integrate_throttle() (+15 more)

### Community 43 - "ICSInputs"
Cohesion: 0.16
Nodes (22): ControlResult, ICSInputs, ICSOutputs, UDP-мост к стенду заказчика (порт 3030) — транспорт пути поставки. `ICSInputs`…, Неизвестные поля исходного JSON; они доступны аудиту, но не закону управления., Команды и mode flags, сериализуемые ровно в ожидаемый стендом JSON., Сериализовать enums и 14 reserved zeros в точные UTF‑8 bytes wire contract., Полная известная входная схема стенда; единицы определены в ``ICSInterface.cs``. (+14 more)

### Community 45 - "3. Этапы реализации"
Cohesion: 0.09
Nodes (21): 1. Подтверждённые проблемы и целевое состояние, 2. Ключевые интерфейсы, 3. Этапы реализации, 4. Тестирование и критерии готовности, 5. Зафиксированные допущения, 6.1. Один dashboard вместо двух, 6.2. Единый источник данных, 6.3. Представления (+13 more)

### Community 46 - "FakeConnector"
Cohesion: 0.10
Nodes (21): FakeConnector, make_ics_inputs(), Статический стенд: всегда один и тот же кадр, отправленное — в `sent_outputs`., Полный пакет стенда: нули по умолчанию + заданные поля., Неизвестный код — не повод предполагать сухую полосу., Погоду задаёт Заказчик; наш `WeatherState` — это прочитанный кадр, а не задание., До рукопожатия заявлять каналы нельзя: стенд ещё не разрешил нам ими управлять., Стенд отдаёт узлы, футы, футы/мин и градусы/с — граница пересчёта проходит… (+13 more)

### Community 47 - "test_profiled_scenarios.py"
Cohesion: 0.28
Nodes (6): compose_scenario(), Собрать сценарий из независимых источников участков., Contracts of the unified aircraft-profiled scenario model., test_automatic_selection_never_falls_back_to_a_draft_profile_branch(), test_composition_keeps_repeated_failures_as_one_set_member(), test_composition_selects_each_phase_and_preserves_provenance()

### Community 49 - "test_full_flight.py"
Cohesion: 0.09
Nodes (36): IntFlag, ControlValid, Биты `ControlValidMask`: какие каналы несёт команда. **Один бит на одно…, _air(), _Clock, _engaged_airborne_sim(), _pump(), parametrize (+28 more)

### Community 50 - "test_go_around.py"
Cohesion: 0.14
Nodes (27): GoAroundManeuver, Состояние идущего ухода на второй круг. Пока он активен, заход не ведётся., _armed_controller(), _drive(), _frame(), Уход на второй круг (fallback в воздухе): условия срабатывания и передача…, На пробеге ухода нет — segment guard (козление удерживает защёлка сегмента,…, Если реверс уже включён — взлёт невозможен, ухода нет. (+19 more)

### Community 51 - "Hybrid Neural PID Controller"
Cohesion: 0.70
Nodes (5): Hybrid Neural PID Controller, Neural PID Gain Scheduler, PPO Training Loop, Preset-Anchored Deterministic Shield, SFT Behavioral-Cloning Warm Start

### Community 52 - "test_approach_criteria.py"
Cohesion: 0.18
Nodes (12): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, Отдельный монитор критерия А.1.1 (не участвует в go-around)., Захватывает А.1.1 после входа в допуск и завершает оценку на 300 ft., frame() (+4 more)

### Community 53 - "run_artifacts.py"
Cohesion: 0.19
Nodes (17): controller_pids(), _csv_value(), default_runs_root(), _effective_configs(), gains_snapshot(), _git_state(), _jsonable(), _matrix_rows() (+9 more)

### Community 54 - "sim_interface.py"
Cohesion: 0.25
Nodes (8): ControlDiagnostics, Enum, Общий контракт симулятора и воздушных сигналов. ICS и X-Plane различаются…, Исчерпывающие причины штатного/аварийного завершения единого runtime loop., Причина остановки вместе с best-effort результатом освобождения backend., Backend-neutral диагностические значения текущего управляющего такта., RunResult, RunStopReason

### Community 55 - "RunwayTracker"
Cohesion: 0.12
Nodes (13): CompletionRule, Решить прямую геодезическую задачу на сферической Земле., Геодезическое guidance в истинной системе направлений., Guidance по курсу ВПП и измеренному отклонению — без собственной геодезии.…, Возвращает отклонение от осевой линии в метрах. >0 - правее оси, <0 - левее., Геодезическое наведение на ось ВПП с упреждением по скорости., RunwayTracker, PidMap (+5 more)

### Community 56 - "ICSSim"
Cohesion: 0.09
Nodes (12): ICSSim, FailureMode, SimInterface, Обмен со стендом заказчика: телеметрия внутрь, команды наружу. Управление…, Принимает ли стенд наши команды. До включения любой `step` уходит вхолостую., Сколько устаревших UDP-кадров сброшено при последнем чтении., Войти в пробег самостоятельно (`ControlMode 0 → 3`)., Перейти `Approach → Landing`; сессия и воздушные каналы сохраняются. (+4 more)

### Community 57 - "ICSInputs"
Cohesion: 0.13
Nodes (14): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, ICSInputs, Evaluate the A.1.1 approach segment and stop at a radio-altitude floor., ControlModeState (+6 more)

### Community 58 - "test_dashboard.py"
Cohesion: 0.20
Nodes (13): _live(), _post(), parametrize, test_active_pid_is_editable_in_classical_and_shadow(), test_gain_change_is_queued_bumpless_and_records_full_event(), test_http_api_is_incremental_pending_and_loopback_only(), test_incremental_snapshot_uses_recorder_objects_and_stays_small_when_idle(), test_live_and_replay_use_the_same_dashboard_snapshot() (+5 more)

### Community 59 - "pretrain.py"
Cohesion: 0.09
Nodes (38): _condition_key(), _fit_feature_normalization(), load_offline_dataset(), _normalized_mse(), _physical_bounds(), _predict(), ndarray, Path (+30 more)

### Community 60 - "._apply"
Cohesion: 0.16
Nodes (7): _finite(), GainChange, Проверить HTTP-запрос и поставить полный PID triplet в control-thread queue., Поставить восстановление gains начала запуска для активного участка., Вызывается runtime ровно в начале control tick., Закрыть tuning и записать отказ для каждого неисполненного запроса., Immutable запрос HTTP-thread, ожидающий применения control-thread.

### Community 61 - "test_control_parity.py"
Cohesion: 0.10
Nodes (21): CompletionRule, Enum, Генератор эталонной кривой скорости пробега. Два закона замедления: колокол…, Как активный наземный сценарий заканчивает управление., Генератор эталонной кривой скорости (Колокол Гаусса)., Начать профиль с фактической скорости текущего участка., То же без лишнего round-trip м/с → узлы → м/с на касании., Возвращает идеальную скорость (м/с) для текущей точки пути. (+13 more)

### Community 62 - "Project Dependencies"
Cohesion: 0.29
Nodes (7): Optional Gymnasium, NumPy, Pandas, Project Dependencies, Pytest, Termcolor, Optional PyTorch

### Community 64 - "PidGainRegressor"
Cohesion: 0.13
Nodes (17): device, PidGainRegressor, Any, Предсказать gains по последнему hidden state окна ``(B,T,F)``., Сохранить веса вместе с полным train↔runtime контрактом., Загрузить модель только после проверки полного train↔runtime контракта., Краткая форма ``load_checkpoint`` для потребителя, которому не нужна metadata., Восстановить и строго проверить normalization из checkpoint. (+9 more)

### Community 66 - "dashboard_core.py"
Cohesion: 0.16
Nodes (11): DashboardSnapshot, main(), _mean(), Один локальный dashboard для live RunRecorder и read-only replay., Запустить локальный read-only replay dashboard до ``Ctrl+C``., Отображаемое имя, PID source и физическая фаза одной панели графика., Инкремент после sequence cursor и редкие metadata при reset., Преобразовать tuples в JSON arrays, не добавляя отсутствующие тяжёлые секции. (+3 more)

### Community 67 - "test_tolerance.py"
Cohesion: 0.06
Nodes (53): FailureState, lateral_limit_m(), lateral_load_situation(), lateral_situation(), normal_load_situation(), IntEnum, Критерии критичности особых ситуаций МС-21 (Приложение 1 к ТЗ). Таблица АП-25…, Классификация скорости касания относительно VAPP и VВПП пред. (+45 more)

### Community 68 - "test_working_ics_dashboard.py"
Cohesion: 0.35
Nodes (10): ClearWeatherILSController, DashboardState, _controller(), _inputs(), Characterization tests for the bench-validated ``working_ics`` dashboard., _record(), test_dashboard_records_four_airborne_views_and_diagnostics(), test_gain_updates_are_immediate_validated_and_share_pitch_with_flare() (+2 more)

### Community 70 - "test_campaign.py"
Cohesion: 0.29
Nodes (14): campaign_phase(), campaign_rows(), campaign_summary(), _config_status(), main(), next_campaign_row(), Path, Порядок и фактический статус кампании из 280 матричных прогонов. (+6 more)

### Community 71 - "Unified Profile-Aware Scenario System"
Cohesion: 0.33
Nodes (6): Technical-Specification Acceptance Gates, Forward-Only Flight Segment Supervisor, Longitudinal and Lateral Ground Channels, PID Run Matrix, Unified Profile-Aware Scenario System, Legacy Scenario Preset Model

### Community 72 - "Interactive PID Dashboard"
Cohesion: 0.25
Nodes (9): Nine-View PID Dashboard, Run Recording Artifacts, buildTabs, draw, Gain Tuning and Snapshot Export, Interactive PID Dashboard, refresh, render (+1 more)

### Community 73 - "MatrixRun"
Cohesion: 0.05
Nodes (15): MatrixCase, MatrixCondition, MatrixRun, _number(), Any, FailureMode, FlightSegment, WeatherState (+7 more)

### Community 74 - "test_weather.py"
Cohesion: 0.18
Nodes (13): compose_wind(), decompose_wind(), (скорость, откуда) → (crosswind, headwind) относительно курса ВПП. crosswind >…, (crosswind, headwind) → (скорость, откуда, °). Обратна `decompose_wind`., Тесты погоды: разбор ветра, шкала скользкости и чтение условий из пакета стенда., Для пробега существенна боковая составляющая, а не «скорость ветра» сама по…, Все семь кодов из фактических пакетов закрыты явно., test_crosswind_from_right_is_perpendicular() (+5 more)

### Community 75 - "ics_sim.py"
Cohesion: 0.10
Nodes (20): Приёмочные пороги из ТЗ (раздел 5). Единый источник истины для runtime…, Геометрия целевой ВПП и высоты установки ЛА. Смена целевой полосы = правка…, Оркестратор классического контура управления — на всём интервале полёта.…, GroundToleranceReport, Мониторы допусков захода, пробега и прямого руления. Отдельно от…, Допуски наземного движения на одном такте без вмешательства в управление., Стенд заказчика как источник телеметрии и приёмник команд. Единственный…, _number() (+12 more)

### Community 76 - "ICSInterface.cs"
Cohesion: 0.36
Nodes (7): External.Systems.ICS, ControlModeState, GearState, ICSInputs, ICSOutputs, ReverseEngineType, UInt64

### Community 77 - "План исправления"
Cohesion: 0.12
Nodes (15): 1. Handshake не повторяет рабочую последовательность, 2. Runtime работает с другой частотой и другой топологией, 3. RunRecorder находится в управляющем потоке, 4. Go-around имеет две отдельные ошибки, 5. Production entrypoint сейчас загрязнён debug-путём, ElevatorCmd действительно отправлялся, Найденные причины, План исправления (+7 more)

### Community 78 - "run_pretrain"
Cohesion: 0.29
Nodes (8): cli(), PretrainRunConfig, Последовательно обучить выбранные участки из одного каталога принятых прогонов., CLI офлайн-обучения; сеть никогда не открывает UDP и не сбрасывает X-Plane., Пути и участки для CLI, обучающего независимые air/ground checkpoints., Итог обучения участка и данные, необходимые для автоматической проверки gate., run_pretrain(), TrainingResult

### Community 79 - ".value"
Cohesion: 0.40
Nodes (3): _jsonable(), Вернуть одно свежее значение; stale/missing представлены ``None``., RunEvent

### Community 80 - "ICS PID Monitor"
Cohesion: 0.22
Nodes (9): Bench-Validated ILS Approach Channel, Tolerance-Gated Go-Around, buildControls, draw, formatTime, Four-Loop PID Tuning, ICS PID Monitor, Live and Historical Timeline (+1 more)

### Community 81 - "run_report.py"
Cohesion: 0.18
Nodes (23): _accepted_segments(), aggregate_matrix_results(), _approach_runway_heading_error(), build_run_report(), _handover_ratio(), main(), _max_abs(), _metrics() (+15 more)

### Community 82 - "Autonomous Landing Controller"
Cohesion: 0.25
Nodes (8): Autonomous Landing Controller, Fourteen-Bit ControlValidMask Layout, Two-Factor ICS Engagement Handshake, ICS UDP JSON Protocol, Repository Guidance for Codex, Telemetry SI Unit Boundary, Autonomous Landing Controller, Repository Guidance for Claude Code

### Community 83 - "X-Plane Dashboard and Runtime Guide"
Cohesion: 0.43
Nodes (7): Dual-Backend SimInterface, ICS-Only Backend Guidance, Aircraft-Profile Checkpoint Isolation, Live A330 Acceptance Checklist, Profile-Aware Flight Scenarios, X-Plane Dashboard and Runtime Guide, X-Plane Resettable Runtime

### Community 84 - "test_working_ics_golden.py"
Cohesion: 0.26
Nodes (11): Касание: обжата **любая основная** стойка. Носовая не участвует — она…, _assert_numeric_result(), ICSInputs, Characterization baseline of the bench-validated ``working_ics`` approach., Канонический контур и формирователь пакета совпадают с эталоном до 1e-12., _replay(), _rows(), _state() (+3 more)

### Community 86 - "promote_candidate.py"
Cohesion: 0.33
Nodes (15): _gain_patch(), main(), promote_candidate(), PromotionError, Path, Проверяемое продвижение dashboard candidate в sparse scenario override., Пересчитать matrix/config hashes, а не доверять двум согласованно изменённым…, Проверить run и записать новый scenario JSON; registry исходников не меняется. (+7 more)

### Community 87 - "scenarios.py"
Cohesion: 0.09
Nodes (27): ConditionMatch, ControlProfile, _copy_approach(), _copy_ground(), _ground_matrix_drafts(), _ground_segments_for_spec(), _GroundPresetSpec, _install_approach_scenarios() (+19 more)

### Community 88 - "import_workbook"
Cohesion: 0.33
Nodes (9): import_workbook(), main(), Any, Path, Одноразовый импорт исходной Excel-матрицы в runtime-каталог JSON., Прочитать книгу целиком; функция не используется production runtime., _scalar(), write_catalog() (+1 more)

### Community 89 - "FlightSegment"
Cohesion: 0.50
Nodes (4): FlightSegment, Enum, str, Участок, для которого выбираются закон управления и условия сценария.

### Community 90 - "LateralChannel"
Cohesion: 0.27
Nodes (6): GuidanceState, LateralChannel, Блок 2: runway guidance → единый нормированный yaw-запрос., Путевой угол на пробеге, курс фюзеляжа на малой скорости. При стремящейся к…, Guidance по тому, что даёт стенд. → словарь guidance или None, если данных нет.…, Вернуть тот же ``GuidanceState``, который использует управляющий такт и…

### Community 91 - "RunReader"
Cohesion: 0.16
Nodes (11): Path, Run-directory и любой поддержанный CSV через один streaming API., RunReader, engaged_inputs(), Кадр стенда, который уже принял управление: `AgentIsActive = 1`, идёт пробег., _frame(), _record_ground_run(), test_legacy_adapter_does_not_invent_missing_pid_terms() (+3 more)

### Community 92 - "initial_segment"
Cohesion: 0.15
Nodes (14): initial_segment(), is_airborne(), FlightSegment, Сообщает ли стенд, что ВС в воздухе и достаточно высоко для приёма захода.…, С какого участка начинать. Пробег — ответ по умолчанию (см. модуль)., Кадр «связи со стендом нет». Нули, а не None: контур проверяет `valid` первым., Стенд при обрыве связи отдаёт НУЛИ с valid=False, а не None. Проверка «поле is…, test_control_step_stops_on_invalid_frame_even_with_numeric_fields() (+6 more)

### Community 93 - ".read_telemetry"
Cohesion: 0.10
Nodes (16): ControlsState, EngagementInputs, ICSOutputs, _clamp(), Начало эпизода: сброс рукопожатия и первый кадр со стенда. Средой распоряжается…, Отправить команду без скрытого чтения следующего RX-кадра., Гонит стимул рукопожатия, пока стенд не подтвердит включение (`AgentIsActive =…, Желаемый уровень реверса [-1, 0] → скорость перемещения РУД (°/с). Тягой (в том… (+8 more)

### Community 95 - "Q: Приступай к выполнению этапа 9 плана [plan.md](docs/plan.md). В процессе старайся упрощать код, удалять лишний и неиспользуемый код, а также максимально покрывать его комментариями."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 9 плана [plan.md](docs/plan.md). В процессе старайся упрощать код, удалять лишний и неиспользуемый код, а также максимально покрывать его комментариями., Source Nodes

### Community 109 - ".enter_segment"
Cohesion: 0.22
Nodes (5): FailureMode, FlightSegment, Scenario, Применить только дельту условий при переходе между участками., Снять один отказ, не переинициализируя отказ, продолжающийся на новом участке.

### Community 110 - "Q: Приступай к выполнению этапа 9 плана docs/plan.md; упрощай код, удаляй лишнее и добавляй комментарии."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 9 плана docs/plan.md; упрощай код, удаляй лишнее и добавляй комментарии., Source Nodes

### Community 111 - "Q: Реализовать этап 0: baseline, golden replay и dashboard characterization"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Реализовать этап 0: baseline, golden replay и dashboard characterization, Source Nodes

### Community 112 - "Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md)., Source Nodes

### Community 113 - "config/approach.py"
Cohesion: 0.22
Nodes (8): ApproachConfig, _pid_from_colleague(), Настройки воздушного участка: заход по ILS, выравнивание, управление скоростью.…, Загрузка настроек из JSON коллеги (`config/ics_clear_weather_pid.json`). Секции…, `PIDConfig` коллеги → аргументы нашего `PIDController`. Предел интегратора у…, Параметры воздушного контура. Значения по умолчанию — настроенные на стенде.…, Наши умолчания и его файл — одно и то же. Разойдутся — расхождение должно быть…, test_config_from_the_colleague_json_matches_our_defaults()

### Community 115 - ".neutralize_airborne"
Cohesion: 0.19
Nodes (5): Обнуляет все органы управления. Отправку делает вызывающий через `ICSSim.step`.…, Совместимое имя старого API; колёсные органы оно больше не обозначает., Сброс к нейтральным командам — новый эпизод начинается с чистого состояния.…, Обнулить только воздушные команды. Нужно, когда воздушный канал не может…, setter

### Community 116 - "Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)., Source Nodes

### Community 117 - "evaluate.py"
Cohesion: 0.18
Nodes (13): _check(), Criterion, evaluate_matrix_run(), _range_check(), Чистые функции приёмки телеметрии по ТЗ и строкам матрицы. Каждый критерий…, Оценить выбранную строку матрицы, не смешивая требования соседних фаз., Один пункт ТЗ: предел, измеренное значение, вердикт и его причина., Вернуть сериализуемую строку отчёта без отдельной DTO-схемы. (+5 more)

### Community 118 - "._approach_step"
Cohesion: 0.14
Nodes (7): Такт воздушного участка. → True, если управлять больше нечем. Касание…, Зафиксировать `Approach → Landing` на 25 ft без смены воздушного закона., Прервать заход с названной причиной. → True (управлять больше нечем)., Начать уход: зафиксировать состояние манёвра и высоту входа., Три блока: speed controller → guidance → allocator., Передать управление с посадки на пробег (`ControlMode 2 → 3`). Момент — первое…, Back-calculation по итоговым командам. No-op, пока у PID не задан…

### Community 124 - "flight.py"
Cohesion: 0.11
Nodes (17): above_decision_height(), above_decision_velocity(), at_lateral_alignment_gate(), ils_blocker(), in_terminal_window(), Участки полёта и переходы между ними. Управление ведётся на всём интервале — от…, Последние футы перед касанием, где прерывать заход опаснее, чем доработать.…, ВС выше высоты решения ухода на второй круг (30 м по ТЗ 5.1.1.2). → уход… (+9 more)

### Community 126 - ".compute"
Cohesion: 0.18
Nodes (5): → (интеграл только с утечкой, интеграл с утечкой и приращением). Оба уже зажаты., Такт регулятора. `measurement` обязателен при `derivative_on_measurement=True`., Back-calculation: подтянуть интегратор к фактически применённой команде. No-op…, Сменить коэффициенты без сброса D-history и с компенсацией интегратором.…, Вес апериодического фильтра D-составляющей за такт `dt`.

### Community 127 - ".from_csv"
Cohesion: 0.17
Nodes (11): _gain_ranges(), _gains_from_manifest(), _gains_from_samples(), _handler_factory(), _load_updates(), Path, RunReader, После recorder.finish держать полный run доступным, но только для чтения. (+3 more)

### Community 128 - ".from_ics"
Cohesion: 0.25
Nodes (6): Фактические погодные условия со стенда (ветер, сцепление, осадки, видимость)., `ICSInputs` → `WeatherState`. Единственный источник фактической погоды. Стенд…, `Visibility` в футах. Без пересчёта 16000 футов читались бы как «ясно» вместо…, test_visibility_is_converted_from_feet(), Стенд шлёт узлы и **футы**; в WeatherState видимость — в метрах., test_from_ics_converts_units()

### Community 129 - "Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md)., Source Nodes

### Community 130 - "Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md)., Source Nodes

### Community 131 - "pid.py"
Cohesion: 0.16
Nodes (9): Типы и порядок коэффициентов пяти наземных PID-регуляторов. Модуль намеренно не…, Полностью пересобрать наземные каналы controller этой конфигурацией., PIDDiagnostics, Пропорционально-интегрально-дифференциальный регулятор. Класс сохраняет прежнюю…, Типизированный снимок последнего такта регулятора., apply_ground_control(), build_pids(), Сборка классического контура из неизменяемой конфигурации. (+1 more)

### Community 134 - "WeatherState"
Cohesion: 0.25
Nodes (7): Any, Погодные условия. Поля — ровно то, что сообщает стенд (см. `from_ics`).…, Собирает ветер из компонент относительно курса ВПП. `crosswind_kts` > 0 — ветер…, Сериализация в примитивы (для логирования/воспроизводимости сценариев)., WeatherState, test_scenario_roundtrip_with_weather_and_failures(), test_weatherstate_from_crosswind()

### Community 135 - "Q: Приступай к выполнению этапа 2 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 2 плана docs/plan.md, Source Nodes

### Community 137 - "ClearWeatherILSController"
Cohesion: 0.15
Nodes (7): DashboardServer, DashboardState, Any, ICSInputs, ClearWeatherILSController, test_roundout_commands_a_material_pitch_increase_before_touchdown(), test_terminal_pitch_hold_starts_before_last_five_feet_guidance_cutoff()

### Community 139 - "xplane_sim.py"
Cohesion: 0.09
Nodes (15): Профили преобразования команд ИСМПУ в органы управления X-Plane., Расширение реестра будущим профилем МС-21 без правки XPlaneSim., Проводка и масштабы конкретного планера X-Plane., register_aircraft_profile(), XPlaneAircraftBinding, Глобальные константы контура управления (перенесены из main.ipynb)., Каналы управления и общий вектор команд. `ControlsState` — разделяемая по…, Слежение за осью ВПП: геодезия, cross-track error, guidance с look-ahead.… (+7 more)

### Community 142 - "pid_controller.py"
Cohesion: 0.13
Nodes (22): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+14 more)

### Community 147 - ".from_dict"
Cohesion: 0.15
Nodes (9): Any, ApproachConfig, _materialize_override(), Применить одноуровневый sparse patch и вернуть полный неизменяемый config., Материализовать базовую ветку и sparse override выбранной строки., Serialize only the canonical profile- and matrix-aware schema v3., Прочитать schema v3 либо явно мигрируемую v1/v2 конфигурацию., test_external_profile_controls_survive_scenario_v2_roundtrip() (+1 more)

### Community 151 - "GuidanceState"
Cohesion: 0.29
Nodes (3): GuidanceState, Совместимость с прежним атрибутом; новый термин явно указывает ось., Совместимость со старым словарным API.

### Community 153 - "weather.py"
Cohesion: 0.18
Nodes (12): Enum, Погодные условия эпизода: описание, шкала сцепления и разбор ветра. Модуль **не…, Состояние ВПП как **монотонная шкала скользкости** 0…15 (0 — сухо, 15 — лёд со…, Код состояния ВПП со стенда → наша шкала. Неизвестный код трактуется как `ICY`,…, runway_condition_from_bench(), RunwayCondition, Коды из фактических пакетов переводятся в свою шкалу скользкости., test_runway_condition_codes_are_remapped_not_passed_through() (+4 more)

### Community 154 - "Normalization"
Cohesion: 0.10
Nodes (16): ArrayLike, Dataset, float32, float64, Normalization, NDArray, Выполнить deterministic inference и вернуть физические gains плюс OOD flag., Покомпонентная standardization и границы обучающей выборки. (+8 more)

### Community 155 - ".__init__"
Cohesion: 0.29
Nodes (5): AircraftProfile, Path, RunwayProfile, WeatherState, XPlaneConnector

### Community 158 - "Q: Приступай к выполнению этапа 4 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 4 плана docs/plan.md, Source Nodes

### Community 159 - "runway_profiles.py"
Cohesion: 0.23
Nodes (9): find_earth_nav_dat(), ILSStation, parse_ils_station(), Path, Профили ВПП и разрешение ILS из установленной базы X-Plane., Точка на продолжении оси; положительное расстояние — до порога., Найти LOC (тип 4) без хардкода частоты., RunwayProfile (+1 more)

### Community 162 - "failures.py"
Cohesion: 0.25
Nodes (6): FailureManager, FailureMode, Enum, Модель отказов бортового оборудования. `FailureState` хранит мультипликативные…, Проецирует набор дискретных отказов в эффективности исполнительных органов., Привести состояние ровно к набору `modes` (то, что сообщил стенд). Пересборка с…

### Community 163 - ".reset"
Cohesion: 0.16
Nodes (6): ApproachSetup, _destination(), Типизированные backend-расширения общего SI-кадра., TelemetryExtensions, StartMode, TouchdownSetup

### Community 164 - "RunSample"
Cohesion: 0.25
Nodes (4): _mode_for(), Один такт: вход, команда и диагностика имеют общий ``tick_id``., Атомарный incremental slice для dashboard, без чтения controller., RunSample

### Community 166 - "test_refactoring_contracts.py"
Cohesion: 0.18
Nodes (12): cli(), main(), Управляющий цикл 20 Гц против стенда заказчика — **весь интервал полёта**.…, Точка входа: подключиться к стенду, выбрать пресет и провести полёт.…, Единственная production CLI-точка для ICS и явного тестового X-Plane backend., parametrize, Эталон разрешён тестам, но не должен стать скрытым runtime dependency., test_production_cli_uses_the_unified_runtime_without_working_ics() (+4 more)

### Community 167 - "Q: Приступай к выполнению этапа 8 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 8 плана [plan.md](docs/plan.md)., Source Nodes

### Community 169 - "VlaydRolloutBridge"
Cohesion: 0.25
Nodes (7): ICSInputs, socket, Hand the validated airborne session to Vlayd's existing rollout loop. The…, Keep Vlayd's engagement latch synchronized during the approach., Run Vlayd's rollout until taxi speed, then send its taxi handoff., VlaydRolloutBridge, test_rollout_bridge_preserves_engagement_and_switches_without_off()

### Community 176 - "LongitudinalChannel"
Cohesion: 0.22
Nodes (6): LongitudinalChannel, Блок 1: скорость → симметричная база тормозов и реверса., Сбросить PID и привязать начало профиля к фактической скорости касания/старта., PIDController, ReferenceTrajectory, RunwayTracker

### Community 181 - "Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md)., Source Nodes

### Community 194 - "on_ground"
Cohesion: 0.20
Nodes (10): on_ground(), Кадр «ВС на полосе»: обжаты все стойки, курс/координаты у порога UUEE 06R., Пресет — стартовое предположение; фактическую конфигурацию сообщает борт., Отказ может быть снят — накапливающий учёт держал бы орган мёртвым до конца…, Единичный таймаут — не повод вернуть рулю авторитет, которого у него нет., test_controller_takes_failures_from_the_bench_not_from_the_preset(), test_failures_are_cleared_when_the_bench_stops_reporting_them(), test_ics_requires_profile_and_records_nonfatal_transition_mismatch() (+2 more)

### Community 202 - "ics.py"
Cohesion: 0.38
Nodes (5): Enum, Константы интерфейса стенда заказчика (ПИВ / ICS). Единый источник правды по…, EngagementState, Автомат включения управления на стенде заказчика. Стенд принимает наши команды…, Состояние **исходящего стимула** (что мы шлём стенду), а не факта включения.…

### Community 208 - "_faults_from_inputs"
Cohesion: 0.40
Nodes (4): ICSInputs, _faults_from_inputs(), Отказы, о которых сообщает борт — **единственный** источник истины об отказах.…, Сигналы отказов со стенда → наши `FailureMode`. Отказы шасси…

### Community 209 - "HandshakeBench"
Cohesion: 0.22
Nodes (6): HandshakeBench, Стенд, включающий управление только после корректного рукопожатия. Ждёт…, Стенд включается по полученной готовности, а не по нашему представлению о ней., Не ждать десять секунд и не принимать управление уже набирающим самолётом., test_airborne_handshake_stops_before_approach_if_takeoff_phase_appears(), test_the_airborne_handshake_is_actually_transmitted_before_approach()

### Community 212 - "backend_factory.py"
Cohesion: 0.21
Nodes (10): ICSBenchConnector, IcsEngagement, get_aircraft_profile(), get_runway_profile(), build_sim(), Any, Path, Единая фабрика backend: ICS по умолчанию, X-Plane явно. (+2 more)

### Community 213 - "resolve_matrix_run"
Cohesion: 0.25
Nodes (7): normalize_code(), Нормализовать латинские A/B и регистр к шифрам книги ``А/Б``., Разрешить только полный ``<шифр>/<номер>`` и вернуть точную строку JSON., Вернуть строки одного шифра в исходном порядке книги., resolve_matrix_run(), runs_for_code(), _matrix_results()

### Community 218 - ".__init__"
Cohesion: 0.40
Nodes (3): ApproachController, SimInterface, Пересобрать воздушный канал под заданные настройки. → новый канал. Именно…

### Community 219 - ".enter_segment"
Cohesion: 0.40
Nodes (4): ConditionMatch, FlightSegment, Сверить ожидаемые условия; стендовые условия никогда не изменяются кодом., Scenario

### Community 221 - "Q: Добавить runtime-проверки наземных допусков ТЗ в _ground_step"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Добавить runtime-проверки наземных допусков ТЗ в _ground_step, Source Nodes

### Community 232 - "Q: Почему прогон runs/20260816T174009.095580Z раскачивает самолёт и не сохраняет паритет с working_ics по логу logs/ics_pid_20260816_104551.csv?"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Почему прогон runs/20260816T174009.095580Z раскачивает самолёт и не сохраняет паритет с working_ics по логу logs/ics_pid_20260816_104551.csv?, Source Nodes

### Community 233 - "Q: Проанализировать три неудачных production-прогона против working_ics и составить план исправления"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Проанализировать три неудачных production-прогона против working_ics и составить план исправления, Source Nodes

### Community 234 - "Q: Почему production-заход терял паритет с working_ics и как это исправлено?"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Почему production-заход терял паритет с working_ics и как это исправлено?, Source Nodes

### Community 235 - "Q: Каков финальный результат исправления runtime-паритета 2026-08-16?"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Каков финальный результат исправления runtime-паритета 2026-08-16?, Source Nodes

### Community 236 - "Q: Проанализировать run 20260816T213847.114116Z, сравнить управление с working_ics и исправить уход по GLIDESLOPE и неисполняемый go-around."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Проанализировать run 20260816T213847.114116Z, сравнить управление с working_ics и исправить уход по GLIDESLOPE и неисполняемый go-around., Source Nodes

## Ambiguous Edges - Review These
- `Unified Profile-Aware Scenario System` → `Legacy Scenario Preset Model`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to
- `Dual-Backend SimInterface` → `ICS-Only Backend Guidance`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **114 isolated node(s):** `Answer`, `Outcome`, `Source Nodes`, `ismpu`, `Answer` (+109 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **119 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `MatrixRun` (3× useful, score=2.745737607)
- `XPlaneSim` (3× useful, score=2.733234673)
- `PidGainRegressor` (2× useful, score=1.832435148)
- `rollout_bridge.py` (2× useful, score=1.832435148)
- `loop.py` (2× useful, score=1.812863387) _(code changed — re-verify)_
- `LateralChannel` (2× useful, score=1.778734041)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Unified Profile-Aware Scenario System` and `Legacy Scenario Preset Model`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Dual-Backend SimInterface` and `ICS-Only Backend Guidance`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Telemetry` connect `Telemetry` to `.from_ics`, `ControlsState`, `xplane_sim.py`, `airborne_inputs`, `control/approach.py`, `test_icd_units.py`, `XPlaneSim`, `test_ics_sim.py`, `ground_allocator.py`, `Telemetry`, `.reset`, `ControllingSystem`, `test_diagnostic_tools.py`, `VlaydRolloutBridge`, `fakes.py`, `ICSInputs`, `FakeConnector`, `LongitudinalChannel`, `test_full_flight.py`, `test_go_around.py`, `test_approach_criteria.py`, `sim_interface.py`, `test_control_parity.py`, `ics_sim.py`, `_faults_from_inputs`, `HandshakeBench`, `test_working_ics_golden.py`, `LateralChannel`, `.enter_segment`, `initial_segment`, `.read_telemetry`, `RunReader`, `.enter_segment`, `flight.py`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Why does `ControllingSystem` connect `ControllingSystem` to `RunRecorder`, `pid.py`, `test_sft_regressors.py`, `test_run_matrix.py`, `airborne_inputs`, `test_xplane_backend.py`, `test_ics_sim.py`, `Telemetry`, `XPlaneConnector`, `test_ground_controller.py`, `test_refactoring_contracts.py`, `sft.py`, `VlaydRolloutBridge`, `fakes.py`, `ICSInputs`, `FakeConnector`, `test_full_flight.py`, `test_go_around.py`, `test_approach_criteria.py`, `RunwayTracker`, `test_dashboard.py`, `test_control_parity.py`, `on_ground`, `test_campaign.py`, `ics_sim.py`, `DatagramSocket`, `.__init__`, `RunReader`, `initial_segment`, `._approach_step`, `flight.py`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Why does `ICSSim` connect `ICSSim` to `on_ground`, `XPlaneConnector`, `test_refactoring_contracts.py`, `test_ics_sim.py`, `VlaydRolloutBridge`, `fakes.py`, `ICSInputs`, `ics_sim.py`, `test_sft_regressors.py`, `FakeConnector`, `HandshakeBench`, `test_full_flight.py`, `test_go_around.py`, `backend_factory.py`, `test_working_ics_golden.py`, `.enter_segment`, `.read_telemetry`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `ControllingSystem` (e.g. with `GroundToleranceReport` and `ToleranceReport`) actually correct?**
  _`ControllingSystem` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 28 inferred relationships involving `Telemetry` (e.g. with `ApproachController` and `ApproachResult`) actually correct?**
  _`Telemetry` has 28 INFERRED edges - model-reasoned connections that need verification._