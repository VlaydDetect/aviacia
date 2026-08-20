# Graph Report - GOSNIIASProject  (2026-08-19)

## Corpus Check
- 140 files · ~141,990 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2543 nodes · 5381 edges · 252 communities (131 shown, 121 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 312 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8ae083e7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_tolerance.py
- GainMap
- ndarray
- test_campaign.py
- ICSBenchConnector
- json_config.py
- SimInterface
- airborne_inputs
- Scenario
- GainKey
- Telemetry
- approach_limits
- float32
- test_sft_regressors.py
- test_ics_connector.py
- test_run_matrix.py
- AircraftProfile
- .from_ics
- ApproachResult
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
- channels.py
- RunRecorder
- flight.py
- Graphify Pipeline
- XPlaneConnector
- ControllingSystem
- test_ground_controller.py
- test_ics_engagement.py
- RunReader
- sft.py
- test_diagnostic_tools.py
- FlightPhase
- floating
- ICSInputs
- device
- 3. Этапы реализации
- .from_checkpoints
- test_profiled_scenarios.py
- Path
- _Clock
- test_go_around.py
- Hybrid Neural PID Controller
- test_approach_criteria.py
- test_full_flight.py
- run_artifacts.py
- RunwayTracker
- ICSSim
- ICSInputs
- test_dashboard.py
- pretrain.py
- .value
- ReferenceTrajectory
- Project Dependencies
- RunRecorder
- PidGainRegressor
- ICSInputs
- dashboard_core.py
- criticality.py
- test_working_ics_dashboard.py
- ICSOutputs
- .setup
- Unified Profile-Aware Scenario System
- Interactive PID Dashboard
- run_matrix.py
- test_weather.py
- RomanLogImporter
- ICSInterface.cs
- План исправления
- SftTrainConfig
- .save_candidate
- ICS PID Monitor
- run_report.py
- Autonomous Landing Controller
- X-Plane Dashboard and Runtime Guide
- test_working_ics_golden.py
- GainSpace
- promote_candidate.py
- scenarios.py
- import_workbook
- .replay
- LateralChannel
- pid.py
- test_control_parity.py
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
- .__init__
- Q: Приступай к выполнению этапа 9 плана docs/plan.md; упрощай код, удаляй лишнее и добавляй комментарии.
- Q: Реализовать этап 0: baseline, golden replay и dashboard characterization
- Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md).
- test_aileron_gains_are_negative_by_design
- ndarray
- engaged_sim
- Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md).
- FakeConnector
- ControlsState
- ControlModeState
- ICSInputs
- ICSOutputs
- socket
- IntEnum
- HandshakeBench
- AircraftProfile
- .compute
- .from_csv
- .from_ics
- Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md).
- Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md).
- control.py
- device
- int64
- .from_dict
- Q: Приступай к выполнению этапа 2 плана docs/plan.md
- ControlsState
- ClearWeatherILSController
- TypedDict
- system.py
- FailureMode
- RunwayProfile
- pid_controller.py
- ControlModeState
- ApproachChannel
- Scenario
- WeatherState
- FailureState
- StartMode
- Enum
- PidMap
- on_ground
- PidMap
- weather.py
- Normalization
- initial_segment
- Scenario
- Path
- Q: Приступай к выполнению этапа 4 плана docs/plan.md
- test_run_reader.py
- RewardWeights
- TypedDict
- ControlModeState
- .enter_segment
- telemetry_from_row
- RegulatorKey
- VlaydRolloutBridge
- Q: Приступай к выполнению этапа 8 плана [plan.md](docs/plan.md).
- ApproachLimits
- .from_dict
- ICSInputs
- PidMap
- ApproachTelemetry
- Any
- ArrayLike
- float32
- SimInterface
- NDArray
- ControllingSystem
- Tensor
- ApproachLimits
- Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md).
- ApproachTelemetry
- _FakeSocket
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
- Path
- PretrainConfig
- ToleranceReport
- RegulatorKey
- Tensor
- GainMap
- NDArray
- Tensor
- ics_engagement.py
- ArrayLike
- float32
- float64
- GainMap
- NDArray
- _faults_from_inputs
- ResilientSender
- GainSpace
- SimInterface
- aircraft_profiles.py
- SimInterface
- Linear
- Normal
- parametrize
- PPOMetrics
- .__init__
- RunResult
- RuntimeState
- GearState
- ScenarioProvider
- Sequential
- SFTDataset
- xplane.md
- sink_situation
- fixture
- detect_landing_flaps
- touched_down
- .reset_derivative
- RunSplit
- Q: Почему прогон runs/20260816T174009.095580Z раскачивает самолёт и не сохраняет паритет с working_ics по логу logs/ics_pid_20260816_104551.csv?
- Q: Проанализировать три неудачных production-прогона против working_ics и составить план исправления
- Q: Почему production-заход терял паритет с working_ics и как это исправлено?
- Q: Каков финальный результат исправления runtime-паритета 2026-08-16?
- Q: Проанализировать run 20260816T213847.114116Z, сравнить управление с working_ics и исправить уход по GLIDESLOPE и неисполняемый go-around.
- _legacy_reference
- test_adopts_rollout_from_the_flight_phase
- test_tracking_does_nothing_when_the_command_is_applied_as_computed
- test_conditional_anti_windup_still_allows_unwinding
- test_exact_leak_matches_the_closed_form_for_constant_error
- test_tracking_unwinds_the_integrator_when_the_actuator_is_dead
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
1. `ControllingSystem` - 129 edges
2. `Telemetry` - 104 edges
3. `ICSSim` - 72 edges
4. `ControlsState` - 57 edges
5. `XPlaneSim` - 54 edges
6. `airborne_inputs()` - 52 edges
7. `RunRecorder` - 50 edges
8. `PIDController` - 46 edges
9. `ICSInputs` - 45 edges
10. `Scenario` - 44 edges

## Surprising Connections (you probably didn't know these)
- `Autonomous Landing Controller` --semantically_similar_to--> `Autonomous Landing Controller`  [INFERRED] [semantically similar]
  CLAUDE.md → AGENTS.md
- `DatagramSocket` --uses--> `ApproachSetup`  [INFERRED]
  tests/test_xplane_backend.py → ismpu/config/scenarios.py
- `MockXPlaneConnector` --uses--> `ApproachSetup`  [INFERRED]
  tests/test_xplane_backend.py → ismpu/config/scenarios.py
- `ScriptedXPlaneConnector` --uses--> `ApproachSetup`  [INFERRED]
  tests/test_xplane_backend.py → ismpu/config/scenarios.py
- `DatagramSocket` --uses--> `TouchdownSetup`  [INFERRED]
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
- **PID Dashboard Ecosystem** — docs_xplane_dashboard_pid_dashboard, ismpu_gui_dashboard_pid_dashboard, ismpu_working_ics_ics_dashboard_ics_pid_monitor [INFERRED 0.85]

## Communities (252 total, 121 thin omitted)

