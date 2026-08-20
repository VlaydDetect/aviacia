# Graph Report - GOSNIIASProject  (2026-08-20)

## Corpus Check
- 140 files · ~141,940 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2543 nodes · 5375 edges · 238 communities (121 shown, 117 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 311 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3edda271`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- RunRecorder
- GainMap
- ndarray
- test_evaluate.py
- rollout_bridge.py
- json_config.py
- SimInterface
- ControlsState
- Scenario
- GainKey
- Telemetry
- test_approach_channel.py
- float32
- test_sft_regressors.py
- ics_connector.py
- test_run_matrix.py
- AircraftProfile
- test_full_flight.py
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
- failures.py
- ._fail
- flight.py
- Graphify Pipeline
- XPlaneConnector
- ControllingSystem
- loop.py
- test_ics_engagement.py
- run_reader.py
- sft.py
- test_diagnostic_tools.py
- fakes.py
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
- run_artifacts.py
- sim_interface.py
- RunwayTracker
- ICSSim
- ICSInputs
- test_dashboard.py
- pretrain.py
- GainChange
- test_control_parity.py
- Project Dependencies
- main
- PidGainRegressor
- ICSInputs
- dashboard_core.py
- test_tolerance.py
- test_working_ics_dashboard.py
- ICSOutputs
- test_campaign.py
- Unified Profile-Aware Scenario System
- Interactive PID Dashboard
- run_matrix.py
- test_weather.py
- RomanLogImporter
- ICSInterface.cs
- План исправления
- SftTrainConfig
- .snapshot
- ICS PID Monitor
- run_report.py
- Autonomous Landing Controller
- X-Plane Dashboard and Runtime Guide
- test_working_ics_golden.py
- GainSpace
- promote_candidate.py
- scenarios.py
- import_workbook
- segments.py
- LateralChannel
- PIDDiagnostics
- MatrixCase
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
- ApproachConfig
- ndarray
- .neutralize_airborne
- Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md).
- ConditionMatch
- _descent_frames
- ControlModeState
- ICSInputs
- ICSOutputs
- socket
- IntEnum
- ._should_go_around
- AircraftProfile
- .compute
- .from_csv
- .from_ics
- Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md).
- Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md).
- control.py
- device
- int64
- WeatherState
- Q: Приступай к выполнению этапа 2 плана docs/plan.md
- ControlsState
- DashboardState
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
- GuidanceState
- PidMap
- weather.py
- Normalization
- .__init__
- Scenario
- Path
- Q: Приступай к выполнению этапа 4 плана docs/plan.md
- .reset
- RewardWeights
- TypedDict
- ControlModeState
- .teleport_approach
- RunSample
- RegulatorKey
- test_refactoring_contracts.py
- Q: Приступай к выполнению этапа 8 плана [plan.md](docs/plan.md).
- ApproachLimits
- FrictionProfile
- ICSInputs
- PidMap
- ApproachTelemetry
- Any
- ArrayLike
- float32
- test_localizer_deflection_turns_the_aircraft_back_to_the_centreline
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
- GainSpace
- SimInterface
- runway_profiles.py
- SimInterface
- Linear
- Normal
- parametrize
- PPOMetrics
- RuntimeState
- ScenarioProvider
- Sequential
- SFTDataset
- xplane.md
- fixture
- RunSplit
- Q: Почему прогон runs/20260816T174009.095580Z раскачивает самолёт и не сохраняет паритет с working_ics по логу logs/ics_pid_20260816_104551.csv?
- Q: Проанализировать три неудачных production-прогона против working_ics и составить план исправления
- Q: Почему production-заход терял паритет с working_ics и как это исправлено?
- Q: Каков финальный результат исправления runtime-паритета 2026-08-16?
- Q: Проанализировать run 20260816T213847.114116Z, сравнить управление с working_ics и исправить уход по GLIDESLOPE и неисполняемый go-around.
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
1. `ControllingSystem` - 125 edges
2. `Telemetry` - 104 edges
3. `ICSSim` - 72 edges
4. `ControlsState` - 57 edges
5. `XPlaneSim` - 54 edges
6. `airborne_inputs()` - 52 edges
7. `RunRecorder` - 48 edges
8. `PIDController` - 46 edges
9. `ICSInputs` - 45 edges
10. `Scenario` - 44 edges

## Surprising Connections (you probably didn't know these)
- `Autonomous Landing Controller` --semantically_similar_to--> `Autonomous Landing Controller`  [INFERRED] [semantically similar]
  CLAUDE.md → AGENTS.md
- `FakeConnector` --uses--> `Telemetry`  [INFERRED]
  tests/fakes.py → ismpu/envs/ics_sim.py
- `HandshakeBench` --uses--> `Telemetry`  [INFERRED]
  tests/fakes.py → ismpu/envs/ics_sim.py
- `KinematicBench` --uses--> `Telemetry`  [INFERRED]
  tests/fakes.py → ismpu/envs/ics_sim.py
- `ScriptedFlightBench` --uses--> `Telemetry`  [INFERRED]
  tests/fakes.py → ismpu/envs/ics_sim.py

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

## Communities (238 total, 117 thin omitted)

### Community 0 - "RunRecorder"
Cohesion: 0.14
Nodes (15): Скопировать канонический preset и заменить только запрошенные условия запуска., Подключить best-effort аудит сырых успешно принятых/отправленных UDP payload., Append-only writer; ошибка диска помечает прогон, но не выходит в control-loop., Дождаться записи всех ранее поставленных элементов и flush файлов., RunRecorder, test_raw_packet_files_keep_exact_udp_json_and_only_observed_tx(), test_recorder_keeps_all_known_ics_fields_and_unknown_raw_fields(), test_recorder_pins_selected_matrix_rows_and_catalog_hash() (+7 more)

### Community 3 - "test_evaluate.py"
Cohesion: 0.16
Nodes (29): _check(), Criterion, evaluate_tz(), _range_check(), Чистые функции приёмки телеметрии по ТЗ и строкам матрицы. Каждый критерий…, Преобразовать наземные метрики запуска в вердикты раздела 5 ТЗ., Вернуть ``FAIL``, если провален хотя бы один применимый критерий., Один пункт ТЗ: предел, измеренное значение, вердикт и его причина. (+21 more)

### Community 4 - "rollout_bridge.py"
Cohesion: 0.11
Nodes (14): ICSBenchConnector, Мост к стенду: JSON поверх UDP, адрес стенда определяется из входящего пакета., Приём телеметрии стенда. Адрес отправителя определяется автоматически., Дождаться кадра и отбросить накопившийся UDP backlog, оставив самый свежий.…, Зафиксировать и разобрать один уже принятый UDP payload., Отправка управления на стенд. → отправлено ли (исключение наружу не…, Число последовательных best-effort ошибок текущего sender., Освободить единственный UDP-сокет коннектора. (+6 more)

### Community 5 - "json_config.py"
Cohesion: 0.13
Nodes (34): approach_control_from_dict(), approach_control_to_dict(), _copy_approach(), dump_scenario(), _finite_tree(), ground_control_from_dict(), ground_control_to_dict(), _legacy_ground() (+26 more)

### Community 6 - "SimInterface"
Cohesion: 0.10
Nodes (5): BaseException, StartMode, Минимальный lifecycle, одинаковый для стенда и X-Plane., SimInterface, Protocol

### Community 7 - "ControlsState"
Cohesion: 0.12
Nodes (30): ControlsState, Разделяемая по тактам структура команд — и наземных, и воздушных. Аннотации…, _our_channel(), Угол сноса не должен превращаться в ошибку курса на локализаторе., Стенд иногда сбрасывает Valid при сохранении пригодного численного значения., Крен парируется элеронами с обратным знаком — это проводка стенда, а не…, Знак глиссады: «ниже глиссады» обязано уменьшать вертикальную скорость…, Триггер выравнивания залипающий: подскок высоты не должен возвращать заход на… (+22 more)

### Community 8 - "Scenario"
Cohesion: 0.08
Nodes (35): AircraftProfile, FailureMode, FlightSegment, match_conditions(), _profile_name(), Сравнить ожидаемые условия участка с одним фактическим кадром backend., Оценить близость telemetry к preset; несовпадение отказа доминирует над погодой., Выбрать ближайший нематричный preset, не допуская draft без явного флага. (+27 more)

### Community 10 - "Telemetry"
Cohesion: 0.07
Nodes (18): Такт манёвра ухода. → True, когда набор устойчив (пора отдать управление…, Набор устойчив: есть и вертикальная скорость вверх, и прирост радиовысоты над…, Телеметрия стенда, приведённая к **СИ**. Проверять надо `valid` **до** полей:…, Кадр «связи со стендом нет». Нули, а не None: контур проверяет `valid` первым., Невалидные ICS-сигналы, которые воздушный закон читает безусловно., Приборная скорость (kt → м/с). Отсечки реверса заданы по ней, а не по путевой., Радиовысота **в футах** — единицы стенда. Порог воздушного включения (400…, Объявлены ли валидными **оба** канала ILS (курсовой и глиссадный). `None` —… (+10 more)

### Community 11 - "test_approach_channel.py"
Cohesion: 0.09
Nodes (31): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+23 more)

### Community 13 - "test_sft_regressors.py"
Cohesion: 0.18
Nodes (13): feature_schema_hash(), GainGuard, Минимальная SFT-модель абсолютных коэффициентов PID и общий runtime guard., Стабильный hash порядка признаков; перестановка является сменой контракта., Проверяет prediction и ограничивает скорость изменения до записи в PID., _checkpoint(), ndarray, Path (+5 more)

### Community 14 - "ics_connector.py"
Cohesion: 0.07
Nodes (32): GearState, ICSOutputs, IntEnum, UDP-мост к стенду заказчика (порт 3030) — транспорт пути поставки. `ICSInputs`…, Разбор телеметрии стенда с совместимостью вперёд. Асимметрия намеренная (JSON-…, Команды и mode flags, сериализуемые ровно в ожидаемый стендом JSON., Сериализовать enums и 14 reserved zeros в точные UTF‑8 bytes wire contract., Отправка best-effort со счётчиком ошибок и разрежённым логом. Windows отдаёт… (+24 more)

### Community 15 - "test_run_matrix.py"
Cohesion: 0.10
Nodes (23): Разрешить только полный ``<шифр>/<номер>`` и вернуть точную строку JSON., resolve_matrix_run(), compose_matrix_scenario(), _install_through_scenarios(), Сценарий по имени либо шифру матрицы, без различия раскладки А/B., Собрать сценарий из конкретных строк APPROACH/ROLLOUT/TAXI.…, Одна строка каталога → минимальный сценарий нужного участка или сквозной пары., Перенести накопленные overrides одного шифра на следующее условие этого же… (+15 more)

### Community 16 - "AircraftProfile"
Cohesion: 0.10
Nodes (10): AircraftProfile, clamp(), Преобразовать воздушные команды ICD в нормированные DataRef X-Plane., Преобразовать нормированные команды пробега в DataRef X-Plane., Расширение реестра будущим профилем МС-21 без правки XPlaneSim., Проводка и масштабы конкретного планера X-Plane., Общая идентичность ЛА и необязательная привязка к X-Plane. Профиль нужен и…, Command refs retained under the historical public name. (+2 more)

### Community 17 - "test_full_flight.py"
Cohesion: 0.05
Nodes (63): IntFlag, ControlValid, Биты `ControlValidMask`: какие каналы несёт команда. **Один бит на одно…, initial_segment(), is_airborne(), FlightSegment, Сообщает ли стенд, что ВС в воздухе и достаточно высоко для приёма захода.…, С какого участка начинать. Пробег — ответ по умолчанию (см. модуль). (+55 more)

### Community 18 - "ApproachResult"
Cohesion: 0.13
Nodes (22): ApproachLimits, ApproachTelemetry, ApproachController, ApproachResult, clamp(), ApproachConfig, Заход по ILS с выравниванием. Телеметрию получает параметром, не читает сам.…, Регуляторы канала по именам — для логов и приёмки, не для… (+14 more)

### Community 19 - "DashboardServer"
Cohesion: 0.15
Nodes (10): DashboardServer, main(), Запустить локальный read-only replay dashboard до ``Ctrl+C``., Отображаемое имя, PID source и физическая фаза одной панели графика., Loopback-only HTTP lifecycle вокруг одного ``DashboardState``., Фактически привязанные host/port, включая ephemeral port 0 в тестах., Идемпотентно запустить daemon HTTP thread., Отклонить pending tuning, остановить thread и закрыть listening socket. (+2 more)

### Community 20 - "test_icd_units.py"
Cohesion: 0.11
Nodes (17): Сверка каждого сигнала стенда с документами Заказчика. Два независимых…, 1 фут/мин = 0.3048/60 м/с. Приближение здесь копится на всём заходе., Нумерация фаз из doc-комментария `FlightPhase` в ICSInterface.cs., −26.5…55.0° — фактическое положение РУД во входной телеметрии, не команда., Наши константы обязаны совпадать с таблицей управляющих сигналов Заказчика., Тиллер задаётся ходом в миллиметрах. Отдельным тестом, потому что ошибка была…, 0–45 мм командует, 0–36.73 мм отчитывается. Подмена недодаёт ~18 % хода., В перечне управляющих сигналов абсолютного положения РУД нет — только скорость.… (+9 more)

### Community 23 - "PIDController"
Cohesion: 0.09
Nodes (31): PIDController, Сброс внутренних состояний (используется при выключении системы)., Забыть разрыв измерения, сохранив накопленный интеграл и текущий выход., test_ground_pids_use_working_ics_numerics_and_explicit_integrator_limits(), _legacy_reference(), Опциональная численность PID (шаг 5): каждый флаг проверяется на том дефекте,…, Если применено ровно то, что выдал PID, коррекции быть не должно., Уставка прыгает, объект стоит на месте — D-составляющая не должна реагировать.… (+23 more)

### Community 25 - "DashboardState"
Cohesion: 0.12
Nodes (11): DashboardState, _finite(), _handler_factory(), _jsonable(), HTTP читает только immutable recorder objects; controller меняет control-thread., Стабильный execution id live/replay источника., Вернуть подписи всех девяти панелей в порядке HTML layout., Проверить HTTP-запрос и поставить полный PID triplet в control-thread queue. (+3 more)

### Community 26 - "test_xplane_backend.py"
Cohesion: 0.09
Nodes (21): ApproachSetup, Начальные условия захода X-Plane на продолжении оси и глиссады., Детерминированно seeded шум/пропуски, применяемые только resettable backend., SensorNoise, DatagramSocket, MockXPlaneConnector, ScriptedXPlaneConnector, test_commands_failures_and_close_release_overrides() (+13 more)

### Community 27 - "test_ics_sim.py"
Cohesion: 0.04
Nodes (63): engaged_sim(), FakeConnector, make_ics_inputs(), on_ground(), Статический стенд: всегда один и тот же кадр, отправленное — в `sent_outputs`., (sim, connector) с завершённым рукопожатием: стенд подтвердил `AgentIsActive =…, Полный пакет стенда: нули по умолчанию + заданные поля., Кадр «ВС на полосе»: обжаты все стойки, курс/координаты у порога UUEE 06R. (+55 more)

### Community 29 - "IcsEngagement"
Cohesion: 0.05
Nodes (27): EngagementInputs, IcsEngagement, Автомат включения. `step(inputs)` вызывается каждый такт до формирования…, Полный сброс — новый эпизод начинается с невключённого состояния., Подхватить уже включённый извне пробег: шлём `ControlMode = Rollout`.…, Войти в пробег самостоятельно: шлём `ControlMode = Rollout`. Это же — передача…, Перейти `Approach → Landing` без нового рукопожатия. Закон остаётся воздушным., Войти в заход самостоятельно: шлём `ControlMode = Approach`. Обычно вызывать не… (+19 more)

### Community 30 - "failures.py"
Cohesion: 0.09
Nodes (26): CompletionRule, LongitudinalChannel, LongitudinalDiagnostics, Блок 1: скорость → симметричная база тормозов и реверса., Сбросить PID и привязать начало профиля к фактической скорости касания/старта., FailureManager, FailureMode, FailureState (+18 more)

### Community 31 - "._fail"
Cohesion: 0.22
Nodes (4): Exception, Поставить запись без блокировки control thread; переполнение инвалидирует run., Сохранить полный effective config; канонические config-файлы не затрагиваются., RunEvent

### Community 32 - "flight.py"
Cohesion: 0.06
Nodes (31): approach_blocker(), ApproachRefused, at_lateral_alignment_gate(), ils_blocker(), in_terminal_window(), Участки полёта и переходы между ними. Управление ведётся на всём интервале — от…, Последние футы перед касанием, где прерывать заход опаснее, чем доработать.…, Полоса подхода к гейту совмещения с осью ± 5 м: `(30 м, 30 м + band]`. Только в… (+23 more)

### Community 33 - "Graphify Pipeline"
Cohesion: 0.08
Nodes (29): Folder Watcher, URL Ingestion, Extra Graph Exports, MCP Graph Server, Confidence Audit Trail, Deterministic Node IDs, Semantic Extraction Contract, Cross-Repository Graph Merge (+21 more)

### Community 34 - "XPlaneConnector"
Cohesion: 0.06
Nodes (23): DataRefSample, Неблокирующий UDP-клиент нативного протокола X-Plane 12., Атомарно снять все свежие значения без раскрытия внутреннего mutable cache., Discard pre-reload values so readiness cannot use stale telemetry., Повторять RREF requests до получения всех значений либо подробного timeout., Отправить один нативный 509-byte DREF packet., Последнее значение DataRef и monotonic timestamp его UDP-пакета., Отправить один нативный CMND packet. (+15 more)

### Community 35 - "ControllingSystem"
Cohesion: 0.06
Nodes (50): ControllingSystem, Связать сценарий с контуром; PID активируются после определения участка., Разорвать D-history после пропуска устаревшей UDP-очереди, не трогая интегралы., Оркестратор классического контура поверх стенда (`envs.ics_sim.ICSSim`).…, Аварийная остановка: обнулить органы и **снять заявку каналов**. Именно…, Готовый кадр `Telemetry` для прямых вызовов `control_step(dt, telemetry,…, (sim, connector) с неизменным кадром у порога ВПП. Скорость задаётся в **м/с**.…, static_sim() (+42 more)

### Community 36 - "loop.py"
Cohesion: 0.13
Nodes (13): ControllingSystem, Глобальные константы контура управления (перенесены из main.ipynb)., Сколько устаревших UDP-кадров сброшено при последнем чтении., _lost_engagement(), Управляющий цикл 20 Гц против стенда заказчика — **весь интервал полёта**.…, Снял ли стенд активность посреди прогона. → пора останавливаться. Без этой…, Компактные перцентили миллисекунд без зависимости в критическом пути., Прогоняет один полёт на уже настроенном контуре. (+5 more)

### Community 37 - "test_ics_engagement.py"
Cohesion: 0.10
Nodes (49): _Clock, _engine(), _pump(), Автомат включения управления на стенде. Два раздельных предмета проверки: *…, По ICD стенд должен два секунды ПОЛУЧАТЬ ModeAIReady=1. Если считать одно лишь…, Обратная защита: 30 кадров можно выпалить за 0.1 с — время тоже обязано пройти., Срыв предусловия обнуляет и время, и счётчик кадров., Требование ICD — непрерывность: пропуск готовности рвёт серию. (+41 more)

### Community 38 - "run_reader.py"
Cohesion: 0.09
Nodes (23): _apply_recorded_gains(), _bool_or_none(), _equal(), main(), _number(), _parse_cell(), ControllingSystem, Path (+15 more)

### Community 39 - "sft.py"
Cohesion: 0.13
Nodes (23): GuardResult, Фактически разрешённые gains и причина ограничений/fallback., apply_gain_vector(), controller_gain_vector(), _feature_value(), feature_vector(), gain_vector_from_row(), _number() (+15 more)

### Community 40 - "test_diagnostic_tools.py"
Cohesion: 0.21
Nodes (18): build_altitude_sweep(), command_for_pulse(), Безопасные elevator/altitude authority sweep без дублирования ICS runner., Чистое преобразование, пригодное и для dry-run, и для ICSSim., safety_reason(), SweepLimits, SweepPulse, validate_pulse() (+10 more)

### Community 41 - "fakes.py"
Cohesion: 0.06
Nodes (30): IntEnum, FlightPhase, Константы интерфейса стенда заказчика (ПИВ / ICS). Единый источник правды по…, Фаза полёта, сообщаемая стендом (`ICSInputs.FlightPhase`)., ControlModeState, Режим управления/индикации, передаваемый в каждом ICSOutputs., decode_airborne(), decode_outputs() (+22 more)

### Community 43 - "ICSInputs"
Cohesion: 0.14
Nodes (24): ControlResult, ICSInputs, Неизвестные поля исходного JSON; они доступны аудиту, но не закону управления., Полная известная входная схема стенда; единицы определены в ``ICSInterface.cs``., airborne_control_mode(), airborne_flare_mode(), deactivate(), live_main() (+16 more)

### Community 45 - "3. Этапы реализации"
Cohesion: 0.09
Nodes (21): 1. Подтверждённые проблемы и целевое состояние, 2. Ключевые интерфейсы, 3. Этапы реализации, 4. Тестирование и критерии готовности, 5. Зафиксированные допущения, 6.1. Один dashboard вместо двух, 6.2. Единый источник данных, 6.3. Представления (+13 more)

### Community 46 - ".from_checkpoints"
Cohesion: 0.50
Nodes (4): checkpoint_metadata(), Path, Сформировать audit metadata загруженного файла, включая SHA-256 содержимого., Загрузить независимые air/ground slots и проверить activation evidence для ICS.

### Community 47 - "test_profiled_scenarios.py"
Cohesion: 0.13
Nodes (12): Any, compose_scenario(), Serialize only the canonical profile- and matrix-aware schema v3., Прочитать schema v3 либо явно мигрируемую v1/v2 конфигурацию., Собрать сценарий из независимых источников участков., test_preset_roundtrips_through_dict(), Contracts of the unified aircraft-profiled scenario model., test_automatic_selection_never_falls_back_to_a_draft_profile_branch() (+4 more)

### Community 49 - "_Clock"
Cohesion: 0.15
Nodes (19): _air(), _Clock, _pump(), Ниже 400 футов стенд управление не отдаёт — гнать туда стимул бессмысленно., Необъявленная радиовысота — «стенд не сообщил», а не «ноль футов». Иначе ВС в…, После касания режим меняется на пробег — но не раньше: смена режима на глиссаде…, Ниже 80 футов потеря `AgentIsActive` не повод бросать органы: до земли секунды., Окно только удерживает подтверждение. Само оно включения не даёт. (+11 more)

### Community 50 - "test_go_around.py"
Cohesion: 0.12
Nodes (28): GoAroundManeuver, Состояние идущего ухода на второй круг. Пока он активен, заход не ведётся., Начать уход: зафиксировать состояние манёвра и высоту входа., _armed_controller(), _drive(), _frame(), Уход на второй круг (fallback в воздухе): условия срабатывания и передача…, На пробеге ухода нет — segment guard (козление удерживает защёлка сегмента,… (+20 more)

### Community 51 - "Hybrid Neural PID Controller"
Cohesion: 0.70
Nodes (5): Hybrid Neural PID Controller, Neural PID Gain Scheduler, PPO Training Loop, Preset-Anchored Deterministic Shield, SFT Behavioral-Cloning Warm Start

### Community 52 - "test_approach_criteria.py"
Cohesion: 0.13
Nodes (15): ApproachController, angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, Отдельный монитор критерия А.1.1 (не участвует в go-around)., Захватывает А.1.1 после входа в допуск и завершает оценку на 300 ft. (+7 more)

### Community 53 - "run_artifacts.py"
Cohesion: 0.15
Nodes (19): Вернуть одно свежее значение; stale/missing представлены ``None``., controller_pids(), _csv_value(), default_runs_root(), _effective_configs(), gains_snapshot(), _git_state(), _jsonable() (+11 more)

### Community 54 - "sim_interface.py"
Cohesion: 0.14
Nodes (13): _destination(), ApproachData, ControlDiagnostics, Enum, Общий контракт симулятора и воздушных сигналов. ICS и X-Plane различаются…, Исчерпывающие причины штатного/аварийного завершения единого runtime loop., Причина остановки вместе с best-effort результатом освобождения backend., Снимок готовности resettable backend для recorder/dashboard. (+5 more)

### Community 55 - "RunwayTracker"
Cohesion: 0.13
Nodes (11): Точка на продолжении оси; положительное расстояние — до порога., Решить прямую геодезическую задачу на сферической Земле., Геодезическое guidance в истинной системе направлений., Guidance по курсу ВПП и измеренному отклонению — без собственной геодезии.…, Возвращает отклонение от осевой линии в метрах. >0 - правее оси, <0 - левее., Геодезическое наведение на ось ВПП с упреждением по скорости., RunwayTracker, test_guidance_on_centerline_small_heading_error() (+3 more)

### Community 56 - "ICSSim"
Cohesion: 0.11
Nodes (11): ICSSim, FailureMode, SimInterface, Обмен со стендом заказчика: телеметрия внутрь, команды наружу. Управление…, Принимает ли стенд наши команды. До включения любой `step` уходит вхолостую., Войти в пробег самостоятельно (`ControlMode 0 → 3`)., На стенде отказы приходят телеметрией, а не инжектируются нами., Снять управление: пустая маска и `ControlMode = Off` несколько кадров подряд.… (+3 more)

### Community 57 - "ICSInputs"
Cohesion: 0.13
Nodes (14): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, ICSInputs, Evaluate the A.1.1 approach segment and stop at a radio-altitude floor., ControlModeState (+6 more)

### Community 58 - "test_dashboard.py"
Cohesion: 0.20
Nodes (13): _live(), _post(), parametrize, test_active_pid_is_editable_in_classical_and_shadow(), test_gain_change_is_queued_bumpless_and_records_full_event(), test_http_api_is_incremental_pending_and_loopback_only(), test_incremental_snapshot_uses_recorder_objects_and_stays_small_when_idle(), test_live_and_replay_use_the_same_dashboard_snapshot() (+5 more)

### Community 59 - "pretrain.py"
Cohesion: 0.10
Nodes (35): _condition_key(), _fit_feature_normalization(), load_offline_dataset(), _normalized_mse(), _physical_bounds(), _predict(), ndarray, Path (+27 more)

### Community 60 - "GainChange"
Cohesion: 0.40
Nodes (3): GainChange, Закрыть tuning и записать отказ для каждого неисполненного запроса., Immutable запрос HTTP-thread, ожидающий применения control-thread.

### Community 61 - "test_control_parity.py"
Cohesion: 0.10
Nodes (21): CompletionRule, Enum, Генератор эталонной кривой скорости пробега. Два закона замедления: колокол…, Как активный наземный сценарий заканчивает управление., Генератор эталонной кривой скорости (Колокол Гаусса)., Начать профиль с фактической скорости текущего участка., То же без лишнего round-trip м/с → узлы → м/с на касании., Возвращает идеальную скорость (м/с) для текущей точки пути. (+13 more)

### Community 62 - "Project Dependencies"
Cohesion: 0.29
Nodes (7): Optional Gymnasium, NumPy, Pandas, Project Dependencies, Pytest, Termcolor, Optional PyTorch

### Community 63 - "main"
Cohesion: 0.29
Nodes (7): cli(), main(), Точка входа: подключиться к стенду, выбрать пресет и провести полёт.…, Единственная production CLI-точка для ICS и явного тестового X-Plane backend., RunRecorder, test_production_cli_uses_the_unified_runtime_without_working_ics(), test_runtime_uses_explicit_matrix_run_id_without_telemetry_guessing()

### Community 64 - "PidGainRegressor"
Cohesion: 0.12
Nodes (15): device, PidGainRegressor, Any, Предсказать gains по последнему hidden state окна ``(B,T,F)``., Сохранить веса вместе с полным train↔runtime контрактом., Загрузить модель только после проверки полного train↔runtime контракта., Краткая форма ``load_checkpoint`` для потребителя, которому не нужна metadata., Восстановить и строго проверить normalization из checkpoint. (+7 more)

### Community 66 - "dashboard_core.py"
Cohesion: 0.20
Nodes (6): _allocator_stage(), _first_present(), _gains_from_samples(), _mean(), Один локальный dashboard для live RunRecorder и read-only replay., _view_point()

### Community 67 - "test_tolerance.py"
Cohesion: 0.09
Nodes (36): lateral_limit_m(), lateral_load_situation(), lateral_situation(), normal_load_situation(), IntEnum, Критерии критичности особых ситуаций МС-21 (Приложение 1 к ТЗ). Таблица АП-25…, Классификация скорости касания относительно VAPP и VВПП пред., Классификация нормальной перегрузки посадочного удара. `heavy` — взлётный вес. (+28 more)

### Community 68 - "test_working_ics_dashboard.py"
Cohesion: 0.19
Nodes (11): ClearWeatherILSController, DashboardState, DashboardServer, _controller(), _inputs(), Characterization tests for the bench-validated ``working_ics`` dashboard., _record(), test_dashboard_records_four_airborne_views_and_diagnostics() (+3 more)

### Community 70 - "test_campaign.py"
Cohesion: 0.21
Nodes (19): campaign_phase(), campaign_rows(), campaign_summary(), _config_status(), main(), next_campaign_row(), Path, Порядок и фактический статус кампании из 280 матричных прогонов. (+11 more)

### Community 71 - "Unified Profile-Aware Scenario System"
Cohesion: 0.33
Nodes (6): Technical-Specification Acceptance Gates, Forward-Only Flight Segment Supervisor, Longitudinal and Lateral Ground Channels, PID Run Matrix, Unified Profile-Aware Scenario System, Legacy Scenario Preset Model

### Community 72 - "Interactive PID Dashboard"
Cohesion: 0.25
Nodes (9): Nine-View PID Dashboard, Run Recording Artifacts, buildTabs, draw, Gain Tuning and Snapshot Export, Interactive PID Dashboard, refresh, render (+1 more)

### Community 73 - "run_matrix.py"
Cohesion: 0.09
Nodes (14): MatrixCondition, MatrixRun, normalize_code(), _number(), Any, WeatherState, Версионированный каталог 280 прогонов исходной Excel-матрицы. Production…, Нормализовать латинские A/B и регистр к шифрам книги ``А/Б``. (+6 more)

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

### Community 79 - ".snapshot"
Cohesion: 0.18
Nodes (6): DashboardSnapshot, Вернуть только новые recorder updates; смена run_id принудительно сбрасывает…, JSON-ready форма ``snapshot`` для ``GET /api/state``., Инкремент после sequence cursor и редкие metadata при reset., Преобразовать tuples в JSON arrays, не добавляя отсутствующие тяжёлые секции., RunEvent

### Community 80 - "ICS PID Monitor"
Cohesion: 0.22
Nodes (9): Bench-Validated ILS Approach Channel, Tolerance-Gated Go-Around, buildControls, draw, formatTime, Four-Loop PID Tuning, ICS PID Monitor, Live and Historical Timeline (+1 more)

### Community 81 - "run_report.py"
Cohesion: 0.15
Nodes (26): _accepted_segments(), aggregate_matrix_results(), _approach_runway_heading_error(), build_run_report(), _environment_diagnostics(), _handover_ratio(), main(), _matrix_results() (+18 more)

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
Cohesion: 0.11
Nodes (24): ApproachConfig, ControlProfile, _copy_approach(), _copy_ground(), _ground_matrix_drafts(), _ground_segments_for_spec(), _GroundPresetSpec, _install_approach_scenarios() (+16 more)

### Community 88 - "import_workbook"
Cohesion: 0.33
Nodes (9): import_workbook(), main(), Any, Path, Одноразовый импорт исходной Excel-матрицы в runtime-каталог JSON., Прочитать книгу целиком; функция не используется production runtime., _scalar(), write_catalog() (+1 more)

### Community 89 - "segments.py"
Cohesion: 0.40
Nodes (5): FlightSegment, Enum, str, Канонические участки управляемого интервала полёта., Участок, для которого выбираются закон управления и условия сценария.

### Community 90 - "LateralChannel"
Cohesion: 0.16
Nodes (10): GuidanceState, LateralChannel, LateralDiagnostics, Блок 2: runway guidance → единый нормированный yaw-запрос., Путевой угол на пробеге, курс фюзеляжа на малой скорости. При стремящейся к…, Guidance по тому, что даёт стенд. → словарь guidance или None, если данных нет.…, Вернуть тот же ``GuidanceState``, который использует управляющий такт и…, PIDController (+2 more)

### Community 92 - "MatrixCase"
Cohesion: 0.13
Nodes (4): MatrixCase, FailureMode, FlightSegment, Производная группировка строк одного шифра; исходные тексты живут в каталоге.

### Community 93 - ".read_telemetry"
Cohesion: 0.08
Nodes (20): ConditionMatch, ControlsState, EngagementInputs, ICSOutputs, _clamp(), FlightSegment, Начало эпизода: сброс рукопожатия и первый кадр со стенда. Средой распоряжается…, Сверить ожидаемые условия; стендовые условия никогда не изменяются кодом. (+12 more)

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

### Community 113 - "ApproachConfig"
Cohesion: 0.25
Nodes (7): ApproachConfig, _pid_from_colleague(), Загрузка настроек из JSON коллеги (`config/ics_clear_weather_pid.json`). Секции…, `PIDConfig` коллеги → аргументы нашего `PIDController`. Предел интегратора у…, Параметры воздушного контура. Значения по умолчанию — настроенные на стенде.…, Наши умолчания и его файл — одно и то же. Разойдутся — расхождение должно быть…, test_config_from_the_colleague_json_matches_our_defaults()

### Community 115 - ".neutralize_airborne"
Cohesion: 0.19
Nodes (5): Обнуляет все органы управления. Отправку делает вызывающий через `ICSSim.step`.…, Совместимое имя старого API; колёсные органы оно больше не обозначает., Сброс к нейтральным командам — новый эпизод начинается с чистого состояния.…, Обнулить только воздушные команды. Нужно, когда воздушный канал не может…, setter

### Community 116 - "Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)., Source Nodes

### Community 117 - "ConditionMatch"
Cohesion: 0.25
Nodes (5): ConditionMatch, Сверка ожидаемых условий с фактической телеметрией backend., Истина, если набор фактических отказов совпал ровно., Истина при практически нулевой нормированной дистанции погоды., Погода остаётся отчётной; неверный отказ делает прогон недопустимым.

### Community 118 - "_descent_frames"
Cohesion: 0.20
Nodes (10): _colleague_controller(), _descent_frames(), Страховка от самообмана: сценарий обязан пройти выравнивание, иначе паритет его…, `ElevatorCmd` — перегрузка в g, и предел ±0.5 действует и на глиссаде, и в…, Оригинальный контур коллеги, настроенный тем же файлом. `None`, если…, Сценарий снижения: высота падает, планка курса и глиссады «дышит», тангаж…, Перенос обязан совпадать с подтверждённым на стенде оригиналом, а не «вести…, test_elevator_stays_inside_the_load_factor_limits_through_the_whole_descent() (+2 more)

### Community 124 - "._should_go_around"
Cohesion: 0.29
Nodes (5): above_decision_height(), above_decision_velocity(), ВС выше высоты решения ухода на второй круг (30 м по ТЗ 5.1.1.2). → уход…, Реверс убран: команды обратной тяги нулевые. В воздухе реверс не выдаётся…, Нужно ли уходить на второй круг по этому такту. → причина или `None`. Только…

### Community 126 - ".compute"
Cohesion: 0.18
Nodes (5): → (интеграл только с утечкой, интеграл с утечкой и приращением). Оба уже зажаты., Такт регулятора. `measurement` обязателен при `derivative_on_measurement=True`., Back-calculation: подтянуть интегратор к фактически применённой команде. No-op…, Сменить коэффициенты без сброса D-history и с компенсацией интегратором.…, Вес апериодического фильтра D-составляющей за такт `dt`.

### Community 127 - ".from_csv"
Cohesion: 0.22
Nodes (9): _gain_ranges(), _gains_from_manifest(), _load_updates(), Path, RunReader, После recorder.finish держать полный run доступным, но только для чтения., Сохранить фактически записанный effective config, не изменяя SCENARIOS., Построить read-only state из run-directory либо поддерживаемого CSV. (+1 more)

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

### Community 134 - "WeatherState"
Cohesion: 0.25
Nodes (7): Any, Погодные условия. Поля — ровно то, что сообщает стенд (см. `from_ics`).…, Собирает ветер из компонент относительно курса ВПП. `crosswind_kts` > 0 — ветер…, Сериализация в примитивы (для логирования/воспроизводимости сценариев)., WeatherState, test_scenario_roundtrip_with_weather_and_failures(), test_weatherstate_from_crosswind()

### Community 135 - "Q: Приступай к выполнению этапа 2 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 2 плана docs/plan.md, Source Nodes

### Community 137 - "DashboardState"
Cohesion: 0.43
Nodes (3): DashboardState, Any, ICSInputs

### Community 139 - "system.py"
Cohesion: 0.08
Nodes (30): ApproachResult, Профили преобразования команд ИСМПУ в органы управления X-Plane., Настройки воздушного участка: заход по ILS, выравнивание, управление скоростью.…, Типы и порядок коэффициентов пяти наземных PID-регуляторов. Модуль намеренно не…, Приёмочные пороги из ТЗ (раздел 5). Единый источник истины для runtime…, Геометрия целевой ВПП и высоты установки ЛА. Смена целевой полосы = правка…, Воздушный канал: заход по ILS, выравнивание, управление скоростью. Перенос…, Каналы управления и общий вектор команд. `ControlsState` — разделяемая по… (+22 more)

### Community 142 - "pid_controller.py"
Cohesion: 0.11
Nodes (25): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+17 more)

### Community 151 - "GuidanceState"
Cohesion: 0.29
Nodes (3): GuidanceState, Совместимость с прежним атрибутом; новый термин явно указывает ось., Совместимость со старым словарным API.

### Community 153 - "weather.py"
Cohesion: 0.18
Nodes (12): Enum, Погодные условия эпизода: описание, шкала сцепления и разбор ветра. Модуль **не…, Состояние ВПП как **монотонная шкала скользкости** 0…15 (0 — сухо, 15 — лёд со…, Код состояния ВПП со стенда → наша шкала. Неизвестный код трактуется как `ICY`,…, runway_condition_from_bench(), RunwayCondition, Коды из фактических пакетов переводятся в свою шкалу скользкости., test_runway_condition_codes_are_remapped_not_passed_through() (+4 more)

### Community 154 - "Normalization"
Cohesion: 0.10
Nodes (17): ArrayLike, Dataset, float32, float64, Normalization, NDArray, Выполнить deterministic inference и вернуть физические gains плюс OOD flag., Проверить prediction и ограничить его относительно accepted preset/предыдущего… (+9 more)

### Community 155 - ".__init__"
Cohesion: 0.29
Nodes (5): AircraftProfile, Path, RunwayProfile, WeatherState, XPlaneConnector

### Community 158 - "Q: Приступай к выполнению этапа 4 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 4 плана docs/plan.md, Source Nodes

### Community 162 - "ControlModeState"
Cohesion: 0.40
Nodes (3): ControlModeState, Сообщить автомату, что кадр **фактически ушёл** на стенд. Вызывается…, Значение `ControlMode` для исходящей команды (стимул). Во время выдержки —…

### Community 164 - "RunSample"
Cohesion: 0.33
Nodes (3): Один такт: вход, команда и диагностика имеют общий ``tick_id``., Атомарный incremental slice для dashboard, без чтения controller., RunSample

### Community 166 - "test_refactoring_contracts.py"
Cohesion: 0.33
Nodes (5): parametrize, Эталон разрешён тестам, но не должен стать скрытым runtime dependency., test_production_modules_never_import_the_working_ics_reference(), test_scenario_json_v1_requires_an_explicit_legacy_profile_override_for_a330(), test_xplane_ignores_failures_outside_rollout_contract()

### Community 167 - "Q: Приступай к выполнению этапа 8 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 8 плана [plan.md](docs/plan.md)., Source Nodes

### Community 176 - "test_localizer_deflection_turns_the_aircraft_back_to_the_centreline"
Cohesion: 0.50
Nodes (4): angle_error_deg(), Разность курсов, приведённая к (-180, 180]., Отклонение планки курса задаёт доворот в сторону оси, а не от неё., test_localizer_deflection_turns_the_aircraft_back_to_the_centreline()

### Community 181 - "Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md)., Source Nodes

### Community 202 - "ics_engagement.py"
Cohesion: 0.50
Nodes (4): Enum, EngagementState, Автомат включения управления на стенде заказчика. Стенд принимает наши команды…, Состояние **исходящего стимула** (что мы шлём стенду), а не факта включения.…

### Community 208 - "_faults_from_inputs"
Cohesion: 0.40
Nodes (4): ICSInputs, _faults_from_inputs(), Отказы, о которых сообщает борт — **единственный** источник истины об отказах.…, Сигналы отказов со стенда → наши `FailureMode`. Отказы шасси…

### Community 212 - "runway_profiles.py"
Cohesion: 0.15
Nodes (17): ICSBenchConnector, IcsEngagement, get_aircraft_profile(), find_earth_nav_dat(), get_runway_profile(), ILSStation, parse_ils_station(), Path (+9 more)

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

## Ambiguous Edges - Review These
- `Unified Profile-Aware Scenario System` → `Legacy Scenario Preset Model`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to
- `Dual-Backend SimInterface` → `ICS-Only Backend Guidance`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **111 isolated node(s):** `ismpu`, `Answer`, `Outcome`, `Source Nodes`, `Answer` (+106 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **117 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `MatrixRun` (3× useful, score=2.783115131)
- `XPlaneSim` (3× useful, score=2.770441995)
- `PidGainRegressor` (2× useful, score=1.857379953)
- `rollout_bridge.py` (2× useful, score=1.857379953)
- `loop.py` (2× useful, score=1.837541763) _(code changed — re-verify)_
- `LateralChannel` (2× useful, score=1.802947817)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Unified Profile-Aware Scenario System` and `Legacy Scenario Preset Model`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Dual-Backend SimInterface` and `ICS-Only Backend Guidance`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Telemetry` connect `Telemetry` to `.from_ics`, `RunRecorder`, `rollout_bridge.py`, `ControlsState`, `system.py`, `test_approach_channel.py`, `test_full_flight.py`, `ApproachResult`, `test_icd_units.py`, `XPlaneSim`, `test_ics_sim.py`, `failures.py`, `flight.py`, `ControllingSystem`, `test_diagnostic_tools.py`, `fakes.py`, `_Clock`, `test_go_around.py`, `test_approach_criteria.py`, `sim_interface.py`, `test_control_parity.py`, `test_tolerance.py`, `_faults_from_inputs`, `test_working_ics_golden.py`, `LateralChannel`, `.read_telemetry`, `.enter_segment`, `._should_go_around`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Why does `ControllingSystem` connect `ControllingSystem` to `RunRecorder`, `control.py`, `rollout_bridge.py`, `Telemetry`, `system.py`, `test_sft_regressors.py`, `test_run_matrix.py`, `test_full_flight.py`, `test_xplane_backend.py`, `test_ics_sim.py`, `failures.py`, `flight.py`, `XPlaneConnector`, `test_refactoring_contracts.py`, `sft.py`, `fakes.py`, `test_go_around.py`, `test_approach_criteria.py`, `ICSSim`, `test_dashboard.py`, `test_control_parity.py`, `test_campaign.py`, `._should_go_around`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `IcsEngagement` connect `IcsEngagement` to `ControlModeState`, `test_ics_engagement.py`, `ics_engagement.py`, `test_full_flight.py`, `_Clock`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `ControllingSystem` (e.g. with `ApproachRefused` and `ToleranceReport`) actually correct?**
  _`ControllingSystem` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `Telemetry` (e.g. with `ApproachController` and `ApproachResult`) actually correct?**
  _`Telemetry` has 31 INFERRED edges - model-reasoned connections that need verification._