# Graph Report - GOSNIIASProject  (2026-08-16)

## Corpus Check
- 139 files · ~141,038 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2529 nodes · 5454 edges · 249 communities (126 shown, 123 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 365 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b2894506`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- criticality.py
- GainMap
- ndarray
- test_weather.py
- ics_sim.py
- json_config.py
- SimInterface
- ControlsState
- Scenario
- GainKey
- channels.py
- LateralChannel
- float32
- test_diagnostic_tools.py
- ICSOutputs
- test_run_matrix.py
- AircraftProfile
- airborne_inputs
- ApproachController
- DashboardServer
- test_icd_units.py
- XPlaneSim
- Any
- PIDController
- ndarray
- DashboardState
- test_xplane_backend.py
- engaged_sim
- Any
- IcsEngagement
- MatrixCase
- RunRecorder
- .invalid
- Graphify Pipeline
- XPlaneConnector
- ControllingSystem
- test_ground_controller.py
- test_ics_engagement.py
- run_reader.py
- sft.py
- .enqueue_gain_update
- fakes.py
- floating
- runner.py
- device
- 3. Этапы реализации
- .from_checkpoints
- test_profiled_scenarios.py
- Path
- test_full_flight.py
- test_go_around.py
- Hybrid Neural PID Controller
- test_approach_criteria.py
- ._approach_step
- run_artifacts.py
- RunwayTracker
- RomanLogImporter
- working_ics/approach_criteria.py
- test_dashboard.py
- pretrain.py
- _load_updates
- test_control_parity.py
- Project Dependencies
- RunRecorder
- PidGainRegressor
- ICSInputs
- dashboard_core.py
- test_tolerance.py
- test_working_ics_dashboard.py
- ICSOutputs
- Telemetry
- Unified Profile-Aware Scenario System
- Interactive PID Dashboard
- MatrixRun
- DashboardState
- failures.py
- ICSInterface.cs
- План исправления
- run_pretrain
- promote_candidate.py
- ICS PID Monitor
- test_working_ics_port.py
- Autonomous Landing Controller
- X-Plane Dashboard and Runtime Guide
- test_working_ics_golden.py
- GainSpace
- run_report.py
- scenarios.py
- import_workbook
- envelope.py
- .setup
- test_campaign.py
- static_sim
- ICSSim
- loop.py
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
- RunReader
- Q: Приступай к выполнению этапа 9 плана docs/plan.md; упрощай код, удаляй лишнее и добавляй комментарии.
- Q: Реализовать этап 0: baseline, golden replay и dashboard characterization
- Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md).
- ICSBenchConnector
- ndarray
- test_ics_sim.py
- Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md).
- roll_limit_deg
- weather.py
- ControlModeState
- ICSInputs
- ICSOutputs
- socket
- test_sft_regressors.py
- _faults_from_inputs
- GuidanceState
- .compute
- .from_csv
- .control_step
- Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md).
- Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md).
- system.py
- device
- int64
- .pids
- Q: Приступай к выполнению этапа 2 плана docs/plan.md
- ICSInputs
- LandingFlapConfiguration
- TypedDict
- protocol.py
- FailureMode
- ICSInputs
- pid_controller.py
- ControlModeState
- ApproachChannel
- ICSOutputs
- .from_ics
- FailureState
- AircraftProfile
- WeatherState
- PidMap
- Any
- PidMap
- ApproachConfig
- Normalization
- test_refactoring_contracts.py
- Scenario
- Path
- Q: Приступай к выполнению этапа 4 плана docs/plan.md
- .from_dict
- RewardWeights
- TypedDict
- runway_condition_from_bench
- ControlsState
- IcsEngagement
- RegulatorKey
- FailureMode
- Q: Приступай к выполнению этапа 8 плана [plan.md](docs/plan.md).
- HandshakeBench
- FlightSegment
- ICSInputs
- PidMap
- _FakeSocket
- Any
- ArrayLike
- float32
- .from_json
- NDArray
- ControllingSystem
- Tensor
- ApproachLimits
- Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md).
- ApproachTelemetry
- .begin_flight
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
- SimInterface
- RegulatorKey
- Tensor
- GainMap
- NDArray
- Tensor
- SimInterface
- ArrayLike
- float32
- float64
- GainMap
- NDArray
- segments.py
- SimInterface
- GainSpace
- SimInterface
- control/approach.py
- SimInterface
- Linear
- Normal
- parametrize
- PPOMetrics
- .neutralize_airborne
- RunResult
- RuntimeState
- Scenario
- ScenarioProvider
- Sequential
- SFTDataset
- ShutdownReport
- StartMode
- fixture
- WeatherState
- ResilientSender
- RunSample
- DashboardServer
- Q: Почему прогон runs/20260816T174009.095580Z раскачивает самолёт и не сохраняет паритет с working_ics по логу logs/ics_pid_20260816_104551.csv?
- Q: Проанализировать три неудачных production-прогона против working_ics и составить план исправления
- Q: Почему production-заход терял паритет с working_ics и как это исправлено?
- Q: Каков финальный результат исправления runtime-паритета 2026-08-16?
- Q: Проанализировать run 20260816T213847.114116Z, сравнить управление с working_ics и исправить уход по GLIDESLOPE и неисполняемый go-around.
- FrictionProfile
- .rudder_cmd
- .send_outputs
- .prepare_go_around
- .run_id
- .view_names
- ApproachController
- ControlModeState
- EngagementInputs
- IntEnum
- str
- RunReader

## God Nodes (most connected - your core abstractions)
1. `ControllingSystem` - 141 edges
2. `Telemetry` - 125 edges
3. `ICSSim` - 80 edges
4. `ControlsState` - 57 edges
5. `XPlaneSim` - 54 edges
6. `airborne_inputs()` - 52 edges
7. `ICSInputs` - 51 edges
8. `PIDController` - 50 edges
9. `RunRecorder` - 50 edges
10. `Scenario` - 49 edges

## Surprising Connections (you probably didn't know these)
- `Autonomous Landing Controller` --semantically_similar_to--> `Autonomous Landing Controller`  [INFERRED] [semantically similar]
  CLAUDE.md → AGENTS.md
- `FakeConnector` --uses--> `FlightPhase`  [INFERRED]
  tests/fakes.py → ismpu/config/ics.py
- `HandshakeBench` --uses--> `FlightPhase`  [INFERRED]
  tests/fakes.py → ismpu/config/ics.py
- `_Clock` --uses--> `FlightPhase`  [INFERRED]
  tests/test_full_flight.py → ismpu/config/ics.py
- `_Clock` --uses--> `FlightPhase`  [INFERRED]
  tests/test_ics_engagement.py → ismpu/config/ics.py

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
- **PID Dashboard Ecosystem** — docs_xplane_dashboard_pid_dashboard, ismpu_gui_dashboard_pid_dashboard, ismpu_working_ics_ics_dashboard_ics_pid_monitor [INFERRED 0.85]

## Communities (249 total, 123 thin omitted)

### Community 0 - "criticality.py"
Cohesion: 0.09
Nodes (26): lateral_limit_m(), lateral_load_situation(), lateral_situation(), normal_load_situation(), IntEnum, Критерии критичности особых ситуаций МС-21 (Приложение 1 к ТЗ). Таблица АП-25…, Классификация скорости касания относительно VAPP и VВПП пред., Классификация нормальной перегрузки посадочного удара. `heavy` — взлётный вес. (+18 more)

### Community 3 - "test_weather.py"
Cohesion: 0.18
Nodes (13): compose_wind(), decompose_wind(), (скорость, откуда) → (crosswind, headwind) относительно курса ВПП. crosswind >…, (crosswind, headwind) → (скорость, откуда, °). Обратна `decompose_wind`., Тесты погоды: разбор ветра, шкала скользкости и чтение условий из пакета стенда., Для пробега существенна боковая составляющая, а не «скорость ветра» сама по…, Все семь кодов из фактических пакетов закрыты явно., test_crosswind_from_right_is_perpendicular() (+5 more)

### Community 4 - "ics_sim.py"
Cohesion: 0.16
Nodes (12): Стенд заказчика как источник телеметрии и приёмник команд. Единственный…, Типизированные backend-расширения общего SI-кадра., TelemetryExtensions, ICSBenchConnector, IntEnum, UDP-мост к стенду заказчика (порт 3030) — транспорт пути поставки. `ICSInputs`…, Мост к стенду: JSON поверх UDP, адрес стенда определяется из входящего пакета., Число последовательных best-effort ошибок текущего sender. (+4 more)

### Community 5 - "json_config.py"
Cohesion: 0.17
Nodes (29): approach_control_from_dict(), approach_control_to_dict(), _copy_approach(), dump_scenario(), _finite_tree(), ground_control_from_dict(), ground_control_to_dict(), _legacy_ground() (+21 more)

### Community 6 - "SimInterface"
Cohesion: 0.07
Nodes (9): BaseException, ApproachConfig, Пересобрать воздушный канал под заданные настройки. → новый канал. Именно…, StartMode, Минимальный lifecycle, одинаковый для стенда и X-Plane., SimInterface, _lost_engagement(), Снял ли стенд активность посреди прогона. → пора останавливаться. Без этой… (+1 more)

### Community 7 - "ControlsState"
Cohesion: 0.10
Nodes (45): ControlsState, Разделяемая по тактам структура команд — и наземных, и воздушных. Аннотации…, _colleague_controller(), _descent_frames(), _our_channel(), Воздушный канал: заход по ILS, выравнивание, скоростной канал. Главный тест…, Страховка от самообмана: сценарий обязан пройти выравнивание, иначе паритет его…, Угол сноса не должен превращаться в ошибку курса на локализаторе. (+37 more)

### Community 8 - "Scenario"
Cohesion: 0.09
Nodes (31): match_conditions(), _profile_name(), AircraftProfile, FailureMode, FlightSegment, WeatherState, Нормированная дистанция сцепления, ветра, осадков и видимости двух условий., Сравнить ожидаемые условия участка с одним фактическим кадром backend. (+23 more)

### Community 10 - "channels.py"
Cohesion: 0.18
Nodes (16): LateralDiagnostics, LongitudinalDiagnostics, Каналы управления и общий вектор команд. `ControlsState` — разделяемая по…, FailureState, Эффективности исполнительных органов. Аннотации типов обязательны: без них…, ActuatorFeedback, ActuatorVector, AllocationDiagnostics (+8 more)

### Community 11 - "LateralChannel"
Cohesion: 0.31
Nodes (5): GuidanceState, LateralChannel, Блок 2: runway guidance → единый нормированный yaw-запрос., Guidance по тому, что даёт стенд. → словарь guidance или None, если данных нет.…, Вернуть тот же ``GuidanceState``, который использует управляющий такт и…

### Community 13 - "test_diagnostic_tools.py"
Cohesion: 0.20
Nodes (19): build_altitude_sweep(), command_for_pulse(), Безопасные elevator/altitude authority sweep без дублирования ICS runner., Чистое преобразование, пригодное и для dry-run, и для ICSSim., safety_reason(), SweepLimits, SweepPulse, validate_pulse() (+11 more)

### Community 14 - "ICSOutputs"
Cohesion: 0.19
Nodes (15): ICSOutputs, Команды и mode flags, сериализуемые ровно в ожидаемый стендом JSON., Сериализовать enums и 14 reserved zeros в точные UTF‑8 bytes wire contract., _connector(), _full_payload(), Транспорт стенда: разбор телеметрии и отправка команд. На проводе чистый JSON…, Стенд делает UTF8.GetString() → JsonConvert. Любые байты перед JSON сломали бы…, Windows отдаёт WSAECONNRESET на UDP, если получатель закрыл порт. Ронять цикл… (+7 more)

### Community 15 - "test_run_matrix.py"
Cohesion: 0.11
Nodes (20): Разрешить только полный ``<шифр>/<номер>`` и вернуть точную строку JSON., resolve_matrix_run(), compose_matrix_scenario(), _install_through_scenarios(), Собрать сценарий из конкретных строк APPROACH/ROLLOUT/TAXI.…, Одна строка каталога → минимальный сценарий нужного участка или сквозной пары., Перенести накопленные overrides одного шифра на следующее условие этого же…, Собрать Б.4 из первой строки и заранее определённой пары законов. (+12 more)

### Community 16 - "AircraftProfile"
Cohesion: 0.08
Nodes (17): AircraftProfile, clamp(), get_aircraft_profile(), Профили преобразования команд ИСМПУ в органы управления X-Plane., Преобразовать воздушные команды ICD в нормированные DataRef X-Plane., Преобразовать нормированные команды пробега в DataRef X-Plane., Расширение реестра будущим профилем МС-21 без правки XPlaneSim., Проводка и масштабы конкретного планера X-Plane. (+9 more)

### Community 17 - "airborne_inputs"
Cohesion: 0.12
Nodes (22): Окончен ли воздушный участок. Два независимых признака, любой достаточен:…, touched_down(), `ICSInputs` → `Telemetry`: поля в СИ + «сырой» пакет для property. Стенд отдаёт…, airborne_inputs(), Кадр «ВС на глиссаде»: стойки не обжаты, ILS валиден, скорость и высота…, Носовая стойка обжимается позже основных — ждать её значит пропустить начало…, «Козление» после касания снимает обжатие на секунду — назад в заход…, Таблицы захода МС-21 к чистому крылу неприменимы — вести по ним нельзя.… (+14 more)

### Community 18 - "ApproachController"
Cohesion: 0.15
Nodes (20): ApproachLimits, ApproachTelemetry, ApproachController, ApproachResult, clamp(), ApproachConfig, Заход по ILS с выравниванием. Телеметрию получает параметром, не читает сам.…, Сброс регуляторов и всей памяти профиля — новый заход начинается с чистого… (+12 more)

### Community 19 - "DashboardServer"
Cohesion: 0.24
Nodes (5): DashboardServer, Loopback-only HTTP lifecycle вокруг одного ``DashboardState``., Фактически привязанные host/port, включая ephemeral port 0 в тестах., Идемпотентно запустить daemon HTTP thread., Отклонить pending tuning, остановить thread и закрыть listening socket.

### Community 20 - "test_icd_units.py"
Cohesion: 0.11
Nodes (17): Сверка каждого сигнала стенда с документами Заказчика. Два независимых…, 1 фут/мин = 0.3048/60 м/с. Приближение здесь копится на всём заходе., Нумерация фаз из doc-комментария `FlightPhase` в ICSInterface.cs., −26.5…55.0° — фактическое положение РУД во входной телеметрии, не команда., Наши константы обязаны совпадать с таблицей управляющих сигналов Заказчика., Тиллер задаётся ходом в миллиметрах. Отдельным тестом, потому что ошибка была…, 0–45 мм командует, 0–36.73 мм отчитывается. Подмена недодаёт ~18 % хода., В перечне управляющих сигналов абсолютного положения РУД нет — только скорость.… (+9 more)

### Community 21 - "XPlaneSim"
Cohesion: 0.05
Nodes (24): ApproachSetup, measured_landing_flaps(), Конфигурация по фактическому углу закрылков. `None` — положение не посадочное.…, _destination(), Посадочная конфигурация механизации; `None` — положение не посадочное. `None`…, Снимок готовности resettable backend для recorder/dashboard., XPlaneDiagnostics, AircraftProfile (+16 more)

### Community 23 - "PIDController"
Cohesion: 0.09
Nodes (31): PIDController, Сброс внутренних состояний (используется при выключении системы)., Забыть разрыв измерения, сохранив накопленный интеграл и текущий выход., test_ground_pids_use_working_ics_numerics_and_explicit_integrator_limits(), _legacy_reference(), Опциональная численность PID (шаг 5): каждый флаг проверяется на том дефекте,…, Если применено ровно то, что выдал PID, коррекции быть не должно., Уставка прыгает, объект стоит на месте — D-составляющая не должна реагировать.… (+23 more)

### Community 25 - "DashboardState"
Cohesion: 0.15
Nodes (9): _allocator_stage(), DashboardState, _first_present(), HTTP читает только immutable recorder objects; controller меняет control-thread., Вернуть только новые recorder updates; смена run_id принудительно сбрасывает…, JSON-ready форма ``snapshot`` для ``GET /api/state``., Вызывается runtime ровно в начале control tick., Сохранить фактически записанный effective config, не изменяя SCENARIOS. (+1 more)

### Community 26 - "test_xplane_backend.py"
Cohesion: 0.09
Nodes (23): ApproachSetup, Начальные условия захода X-Plane на продолжении оси и глиссады., Начальные условия быстрого старта непосредственно с пробега., Детерминированно seeded шум/пропуски, применяемые только resettable backend., SensorNoise, TouchdownSetup, DatagramSocket, MockXPlaneConnector (+15 more)

### Community 27 - "engaged_sim"
Cohesion: 0.12
Nodes (16): engaged_sim(), (sim, connector) с завершённым рукопожатием: стенд подтвердил `AgentIsActive =…, Регресс: расширение структуры не должно протащить руль высоты в маску пробега., test_ground_frame_still_declares_only_the_ground_channels(), Разделение органов из таблицы Заказчика: тиллер — на рулении, педальный пост —…, Базовый контур на стенде: `control_step` сам читает телеметрию и сам отправляет., На стенде каждый лишний `read_telemetry` — лишний приём UDP. Каждый такт явно…, Замолчать нельзя: последнее отклонение осталось бы приложенным до сторожа на… (+8 more)

### Community 29 - "IcsEngagement"
Cohesion: 0.04
Nodes (37): AircraftProfile, RunwayProfile, ControlModeState, Режим управления/индикации, передаваемый в каждом ICSOutputs., EngagementInputs, EngagementState, IcsEngagement, Enum (+29 more)

### Community 30 - "MatrixCase"
Cohesion: 0.11
Nodes (7): MatrixCase, Производная группировка строк одного шифра; исходные тексты живут в каталоге., ConditionMatch, Сверка ожидаемых условий с фактической телеметрией backend., Истина, если набор фактических отказов совпал ровно., Истина при практически нулевой нормированной дистанции погоды., Погода остаётся отчётной; неверный отказ делает прогон недопустимым.

### Community 31 - "RunRecorder"
Cohesion: 0.15
Nodes (9): Exception, Подключить best-effort аудит сырых успешно принятых/отправленных UDP payload., _mode_for(), Append-only writer; ошибка диска помечает прогон, но не выходит в control-loop., Дождаться записи всех ранее поставленных элементов и flush файлов., Поставить запись без блокировки control thread; переполнение инвалидирует run., Сохранить полный effective config; канонические config-файлы не затрагиваются., RunEvent (+1 more)

### Community 32 - ".invalid"
Cohesion: 0.15
Nodes (13): initial_segment(), is_airborne(), FlightSegment, Сообщает ли стенд, что ВС в воздухе и достаточно высоко для приёма захода.…, С какого участка начинать. Пробег — ответ по умолчанию (см. модуль)., Кадр «связи со стендом нет». Нули, а не None: контур проверяет `valid` первым., Размерный закон по нулям выдал бы правдоподобное отклонение по несуществующим…, test_no_bench_packet_means_no_airborne_command() (+5 more)

### Community 33 - "Graphify Pipeline"
Cohesion: 0.08
Nodes (29): Folder Watcher, URL Ingestion, Extra Graph Exports, MCP Graph Server, Confidence Audit Trail, Deterministic Node IDs, Semantic Extraction Contract, Cross-Repository Graph Merge (+21 more)

### Community 34 - "XPlaneConnector"
Cohesion: 0.06
Nodes (22): DataRefSample, Атомарно снять все свежие значения без раскрытия внутреннего mutable cache., Discard pre-reload values so readiness cannot use stale telemetry., Повторять RREF requests до получения всех значений либо подробного timeout., Отправить один нативный 509-byte DREF packet., Последнее значение DataRef и monotonic timestamp его UDP-пакета., Отправить один нативный CMND packet., Перезагрузить текущий самолёт без открытия aircraft chooser. (+14 more)

### Community 35 - "ControllingSystem"
Cohesion: 0.09
Nodes (35): Скопировать канонический preset и заменить только запрошенные условия запуска., ControllingSystem, Связать сценарий с контуром; PID активируются после определения участка., Разорвать D-history после пропуска устаревшей UDP-очереди, не трогая интегралы., Оркестратор классического контура поверх стенда (`envs.ics_sim.ICSSim`).…, Аварийная остановка: обнулить органы и **снять заявку каналов**. Именно…, Готовый кадр `Telemetry` для прямых вызовов `control_step(dt, telemetry,…, telemetry() (+27 more)

### Community 36 - "test_ground_controller.py"
Cohesion: 0.13
Nodes (21): Сколько устаревших UDP-кадров сброшено при последнем чтении., Scenario, Компактные перцентили миллисекунд без зависимости в критическом пути., Прогоняет один полёт на уже настроенном контуре., run(), _timing_summary(), _direct_ground_frame(), parametrize (+13 more)

### Community 37 - "test_ics_engagement.py"
Cohesion: 0.10
Nodes (49): _Clock, _engine(), _pump(), Автомат включения управления на стенде. Два раздельных предмета проверки: *…, По ICD стенд должен два секунды ПОЛУЧАТЬ ModeAIReady=1. Если считать одно лишь…, Обратная защита: 30 кадров можно выпалить за 0.1 с — время тоже обязано пройти., Срыв предусловия обнуляет и время, и счётчик кадров., Требование ICD — непрерывность: пропуск готовности рвёт серию. (+41 more)

### Community 38 - "run_reader.py"
Cohesion: 0.12
Nodes (19): _apply_recorded_gains(), _bool_or_none(), _equal(), main(), _number(), _parse_cell(), ControllingSystem, Единое потоковое чтение run-directory, replay и прежних CSV. (+11 more)

### Community 39 - "sft.py"
Cohesion: 0.13
Nodes (23): GuardResult, Фактически разрешённые gains и причина ограничений/fallback., apply_gain_vector(), controller_gain_vector(), _feature_value(), feature_vector(), gain_vector_from_row(), _number() (+15 more)

### Community 40 - ".enqueue_gain_update"
Cohesion: 0.25
Nodes (4): _finite(), _jsonable(), Проверить HTTP-запрос и поставить полный PID triplet в control-thread queue., Поставить восстановление gains начала запуска для активного участка.

### Community 41 - "fakes.py"
Cohesion: 0.07
Nodes (29): FlightPhase, IntEnum, Фаза полёта, сообщаемая стендом (`ICSInputs.FlightPhase`)., decode_airborne(), engaged_inputs(), flight_sim(), _integrate_throttle(), kinematic_sim() (+21 more)

### Community 43 - "runner.py"
Cohesion: 0.18
Nodes (20): ControlResult, airborne_control_mode(), airborne_flare_mode(), deactivate(), live_main(), main(), main_gear_contact(), make_airborne_output() (+12 more)

### Community 45 - "3. Этапы реализации"
Cohesion: 0.09
Nodes (21): 1. Подтверждённые проблемы и целевое состояние, 2. Ключевые интерфейсы, 3. Этапы реализации, 4. Тестирование и критерии готовности, 5. Зафиксированные допущения, 6.1. Один dashboard вместо двух, 6.2. Единый источник данных, 6.3. Представления (+13 more)

### Community 46 - ".from_checkpoints"
Cohesion: 0.28
Nodes (8): checkpoint_metadata(), Path, Сформировать audit metadata загруженного файла, включая SHA-256 содержимого., Загрузить независимые air/ground slots и проверить activation evidence для ICS., _checkpoint(), ndarray, test_checkpoint_contract_and_ics_activation_gate(), test_runtime_predicts_each_tick_after_40_frames_and_falls_back_before_it()

### Community 47 - "test_profiled_scenarios.py"
Cohesion: 0.11
Nodes (15): compose_scenario(), Any, Serialize only the canonical profile- and matrix-aware schema v3., Прочитать schema v3 либо явно мигрируемую v1/v2 конфигурацию., Сценарий по имени либо шифру матрицы, без различия раскладки А/B., Собрать сценарий из независимых источников участков., resolve_scenario(), test_preset_roundtrips_through_dict() (+7 more)

### Community 49 - "test_full_flight.py"
Cohesion: 0.09
Nodes (34): IntFlag, ControlValid, Константы интерфейса стенда заказчика (ПИВ / ICS). Единый источник правды по…, Биты `ControlValidMask`: какие каналы несёт команда. **Один бит на одно…, _air(), _Clock, _engaged_airborne_sim(), _pump() (+26 more)

### Community 50 - "test_go_around.py"
Cohesion: 0.10
Nodes (34): at_lateral_alignment_gate(), ils_blocker(), in_terminal_window(), Участки полёта и переходы между ними. Управление ведётся на всём интервале — от…, Последние футы перед касанием, где прерывать заход опаснее, чем доработать.…, Полоса подхода к гейту совмещения с осью ± 5 м: `(30 м, 30 м + band]`. Только в…, Почему нельзя продолжать заход по этому кадру. `None` — можно. Закон читает…, GoAroundManeuver (+26 more)

### Community 51 - "Hybrid Neural PID Controller"
Cohesion: 0.70
Nodes (5): Hybrid Neural PID Controller, Neural PID Gain Scheduler, PPO Training Loop, Preset-Anchored Deterministic Shield, SFT Behavioral-Cloning Warm Start

### Community 52 - "test_approach_criteria.py"
Cohesion: 0.18
Nodes (12): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, Отдельный монитор критерия А.1.1 (не участвует в go-around)., Захватывает А.1.1 после входа в допуск и завершает оценку на 300 ft., frame() (+4 more)

### Community 53 - "._approach_step"
Cohesion: 0.10
Nodes (12): above_decision_height(), ВС выше высоты решения ухода на второй круг (30 м по ТЗ 5.1.1.2). → уход…, Такт воздушного участка. → True, если управлять больше нечем. Касание…, Зафиксировать `Approach → Landing` на 25 ft без смены воздушного закона., Прервать заход с названной причиной. → True (управлять больше нечем)., Реверс убран: команды обратной тяги нулевые. В воздухе реверс не выдаётся…, Нужно ли уходить на второй круг по этому такту. → причина или `None`. Только…, Начать уход: зафиксировать состояние манёвра и высоту входа. (+4 more)

### Community 54 - "run_artifacts.py"
Cohesion: 0.16
Nodes (18): Вернуть одно свежее значение; stale/missing представлены ``None``., controller_pids(), _csv_value(), default_runs_root(), _effective_configs(), gains_snapshot(), _git_state(), _jsonable() (+10 more)

### Community 55 - "RunwayTracker"
Cohesion: 0.12
Nodes (12): Точка на продолжении оси; положительное расстояние — до порога., Решить прямую геодезическую задачу на сферической Земле., Геодезическое guidance в истинной системе направлений., Guidance по курсу ВПП и измеренному отклонению — без собственной геодезии.…, Возвращает отклонение от осевой линии в метрах. >0 - правее оси, <0 - левее., Геодезическое наведение на ось ВПП с упреждением по скорости., RunwayTracker, test_guidance_on_centerline_small_heading_error() (+4 more)

### Community 56 - "RomanLogImporter"
Cohesion: 0.19
Nodes (10): _number(), Path, Импорт и проверка внешних CSV-прогонов roman_aviacia_ics., Потоково нормализует основной и authority CSV Романа., RomanLogImporter, verify_manifest(), fixture, roman_csv() (+2 more)

### Community 57 - "working_ics/approach_criteria.py"
Cohesion: 0.21
Nodes (7): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, ICSInputs, Evaluate the A.1.1 approach segment and stop at a radio-altitude floor.

### Community 58 - "test_dashboard.py"
Cohesion: 0.20
Nodes (13): _live(), _post(), parametrize, test_active_pid_is_editable_in_classical_and_shadow(), test_gain_change_is_queued_bumpless_and_records_full_event(), test_http_api_is_incremental_pending_and_loopback_only(), test_incremental_snapshot_uses_recorder_objects_and_stays_small_when_idle(), test_live_and_replay_use_the_same_dashboard_snapshot() (+5 more)

### Community 59 - "pretrain.py"
Cohesion: 0.10
Nodes (29): _fit_feature_normalization(), _normalized_mse(), _physical_bounds(), _predict(), ndarray, Офлайн-SFT двух PID gain-регрессоров из принятых ``approach/ground.csv``., Стратифицировать по условиям, назначая целый run ровно одному split., Один принятый прогон, уже приведённый к матрицам признаков и целей.… (+21 more)

### Community 60 - "_load_updates"
Cohesion: 0.25
Nodes (5): _load_updates(), RunReader, Закрыть tuning и записать отказ для каждого неисполненного запроса., После recorder.finish держать полный run доступным, но только для чтения., RunEvent

### Community 61 - "test_control_parity.py"
Cohesion: 0.11
Nodes (20): CompletionRule, Enum, Генератор эталонной кривой скорости пробега. Два закона замедления: колокол…, Как активный наземный сценарий заканчивает управление., Генератор эталонной кривой скорости (Колокол Гаусса)., Начать профиль с фактической скорости текущего участка., То же без лишнего round-trip м/с → узлы → м/с на касании., Возвращает идеальную скорость (м/с) для текущей точки пути. (+12 more)

### Community 62 - "Project Dependencies"
Cohesion: 0.29
Nodes (7): Optional Gymnasium, NumPy, Pandas, Project Dependencies, Pytest, Termcolor, Optional PyTorch

### Community 64 - "PidGainRegressor"
Cohesion: 0.11
Nodes (18): device, GainGuard, PidGainRegressor, Any, Минимальная SFT-модель абсолютных коэффициентов PID и общий runtime guard., Предсказать gains по последнему hidden state окна ``(B,T,F)``., Сохранить веса вместе с полным train↔runtime контрактом., Загрузить модель только после проверки полного train↔runtime контракта. (+10 more)

### Community 66 - "dashboard_core.py"
Cohesion: 0.14
Nodes (13): DashboardSnapshot, GainChange, main(), _mean(), Один локальный dashboard для live RunRecorder и read-only replay., Запустить локальный read-only replay dashboard до ``Ctrl+C``., Отображаемое имя, PID source и физическая фаза одной панели графика., Immutable запрос HTTP-thread, ожидающий применения control-thread. (+5 more)

### Community 67 - "test_tolerance.py"
Cohesion: 0.15
Nodes (23): evaluate_approach_tolerances(), _glideslope_tolerance_deg(), ApproachLimits, ApproachTelemetry, FailureMode, Монитор допусков захода в реальном времени + классификация особой ситуации.…, Результат проверки допусков захода на одном такте. `landing_allowed` — все ли…, Допуск по глиссаде с учётом отказа (ТЗ 5.1.2.1–5.1.2.3), самый мягкий из… (+15 more)

### Community 68 - "test_working_ics_dashboard.py"
Cohesion: 0.35
Nodes (10): ClearWeatherILSController, DashboardState, _controller(), _inputs(), Characterization tests for the bench-validated ``working_ics`` dashboard., _record(), test_dashboard_records_four_airborne_views_and_diagnostics(), test_gain_updates_are_immediate_validated_and_share_pitch_with_flare() (+2 more)

### Community 70 - "Telemetry"
Cohesion: 0.09
Nodes (13): Телеметрия стенда, приведённая к **СИ**. Проверять надо `valid` **до** полей:…, Невалидные ICS-сигналы, которые воздушный закон читает безусловно., Приборная скорость (kt → м/с). Отсечки реверса заданы по ней, а не по путевой., Радиовысота **в футах** — единицы стенда. Порог воздушного включения (400…, Объявлены ли валидными **оба** канала ILS (курсовой и глиссадный). `None` —…, Боковое отклонение от оси, измеренное стендом. Позволяет не считать геодезию…, Обжатие ВСЕХ стоек. Диагностический сигнал; условие включения проверяет сам…, Фаза полёта по `config.ics.FlightPhase` — по ней распознаётся уже идущий пробег. (+5 more)

### Community 71 - "Unified Profile-Aware Scenario System"
Cohesion: 0.33
Nodes (6): Technical-Specification Acceptance Gates, Forward-Only Flight Segment Supervisor, Longitudinal and Lateral Ground Channels, PID Run Matrix, Unified Profile-Aware Scenario System, Legacy Scenario Preset Model

### Community 72 - "Interactive PID Dashboard"
Cohesion: 0.25
Nodes (9): Nine-View PID Dashboard, Run Recording Artifacts, buildTabs, draw, Gain Tuning and Snapshot Export, Interactive PID Dashboard, refresh, render (+1 more)

### Community 73 - "MatrixRun"
Cohesion: 0.08
Nodes (16): MatrixCondition, MatrixRun, normalize_code(), _number(), Any, FailureMode, FlightSegment, WeatherState (+8 more)

### Community 74 - "DashboardState"
Cohesion: 0.36
Nodes (3): DashboardState, Any, ICSInputs

### Community 75 - "failures.py"
Cohesion: 0.25
Nodes (6): FailureManager, FailureMode, Enum, Модель отказов бортового оборудования. `FailureState` хранит мультипликативные…, Проецирует набор дискретных отказов в эффективности исполнительных органов., Привести состояние ровно к набору `modes` (то, что сообщил стенд). Пересборка с…

### Community 76 - "ICSInterface.cs"
Cohesion: 0.36
Nodes (7): External.Systems.ICS, ControlModeState, GearState, ICSInputs, ICSOutputs, ReverseEngineType, UInt64

### Community 77 - "План исправления"
Cohesion: 0.12
Nodes (15): 1. Handshake не повторяет рабочую последовательность, 2. Runtime работает с другой частотой и другой топологией, 3. RunRecorder находится в управляющем потоке, 4. Go-around имеет две отдельные ошибки, 5. Production entrypoint сейчас загрязнён debug-путём, ElevatorCmd действительно отправлялся, Найденные причины, План исправления (+7 more)

### Community 78 - "run_pretrain"
Cohesion: 0.29
Nodes (8): cli(), PretrainRunConfig, Последовательно обучить выбранные участки из одного каталога принятых прогонов., CLI офлайн-обучения; сеть никогда не открывает UDP и не сбрасывает X-Plane., Пути и участки для CLI, обучающего независимые air/ground checkpoints., Итог обучения участка и данные, необходимые для автоматической проверки gate., run_pretrain(), TrainingResult

### Community 79 - "promote_candidate.py"
Cohesion: 0.33
Nodes (15): _gain_patch(), main(), promote_candidate(), PromotionError, Path, Проверяемое продвижение dashboard candidate в sparse scenario override., Пересчитать matrix/config hashes, а не доверять двум согласованно изменённым…, Проверить run и записать новый scenario JSON; registry исходников не меняется. (+7 more)

### Community 80 - "ICS PID Monitor"
Cohesion: 0.22
Nodes (9): Bench-Validated ILS Approach Channel, Tolerance-Gated Go-Around, buildControls, draw, formatTime, Four-Loop PID Tuning, ICS PID Monitor, Live and Historical Timeline (+1 more)

### Community 81 - "test_working_ics_port.py"
Cohesion: 0.19
Nodes (8): ICSInputs, Hand the validated airborne session to Vlayd's existing rollout loop. The…, Keep Vlayd's engagement latch synchronized during the approach., Run Vlayd's rollout until taxi speed, then send its taxi handoff., VlaydRolloutBridge, test_rollout_bridge_preserves_engagement_and_switches_without_off(), test_roundout_commands_a_material_pitch_increase_before_touchdown(), test_terminal_pitch_hold_starts_before_last_five_feet_guidance_cutoff()

### Community 82 - "Autonomous Landing Controller"
Cohesion: 0.25
Nodes (8): Autonomous Landing Controller, Fourteen-Bit ControlValidMask Layout, Two-Factor ICS Engagement Handshake, ICS UDP JSON Protocol, Repository Guidance for Codex, Telemetry SI Unit Boundary, Autonomous Landing Controller, Repository Guidance for Claude Code

### Community 83 - "X-Plane Dashboard and Runtime Guide"
Cohesion: 0.43
Nodes (7): Dual-Backend SimInterface, ICS-Only Backend Guidance, Aircraft-Profile Checkpoint Isolation, Live A330 Acceptance Checklist, Profile-Aware Flight Scenarios, X-Plane Dashboard and Runtime Guide, X-Plane Resettable Runtime

### Community 84 - "test_working_ics_golden.py"
Cohesion: 0.26
Nodes (11): Касание: обжата **любая основная** стойка. Носовая не участвует — она…, _assert_numeric_result(), ICSInputs, Characterization baseline of the bench-validated ``working_ics`` approach., Канонический контур и формирователь пакета совпадают с эталоном до 1e-12., _replay(), _rows(), _state() (+3 more)

### Community 86 - "run_report.py"
Cohesion: 0.07
Nodes (59): Приёмочные пороги из ТЗ (раздел 5). Единый источник истины для runtime…, _check(), Criterion, evaluate_matrix_run(), evaluate_tz(), _range_check(), Чистые функции приёмки телеметрии по ТЗ и строкам матрицы. Каждый критерий…, Преобразовать наземные метрики запуска в вердикты раздела 5 ТЗ. (+51 more)

### Community 87 - "scenarios.py"
Cohesion: 0.09
Nodes (33): ApproachConfig, Настройки воздушного участка: заход по ILS, выравнивание, управление скоростью.…, Параметры воздушного контура. Значения по умолчанию — настроенные на стенде.…, ControlProfile, _copy_approach(), _copy_ground(), _ground_matrix_drafts(), _ground_segments_for_spec() (+25 more)

### Community 88 - "import_workbook"
Cohesion: 0.39
Nodes (8): import_workbook(), main(), Any, Path, Одноразовый импорт исходной Excel-матрицы в runtime-каталог JSON., Прочитать книгу целиком; функция не используется production runtime., _scalar(), write_catalog()

### Community 89 - "envelope.py"
Cohesion: 0.14
Nodes (19): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), Enum (+11 more)

### Community 90 - ".setup"
Cohesion: 0.15
Nodes (9): CompletionRule, LongitudinalChannel, Блок 1: скорость → симметричная база тормозов и реверса., Сбросить PID и привязать начало профиля к фактической скорости касания/старта., PIDController, PidMap, ReferenceTrajectory, RunwayTracker (+1 more)

### Community 91 - "test_campaign.py"
Cohesion: 0.29
Nodes (14): campaign_phase(), campaign_rows(), campaign_summary(), _config_status(), main(), next_campaign_row(), Path, Порядок и фактический статус кампании из 280 матричных прогонов. (+6 more)

### Community 92 - "static_sim"
Cohesion: 0.14
Nodes (14): decode_outputs(), Отправленные команды в нормированном виде — для сравнения траекторий.…, `ICSOutputs` → (brake_l, brake_r, thr_l_rate, thr_r_rate, steer), всё…, (sim, connector) с неизменным кадром у порога ВПП. Скорость задаётся в **м/с**.…, static_sim(), NWS_FAIL отключает стойку/педаль, но оставляет руль и дифференциальные органы., Стенд при обрыве связи отдаёт НУЛИ с valid=False, а не None. Проверка «поле is…, test_control_step_emits_five_bounded_commands() (+6 more)

### Community 93 - "ICSSim"
Cohesion: 0.06
Nodes (26): ConditionMatch, _clamp(), ICSSim, ControlsState, FailureMode, FlightSegment, Scenario, StartMode (+18 more)

### Community 94 - "loop.py"
Cohesion: 0.12
Nodes (17): ControlDiagnostics, Enum, Общий контракт симулятора и воздушных сигналов. ICS и X-Plane различаются…, Результат безусловного best-effort отключения backend., Исчерпывающие причины штатного/аварийного завершения единого runtime loop., Причина остановки вместе с best-effort результатом освобождения backend., Backend-neutral диагностические значения текущего управляющего такта., RunResult (+9 more)

### Community 95 - "Q: Приступай к выполнению этапа 9 плана [plan.md](docs/plan.md). В процессе старайся упрощать код, удалять лишний и неиспользуемый код, а также максимально покрывать его комментариями."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 9 плана [plan.md](docs/plan.md). В процессе старайся упрощать код, удалять лишний и неиспользуемый код, а также максимально покрывать его комментариями., Source Nodes

### Community 109 - "RunReader"
Cohesion: 0.17
Nodes (10): Path, Run-directory и любой поддержанный CSV через один streaming API., RunReader, _frame(), _record_ground_run(), test_approach_stream_has_three_pid_states_and_replays_at_1e_12(), test_legacy_adapter_does_not_invent_missing_pid_terms(), test_report_contains_matrix_metrics_and_aggregation_uses_workbook_columns() (+2 more)

### Community 110 - "Q: Приступай к выполнению этапа 9 плана docs/plan.md; упрощай код, удаляй лишнее и добавляй комментарии."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 9 плана docs/plan.md; упрощай код, удаляй лишнее и добавляй комментарии., Source Nodes

### Community 111 - "Q: Реализовать этап 0: baseline, golden replay и dashboard characterization"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Реализовать этап 0: baseline, golden replay и dashboard characterization, Source Nodes

### Community 112 - "Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md)., Source Nodes

### Community 115 - "test_ics_sim.py"
Cohesion: 0.05
Nodes (53): FakeConnector, make_ics_inputs(), on_ground(), Статический стенд: всегда один и тот же кадр, отправленное — в `sent_outputs`., Полный пакет стенда: нули по умолчанию + заданные поля., Кадр «ВС на полосе»: обжаты все стойки, курс/координаты у порога UUEE 06R., _cold_sim(), Тесты стенда (`ICSSim`) и подбора сценария — без реального стенда. (+45 more)

### Community 116 - "Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)., Source Nodes

### Community 117 - "roll_limit_deg"
Cohesion: 0.50
Nodes (4): Предел крена по высоте: чем ниже, тем меньше запас до касания законцовкой.…, roll_limit_deg(), Чем ниже, тем меньше запас до касания законцовкой; настроенный предел не…, test_roll_limit_tightens_towards_the_ground()

### Community 118 - "weather.py"
Cohesion: 0.21
Nodes (8): Геометрия целевой ВПП и высоты установки ЛА. Смена целевой полосы = правка…, Enum, Погодные условия эпизода: описание, шкала сцепления и разбор ветра. Модуль **не…, Состояние ВПП как **монотонная шкала скользкости** 0…15 (0 — сухо, 15 — лёд со…, RunwayCondition, Converts, Преобразовать координату из градусов, минут и секунд в signed degrees., Коэффициенты перевода единиц на границе телеметрии и управления.

### Community 123 - "test_sft_regressors.py"
Cohesion: 0.11
Nodes (23): Dataset, feature_schema_hash(), Стабильный hash порядка признаков; перестановка является сменой контракта., Оценить mean/scale и обучающие min/max по конечной двумерной выборке., _condition_key(), load_offline_dataset(), Path, Прочитать только PASS/accepted/classical run-directories; live backend не… (+15 more)

### Community 124 - "_faults_from_inputs"
Cohesion: 0.50
Nodes (3): _faults_from_inputs(), Отказы, о которых сообщает борт — **единственный** источник истины об отказах.…, Сигналы отказов со стенда → наши `FailureMode`. Отказы шасси…

### Community 125 - "GuidanceState"
Cohesion: 0.29
Nodes (3): GuidanceState, Совместимость с прежним атрибутом; новый термин явно указывает ось., Совместимость со старым словарным API.

### Community 126 - ".compute"
Cohesion: 0.18
Nodes (5): → (интеграл только с утечкой, интеграл с утечкой и приращением). Оба уже зажаты., Такт регулятора. `measurement` обязателен при `derivative_on_measurement=True`., Back-calculation: подтянуть интегратор к фактически применённой команде. No-op…, Сменить коэффициенты без сброса D-history и с компенсацией интегратором.…, Вес апериодического фильтра D-составляющей за такт `dt`.

### Community 127 - ".from_csv"
Cohesion: 0.22
Nodes (7): _gain_ranges(), _gains_from_manifest(), _gains_from_samples(), _handler_factory(), Path, Построить read-only state из run-directory либо поддерживаемого CSV., Build safe dashboard sliders from the scenarios users can actually run. The…

### Community 128 - ".control_step"
Cohesion: 0.18
Nodes (5): Привести модель отказов к тому, что сообщает борт (`ICSInputs.Fault*`). Отказы…, Такт управления. → True, если управление окончено (или телеметрия невалидна).…, Три блока: speed controller → guidance → allocator., Передать управление в руление (`ControlMode 3 → 4`) — пробег окончен.…, Back-calculation по итоговым командам. No-op, пока у PID не задан…

### Community 129 - "Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md)., Source Nodes

### Community 130 - "Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md)., Source Nodes

### Community 131 - "system.py"
Cohesion: 0.13
Nodes (11): Глобальные константы контура управления (перенесены из main.ipynb)., Типы и порядок коэффициентов пяти наземных PID-регуляторов. Модуль намеренно не…, Полностью пересобрать наземные каналы controller этой конфигурацией., PIDDiagnostics, Пропорционально-интегрально-дифференциальный регулятор. Класс сохраняет прежнюю…, Типизированный снимок последнего такта регулятора., Оркестратор классического контура управления — на всём интервале полёта.…, apply_ground_control() (+3 more)

### Community 135 - "Q: Приступай к выполнению этапа 2 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 2 плана docs/plan.md, Source Nodes

### Community 137 - "LandingFlapConfiguration"
Cohesion: 0.36
Nodes (10): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+2 more)

### Community 139 - "protocol.py"
Cohesion: 0.25
Nodes (6): ControlModeState, GearState, ICSOutputs, Any, IntEnum, ReverseEngineType

### Community 141 - "ICSInputs"
Cohesion: 0.24
Nodes (6): ICSInputs, Неизвестные поля исходного JSON; они доступны аудиту, но не закону управления., Приём телеметрии стенда. Адрес отправителя определяется автоматически., Дождаться кадра и отбросить накопившийся UDP backlog, оставив самый свежий.…, Зафиксировать и разобрать один уже принятый UDP payload., Полная известная входная схема стенда; единицы определены в ``ICSInterface.cs``.

### Community 142 - "pid_controller.py"
Cohesion: 0.16
Nodes (14): roll_limit_deg(), Exact package port of the ICS approach contour validated in ``aviacia_v2``. The…, angle_error_deg(), clamp(), ClearWeatherILSController, ControllerConfig, ControlResult, PID (+6 more)

### Community 146 - ".from_ics"
Cohesion: 0.22
Nodes (7): WeatherState, Фактические погодные условия со стенда (ветер, сцепление, осадки, видимость)., `ICSInputs` → `WeatherState`. Единственный источник фактической погоды. Стенд…, `Visibility` в футах. Без пересчёта 16000 футов читались бы как «ясно» вместо…, test_visibility_is_converted_from_feet(), Стенд шлёт узлы и **футы**; в WeatherState видимость — в метрах., test_from_ics_converts_units()

### Community 149 - "WeatherState"
Cohesion: 0.25
Nodes (7): Any, Погодные условия. Поля — ровно то, что сообщает стенд (см. `from_ics`).…, Собирает ветер из компонент относительно курса ВПП. `crosswind_kts` > 0 — ветер…, Сериализация в примитивы (для логирования/воспроизводимости сценариев)., WeatherState, test_scenario_roundtrip_with_weather_and_failures(), test_weatherstate_from_crosswind()

### Community 154 - "Normalization"
Cohesion: 0.15
Nodes (12): ArrayLike, float32, float64, Normalization, NDArray, Выполнить deterministic inference и вернуть физические gains плюс OOD flag., Проверить prediction и ограничить его относительно accepted preset/предыдущего…, Покомпонентная standardization и границы обучающей выборки. (+4 more)

### Community 155 - "test_refactoring_contracts.py"
Cohesion: 0.14
Nodes (15): find_earth_nav_dat(), get_runway_profile(), ILSStation, parse_ils_station(), Path, Профили ВПП и разрешение ILS из установленной базы X-Plane., Найти LOC (тип 4) без хардкода частоты., RunwayProfile (+7 more)

### Community 158 - "Q: Приступай к выполнению этапа 4 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 4 плана docs/plan.md, Source Nodes

### Community 159 - ".from_dict"
Cohesion: 0.22
Nodes (8): GearState, Разбор телеметрии стенда с совместимостью вперёд. Асимметрия намеренная (JSON-…, Дискретное положение стойки в кодировке ICSInputs., Подставить ноль значило бы выдумать телеметрию, по которой считается управление., Новый сигнал не роняет разбор и не входит в закон, но не теряется для записи., test_missing_fields_raise_instead_of_defaulting_to_zero(), test_parses_a_complete_payload(), test_unknown_fields_are_preserved_for_audit_but_not_exposed_as_signals()

### Community 162 - "runway_condition_from_bench"
Cohesion: 0.25
Nodes (8): Код состояния ВПП со стенда → наша шкала. Неизвестный код трактуется как `ICY`,…, runway_condition_from_bench(), Коды из фактических пакетов переводятся в свою шкалу скользкости., test_runway_condition_codes_are_remapped_not_passed_through(), Коды стенда не упорядочены по скользкости: WET RUBBER=14 близок к WET=2. Подать…, Предположить сухую полосу — разрешить максимальное торможение там, где оно…, test_bench_codes_map_to_a_monotone_slipperiness_scale(), test_unknown_bench_code_is_treated_as_slippery()

### Community 167 - "Q: Приступай к выполнению этапа 8 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 8 плана [plan.md](docs/plan.md)., Source Nodes

### Community 168 - "HandshakeBench"
Cohesion: 0.29
Nodes (4): HandshakeBench, Стенд, включающий управление только после корректного рукопожатия. Ждёт…, Стенд включается по полученной готовности, а не по нашему представлению о ней., test_the_airborne_handshake_is_actually_transmitted_before_approach()

### Community 176 - ".from_json"
Cohesion: 0.33
Nodes (5): _pid_from_colleague(), Загрузка настроек из JSON коллеги (`config/ics_clear_weather_pid.json`). Секции…, `PIDConfig` коллеги → аргументы нашего `PIDController`. Предел интегратора у…, Наши умолчания и его файл — одно и то же. Разойдутся — расхождение должно быть…, test_config_from_the_colleague_json_matches_our_defaults()

### Community 181 - "Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md)., Source Nodes

### Community 183 - ".begin_flight"
Cohesion: 0.19
Nodes (11): approach_blocker(), ApproachRefused, Воздушный участок начинать нельзя — с названной причиной. Отдельное исключение,…, Можно ли вообще судить об участке по этому кадру. Кадр без пакета стенда…, Почему нельзя вести заход по этому кадру. `None` — можно. Пока проверка одна,…, segment_is_decidable(), FlightSegment, Пересобрать stateful PID и уведомить backend до первого такта участка. (+3 more)

### Community 208 - "segments.py"
Cohesion: 0.40
Nodes (5): FlightSegment, Enum, str, Канонические участки управляемого интервала полёта., Участок, для которого выбираются закон управления и условия сценария.

### Community 212 - "control/approach.py"
Cohesion: 0.33
Nodes (5): angle_error_deg(), Воздушный канал: заход по ILS, выравнивание, управление скоростью. Перенос…, Разность курсов, приведённая к (-180, 180]., ApproachData, Backend-независимый срез сигналов для захода и ухода на второй круг.

### Community 218 - ".neutralize_airborne"
Cohesion: 0.33
Nodes (3): Обнуляет все органы управления. Отправку делает вызывающий через `ICSSim.step`.…, Сброс к нейтральным командам — новый эпизод начинается с чистого состояния.…, Обнулить только воздушные команды. Нужно, когда воздушный канал не может…

### Community 229 - "ResilientSender"
Cohesion: 0.33
Nodes (3): Отправка best-effort со счётчиком ошибок и разрежённым логом. Windows отдаёт…, → True если отправлено. Исключение наружу не выпускается., ResilientSender

### Community 230 - "RunSample"
Cohesion: 0.33
Nodes (3): Один такт: вход, команда и диагностика имеют общий ``tick_id``., Атомарный incremental slice для dashboard, без чтения controller., RunSample

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
- **110 isolated node(s):** `ElevatorCmd действительно отправлялся`, `1. Handshake не повторяет рабочую последовательность`, `2. Runtime работает с другой частотой и другой топологией`, `3. RunRecorder находится в управляющем потоке`, `4. Go-around имеет две отдельные ошибки` (+105 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **123 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `MatrixRun` (3× useful, score=2.98124288)
- `XPlaneSim` (3× useful, score=2.967667554)
- `PidGainRegressor` (2× useful, score=1.989605352)
- `rollout_bridge.py` (2× useful, score=1.989605352)
- `loop.py` (2× useful, score=1.968354898) _(code changed — re-verify)_
- `LateralChannel` (2× useful, score=1.931298235)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Unified Profile-Aware Scenario System` and `Legacy Scenario Preset Model`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Dual-Backend SimInterface` and `ICS-Only Backend Guidance`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Telemetry` connect `Telemetry` to `.control_step`, `system.py`, `ics_sim.py`, `SimInterface`, `ControlsState`, `Scenario`, `channels.py`, `LateralChannel`, `ICSInputs`, `ICSOutputs`, `test_diagnostic_tools.py`, `airborne_inputs`, `ApproachController`, `.from_ics`, `test_icd_units.py`, `XPlaneSim`, `test_xplane_backend.py`, `test_refactoring_contracts.py`, `IcsEngagement`, `MatrixCase`, `.invalid`, `ControllingSystem`, `test_ground_controller.py`, `HandshakeBench`, `fakes.py`, `test_full_flight.py`, `test_go_around.py`, `test_approach_criteria.py`, `._approach_step`, `.begin_flight`, `test_control_parity.py`, `test_tolerance.py`, `test_working_ics_port.py`, `control/approach.py`, `test_working_ics_golden.py`, `scenarios.py`, `.setup`, `static_sim`, `ICSSim`, `loop.py`, `RunReader`, `test_ics_sim.py`, `_faults_from_inputs`?**
  _High betweenness centrality (0.164) - this node is a cross-community bridge._
- **Why does `ControllingSystem` connect `ControllingSystem` to `.control_step`, `system.py`, `ics_sim.py`, `SimInterface`, `Scenario`, `test_run_matrix.py`, `airborne_inputs`, `ApproachController`, `PIDController`, `test_xplane_backend.py`, `engaged_sim`, `test_refactoring_contracts.py`, `MatrixCase`, `XPlaneConnector`, `test_ground_controller.py`, `sft.py`, `fakes.py`, `.from_checkpoints`, `test_full_flight.py`, `test_go_around.py`, `test_approach_criteria.py`, `._approach_step`, `.begin_flight`, `test_dashboard.py`, `test_control_parity.py`, `Telemetry`, `test_working_ics_port.py`, `scenarios.py`, `.setup`, `test_campaign.py`, `static_sim`, `loop.py`, `RunReader`, `test_ics_sim.py`, `test_sft_regressors.py`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Why does `ICSInputs` connect `ICSInputs` to `ics_sim.py`, `ICSOutputs`, `airborne_inputs`, `ApproachController`, `DashboardServer`, `WeatherState`, `DashboardState`, `RunRecorder`, `.from_dict`, `ControllingSystem`, `HandshakeBench`, `fakes.py`, `runner.py`, `_FakeSocket`, `run_artifacts.py`, `dashboard_core.py`, `test_working_ics_dashboard.py`, `Telemetry`, `test_working_ics_port.py`, `control/approach.py`, `ICSSim`, `RunSample`, `FrictionProfile`, `test_ics_sim.py`, `weather.py`, `_faults_from_inputs`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `ControllingSystem` (e.g. with `ApproachSetup` and `ConditionMatch`) actually correct?**
  _`ControllingSystem` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 51 inferred relationships involving `Telemetry` (e.g. with `ApproachSetup` and `ConditionMatch`) actually correct?**
  _`Telemetry` has 51 INFERRED edges - model-reasoned connections that need verification._