### Community 0 - "test_tolerance.py"
Cohesion: 0.24
Nodes (16): ApproachResult, evaluate_approach_tolerances(), _glideslope_tolerance_deg(), FailureMode, Допуск по глиссаде с учётом отказа (ТЗ 5.1.2.1–5.1.2.3), самый мягкий из…, Проверить допуски захода по текущему такту. Команды не трогает. `result` —…, Допуски захода: классификаторы критичности (Приложение 1) и рантайм-монитор.…, 0.6° вне штатного допуска 0.5°, но в пределах допуска при отказе шасси (0.7°). (+8 more)

### Community 3 - "test_campaign.py"
Cohesion: 0.09
Nodes (47): campaign_phase(), campaign_rows(), campaign_summary(), _config_status(), main(), next_campaign_row(), Path, Порядок и фактический статус кампании из 280 матричных прогонов. (+39 more)

### Community 4 - "ICSBenchConnector"
Cohesion: 0.13
Nodes (10): ICSBenchConnector, Мост к стенду: JSON поверх UDP, адрес стенда определяется из входящего пакета., Подключить best-effort аудит сырых успешно принятых/отправленных UDP payload., Приём телеметрии стенда. Адрес отправителя определяется автоматически., Дождаться кадра и отбросить накопившийся UDP backlog, оставив самый свежий.…, Зафиксировать и разобрать один уже принятый UDP payload., Отправка управления на стенд. → отправлено ли (исключение наружу не…, Число последовательных best-effort ошибок текущего sender. (+2 more)

### Community 5 - "json_config.py"
Cohesion: 0.13
Nodes (36): approach_control_from_dict(), approach_control_to_dict(), _copy_approach(), dump_scenario(), _finite_tree(), ground_control_from_dict(), ground_control_to_dict(), _legacy_ground() (+28 more)

### Community 6 - "SimInterface"
Cohesion: 0.10
Nodes (5): BaseException, StartMode, Минимальный lifecycle, одинаковый для стенда и X-Plane., SimInterface, Protocol

### Community 7 - "airborne_inputs"
Cohesion: 0.12
Nodes (35): angle_error_deg(), Разность курсов, приведённая к (-180, 180]., airborne_inputs(), Кадр «ВС на глиссаде»: стойки не обжаты, ILS валиден, скорость и высота…, _our_channel(), Воздушный канал: заход по ILS, выравнивание, скоростной канал. Главный тест…, Угол сноса не должен превращаться в ошибку курса на локализаторе., Стенд иногда сбрасывает Valid при сохранении пригодного численного значения. (+27 more)

### Community 8 - "Scenario"
Cohesion: 0.12
Nodes (25): AircraftProfile, FailureMode, FlightSegment, _profile_name(), Оценить близость telemetry к preset; несовпадение отказа доминирует над погодой., Выбрать ближайший нематричный preset, не допуская draft без явного флага., Подобрать нематричный preset по валидной telemetry или безопасным defaults., Полный профильный сценарий APPROACH → ROLLOUT → TAXI. (+17 more)

### Community 10 - "Telemetry"
Cohesion: 0.07
Nodes (20): measured_landing_flaps(), Конфигурация по фактическому углу закрылков. `None` — положение не посадочное.…, _destination(), Телеметрия стенда, приведённая к **СИ**. Проверять надо `valid` **до** полей:…, Кадр «связи со стендом нет». Нули, а не None: контур проверяет `valid` первым., Невалидные ICS-сигналы, которые воздушный закон читает безусловно., Приборная скорость (kt → м/с). Отсечки реверса заданы по ней, а не по путевой., Радиовысота **в футах** — единицы стенда. Порог воздушного включения (400… (+12 more)

### Community 11 - "approach_limits"
Cohesion: 0.13
Nodes (16): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), LandingFlapConfiguration, _linear_interpolate(), Enum, str (+8 more)

### Community 13 - "test_sft_regressors.py"
Cohesion: 0.18
Nodes (13): feature_schema_hash(), GainGuard, Минимальная SFT-модель абсолютных коэффициентов PID и общий runtime guard., Стабильный hash порядка признаков; перестановка является сменой контракта., Проверяет prediction и ограничивает скорость изменения до записи в PID., _checkpoint(), ndarray, Path (+5 more)

### Community 14 - "test_ics_connector.py"
Cohesion: 0.19
Nodes (15): ICSOutputs, Команды и mode flags, сериализуемые ровно в ожидаемый стендом JSON., Сериализовать enums и 14 reserved zeros в точные UTF‑8 bytes wire contract., _connector(), _full_payload(), Транспорт стенда: разбор телеметрии и отправка команд. На проводе чистый JSON…, Стенд делает UTF8.GetString() → JsonConvert. Любые байты перед JSON сломали бы…, Windows отдаёт WSAECONNRESET на UDP, если получатель закрыл порт. Ронять цикл… (+7 more)

### Community 15 - "test_run_matrix.py"
Cohesion: 0.09
Nodes (24): Разрешить только полный ``<шифр>/<номер>`` и вернуть точную строку JSON., resolve_matrix_run(), compose_matrix_scenario(), _install_through_scenarios(), Сценарий по имени либо шифру матрицы, без различия раскладки А/B., Собрать сценарий из конкретных строк APPROACH/ROLLOUT/TAXI.…, Одна строка каталога → минимальный сценарий нужного участка или сквозной пары., Перенести накопленные overrides одного шифра на следующее условие этого же… (+16 more)

### Community 16 - "AircraftProfile"
Cohesion: 0.10
Nodes (10): AircraftProfile, clamp(), Преобразовать воздушные команды ICD в нормированные DataRef X-Plane., Преобразовать нормированные команды пробега в DataRef X-Plane., Расширение реестра будущим профилем МС-21 без правки XPlaneSim., Проводка и масштабы конкретного планера X-Plane., Общая идентичность ЛА и необязательная привязка к X-Plane. Профиль нужен и…, Command refs retained under the historical public name. (+2 more)

### Community 17 - ".from_ics"
Cohesion: 0.11
Nodes (20): `ICSInputs` → `Telemetry`: поля в СИ + «сырой» пакет для property. Стенд отдаёт…, engaged_inputs(), Кадр стенда, который уже принял управление: `AgentIsActive = 1`, идёт пробег., test_accepted_promotion_allows_fixed_row_specific_overrides(), «Козление» после касания снимает обжатие на секунду — назад в заход…, В такте касания команда обязана быть уже наземной, а не последней командой…, Таблицы захода МС-21 к чистому крылу неприменимы — вести по ним нельзя.…, Координаты захода не делают безопасным кадр с оставшимся INIT_CLIMB и взлётным… (+12 more)

### Community 18 - "ApproachResult"
Cohesion: 0.10
Nodes (29): ApproachLimits, ApproachTelemetry, Предел крена по высоте: чем ниже, тем меньше запас до касания законцовкой.…, roll_limit_deg(), ApproachController, ApproachResult, clamp(), ApproachConfig (+21 more)

### Community 19 - "DashboardServer"
Cohesion: 0.24
Nodes (5): DashboardServer, Loopback-only HTTP lifecycle вокруг одного ``DashboardState``., Фактически привязанные host/port, включая ephemeral port 0 в тестах., Идемпотентно запустить daemon HTTP thread., Отклонить pending tuning, остановить thread и закрыть listening socket.

### Community 20 - "test_icd_units.py"
Cohesion: 0.10
Nodes (19): Сверка каждого сигнала стенда с документами Заказчика. Два независимых…, Стенд шлёт узлы, футы, фут/мин и град/с — граница пересчёта в СИ проходит в…, 1 фут/мин = 0.3048/60 м/с. Приближение здесь копится на всём заходе., Нумерация фаз из doc-комментария `FlightPhase` в ICSInterface.cs., −26.5…55.0° — фактическое положение РУД во входной телеметрии, не команда., Наши константы обязаны совпадать с таблицей управляющих сигналов Заказчика., Тиллер задаётся ходом в миллиметрах. Отдельным тестом, потому что ошибка была…, 0–45 мм командует, 0–36.73 мм отчитывается. Подмена недодаёт ~18 % хода. (+11 more)

### Community 21 - "XPlaneSim"
Cohesion: 0.07
Nodes (15): ApproachSetup, AircraftProfile, ControlsState, FailureMode, FlightSegment, Path, RunwayProfile, Scenario (+7 more)

### Community 23 - "PIDController"
Cohesion: 0.12
Nodes (23): PIDController, Сброс внутренних состояний (используется при выключении системы)., test_pid_anti_windup_clamp(), test_pid_filtered_derivative(), test_pid_output_clamped_to_bounds(), test_pid_proportional_and_integral_accumulation(), test_pid_zero_dt_returns_zero(), Опциональная численность PID (шаг 5): каждый флаг проверяется на том дефекте,… (+15 more)

### Community 25 - "DashboardState"
Cohesion: 0.14
Nodes (9): _allocator_stage(), DashboardState, _first_present(), HTTP читает только immutable recorder objects; controller меняет control-thread., Стабильный execution id live/replay источника., Вернуть подписи всех девяти панелей в порядке HTML layout., Вернуть только новые recorder updates; смена run_id принудительно сбрасывает…, JSON-ready форма ``snapshot`` для ``GET /api/state``. (+1 more)

### Community 26 - "test_xplane_backend.py"
Cohesion: 0.09
Nodes (21): Детерминированно seeded шум/пропуски, применяемые только resettable backend., Скопировать канонический preset и заменить только запрошенные условия запуска., SensorNoise, test_xplane_ignores_failures_outside_rollout_contract(), DatagramSocket, MockXPlaneConnector, ScriptedXPlaneConnector, test_commands_failures_and_close_release_overrides() (+13 more)

### Community 27 - "test_ics_sim.py"
Cohesion: 0.06
Nodes (35): make_ics_inputs(), Полный пакет стенда: нули по умолчанию + заданные поля., Тесты стенда (`ICSSim`) и подбора сценария — без реального стенда., Неизвестный код — не повод предполагать сухую полосу., Погоду задаёт Заказчик; наш `WeatherState` — это прочитанный кадр, а не задание., До рукопожатия заявлять каналы нельзя: стенд ещё не разрешил нам ими управлять., Заявить канал, который не формируешь, — взять ответственность за неуправляемый…, 31 — единственная маска, с которой заход реально прошёл на стенде. Проверяется… (+27 more)

### Community 29 - "IcsEngagement"
Cohesion: 0.05
Nodes (27): EngagementInputs, IcsEngagement, Автомат включения. `step(inputs)` вызывается каждый такт до формирования…, Полный сброс — новый эпизод начинается с невключённого состояния., Подхватить уже включённый извне пробег: шлём `ControlMode = Rollout`.…, Войти в пробег самостоятельно: шлём `ControlMode = Rollout`. Это же — передача…, Перейти `Approach → Landing` без нового рукопожатия. Закон остаётся воздушным., Войти в заход самостоятельно: шлём `ControlMode = Approach`. Обычно вызывать не… (+19 more)

### Community 30 - "channels.py"
Cohesion: 0.11
Nodes (22): LateralDiagnostics, LongitudinalDiagnostics, Каналы управления и общий вектор команд. `ControlsState` — разделяемая по…, FailureManager, FailureMode, FailureState, Enum, Модель отказов бортового оборудования. `FailureState` хранит мультипликативные… (+14 more)

### Community 31 - "RunRecorder"
Cohesion: 0.09
Nodes (23): Exception, _csv_value(), default_runs_root(), _effective_configs(), _git_state(), _jsonable(), _matrix_rows(), _mode_for() (+15 more)

### Community 32 - "flight.py"
Cohesion: 0.06
Nodes (29): above_decision_height(), above_decision_velocity(), approach_blocker(), at_lateral_alignment_gate(), ils_blocker(), in_terminal_window(), Участки полёта и переходы между ними. Управление ведётся на всём интервале — от…, Последние футы перед касанием, где прерывать заход опаснее, чем доработать.… (+21 more)

### Community 33 - "Graphify Pipeline"
Cohesion: 0.08
Nodes (29): Folder Watcher, URL Ingestion, Extra Graph Exports, MCP Graph Server, Confidence Audit Trail, Deterministic Node IDs, Semantic Extraction Contract, Cross-Repository Graph Merge (+21 more)

### Community 34 - "XPlaneConnector"
Cohesion: 0.06
Nodes (22): DataRefSample, Атомарно снять все свежие значения без раскрытия внутреннего mutable cache., Discard pre-reload values so readiness cannot use stale telemetry., Повторять RREF requests до получения всех значений либо подробного timeout., Отправить один нативный 509-byte DREF packet., Последнее значение DataRef и monotonic timestamp его UDP-пакета., Отправить один нативный CMND packet., Перезагрузить текущий самолёт без открытия aircraft chooser. (+14 more)

### Community 35 - "ControllingSystem"
Cohesion: 0.07
Nodes (34): ControllingSystem, Связать сценарий с контуром; PID активируются после определения участка., Привести модель отказов к тому, что сообщает борт (`ICSInputs.Fault*`). Отказы…, Такт управления. → True, если управление окончено (или телеметрия невалидна).…, Разорвать D-history после пропуска устаревшей UDP-очереди, не трогая интегралы., Три блока: speed controller → guidance → allocator., Оркестратор классического контура поверх стенда (`envs.ics_sim.ICSSim`).…, Передать управление в руление (`ControlMode 3 → 4`) — пробег окончен.… (+26 more)

### Community 36 - "test_ground_controller.py"
Cohesion: 0.07
Nodes (36): Результат безусловного best-effort отключения backend., Причина остановки вместе с best-effort результатом освобождения backend., RunResult, ShutdownReport, cli(), _lost_engagement(), main(), Scenario (+28 more)

### Community 37 - "test_ics_engagement.py"
Cohesion: 0.10
Nodes (49): ControlModeState, Режим управления/индикации, передаваемый в каждом ICSOutputs., _Clock, _engine(), _pump(), Автомат включения управления на стенде. Два раздельных предмета проверки: *…, По ICD стенд должен два секунды ПОЛУЧАТЬ ModeAIReady=1. Если считать одно лишь…, Обратная защита: 30 кадров можно выпалить за 0.1 с — время тоже обязано пройти. (+41 more)

### Community 38 - "RunReader"
Cohesion: 0.14
Nodes (11): main(), _number(), _parse_cell(), Path, Типизированный поток новых и legacy-строк с синтетическими ID для старых CSV., Run-directory и любой поддержанный CSV через один streaming API., Нормализованные строки; отсутствующие P/D legacy-лога остаются ``None``., replay_run() (+3 more)

### Community 39 - "sft.py"
Cohesion: 0.13
Nodes (23): GuardResult, Фактически разрешённые gains и причина ограничений/fallback., apply_gain_vector(), controller_gain_vector(), _feature_value(), feature_vector(), gain_vector_from_row(), _number() (+15 more)

### Community 40 - "test_diagnostic_tools.py"
Cohesion: 0.20
Nodes (19): build_altitude_sweep(), command_for_pulse(), Безопасные elevator/altitude authority sweep без дублирования ICS runner., Чистое преобразование, пригодное и для dry-run, и для ICSSim., safety_reason(), SweepLimits, SweepPulse, validate_pulse() (+11 more)

### Community 41 - "FlightPhase"
Cohesion: 0.09
Nodes (18): IntEnum, FlightPhase, Фаза полёта, сообщаемая стендом (`ICSInputs.FlightPhase`)., flight_sim(), _integrate_throttle(), kinematic_sim(), KinematicBench, Ход рычага РУД за такт: интеграл команды-скорости, зажатый физическим… (+10 more)

### Community 43 - "ICSInputs"
Cohesion: 0.15
Nodes (23): ControlResult, ICSInputs, Неизвестные поля исходного JSON; они доступны аудиту, но не закону управления., Полная известная входная схема стенда; единицы определены в ``ICSInterface.cs``., airborne_control_mode(), airborne_flare_mode(), deactivate(), live_main() (+15 more)

### Community 45 - "3. Этапы реализации"
Cohesion: 0.09
Nodes (21): 1. Подтверждённые проблемы и целевое состояние, 2. Ключевые интерфейсы, 3. Этапы реализации, 4. Тестирование и критерии готовности, 5. Зафиксированные допущения, 6.1. Один dashboard вместо двух, 6.2. Единый источник данных, 6.3. Представления (+13 more)

### Community 46 - ".from_checkpoints"
Cohesion: 0.50
Nodes (4): checkpoint_metadata(), Path, Сформировать audit metadata загруженного файла, включая SHA-256 содержимого., Загрузить независимые air/ground slots и проверить activation evidence для ICS.

### Community 47 - "test_profiled_scenarios.py"
Cohesion: 0.28
Nodes (6): compose_scenario(), Собрать сценарий из независимых источников участков., Contracts of the unified aircraft-profiled scenario model., test_automatic_selection_never_falls_back_to_a_draft_profile_branch(), test_composition_keeps_repeated_failures_as_one_set_member(), test_composition_selects_each_phase_and_preserves_provenance()

### Community 49 - "_Clock"
Cohesion: 0.15
Nodes (19): _air(), _Clock, _pump(), Ниже 400 футов стенд управление не отдаёт — гнать туда стимул бессмысленно., Необъявленная радиовысота — «стенд не сообщил», а не «ноль футов». Иначе ВС в…, После касания режим меняется на пробег — но не раньше: смена режима на глиссаде…, Ниже 80 футов потеря `AgentIsActive` не повод бросать органы: до земли секунды., Окно только удерживает подтверждение. Само оно включения не даёт. (+11 more)

### Community 50 - "test_go_around.py"
Cohesion: 0.15
Nodes (25): _armed_controller(), _drive(), _frame(), Уход на второй круг (fallback в воздухе): условия срабатывания и передача…, На пробеге ухода нет — segment guard (козление удерживает защёлка сегмента,…, Если реверс уже включён — взлёт невозможен, ухода нет., Устойчивый набор (прирост высоты + положительная верт. скорость) завершает…, После установившегося набора цикл снимает заявку каналов (ControlMode=Off,… (+17 more)

### Community 51 - "Hybrid Neural PID Controller"
Cohesion: 0.70
Nodes (5): Hybrid Neural PID Controller, Neural PID Gain Scheduler, PPO Training Loop, Preset-Anchored Deterministic Shield, SFT Behavioral-Cloning Warm Start

### Community 52 - "test_approach_criteria.py"
Cohesion: 0.18
Nodes (12): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, Отдельный монитор критерия А.1.1 (не участвует в go-around)., Захватывает А.1.1 после входа в допуск и завершает оценку на 300 ft., frame() (+4 more)

### Community 53 - "test_full_flight.py"
Cohesion: 0.16
Nodes (16): IntFlag, ControlValid, Биты `ControlValidMask`: какие каналы несёт команда. **Один бит на одно…, _engaged_airborne_sim(), parametrize, Управление на всём интервале полёта: заход → касание → пробег → руление.…, (sim, conn), где стенд уже принял воздушное управление (`ControlMode =…, ТЗ 5.1.5: показатели выдерживания — отчёт, идущий вместе с командой. (+8 more)

### Community 54 - "run_artifacts.py"
Cohesion: 0.12
Nodes (21): Канонические участки управляемого интервала полёта., ApproachData, ControlDiagnostics, Enum, Общий контракт симулятора и воздушных сигналов. ICS и X-Plane различаются…, Исчерпывающие причины штатного/аварийного завершения единого runtime loop., Снимок готовности resettable backend для recorder/dashboard., Backend-neutral диагностические значения текущего управляющего такта. (+13 more)

### Community 55 - "RunwayTracker"
Cohesion: 0.08
Nodes (22): find_earth_nav_dat(), ILSStation, parse_ils_station(), Path, Точка на продолжении оси; положительное расстояние — до порога., Найти LOC (тип 4) без хардкода частоты., RunwayProfile, GuidanceState (+14 more)

### Community 56 - "ICSSim"
Cohesion: 0.10
Nodes (11): ICSSim, FailureMode, SimInterface, Обмен со стендом заказчика: телеметрия внутрь, команды наружу. Управление…, Принимает ли стенд наши команды. До включения любой `step` уходит вхолостую., Сколько устаревших UDP-кадров сброшено при последнем чтении., Войти в пробег самостоятельно (`ControlMode 0 → 3`)., Перейти `Approach → Landing`; сессия и воздушные каналы сохраняются. (+3 more)

### Community 57 - "ICSInputs"
Cohesion: 0.12
Nodes (15): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, ICSInputs, Evaluate the A.1.1 approach segment and stop at a radio-altitude floor., Exact package port of the ICS approach contour validated in ``aviacia_v2``. The… (+7 more)

### Community 58 - "test_dashboard.py"
Cohesion: 0.20
Nodes (13): _live(), _post(), parametrize, test_active_pid_is_editable_in_classical_and_shadow(), test_gain_change_is_queued_bumpless_and_records_full_event(), test_http_api_is_incremental_pending_and_loopback_only(), test_incremental_snapshot_uses_recorder_objects_and_stays_small_when_idle(), test_live_and_replay_use_the_same_dashboard_snapshot() (+5 more)

### Community 59 - "pretrain.py"
Cohesion: 0.10
Nodes (35): _condition_key(), _fit_feature_normalization(), load_offline_dataset(), _normalized_mse(), _physical_bounds(), _predict(), ndarray, Path (+27 more)

### Community 60 - ".value"
Cohesion: 0.13
Nodes (9): _finite(), GainChange, _jsonable(), Проверить HTTP-запрос и поставить полный PID triplet в control-thread queue., Поставить восстановление gains начала запуска для активного участка., Вызывается runtime ровно в начале control tick., Закрыть tuning и записать отказ для каждого неисполненного запроса., Immutable запрос HTTP-thread, ожидающий применения control-thread. (+1 more)

### Community 61 - "ReferenceTrajectory"
Cohesion: 0.19
Nodes (8): Генератор эталонной кривой скорости (Колокол Гаусса)., Начать профиль с фактической скорости текущего участка., То же без лишнего round-trip м/с → узлы → м/с на касании., Возвращает идеальную скорость (м/с) для текущей точки пути., ReferenceTrajectory, TrajectoryState, test_equally_slow_law_endpoints(), test_gauss_bell_endpoints_and_monotonicity()

### Community 62 - "Project Dependencies"
Cohesion: 0.29
Nodes (7): Optional Gymnasium, NumPy, Pandas, Project Dependencies, Pytest, Termcolor, Optional PyTorch

### Community 64 - "PidGainRegressor"
Cohesion: 0.12
Nodes (15): device, PidGainRegressor, Any, Предсказать gains по последнему hidden state окна ``(B,T,F)``., Сохранить веса вместе с полным train↔runtime контрактом., Загрузить модель только после проверки полного train↔runtime контракта., Краткая форма ``load_checkpoint`` для потребителя, которому не нужна metadata., Восстановить и строго проверить normalization из checkpoint. (+7 more)

### Community 66 - "dashboard_core.py"
Cohesion: 0.16
Nodes (11): DashboardSnapshot, main(), _mean(), Один локальный dashboard для live RunRecorder и read-only replay., Запустить локальный read-only replay dashboard до ``Ctrl+C``., Отображаемое имя, PID source и физическая фаза одной панели графика., Инкремент после sequence cursor и редкие metadata при reset., Преобразовать tuples в JSON arrays, не добавляя отсутствующие тяжёлые секции. (+3 more)

### Community 67 - "criticality.py"
Cohesion: 0.11
Nodes (22): lateral_limit_m(), lateral_load_situation(), lateral_situation(), normal_load_situation(), IntEnum, Критерии критичности особых ситуаций МС-21 (Приложение 1 к ТЗ). Таблица АП-25…, Классификация скорости касания относительно VAPP и VВПП пред., Классификация нормальной перегрузки посадочного удара. `heavy` — взлётный вес. (+14 more)

### Community 68 - "test_working_ics_dashboard.py"
Cohesion: 0.35
Nodes (10): ClearWeatherILSController, DashboardState, _controller(), _inputs(), Characterization tests for the bench-validated ``working_ics`` dashboard., _record(), test_dashboard_records_four_airborne_views_and_diagnostics(), test_gain_updates_are_immediate_validated_and_share_pitch_with_flare() (+2 more)

### Community 70 - ".setup"
Cohesion: 0.25
Nodes (6): CompletionRule, LongitudinalChannel, Блок 1: скорость → симметричная база тормозов и реверса., Сбросить PID и привязать начало профиля к фактической скорости касания/старта., PidMap, VelocityLaw

### Community 71 - "Unified Profile-Aware Scenario System"
Cohesion: 0.33
Nodes (6): Technical-Specification Acceptance Gates, Forward-Only Flight Segment Supervisor, Longitudinal and Lateral Ground Channels, PID Run Matrix, Unified Profile-Aware Scenario System, Legacy Scenario Preset Model

### Community 72 - "Interactive PID Dashboard"
Cohesion: 0.25
Nodes (9): Nine-View PID Dashboard, Run Recording Artifacts, buildTabs, draw, Gain Tuning and Snapshot Export, Interactive PID Dashboard, refresh, render (+1 more)

### Community 73 - "run_matrix.py"
Cohesion: 0.05
Nodes (20): MatrixCase, MatrixCondition, MatrixRun, normalize_code(), _number(), Any, FailureMode, FlightSegment (+12 more)

### Community 74 - "test_weather.py"
Cohesion: 0.18
Nodes (13): compose_wind(), decompose_wind(), (скорость, откуда) → (crosswind, headwind) относительно курса ВПП. crosswind >…, (crosswind, headwind) → (скорость, откуда, °). Обратна `decompose_wind`., Тесты погоды: разбор ветра, шкала скользкости и чтение условий из пакета стенда., Для пробега существенна боковая составляющая, а не «скорость ветра» сама по…, Все семь кодов из фактических пакетов закрыты явно., test_crosswind_from_right_is_perpendicular() (+5 more)

### Community 75 - "RomanLogImporter"
Cohesion: 0.19
Nodes (10): _number(), Path, Импорт и проверка внешних CSV-прогонов roman_aviacia_ics., Потоково нормализует основной и authority CSV Романа., RomanLogImporter, verify_manifest(), fixture, roman_csv() (+2 more)

### Community 76 - "ICSInterface.cs"
Cohesion: 0.36
Nodes (7): External.Systems.ICS, ControlModeState, GearState, ICSInputs, ICSOutputs, ReverseEngineType, UInt64

### Community 77 - "План исправления"
Cohesion: 0.12
Nodes (15): 1. Handshake не повторяет рабочую последовательность, 2. Runtime работает с другой частотой и другой топологией, 3. RunRecorder находится в управляющем потоке, 4. Go-around имеет две отдельные ошибки, 5. Production entrypoint сейчас загрязнён debug-путём, ElevatorCmd действительно отправлялся, Найденные причины, План исправления (+7 more)

### Community 78 - "SftTrainConfig"
Cohesion: 0.22
Nodes (10): cli(), PretrainRunConfig, Последовательно обучить выбранные участки из одного каталога принятых прогонов., CLI офлайн-обучения; сеть никогда не открывает UDP и не сбрасывает X-Plane., Численные параметры одного воспроизводимого запуска обучения., Пути и участки для CLI, обучающего независимые air/ground checkpoints., Итог обучения участка и данные, необходимые для автоматической проверки gate., run_pretrain() (+2 more)

### Community 79 - ".save_candidate"
Cohesion: 0.32
Nodes (5): _load_updates(), RunReader, После recorder.finish держать полный run доступным, но только для чтения., Сохранить фактически записанный effective config, не изменяя SCENARIOS., RunEvent

### Community 80 - "ICS PID Monitor"
Cohesion: 0.22
Nodes (9): Bench-Validated ILS Approach Channel, Tolerance-Gated Go-Around, buildControls, draw, formatTime, Four-Loop PID Tuning, ICS PID Monitor, Live and Historical Timeline (+1 more)

### Community 81 - "run_report.py"
Cohesion: 0.18
Nodes (23): _accepted_segments(), _approach_runway_heading_error(), build_run_report(), _environment_diagnostics(), _handover_ratio(), _matrix_results(), _max_abs(), _metrics() (+15 more)

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
Nodes (29): ConditionMatch, ControlProfile, _copy_approach(), _copy_ground(), _ground_matrix_drafts(), _ground_segments_for_spec(), _GroundPresetSpec, _install_approach_scenarios() (+21 more)

### Community 88 - "import_workbook"
Cohesion: 0.33
Nodes (9): import_workbook(), main(), Any, Path, Одноразовый импорт исходной Excel-матрицы в runtime-каталог JSON., Прочитать книгу целиком; функция не используется production runtime., _scalar(), write_catalog() (+1 more)

### Community 89 - ".replay"
Cohesion: 0.14
Nodes (10): FlightSegment, Enum, str, Участок, для которого выбираются закон управления и условия сценария., _equal(), ControllingSystem, Пересчитать команды без backend/UDP и сверить каждый записанный такт., ReplayMismatch (+2 more)

### Community 90 - "LateralChannel"
Cohesion: 0.27
Nodes (6): GuidanceState, LateralChannel, Блок 2: runway guidance → единый нормированный yaw-запрос., Путевой угол на пробеге, курс фюзеляжа на малой скорости. При стремящейся к…, Guidance по тому, что даёт стенд. → словарь guidance или None, если данных нет.…, Вернуть тот же ``GuidanceState``, который использует управляющий такт и…

### Community 91 - "pid.py"
Cohesion: 0.29
Nodes (4): Типы и порядок коэффициентов пяти наземных PID-регуляторов. Модуль намеренно не…, PIDDiagnostics, Пропорционально-интегрально-дифференциальный регулятор. Класс сохраняет прежнюю…, Типизированный снимок последнего такта регулятора.

### Community 92 - "test_control_parity.py"
Cohesion: 0.13
Nodes (20): CompletionRule, Enum, Генератор эталонной кривой скорости пробега. Два закона замедления: колокол…, Как активный наземный сценарий заканчивает управление., VelocityLaw, str, decode_outputs(), `ICSOutputs` → (brake_l, brake_r, thr_l_rate, thr_r_rate, steer), всё… (+12 more)

### Community 93 - ".read_telemetry"
Cohesion: 0.10
Nodes (16): ControlsState, EngagementInputs, ICSOutputs, _clamp(), Начало эпизода: сброс рукопожатия и первый кадр со стенда. Средой распоряжается…, Отправить команду без скрытого чтения следующего RX-кадра., Гонит стимул рукопожатия, пока стенд не подтвердит включение (`AgentIsActive =…, Желаемый уровень реверса [-1, 0] → скорость перемещения РУД (°/с). Тягой (в том… (+8 more)

### Community 95 - "Q: Приступай к выполнению этапа 9 плана [plan.md](docs/plan.md). В процессе старайся упрощать код, удалять лишний и неиспользуемый код, а также максимально покрывать его комментариями."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 9 плана [plan.md](docs/plan.md). В процессе старайся упрощать код, удалять лишний и неиспользуемый код, а также максимально покрывать его комментариями., Source Nodes

### Community 109 - ".__init__"
Cohesion: 0.15
Nodes (9): Any, ApproachConfig, ApproachController, _materialize_override(), Применить одноуровневый sparse patch и вернуть полный неизменяемый config., Материализовать базовую ветку и sparse override выбранной строки., Serialize only the canonical profile- and matrix-aware schema v3., SimInterface (+1 more)

### Community 110 - "Q: Приступай к выполнению этапа 9 плана docs/plan.md; упрощай код, удаляй лишнее и добавляй комментарии."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 9 плана docs/plan.md; упрощай код, удаляй лишнее и добавляй комментарии., Source Nodes

### Community 111 - "Q: Реализовать этап 0: baseline, golden replay и dashboard characterization"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Реализовать этап 0: baseline, golden replay и dashboard characterization, Source Nodes

### Community 112 - "Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md)., Source Nodes

### Community 113 - "test_aileron_gains_are_negative_by_design"
Cohesion: 0.20
Nodes (9): ApproachConfig, _pid_from_colleague(), Загрузка настроек из JSON коллеги (`config/ics_clear_weather_pid.json`). Секции…, `PIDConfig` коллеги → аргументы нашего `PIDController`. Предел интегратора у…, Параметры воздушного контура. Значения по умолчанию — настроенные на стенде.…, Крен парируется элеронами с обратным знаком — это проводка стенда, а не…, Наши умолчания и его файл — одно и то же. Разойдутся — расхождение должно быть…, test_aileron_gains_are_negative_by_design() (+1 more)

### Community 115 - "engaged_sim"
Cohesion: 0.12
Nodes (16): engaged_sim(), (sim, connector) с завершённым рукопожатием: стенд подтвердил `AgentIsActive =…, Регресс: расширение структуры не должно протащить руль высоты в маску пробега., test_ground_frame_still_declares_only_the_ground_channels(), Разделение органов из таблицы Заказчика: тиллер — на рулении, педальный пост —…, Базовый контур на стенде: `control_step` сам читает телеметрию и сам отправляет., На стенде каждый лишний `read_telemetry` — лишний приём UDP. Каждый такт явно…, Замолчать нельзя: последнее отклонение осталось бы приложенным до сторожа на… (+8 more)

### Community 116 - "Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)., Source Nodes

### Community 117 - "FakeConnector"
Cohesion: 0.17
Nodes (7): FakeConnector, Статический стенд: всегда один и тот же кадр, отправленное — в `sent_outputs`., Отправленные команды в нормированном виде — для сравнения траекторий.…, test_read_telemetry_invalid_on_timeout(), test_weather_is_none_without_a_bench_packet(), test_ics_shutdown_is_idempotent_and_releases_every_channel(), test_runtime_predicts_each_tick_after_40_frames_and_falls_back_before_it()

### Community 118 - "ControlsState"
Cohesion: 0.11
Nodes (19): ControlsState, Обнуляет все органы управления. Отправку делает вызывающий через `ICSSim.step`.…, Совместимое имя старого API; колёсные органы оно больше не обозначает., Разделяемая по тактам структура команд — и наземных, и воздушных. Аннотации…, Сброс к нейтральным командам — новый эпизод начинается с чистого состояния.…, Обнулить только воздушные команды. Нужно, когда воздушный канал не может…, setter, _colleague_controller() (+11 more)

### Community 124 - "HandshakeBench"
Cohesion: 0.12
Nodes (13): HandshakeBench, Стенд, включающий управление только после корректного рукопожатия. Ждёт…, Стенд включается по полученной готовности, а не по нашему представлению о ней., Не ждать десять секунд и не принимать управление уже набирающим самолётом., test_airborne_handshake_stops_before_approach_if_takeoff_phase_appears(), test_the_airborne_handshake_is_actually_transmitted_before_approach(), _cold_sim(), Сквозной прогрев: маска нулевая, пока стенд не подтвердил `AgentIsActive = 1`. (+5 more)

### Community 126 - ".compute"
Cohesion: 0.18
Nodes (5): → (интеграл только с утечкой, интеграл с утечкой и приращением). Оба уже зажаты., Такт регулятора. `measurement` обязателен при `derivative_on_measurement=True`., Back-calculation: подтянуть интегратор к фактически применённой команде. No-op…, Сменить коэффициенты без сброса D-history и с компенсацией интегратором.…, Вес апериодического фильтра D-составляющей за такт `dt`.

### Community 127 - ".from_csv"
Cohesion: 0.22
Nodes (7): _gain_ranges(), _gains_from_manifest(), _gains_from_samples(), _handler_factory(), Path, Построить read-only state из run-directory либо поддерживаемого CSV., Build safe dashboard sliders from the scenarios users can actually run. The…

### Community 128 - ".from_ics"
Cohesion: 0.25
Nodes (6): Фактические погодные условия со стенда (ветер, сцепление, осадки, видимость)., `ICSInputs` → `WeatherState`. Единственный источник фактической погоды. Стенд…, `Visibility` в футах. Без пересчёта 16000 футов читались бы как «ясно» вместо…, test_visibility_is_converted_from_feet(), Стенд шлёт узлы и **футы**; в WeatherState видимость — в метрах., test_from_ics_converts_units()

### Community 129 - "Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md)., Source Nodes

### Community 130 - "Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md)., Source Nodes

### Community 131 - "control.py"
Cohesion: 0.36
Nodes (5): Полностью пересобрать наземные каналы controller этой конфигурацией., apply_ground_control(), build_pids(), Сборка классического контура из неизменяемой конфигурации., Фабрики stateful-объектов; config-модули хранят только данные.

### Community 134 - ".from_dict"
Cohesion: 0.17
Nodes (10): Прочитать schema v3 либо явно мигрируемую v1/v2 конфигурацию., Any, Погодные условия. Поля — ровно то, что сообщает стенд (см. `from_ics`).…, Собирает ветер из компонент относительно курса ВПП. `crosswind_kts` > 0 — ветер…, Сериализация в примитивы (для логирования/воспроизводимости сценариев)., WeatherState, test_scenario_roundtrip_with_weather_and_failures(), test_external_profile_controls_survive_scenario_v2_roundtrip() (+2 more)

### Community 135 - "Q: Приступай к выполнению этапа 2 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 2 плана docs/plan.md, Source Nodes

### Community 137 - "ClearWeatherILSController"
Cohesion: 0.16
Nodes (8): DashboardServer, DashboardState, Any, ICSInputs, ClearWeatherILSController, ControlResult, test_roundout_commands_a_material_pitch_increase_before_touchdown(), test_terminal_pitch_hold_starts_before_last_five_feet_guidance_cutoff()

### Community 139 - "system.py"
Cohesion: 0.08
Nodes (31): Настройки воздушного участка: заход по ILS, выравнивание, управление скоростью.…, Глобальные константы контура управления (перенесены из main.ipynb)., Эксплуатационные ограничения захода и посадки (МС-21). Перенесено из…, Константы интерфейса стенда заказчика (ПИВ / ICS). Единый источник правды по…, Приёмочные пороги из ТЗ (раздел 5). Единый источник истины для runtime…, Профили ВПП и разрешение ILS из установленной базы X-Plane., Геометрия целевой ВПП и высоты установки ЛА. Смена целевой полосы = правка…, Воздушный канал: заход по ILS, выравнивание, управление скоростью. Перенос… (+23 more)

### Community 142 - "pid_controller.py"
Cohesion: 0.14
Nodes (20): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+12 more)

### Community 151 - "on_ground"
Cohesion: 0.20
Nodes (10): on_ground(), Кадр «ВС на полосе»: обжаты все стойки, курс/координаты у порога UUEE 06R., Пресет — стартовое предположение; фактическую конфигурацию сообщает борт., Отказ может быть снят — накапливающий учёт держал бы орган мёртвым до конца…, Единичный таймаут — не повод вернуть рулю авторитет, которого у него нет., test_controller_takes_failures_from_the_bench_not_from_the_preset(), test_failures_are_cleared_when_the_bench_stops_reporting_them(), test_ics_requires_profile_and_records_nonfatal_transition_mismatch() (+2 more)

### Community 153 - "weather.py"
Cohesion: 0.18
Nodes (12): Enum, Погодные условия эпизода: описание, шкала сцепления и разбор ветра. Модуль **не…, Состояние ВПП как **монотонная шкала скользкости** 0…15 (0 — сухо, 15 — лёд со…, Код состояния ВПП со стенда → наша шкала. Неизвестный код трактуется как `ICY`,…, runway_condition_from_bench(), RunwayCondition, Коды из фактических пакетов переводятся в свою шкалу скользкости., test_runway_condition_codes_are_remapped_not_passed_through() (+4 more)

### Community 154 - "Normalization"
Cohesion: 0.10
Nodes (17): ArrayLike, Dataset, float32, float64, Normalization, NDArray, Выполнить deterministic inference и вернуть физические gains плюс OOD flag., Проверить prediction и ограничить его относительно accepted preset/предыдущего… (+9 more)

### Community 155 - "initial_segment"
Cohesion: 0.28
Nodes (9): initial_segment(), is_airborne(), FlightSegment, Сообщает ли стенд, что ВС в воздухе и достаточно высоко для приёма захода.…, С какого участка начинать. Пробег — ответ по умолчанию (см. модуль)., Синтетический кадр — «нечем судить», а не «в воздухе». На таких кадрах работают…, test_a_frame_without_a_bench_packet_is_never_airborne(), test_airborne_frame_starts_on_the_approach() (+1 more)

### Community 158 - "Q: Приступай к выполнению этапа 4 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 4 плана docs/plan.md, Source Nodes

### Community 159 - "test_run_reader.py"
Cohesion: 0.33
Nodes (8): aggregate_matrix_results(), main(), Собрать последние результаты выбранных строк в CSV с колонками исходной книги., _frame(), _record_ground_run(), test_report_contains_matrix_metrics_and_aggregation_uses_workbook_columns(), test_report_exposes_go_around_command_to_feedback_metrics(), test_run_reader_streams_samples_events_and_replays_controller()

### Community 162 - "ControlModeState"
Cohesion: 0.40
Nodes (3): ControlModeState, Сообщить автомату, что кадр **фактически ушёл** на стенд. Вызывается…, Значение `ControlMode` для исходящей команды (стимул). Во время выдержки —…

### Community 163 - ".enter_segment"
Cohesion: 0.40
Nodes (4): ConditionMatch, FlightSegment, Сверить ожидаемые условия; стендовые условия никогда не изменяются кодом., Scenario

### Community 164 - "telemetry_from_row"
Cohesion: 0.22
Nodes (8): ICSBenchConnector, IcsEngagement, _bool_or_none(), Восстановить входной кадр: raw ICS приоритетен, иначе SI/backend-neutral slice., _runway_profile_from_row(), telemetry_from_row(), RunwayProfile, Telemetry

### Community 166 - "VlaydRolloutBridge"
Cohesion: 0.33
Nodes (6): ICSInputs, Hand the validated airborne session to Vlayd's existing rollout loop. The…, Keep Vlayd's engagement latch synchronized during the approach., Run Vlayd's rollout until taxi speed, then send its taxi handoff., VlaydRolloutBridge, test_rollout_bridge_preserves_engagement_and_switches_without_off()

### Community 167 - "Q: Приступай к выполнению этапа 8 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 8 плана [plan.md](docs/plan.md)., Source Nodes

### Community 169 - ".from_dict"
Cohesion: 0.29
Nodes (6): Разбор телеметрии стенда с совместимостью вперёд. Асимметрия намеренная (JSON-…, Подставить ноль значило бы выдумать телеметрию, по которой считается управление., Новый сигнал не роняет разбор и не входит в закон, но не теряется для записи., test_missing_fields_raise_instead_of_defaulting_to_zero(), test_parses_a_complete_payload(), test_unknown_fields_are_preserved_for_audit_but_not_exposed_as_signals()

### Community 181 - "Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md)., Source Nodes

### Community 202 - "ics_engagement.py"
Cohesion: 0.50
Nodes (4): Enum, EngagementState, Автомат включения управления на стенде заказчика. Стенд принимает наши команды…, Состояние **исходящего стимула** (что мы шлём стенду), а не факта включения.…

### Community 208 - "_faults_from_inputs"
Cohesion: 0.40
Nodes (4): ICSInputs, _faults_from_inputs(), Отказы, о которых сообщает борт — **единственный** источник истины об отказах.…, Сигналы отказов со стенда → наши `FailureMode`. Отказы шасси…

### Community 209 - "ResilientSender"
Cohesion: 0.33
Nodes (3): Отправка best-effort со счётчиком ошибок и разрежённым логом. Windows отдаёт…, → True если отправлено. Исключение наружу не выпускается., ResilientSender

### Community 212 - "aircraft_profiles.py"
Cohesion: 0.21
Nodes (9): get_aircraft_profile(), Профили преобразования команд ИСМПУ в органы управления X-Plane., get_runway_profile(), build_sim(), Any, Path, Единая фабрика backend: ICS по умолчанию, X-Plane явно., Создать backend; для ICS геодезия включается только явным ``runway_profile``. (+1 more)

### Community 218 - ".__init__"
Cohesion: 0.40
Nodes (3): PIDController, ReferenceTrajectory, RunwayTracker

### Community 221 - "GearState"
Cohesion: 0.40
Nodes (5): GearState, IntEnum, Дискретное положение стойки в кодировке ICSInputs., Состояние створок реверса; величину задаёт отрицательный throttle rate., ReverseEngineType

### Community 226 - "sink_situation"
Cohesion: 0.50
Nodes (4): Классификация вертикальной скорости касания. `heavy` — взлётный вес 69100–79250…, sink_situation(), Пороги вертикальной скорости касания 472 / 600 / 736 fpm (посадочный вес)., test_sink_situation_bands()

### Community 228 - "detect_landing_flaps"
Cohesion: 0.50
Nodes (4): detect_landing_flaps(), Конфигурация по углу закрылков, с запасным вариантом для расчёта ограничений., Непосадочное положение — это `None`, а не молчаливая подмена предположением., test_landing_flap_detection_reports_a_non_landing_configuration()

### Community 229 - "touched_down"
Cohesion: 0.50
Nodes (4): Окончен ли воздушный участок. Два независимых признака, любой достаточен:…, touched_down(), Носовая стойка обжимается позже основных — ждать её значит пропустить начало…, test_touchdown_is_any_main_gear_not_the_nose()

### Community 231 - "RunSplit"
Cohesion: 0.50
Nodes (3): Разбиение по целым прогонам; один ``run_id`` встречается ровно в одной части., Сериализовать membership split для checkpoint-аудита и leakage-проверки., RunSplit

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

### Community 237 - "_legacy_reference"
Cohesion: 0.67
Nodes (3): _legacy_reference(), Независимая реализация ПРЕЖНЕЙ численности — эталон для проверки парити., test_defaults_reproduce_the_legacy_numerics_bit_for_bit()

## Ambiguous Edges - Review These
- `Unified Profile-Aware Scenario System` → `Legacy Scenario Preset Model`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to
- `Dual-Backend SimInterface` → `ICS-Only Backend Guidance`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **111 isolated node(s):** `ismpu`, `Answer`, `Outcome`, `Source Nodes`, `Answer` (+106 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **121 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `MatrixRun` (3× useful, score=2.78338871)
- `XPlaneSim` (3× useful, score=2.770714328)
- `PidGainRegressor` (2× useful, score=1.857562533)
- `rollout_bridge.py` (2× useful, score=1.857562533)
- `loop.py` (2× useful, score=1.837722393)
- `LateralChannel` (2× useful, score=1.803125046)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Unified Profile-Aware Scenario System` and `Legacy Scenario Preset Model`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Dual-Backend SimInterface` and `ICS-Only Backend Guidance`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Telemetry` connect `Telemetry` to `.from_ics`, `test_tolerance.py`, `airborne_inputs`, `system.py`, `.from_ics`, `ApproachResult`, `test_icd_units.py`, `XPlaneSim`, `test_ics_sim.py`, `channels.py`, `test_run_reader.py`, `flight.py`, `ControllingSystem`, `.enter_segment`, `test_ground_controller.py`, `VlaydRolloutBridge`, `test_diagnostic_tools.py`, `FlightPhase`, `_Clock`, `test_go_around.py`, `test_approach_criteria.py`, `test_full_flight.py`, `run_artifacts.py`, `.setup`, `_faults_from_inputs`, `test_working_ics_golden.py`, `LateralChannel`, `test_control_parity.py`, `.read_telemetry`, `FakeConnector`, `ControlsState`, `HandshakeBench`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._
- **Why does `ControllingSystem` connect `ControllingSystem` to `control.py`, `Telemetry`, `system.py`, `test_sft_regressors.py`, `test_run_matrix.py`, `.from_ics`, `on_ground`, `test_xplane_backend.py`, `test_ics_sim.py`, `test_run_reader.py`, `flight.py`, `XPlaneConnector`, `test_ground_controller.py`, `VlaydRolloutBridge`, `RunReader`, `sft.py`, `FlightPhase`, `test_go_around.py`, `test_approach_criteria.py`, `test_full_flight.py`, `test_dashboard.py`, `.setup`, `test_control_parity.py`, `.__init__`, `engaged_sim`, `FakeConnector`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Why does `ICSInputs` connect `ICSInputs` to `ICSBenchConnector`, `.from_dict`, `airborne_inputs`, `system.py`, `test_ics_connector.py`, `.from_ics`, `ApproachResult`, `DashboardServer`, `on_ground`, `weather.py`, `DashboardState`, `test_ics_sim.py`, `RunRecorder`, `ControllingSystem`, `VlaydRolloutBridge`, `.from_dict`, `FlightPhase`, `run_artifacts.py`, `_FakeSocket`, `.value`, `dashboard_core.py`, `test_working_ics_dashboard.py`, `run_matrix.py`, `FakeConnector`, `HandshakeBench`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `ControllingSystem` (e.g. with `ApproachRefused` and `ToleranceReport`) actually correct?**
  _`ControllingSystem` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `Telemetry` (e.g. with `ApproachController` and `ApproachResult`) actually correct?**
  _`Telemetry` has 31 INFERRED edges - model-reasoned connections that need verification._