# Graph Report - GOSNIIASProject  (2026-08-16)

## Corpus Check
- 132 files · ~135,982 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2442 nodes · 5312 edges · 230 communities (106 shown, 124 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 368 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `df50b40a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- criticality.py
- GainMap
- ndarray
- test_weather.py
- run_reader.py
- json_config.py
- SimInterface
- ControlsState
- Scenario
- GainKey
- ground_allocator.py
- LateralChannel
- float32
- test_refactoring_contracts.py
- ICSOutputs
- scenario_for_matrix_run
- AircraftProfile
- ils_blocker
- ApproachResult
- DashboardServer
- weather.py
- XPlaneSim
- Any
- PIDController
- ndarray
- DashboardState
- test_xplane_backend.py
- engaged_sim
- Any
- IcsEngagement
- .__init__
- RunRecorder
- .invalid
- Graphify Pipeline
- XPlaneConnector
- ControllingSystem
- test_ground_controller.py
- test_ics_engagement.py
- RunReader
- sft.py
- .snapshot
- HandshakeBench
- floating
- ICSInputs
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
- ICSInputs
- test_dashboard.py
- pretrain.py
- GainChange
- test_control_parity.py
- Project Dependencies
- loop.py
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
- ClearWeatherILSController
- FailureState
- ICSInterface.cs
- DatagramSocket
- run_pretrain
- promote_candidate.py
- ICS PID Monitor
- segments.py
- Autonomous Landing Controller
- X-Plane Dashboard and Runtime Guide
- test_working_ics_golden.py
- GainSpace
- run_report.py
- scenarios.py
- import_workbook
- envelope.py
- LongitudinalChannel
- pid.py
- static_sim
- ICSSim
- ics_sim.py
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
- IntEnum
- Q: Приступай к выполнению этапа 9 плана docs/plan.md; упрощай код, удаляй лишнее и добавляй комментарии.
- Q: Реализовать этап 0: baseline, golden replay и dashboard characterization
- Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md).
- ICSBenchConnector
- ndarray
- test_ics_sim.py
- Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md).
- roll_limit_deg
- IntEnum
- ControlModeState
- ICSInputs
- ICSOutputs
- socket
- test_sft_regressors.py
- _faults_from_inputs
- GuidanceState
- .compute
- .from_csv
- test_adopts_rollout_from_the_flight_phase
- Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md).
- Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md).
- control.py
- device
- int64
- PIDController
- Q: Приступай к выполнению этапа 2 плана docs/plan.md
- ICSInputs
- .confirmed
- TypedDict
- ApproachConfig
- FailureMode
- .request_landing
- pid_controller.py
- ControlModeState
- ApproachChannel
- ICSOutputs
- ApproachConfig
- FailureState
- AircraftProfile
- ControlsState
- PidMap
- Any
- PidMap
- ApproachConfig
- Normalization
- fakes.py
- Scenario
- Path
- Q: Приступай к выполнению этапа 4 плана docs/plan.md
- ConditionMatch
- RewardWeights
- TypedDict
- Scenario
- ControlsState
- aircraft_profiles.py
- RegulatorKey
- FailureMode
- Q: Приступай к выполнению этапа 8 плана [plan.md](docs/plan.md).
- ApproachSetup
- FlightSegment
- ICSInputs
- PidMap
- Scenario
- Any
- ArrayLike
- float32
- TouchdownSetup
- NDArray
- ControllingSystem
- Tensor
- ApproachLimits
- Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md).
- ApproachTelemetry
- initial_segment
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
- Scenario
- SimInterface
- GainSpace
- SimInterface
- ControlsState
- SimInterface
- Linear
- Normal
- parametrize
- PPOMetrics
- RunReader
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
- XPlaneConnector

## God Nodes (most connected - your core abstractions)
1. `ControllingSystem` - 140 edges
2. `Telemetry` - 119 edges
3. `ControlsState` - 81 edges
4. `ICSSim` - 74 edges
5. `Scenario` - 71 edges
6. `XPlaneSim` - 58 edges
7. `airborne_inputs()` - 48 edges
8. `ICSInputs` - 42 edges
9. `PIDController` - 40 edges
10. `IcsEngagement` - 40 edges

## Surprising Connections (you probably didn't know these)
- `Autonomous Landing Controller` --semantically_similar_to--> `Autonomous Landing Controller`  [INFERRED] [semantically similar]
  CLAUDE.md → AGENTS.md
- `DatagramSocket` --uses--> `ApproachSetup`  [INFERRED]
  tests/test_xplane_backend.py → ismpu/config/scenarios.py
- `MockXPlaneConnector` --uses--> `ApproachSetup`  [INFERRED]
  tests/test_xplane_backend.py → ismpu/config/scenarios.py
- `DatagramSocket` --uses--> `TouchdownSetup`  [INFERRED]
  tests/test_xplane_backend.py → ismpu/config/scenarios.py
- `MockXPlaneConnector` --uses--> `TouchdownSetup`  [INFERRED]
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
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach_criteria.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/flight.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/ground_allocator.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/tolerance.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`

## Hyperedges (group relationships)
- **Graphify Extraction and Build Flow** — _codex_skills_graphify_skill_structural_extraction, _codex_skills_graphify_skill_semantic_extraction, _codex_skills_graphify_references_extraction_spec_semantic_extraction_contract, _codex_skills_graphify_references_update_build_merge [EXTRACTED 1.00]
- **PID Dashboard Ecosystem** — docs_xplane_dashboard_pid_dashboard, ismpu_gui_dashboard_pid_dashboard, ismpu_working_ics_ics_dashboard_ics_pid_monitor [INFERRED 0.85]

## Communities (230 total, 124 thin omitted)

### Community 0 - "criticality.py"
Cohesion: 0.09
Nodes (26): lateral_limit_m(), lateral_load_situation(), lateral_situation(), normal_load_situation(), IntEnum, Критерии критичности особых ситуаций МС-21 (Приложение 1 к ТЗ). Таблица АП-25…, Классификация скорости касания относительно VAPP и VВПП пред., Классификация нормальной перегрузки посадочного удара. `heavy` — взлётный вес. (+18 more)

### Community 3 - "test_weather.py"
Cohesion: 0.08
Nodes (26): WeatherState, Фактические погодные условия со стенда (ветер, сцепление, осадки, видимость)., compose_wind(), decompose_wind(), `ICSInputs` → `WeatherState`. Единственный источник фактической погоды. Стенд…, Собирает ветер из компонент относительно курса ВПП. `crosswind_kts` > 0 — ветер…, (скорость, откуда) → (crosswind, headwind) относительно курса ВПП. crosswind >…, (crosswind, headwind) → (скорость, откуда, °). Обратна `decompose_wind`. (+18 more)

### Community 4 - "run_reader.py"
Cohesion: 0.15
Nodes (15): IntEnum, ControlModeState, GearState, UDP-мост к стенду заказчика (порт 3030) — транспорт пути поставки. `ICSInputs`…, Дискретное положение стойки в кодировке ICSInputs., Режим управления/индикации, передаваемый в каждом ICSOutputs., Состояние створок реверса; величину задаёт отрицательный throttle rate., ReverseEngineType (+7 more)

### Community 5 - "json_config.py"
Cohesion: 0.10
Nodes (41): approach_control_from_dict(), approach_control_to_dict(), _copy_approach(), dump_scenario(), _finite_tree(), ground_control_from_dict(), ground_control_to_dict(), _legacy_ground() (+33 more)

### Community 6 - "SimInterface"
Cohesion: 0.11
Nodes (5): BaseException, StartMode, Минимальный lifecycle, одинаковый для стенда и X-Plane., SimInterface, Protocol

### Community 7 - "ControlsState"
Cohesion: 0.05
Nodes (80): _pid_from_colleague(), Загрузка настроек из JSON коллеги (`config/ics_clear_weather_pid.json`). Секции…, `PIDConfig` коллеги → аргументы нашего `PIDController`. Предел интегратора у…, angle_error_deg(), Разность курсов, приведённая к (-180, 180]., ControlsState, Обнуляет все органы управления. Отправку делает вызывающий через `ICSSim.step`.…, Совместимое имя старого API; колёсные органы оно больше не обозначает. (+72 more)

### Community 8 - "Scenario"
Cohesion: 0.08
Nodes (35): match_conditions(), _profile_name(), AircraftProfile, FailureMode, FlightSegment, WeatherState, Нормированная дистанция сцепления, ветра, осадков и видимости двух условий., Сравнить ожидаемые условия участка с одним фактическим кадром backend. (+27 more)

### Community 10 - "ground_allocator.py"
Cohesion: 0.19
Nodes (12): LongitudinalDiagnostics, ActuatorFeedback, ActuatorVector, AllocationDiagnostics, _clamp(), GroundControlAllocator, FlightSegment, Детерминированное распределение наземного yaw-запроса по органам управления. (+4 more)

### Community 11 - "LateralChannel"
Cohesion: 0.23
Nodes (7): GuidanceState, LateralChannel, LateralDiagnostics, Блок 2: runway guidance → единый нормированный yaw-запрос., Guidance по тому, что даёт стенд. → словарь guidance или None, если данных нет.…, Вернуть тот же ``GuidanceState``, который использует управляющий такт и…, RunwayTracker

### Community 13 - "test_refactoring_contracts.py"
Cohesion: 0.13
Nodes (11): DataRefSample, Неблокирующий UDP-клиент нативного протокола X-Plane 12., Последнее значение DataRef и monotonic timestamp его UDP-пакета., DatagramSocket, DREF/CMND/VEHS bytes are the contract; a duplicate client is not an oracle., Эталон разрешён тестам, но не должен стать скрытым runtime dependency., test_ics_shutdown_is_idempotent_and_releases_every_channel(), test_production_modules_never_import_the_working_ics_reference() (+3 more)

### Community 14 - "ICSOutputs"
Cohesion: 0.06
Nodes (32): ICSBenchConnector, ICSOutputs, Разбор телеметрии стенда с совместимостью вперёд. Асимметрия намеренная (JSON-…, Команды и mode flags, сериализуемые ровно в ожидаемый стендом JSON., Сериализовать enums и 14 reserved zeros в точные UTF‑8 bytes wire contract., Отправка best-effort со счётчиком ошибок и разрежённым логом. Windows отдаёт…, → True если отправлено. Исключение наружу не выпускается., Мост к стенду: JSON поверх UDP, адрес стенда определяется из входящего пакета. (+24 more)

### Community 15 - "scenario_for_matrix_run"
Cohesion: 0.11
Nodes (21): Разрешить только полный ``<шифр>/<номер>`` и вернуть точную строку JSON., resolve_matrix_run(), compose_matrix_scenario(), _install_through_scenarios(), Собрать сценарий из конкретных строк APPROACH/ROLLOUT/TAXI.…, Одна строка каталога → минимальный сценарий нужного участка или сквозной пары., Перенести накопленные overrides одного шифра на следующее условие этого же…, Собрать Б.4 из первой строки и заранее определённой пары законов. (+13 more)

### Community 16 - "AircraftProfile"
Cohesion: 0.10
Nodes (10): AircraftProfile, clamp(), Преобразовать воздушные команды ICD в нормированные DataRef X-Plane., Преобразовать нормированные команды пробега в DataRef X-Plane., Расширение реестра будущим профилем МС-21 без правки XPlaneSim., Проводка и масштабы конкретного планера X-Plane., Общая идентичность ЛА и необязательная привязка к X-Plane. Профиль нужен и…, Command refs retained under the historical public name. (+2 more)

### Community 17 - "ils_blocker"
Cohesion: 0.50
Nodes (4): ils_blocker(), in_terminal_window(), Последние футы перед касанием, где прерывать заход опаснее, чем доработать.…, Почему нельзя продолжать заход по этому кадру. `None` — можно. Закон читает…

### Community 18 - "ApproachResult"
Cohesion: 0.15
Nodes (19): ApproachLimits, ApproachTelemetry, ApproachController, ApproachResult, clamp(), Заход по ILS с выравниванием. Телеметрию получает параметром, не читает сам.…, Сброс регуляторов и всей памяти профиля — новый заход начинается с чистого…, Такт воздушного управления: пишет команды в `state`, возвращает диагностику.… (+11 more)

### Community 19 - "DashboardServer"
Cohesion: 0.15
Nodes (10): DashboardServer, main(), Запустить локальный read-only replay dashboard до ``Ctrl+C``., Отображаемое имя, PID source и физическая фаза одной панели графика., Loopback-only HTTP lifecycle вокруг одного ``DashboardState``., Фактически привязанные host/port, включая ephemeral port 0 в тестах., Идемпотентно запустить daemon HTTP thread., Отклонить pending tuning, остановить thread и закрыть listening socket. (+2 more)

### Community 20 - "weather.py"
Cohesion: 0.09
Nodes (25): Enum, Погодные условия эпизода: описание, шкала сцепления и разбор ветра. Модуль **не…, Состояние ВПП как **монотонная шкала скользкости** 0…15 (0 — сухо, 15 — лёд со…, Код состояния ВПП со стенда → наша шкала. Неизвестный код трактуется как `ICY`,…, runway_condition_from_bench(), RunwayCondition, Сверка каждого сигнала стенда с документами Заказчика. Два независимых…, 1 фут/мин = 0.3048/60 м/с. Приближение здесь копится на всём заходе. (+17 more)

### Community 21 - "XPlaneSim"
Cohesion: 0.12
Nodes (4): Снимок готовности resettable backend для recorder/dashboard., XPlaneDiagnostics, StartMode, XPlaneSim

### Community 23 - "PIDController"
Cohesion: 0.11
Nodes (29): PIDController, Сброс внутренних состояний (используется при выключении системы)., _legacy_reference(), Опциональная численность PID (шаг 5): каждый флаг проверяется на том дефекте,…, Если применено ровно то, что выдал PID, коррекции быть не должно., Уставка прыгает, объект стоит на месте — D-составляющая не должна реагировать.…, Выход ИЗ насыщения должен разрешаться всегда, иначе регулятор залипнет. kp…, Если насыщает уже пропорциональная часть, интегрировать нельзя вообще — и это… (+21 more)

### Community 25 - "DashboardState"
Cohesion: 0.15
Nodes (9): DashboardState, _finite(), _handler_factory(), HTTP читает только immutable recorder objects; controller меняет control-thread., Стабильный execution id live/replay источника., Вернуть подписи всех девяти панелей в порядке HTML layout., Проверить HTTP-запрос и поставить полный PID triplet в control-thread queue., Поставить восстановление gains начала запуска для активного участка. (+1 more)

### Community 26 - "test_xplane_backend.py"
Cohesion: 0.13
Nodes (13): MockXPlaneConnector, test_commands_failures_and_close_release_overrides(), test_exact_taxi_row_starts_xplane_and_controller_in_taxi_at_15_knots(), test_failed_approach_setup_releases_overrides_and_pause(), test_ignored_xplane_failure_participates_in_segment_delta_and_is_cleared(), test_missing_or_stale_required_data_makes_xplane_telemetry_invalid(), test_profile_rejects_unknown_aircraft_and_clamps_commands(), test_reload_renews_subscriptions_and_sensor_dropout_is_applied() (+5 more)

### Community 27 - "engaged_sim"
Cohesion: 0.12
Nodes (16): engaged_sim(), (sim, connector) с завершённым рукопожатием: стенд подтвердил `AgentIsActive =…, Регресс: расширение структуры не должно протащить руль высоты в маску пробега., test_ground_frame_still_declares_only_the_ground_channels(), Разделение органов из таблицы Заказчика: тиллер — на рулении, педальный пост —…, Базовый контур на стенде: `control_step` сам читает телеметрию и сам отправляет., На стенде каждый лишний `read_telemetry` — лишний приём UDP. Кадр, вернувшийся…, Замолчать нельзя: последнее отклонение осталось бы приложенным до сторожа на… (+8 more)

### Community 29 - "IcsEngagement"
Cohesion: 0.05
Nodes (27): ControlModeState, EngagementInputs, IcsEngagement, Автомат включения. `step(inputs)` вызывается каждый такт до формирования…, Полный сброс — новый эпизод начинается с невключённого состояния., Сообщить автомату, что кадр **фактически ушёл** на стенд. Вызывается…, Подхватить уже включённый извне пробег: шлём `ControlMode = Rollout`.…, Войти в пробег самостоятельно: шлём `ControlMode = Rollout`. Это же — передача… (+19 more)

### Community 30 - ".__init__"
Cohesion: 0.14
Nodes (8): AircraftProfile, FailureMode, FlightSegment, Path, RunwayProfile, WeatherState, Применить только дельту условий при переходе между участками., Снять один отказ, не переинициализируя отказ, продолжающийся на новом участке.

### Community 31 - "RunRecorder"
Cohesion: 0.18
Nodes (6): Exception, Append-only writer; ошибка диска помечает прогон, но не выходит в control-loop., Атомарный incremental slice для dashboard, без чтения controller., Сохранить полный effective config; канонические config-файлы не затрагиваются., RunEvent, RunRecorder

### Community 32 - ".invalid"
Cohesion: 0.17
Nodes (11): Кадр «связи со стендом нет». Нули, а не None: контур проверяет `valid` первым., Стенд при обрыве связи отдаёт НУЛИ с valid=False, а не None. Проверка «поле is…, test_control_step_stops_on_invalid_frame_even_with_numeric_fields(), Синтетический кадр — «нечем судить», а не «в воздухе». На таких кадрах работают…, Первый `read_telemetry` может вернуться по таймауту — это не «мы на полосе».…, test_a_frame_without_a_bench_packet_is_never_airborne(), test_the_segment_is_not_decided_by_a_frame_without_a_bench_packet(), Единичный таймаут — не повод вернуть рулю авторитет, которого у него нет. (+3 more)

### Community 33 - "Graphify Pipeline"
Cohesion: 0.08
Nodes (29): Folder Watcher, URL Ingestion, Extra Graph Exports, MCP Graph Server, Confidence Audit Trail, Deterministic Node IDs, Semantic Extraction Contract, Cross-Repository Graph Merge (+21 more)

### Community 34 - "XPlaneConnector"
Cohesion: 0.08
Nodes (16): Атомарно снять все свежие значения без раскрытия внутреннего mutable cache., Discard pre-reload values so readiness cannot use stale telemetry., Повторять RREF requests до получения всех значений либо подробного timeout., Отправить один нативный 509-byte DREF packet., Отправить один нативный CMND packet., Перезагрузить текущий самолёт без открытия aircraft chooser., Снять X‑Plane failures перед применением нового Scenario., Телепортировать aircraft через VEHS; packet дублируется из-за особенности… (+8 more)

### Community 35 - "ControllingSystem"
Cohesion: 0.06
Nodes (46): Скопировать канонический preset и заменить только запрошенные условия запуска., ControllingSystem, Связать сценарий с контуром; PID активируются после определения участка., Привести модель отказов к тому, что сообщает борт (`ICSInputs.Fault*`). Отказы…, Такт управления. → True, если управление окончено (или телеметрия невалидна).…, Три блока: speed controller → guidance → allocator., Оркестратор классического контура поверх стенда (`envs.ics_sim.ICSSim`).…, Передать управление в руление (`ControlMode 3 → 4`) — пробег окончен.… (+38 more)

### Community 36 - "test_ground_controller.py"
Cohesion: 0.08
Nodes (33): `ICSInputs` → `Telemetry`: поля в СИ + «сырой» пакет для property. Стенд отдаёт…, engaged_inputs(), Кадр стенда, который уже принял управление: `AgentIsActive = 1`, идёт пробег., test_accepted_promotion_allows_fixed_row_specific_overrides(), «Козление» после касания снимает обжатие на секунду — назад в заход…, В такте касания команда обязана быть уже наземной, а не последней командой…, Таблицы захода МС-21 к чистому крылу неприменимы — вести по ним нельзя.…, Нулевое отклонение при снятой валидности неотличимо от «точно на оси». (+25 more)

### Community 37 - "test_ics_engagement.py"
Cohesion: 0.11
Nodes (43): _Clock, _engine(), _pump(), Автомат включения управления на стенде. Два раздельных предмета проверки: *…, По ICD стенд должен два секунды ПОЛУЧАТЬ ModeAIReady=1. Если считать одно лишь…, Обратная защита: 30 кадров можно выпалить за 0.1 с — время тоже обязано пройти., Срыв предусловия обнуляет и время, и счётчик кадров., Требование ICD — непрерывность: пропуск готовности рвёт серию. (+35 more)

### Community 38 - "RunReader"
Cohesion: 0.09
Nodes (18): Один такт: вход, команда и диагностика имеют общий ``tick_id``., RunSample, _apply_recorded_gains(), _equal(), main(), _number(), _parse_cell(), ControllingSystem (+10 more)

### Community 39 - "sft.py"
Cohesion: 0.13
Nodes (23): GuardResult, Фактически разрешённые gains и причина ограничений/fallback., apply_gain_vector(), controller_gain_vector(), _feature_value(), feature_vector(), gain_vector_from_row(), _number() (+15 more)

### Community 40 - ".snapshot"
Cohesion: 0.17
Nodes (7): DashboardSnapshot, _jsonable(), Вернуть только новые recorder updates; смена run_id принудительно сбрасывает…, JSON-ready форма ``snapshot`` для ``GET /api/state``., Инкремент после sequence cursor и редкие metadata при reset., Преобразовать tuples в JSON arrays, не добавляя отсутствующие тяжёлые секции., RunEvent

### Community 41 - "HandshakeBench"
Cohesion: 0.12
Nodes (10): HandshakeBench, kinematic_sim(), KinematicBench, Стенд, включающий управление только после корректного рукопожатия. Ждёт…, Мини-модель стенда: замедление ~ команде тормоза/реверса, ход вдоль осевой ВПП.…, (sim, bench) на кинематической модели — стенд уже принял управление., На пробеге показатели считает наземный канал — в **метрах** от осевой, а не в…, Стенд включается по полученной готовности, а не по нашему представлению о ней. (+2 more)

### Community 43 - "ICSInputs"
Cohesion: 0.14
Nodes (24): ControlResult, ICSInputs, Неизвестные поля исходного JSON; они доступны аудиту, но не закону управления., Полная известная входная схема стенда; единицы определены в ``ICSInterface.cs``., airborne_control_mode(), airborne_flare_mode(), deactivate(), live_main() (+16 more)

### Community 45 - "3. Этапы реализации"
Cohesion: 0.09
Nodes (21): 1. Подтверждённые проблемы и целевое состояние, 2. Ключевые интерфейсы, 3. Этапы реализации, 4. Тестирование и критерии готовности, 5. Зафиксированные допущения, 6.1. Один dashboard вместо двух, 6.2. Единый источник данных, 6.3. Представления (+13 more)

### Community 46 - ".from_checkpoints"
Cohesion: 0.28
Nodes (8): checkpoint_metadata(), Path, Сформировать audit metadata загруженного файла, включая SHA-256 содержимого., Загрузить независимые air/ground slots и проверить activation evidence для ICS., _checkpoint(), ndarray, test_checkpoint_contract_and_ics_activation_gate(), test_runtime_predicts_each_tick_after_40_frames_and_falls_back_before_it()

### Community 47 - "test_profiled_scenarios.py"
Cohesion: 0.13
Nodes (12): compose_scenario(), Any, Serialize only the canonical profile- and matrix-aware schema v3., Прочитать schema v3 либо явно мигрируемую v1/v2 конфигурацию., Собрать сценарий из независимых источников участков., test_preset_roundtrips_through_dict(), Contracts of the unified aircraft-profiled scenario model., test_automatic_selection_never_falls_back_to_a_draft_profile_branch() (+4 more)

### Community 49 - "test_full_flight.py"
Cohesion: 0.09
Nodes (36): IntFlag, ControlValid, FlightPhase, Биты `ControlValidMask`: какие каналы несёт команда. **Один бит на одно…, Фаза полёта, сообщаемая стендом (`ICSInputs.FlightPhase`)., EngagementState, Enum, Автомат включения управления на стенде заказчика. Стенд принимает наши команды… (+28 more)

### Community 50 - "test_go_around.py"
Cohesion: 0.14
Nodes (25): GoAroundManeuver, Состояние идущего ухода на второй круг. Пока он активен, заход не ведётся., _armed_controller(), _drive(), _frame(), Уход на второй круг (fallback в воздухе): условия срабатывания и передача…, На пробеге ухода нет — segment guard (козление удерживает защёлка сегмента,…, Если реверс уже включён — взлёт невозможен, ухода нет. (+17 more)

### Community 51 - "Hybrid Neural PID Controller"
Cohesion: 0.70
Nodes (5): Hybrid Neural PID Controller, Neural PID Gain Scheduler, PPO Training Loop, Preset-Anchored Deterministic Shield, SFT Behavioral-Cloning Warm Start

### Community 52 - "test_approach_criteria.py"
Cohesion: 0.18
Nodes (12): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, Отдельный монитор критерия А.1.1 (не участвует в go-around)., Захватывает А.1.1 после входа в допуск и завершает оценку на 300 ft., frame() (+4 more)

### Community 53 - "._approach_step"
Cohesion: 0.09
Nodes (16): above_decision_height(), at_lateral_alignment_gate(), ВС выше высоты решения ухода на второй круг (30 м по ТЗ 5.1.1.2). → уход…, Полоса подхода к гейту совмещения с осью ± 5 м: `(30 м, 30 м + band]`. Только в…, Окончен ли воздушный участок. Два независимых признака, любой достаточен:…, touched_down(), Такт воздушного участка. → True, если управлять больше нечем. Касание…, Зафиксировать `Approach → Landing` на 25 ft без смены воздушного закона. (+8 more)

### Community 54 - "run_artifacts.py"
Cohesion: 0.15
Nodes (19): Вызывается runtime ровно в начале control tick., Вернуть одно свежее значение; stale/missing представлены ``None``., controller_pids(), _csv_value(), default_runs_root(), _effective_configs(), gains_snapshot(), _git_state() (+11 more)

### Community 55 - "RunwayTracker"
Cohesion: 0.13
Nodes (11): Точка на продолжении оси; положительное расстояние — до порога., Решить прямую геодезическую задачу на сферической Земле., Геодезическое guidance в истинной системе направлений., Guidance по курсу ВПП и измеренному отклонению — без собственной геодезии.…, Возвращает отклонение от осевой линии в метрах. >0 - правее оси, <0 - левее., Геодезическое наведение на ось ВПП с упреждением по скорости., RunwayTracker, test_xte_sign_left_is_negative() (+3 more)

### Community 56 - "RomanLogImporter"
Cohesion: 0.15
Nodes (13): _number(), Path, Импорт и проверка внешних CSV-прогонов roman_aviacia_ics., Потоково нормализует основной и authority CSV Романа., RomanLogImporter, verify_manifest(), Converts, Преобразовать координату из градусов, минут и секунд в signed degrees. (+5 more)

### Community 57 - "ICSInputs"
Cohesion: 0.12
Nodes (15): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, ICSInputs, Evaluate the A.1.1 approach segment and stop at a radio-altitude floor., Exact package port of the ICS approach contour validated in ``aviacia_v2``. The… (+7 more)

### Community 58 - "test_dashboard.py"
Cohesion: 0.20
Nodes (13): _live(), _post(), parametrize, test_active_pid_is_editable_in_classical_and_shadow(), test_gain_change_is_queued_bumpless_and_records_full_event(), test_http_api_is_incremental_pending_and_loopback_only(), test_incremental_snapshot_uses_recorder_objects_and_stays_small_when_idle(), test_live_and_replay_use_the_same_dashboard_snapshot() (+5 more)

### Community 59 - "pretrain.py"
Cohesion: 0.10
Nodes (29): _fit_feature_normalization(), _normalized_mse(), _physical_bounds(), _predict(), ndarray, Офлайн-SFT двух PID gain-регрессоров из принятых ``approach/ground.csv``., Стратифицировать по условиям, назначая целый run ровно одному split., Один принятый прогон, уже приведённый к матрицам признаков и целей.… (+21 more)

### Community 60 - "GainChange"
Cohesion: 0.33
Nodes (3): GainChange, Закрыть tuning и записать отказ для каждого неисполненного запроса., Immutable запрос HTTP-thread, ожидающий применения control-thread.

### Community 61 - "test_control_parity.py"
Cohesion: 0.10
Nodes (21): CompletionRule, Enum, Генератор эталонной кривой скорости пробега. Два закона замедления: колокол…, Как активный наземный сценарий заканчивает управление., Генератор эталонной кривой скорости (Колокол Гаусса)., Начать профиль с фактической скорости текущего участка., То же без лишнего round-trip м/с → узлы → м/с на касании., Возвращает идеальную скорость (м/с) для текущей точки пути. (+13 more)

### Community 62 - "Project Dependencies"
Cohesion: 0.29
Nodes (7): Optional Gymnasium, NumPy, Pandas, Project Dependencies, Pytest, Termcolor, Optional PyTorch

### Community 63 - "loop.py"
Cohesion: 0.14
Nodes (17): Сценарий по имени либо шифру матрицы, без различия раскладки А/B., resolve_scenario(), Причина остановки вместе с best-effort результатом освобождения backend., RunResult, Вернуть сериализуемую строку отчёта без отдельной DTO-схемы., cli(), _lost_engagement(), main() (+9 more)

### Community 64 - "PidGainRegressor"
Cohesion: 0.11
Nodes (18): device, GainGuard, PidGainRegressor, Any, Минимальная SFT-модель абсолютных коэффициентов PID и общий runtime guard., Предсказать gains по последнему hidden state окна ``(B,T,F)``., Сохранить веса вместе с полным train↔runtime контрактом., Загрузить модель только после проверки полного train↔runtime контракта. (+10 more)

### Community 66 - "dashboard_core.py"
Cohesion: 0.20
Nodes (6): _allocator_stage(), _first_present(), _gains_from_samples(), _mean(), Один локальный dashboard для live RunRecorder и read-only replay., _view_point()

### Community 67 - "test_tolerance.py"
Cohesion: 0.15
Nodes (23): evaluate_approach_tolerances(), _glideslope_tolerance_deg(), ApproachLimits, ApproachTelemetry, FailureMode, Монитор допусков захода в реальном времени + классификация особой ситуации.…, Результат проверки допусков захода на одном такте. `landing_allowed` — все ли…, Допуск по глиссаде с учётом отказа (ТЗ 5.1.2.1–5.1.2.3), самый мягкий из… (+15 more)

### Community 68 - "test_working_ics_dashboard.py"
Cohesion: 0.35
Nodes (10): ClearWeatherILSController, DashboardState, _controller(), _inputs(), Characterization tests for the bench-validated ``working_ics`` dashboard., _record(), test_dashboard_records_four_airborne_views_and_diagnostics(), test_gain_updates_are_immediate_validated_and_share_pitch_with_flare() (+2 more)

### Community 70 - "Telemetry"
Cohesion: 0.07
Nodes (18): Такт манёвра ухода. → True, когда набор устойчив (пора отдать управление…, Набор устойчив: есть и вертикальная скорость вверх, и прирост радиовысоты над…, Невалидные ICS-сигналы, которые воздушный закон читает безусловно., Приборная скорость (kt → м/с). Отсечки реверса заданы по ней, а не по путевой., Радиовысота **в футах** — единицы стенда. Порог воздушного включения (400…, Объявлены ли валидными **оба** канала ILS (курсовой и глиссадный). `None` —…, Посадочная конфигурация механизации; `None` — положение не посадочное. `None`…, Боковое отклонение от оси, измеренное стендом. Позволяет не считать геодезию… (+10 more)

### Community 71 - "Unified Profile-Aware Scenario System"
Cohesion: 0.33
Nodes (6): Technical-Specification Acceptance Gates, Forward-Only Flight Segment Supervisor, Longitudinal and Lateral Ground Channels, PID Run Matrix, Unified Profile-Aware Scenario System, Legacy Scenario Preset Model

### Community 72 - "Interactive PID Dashboard"
Cohesion: 0.25
Nodes (9): Nine-View PID Dashboard, Run Recording Artifacts, buildTabs, draw, Gain Tuning and Snapshot Export, Interactive PID Dashboard, refresh, render (+1 more)

### Community 73 - "MatrixRun"
Cohesion: 0.05
Nodes (20): MatrixCase, MatrixCondition, MatrixRun, normalize_code(), _number(), Any, FailureMode, FlightSegment (+12 more)

### Community 74 - "ClearWeatherILSController"
Cohesion: 0.16
Nodes (8): DashboardServer, DashboardState, Any, ICSInputs, ClearWeatherILSController, ControlResult, test_roundout_commands_a_material_pitch_increase_before_touchdown(), test_terminal_pitch_hold_starts_before_last_five_feet_guidance_cutoff()

### Community 75 - "FailureState"
Cohesion: 0.17
Nodes (9): ApproachController, FailureManager, FailureMode, FailureState, Enum, Эффективности исполнительных органов. Аннотации типов обязательны: без них…, Проецирует набор дискретных отказов в эффективности исполнительных органов., Привести состояние ровно к набору `modes` (то, что сообщил стенд). Пересборка с… (+1 more)

### Community 76 - "ICSInterface.cs"
Cohesion: 0.36
Nodes (7): External.Systems.ICS, ControlModeState, GearState, ICSInputs, ICSOutputs, ReverseEngineType, UInt64

### Community 78 - "run_pretrain"
Cohesion: 0.29
Nodes (8): cli(), PretrainRunConfig, Последовательно обучить выбранные участки из одного каталога принятых прогонов., CLI офлайн-обучения; сеть никогда не открывает UDP и не сбрасывает X-Plane., Пути и участки для CLI, обучающего независимые air/ground checkpoints., Итог обучения участка и данные, необходимые для автоматической проверки gate., run_pretrain(), TrainingResult

### Community 79 - "promote_candidate.py"
Cohesion: 0.33
Nodes (15): _gain_patch(), main(), promote_candidate(), PromotionError, Path, Проверяемое продвижение dashboard candidate в sparse scenario override., Пересчитать matrix/config hashes, а не доверять двум согласованно изменённым…, Проверить run и записать новый scenario JSON; registry исходников не меняется. (+7 more)

### Community 80 - "ICS PID Monitor"
Cohesion: 0.22
Nodes (9): Bench-Validated ILS Approach Channel, Tolerance-Gated Go-Around, buildControls, draw, formatTime, Four-Loop PID Tuning, ICS PID Monitor, Live and Historical Timeline (+1 more)

### Community 81 - "segments.py"
Cohesion: 0.18
Nodes (11): FlightSegment, Enum, str, Канонические участки управляемого интервала полёта., Участок, для которого выбираются закон управления и условия сценария., ICSInputs, socket, Hand the validated airborne session to Vlayd's existing rollout loop. The… (+3 more)

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
Cohesion: 0.06
Nodes (73): Приёмочные пороги из ТЗ (раздел 5). Единый источник истины для runtime…, campaign_phase(), campaign_rows(), campaign_summary(), _config_status(), main(), next_campaign_row(), Path (+65 more)

### Community 87 - "scenarios.py"
Cohesion: 0.09
Nodes (33): ApproachConfig, Настройки воздушного участка: заход по ILS, выравнивание, управление скоростью.…, Параметры воздушного контура. Значения по умолчанию — настроенные на стенде.…, ControlProfile, _copy_approach(), _copy_ground(), _ground_matrix_drafts(), _ground_segments_for_spec() (+25 more)

### Community 88 - "import_workbook"
Cohesion: 0.33
Nodes (9): import_workbook(), main(), Any, Path, Одноразовый импорт исходной Excel-матрицы в runtime-каталог JSON., Прочитать книгу целиком; функция не используется production runtime., _scalar(), write_catalog() (+1 more)

### Community 89 - "envelope.py"
Cohesion: 0.12
Nodes (23): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+15 more)

### Community 90 - "LongitudinalChannel"
Cohesion: 0.20
Nodes (7): CompletionRule, LongitudinalChannel, Блок 1: скорость → симметричная база тормозов и реверса., Сбросить PID и привязать начало профиля к фактической скорости касания/старта., PidMap, ReferenceTrajectory, VelocityLaw

### Community 91 - "pid.py"
Cohesion: 0.29
Nodes (4): Типы и порядок коэффициентов пяти наземных PID-регуляторов. Модуль намеренно не…, PIDDiagnostics, Пропорционально-интегрально-дифференциальный регулятор. Класс сохраняет прежнюю…, Типизированный снимок последнего такта регулятора.

### Community 92 - "static_sim"
Cohesion: 0.11
Nodes (18): decode_outputs(), _integrate_throttle(), Отправленные команды в нормированном виде — для сравнения траекторий.…, `ICSOutputs` → (brake_l, brake_r, thr_l_rate, thr_r_rate, steer), всё…, Ход рычага РУД за такт: интеграл команды-скорости, зажатый физическим…, Доля обратной тяги по фактическому углу РУД: 0 в положительном секторе, 1 на…, (sim, connector) с неизменным кадром у порога ВПП. Скорость задаётся в **м/с**.…, Замедление считается по **фактическому** углу РУД, а не по команде. Тягой… (+10 more)

### Community 93 - "ICSSim"
Cohesion: 0.06
Nodes (24): EngagementInputs, ICSSim, FailureMode, StartMode, Обмен со стендом заказчика: телеметрия внутрь, команды наружу. Управление…, Принимает ли стенд наши команды. До включения любой `step` уходит вхолостую., Начало эпизода: сброс рукопожатия и первый кадр со стенда. Средой распоряжается…, Гонит стимул рукопожатия, пока стенд не подтвердит включение (`AgentIsActive =… (+16 more)

### Community 94 - "ics_sim.py"
Cohesion: 0.08
Nodes (28): Глобальные константы контура управления (перенесены из main.ipynb)., Константы интерфейса стенда заказчика (ПИВ / ICS). Единый источник правды по…, ConditionMatch, Сверка ожидаемых условий с фактической телеметрией backend., Истина, если набор фактических отказов совпал ровно., Истина при практически нулевой нормированной дистанции погоды., Погода остаётся отчётной; неверный отказ делает прогон недопустимым., Воздушный канал: заход по ILS, выравнивание, управление скоростью. Перенос… (+20 more)

### Community 95 - "Q: Приступай к выполнению этапа 9 плана [plan.md](docs/plan.md). В процессе старайся упрощать код, удалять лишний и неиспользуемый код, а также максимально покрывать его комментариями."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 9 плана [plan.md](docs/plan.md). В процессе старайся упрощать код, удалять лишний и неиспользуемый код, а также максимально покрывать его комментариями., Source Nodes

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
Cohesion: 0.07
Nodes (40): FakeConnector, make_ics_inputs(), on_ground(), Статический стенд: всегда один и тот же кадр, отправленное — в `sent_outputs`., Полный пакет стенда: нули по умолчанию + заданные поля., Кадр «ВС на полосе»: обжаты все стойки, курс/координаты у порога UUEE 06R., _cold_sim(), Тесты стенда (`ICSSim`) и подбора сценария — без реального стенда. (+32 more)

### Community 116 - "Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)., Source Nodes

### Community 117 - "roll_limit_deg"
Cohesion: 0.50
Nodes (4): Предел крена по высоте: чем ниже, тем меньше запас до касания законцовкой.…, roll_limit_deg(), Чем ниже, тем меньше запас до касания законцовкой; настроенный предел не…, test_roll_limit_tightens_towards_the_ground()

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
Cohesion: 0.15
Nodes (6): → (интеграл только с утечкой, интеграл с утечкой и приращением). Оба уже зажаты., Такт регулятора. `measurement` обязателен при `derivative_on_measurement=True`., Back-calculation: подтянуть интегратор к фактически применённой команде. No-op…, Сменить коэффициенты без сброса D-history и с компенсацией интегратором.…, Вес апериодического фильтра D-составляющей за такт `dt`., ValueError

### Community 127 - ".from_csv"
Cohesion: 0.22
Nodes (9): _gain_ranges(), _gains_from_manifest(), _load_updates(), Path, RunReader, После recorder.finish держать полный run доступным, но только для чтения., Сохранить фактически записанный effective config, не изменяя SCENARIOS., Построить read-only state из run-directory либо поддерживаемого CSV. (+1 more)

### Community 128 - "test_adopts_rollout_from_the_flight_phase"
Cohesion: 0.33
Nodes (4): Валидный кадр с AgentIsActive = 0 — стенд снял активацию, значит и мы больше не…, `ControlMode` нет во входной структуре, поэтому подхват опирается на фазу…, test_adopts_rollout_from_the_flight_phase(), test_confirmation_clears_when_the_bench_deactivates()

### Community 129 - "Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md)., Source Nodes

### Community 130 - "Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md)., Source Nodes

### Community 131 - "control.py"
Cohesion: 0.36
Nodes (5): Полностью пересобрать наземные каналы controller этой конфигурацией., apply_ground_control(), build_pids(), Сборка классического контура из неизменяемой конфигурации., Фабрики stateful-объектов; config-модули хранят только данные.

### Community 135 - "Q: Приступай к выполнению этапа 2 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 2 плана docs/plan.md, Source Nodes

### Community 142 - "pid_controller.py"
Cohesion: 0.14
Nodes (20): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+12 more)

### Community 154 - "Normalization"
Cohesion: 0.15
Nodes (12): ArrayLike, float32, float64, Normalization, NDArray, Выполнить deterministic inference и вернуть физические gains плюс OOD flag., Проверить prediction и ограничить его относительно accepted preset/предыдущего…, Покомпонентная standardization и границы обучающей выборки. (+4 more)

### Community 155 - "fakes.py"
Cohesion: 0.16
Nodes (15): _destination(), find_earth_nav_dat(), get_runway_profile(), ILSStation, parse_ils_station(), Path, Профили ВПП и разрешение ILS из установленной базы X-Plane., Найти LOC (тип 4) без хардкода частоты. (+7 more)

### Community 158 - "Q: Приступай к выполнению этапа 4 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 4 плана docs/plan.md, Source Nodes

### Community 164 - "aircraft_profiles.py"
Cohesion: 0.15
Nodes (11): IcsEngagement, get_aircraft_profile(), Профили преобразования команд ИСМПУ в органы управления X-Plane., build_sim(), Any, Path, Единая фабрика backend: ICS по умолчанию, X-Plane явно., Создать backend; для ICS геодезия включается только явным ``runway_profile``. (+3 more)

### Community 167 - "Q: Приступай к выполнению этапа 8 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 8 плана [plan.md](docs/plan.md)., Source Nodes

### Community 181 - "Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md)., Source Nodes

### Community 183 - "initial_segment"
Cohesion: 0.13
Nodes (17): approach_blocker(), ApproachRefused, initial_segment(), is_airborne(), FlightSegment, Воздушный участок начинать нельзя — с названной причиной. Отдельное исключение,…, Сообщает ли стенд, что ВС в воздухе и достаточно высоко для приёма захода.…, Можно ли вообще судить об участке по этому кадру. Кадр без пакета стенда… (+9 more)

## Ambiguous Edges - Review These
- `Unified Profile-Aware Scenario System` → `Legacy Scenario Preset Model`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to
- `Dual-Backend SimInterface` → `ICS-Only Backend Guidance`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **83 isolated node(s):** `Answer`, `Outcome`, `Source Nodes`, `Answer`, `Outcome` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **124 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `loop.py` (2× useful, score=1.980703285) _(code changed — re-verify)_
- `ICSSim` (2× useful, score=1.964703533) _(code changed — re-verify)_
- `LateralChannel` (2× useful, score=1.94341415) _(code changed — re-verify)_
- `ObservationBuilder` (2× useful, score=1.923717827) _(code changed — re-verify)_

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Unified Profile-Aware Scenario System` and `Legacy Scenario Preset Model`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Dual-Backend SimInterface` and `ICS-Only Backend Guidance`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `ControllingSystem` connect `ControllingSystem` to `control.py`, `json_config.py`, `SimInterface`, `ControlsState`, `Scenario`, `LateralChannel`, `test_refactoring_contracts.py`, `scenario_for_matrix_run`, `test_xplane_backend.py`, `engaged_sim`, `.invalid`, `test_ground_controller.py`, `sft.py`, `HandshakeBench`, `.from_checkpoints`, `test_full_flight.py`, `test_go_around.py`, `test_approach_criteria.py`, `._approach_step`, `initial_segment`, `test_dashboard.py`, `test_control_parity.py`, `loop.py`, `Telemetry`, `FailureState`, `DatagramSocket`, `segments.py`, `scenarios.py`, `LongitudinalChannel`, `static_sim`, `ICSSim`, `ics_sim.py`, `test_ics_sim.py`, `test_sft_regressors.py`?**
  _High betweenness centrality (0.135) - this node is a cross-community bridge._
- **Why does `Telemetry` connect `Telemetry` to `test_weather.py`, `run_reader.py`, `json_config.py`, `SimInterface`, `ControlsState`, `Scenario`, `ground_allocator.py`, `LateralChannel`, `ICSOutputs`, `weather.py`, `XPlaneSim`, `fakes.py`, `.__init__`, `.invalid`, `ControllingSystem`, `test_ground_controller.py`, `HandshakeBench`, `ICSInputs`, `test_full_flight.py`, `test_go_around.py`, `test_approach_criteria.py`, `._approach_step`, `initial_segment`, `test_control_parity.py`, `loop.py`, `test_tolerance.py`, `segments.py`, `test_working_ics_golden.py`, `scenarios.py`, `LongitudinalChannel`, `static_sim`, `ICSSim`, `ics_sim.py`, `test_ics_sim.py`, `_faults_from_inputs`?**
  _High betweenness centrality (0.127) - this node is a cross-community bridge._
- **Why does `ControlsState` connect `ControlsState` to `json_config.py`, `SimInterface`, `ground_allocator.py`, `AircraftProfile`, `XPlaneSim`, `test_xplane_backend.py`, `engaged_sim`, `ControllingSystem`, `aircraft_profiles.py`, `ICSInputs`, `test_go_around.py`, `loop.py`, `Telemetry`, `FailureState`, `DatagramSocket`, `test_working_ics_golden.py`, `ICSSim`, `ics_sim.py`, `test_ics_sim.py`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 22 inferred relationships involving `ControllingSystem` (e.g. with `ApproachSetup` and `ConditionMatch`) actually correct?**
  _`ControllingSystem` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `Telemetry` (e.g. with `ApproachSetup` and `ConditionMatch`) actually correct?**
  _`Telemetry` has 46 INFERRED edges - model-reasoned connections that need verification._