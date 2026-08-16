# Graph Report - GOSNIIASProject  (2026-08-16)

## Corpus Check
- 139 files · ~141,463 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2538 nodes · 5432 edges · 229 communities (109 shown, 120 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 366 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8dd56ae7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_tolerance.py
- GainMap
- ndarray
- run_report.py
- ICSBenchConnector
- test_refactoring_contracts.py
- SimInterface
- ControlsState
- Scenario
- GainKey
- Telemetry
- .from_dict
- float32
- pid.py
- test_ics_connector.py
- test_run_matrix.py
- AircraftProfile
- test_full_flight.py
- ApproachController
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
- ConditionMatch
- RunRecorder
- ._should_go_around
- Graphify Pipeline
- XPlaneConnector
- .from_preset
- ControllingSystem
- test_ics_engagement.py
- RunReader
- sft.py
- .enqueue_gain_update
- HandshakeBench
- floating
- ICSInputs
- device
- 3. Этапы реализации
- test_sft_regressors.py
- main
- Path
- _Clock
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
- GoAroundManeuver
- test_working_ics_dashboard.py
- ICSOutputs
- ics_engagement.py
- Unified Profile-Aware Scenario System
- Interactive PID Dashboard
- MatrixRun
- run_matrix.py
- FailureManager
- ICSInterface.cs
- План исправления
- SftTrainConfig
- promote_candidate.py
- ICS PID Monitor
- VlaydRolloutBridge
- Autonomous Landing Controller
- X-Plane Dashboard and Runtime Guide
- test_working_ics_golden.py
- GainSpace
- test_evaluate.py
- scenarios.py
- import_workbook
- test_approach_channel.py
- runs_for_code
- test_campaign.py
- static_sim
- ICSSim
- .__init__
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
- .set_packet_observer
- Q: Приступай к выполнению этапа 9 плана docs/plan.md; упрощай код, удаляй лишнее и добавляй комментарии.
- Q: Реализовать этап 0: baseline, golden replay и dashboard characterization
- Q: Приступай к выполнению этапа 1 плана [plan.md](docs/plan.md).
- .reset
- ndarray
- test_ics_sim.py
- Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md).
- .reset_derivative
- .flush
- ControlModeState
- ICSInputs
- ICSOutputs
- socket
- IntEnum
- _faults_from_inputs
- AircraftProfile
- .compute
- .from_csv
- .control_step
- Q: Приступай к выполнению этапа 5 плана [plan.md](docs/plan.md).
- Q: Приступай к выполнению этапа 6 плана [plan.md](docs/plan.md).
- control.py
- device
- int64
- .pids
- Q: Приступай к выполнению этапа 2 плана docs/plan.md
- ControlsState
- LandingFlapConfiguration
- TypedDict
- FailureMode
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
- Any
- PidMap
- ApproachConfig
- Normalization
- ics_sim.py
- Scenario
- Path
- Q: Приступай к выполнению этапа 4 плана docs/plan.md
- RewardWeights
- TypedDict
- ControlsState
- IcsEngagement
- RegulatorKey
- Q: Приступай к выполнению этапа 8 плана [plan.md](docs/plan.md).
- FlightSegment
- ICSInputs
- PidMap
- Any
- ArrayLike
- float32
- NDArray
- ControllingSystem
- Tensor
- ApproachLimits
- Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md).
- ApproachTelemetry
- ApproachRefused
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
- SimInterface
- GainSpace
- SimInterface
- SimInterface
- Linear
- Normal
- parametrize
- PPOMetrics
- RunResult
- RuntimeState
- ScenarioProvider
- Sequential
- SFTDataset
- fixture
- RunSample
- Q: Почему прогон runs/20260816T174009.095580Z раскачивает самолёт и не сохраняет паритет с working_ics по логу logs/ics_pid_20260816_104551.csv?
- Q: Проанализировать три неудачных production-прогона против working_ics и составить план исправления
- Q: Почему production-заход терял паритет с working_ics и как это исправлено?
- Q: Каков финальный результат исправления runtime-паритета 2026-08-16?
- Q: Проанализировать run 20260816T213847.114116Z, сравнить управление с working_ics и исправить уход по GLIDESLOPE и неисполняемый go-around.
- FrictionProfile
- .run_id
- .view_names
- ApproachController
- ControlModeState
- EngagementInputs
- str
- RunReader

## God Nodes (most connected - your core abstractions)
1. `ControllingSystem` - 140 edges
2. `Telemetry` - 117 edges
3. `ICSSim` - 75 edges
4. `ControlsState` - 66 edges
5. `XPlaneSim` - 54 edges
6. `airborne_inputs()` - 52 edges
7. `RunRecorder` - 50 edges
8. `PIDController` - 49 edges
9. `Scenario` - 49 edges
10. `IcsEngagement` - 47 edges

## Surprising Connections (you probably didn't know these)
- `Autonomous Landing Controller` --semantically_similar_to--> `Autonomous Landing Controller`  [INFERRED] [semantically similar]
  CLAUDE.md → AGENTS.md
- `_Clock` --uses--> `ControlValid`  [INFERRED]
  tests/test_full_flight.py → ismpu/config/ics.py
- `FakeConnector` --uses--> `FlightPhase`  [INFERRED]
  tests/fakes.py → ismpu/config/ics.py
- `HandshakeBench` --uses--> `FlightPhase`  [INFERRED]
  tests/fakes.py → ismpu/config/ics.py
- `KinematicBench` --uses--> `FlightPhase`  [INFERRED]
  tests/fakes.py → ismpu/config/ics.py

## Import Cycles
- 3-file cycle: `ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/control/channels.py`
- 3-file cycle: `ismpu/config/scenarios.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 3-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 3-file cycle: `ismpu/config/aircraft_profiles.py -> ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/config/aircraft_profiles.py`
- 4-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 4-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/tolerance.py -> ismpu/control/approach.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/flight.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/ground_allocator.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/approach_criteria.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/scenarios.py -> ismpu/control/system.py -> ismpu/control/tolerance.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py`
- 5-file cycle: `ismpu/config/aircraft_profiles.py -> ismpu/control/channels.py -> ismpu/envs/ics_sim.py -> ismpu/envs/sim_interface.py -> ismpu/config/scenarios.py -> ismpu/config/aircraft_profiles.py`

## Hyperedges (group relationships)
- **Graphify Extraction and Build Flow** — _codex_skills_graphify_skill_structural_extraction, _codex_skills_graphify_skill_semantic_extraction, _codex_skills_graphify_references_extraction_spec_semantic_extraction_contract, _codex_skills_graphify_references_update_build_merge [EXTRACTED 1.00]
- **PID Dashboard Ecosystem** — docs_xplane_dashboard_pid_dashboard, ismpu_gui_dashboard_pid_dashboard, ismpu_working_ics_ics_dashboard_ics_pid_monitor [INFERRED 0.85]

## Communities (229 total, 120 thin omitted)

### Community 0 - "test_tolerance.py"
Cohesion: 0.07
Nodes (48): lateral_limit_m(), lateral_load_situation(), lateral_situation(), normal_load_situation(), IntEnum, Критерии критичности особых ситуаций МС-21 (Приложение 1 к ТЗ). Таблица АП-25…, Классификация скорости касания относительно VAPP и VВПП пред., Классификация нормальной перегрузки посадочного удара. `heavy` — взлётный вес. (+40 more)

### Community 3 - "run_report.py"
Cohesion: 0.15
Nodes (26): _accepted_segments(), aggregate_matrix_results(), _approach_runway_heading_error(), build_run_report(), _environment_diagnostics(), _handover_ratio(), main(), _matrix_results() (+18 more)

### Community 4 - "ICSBenchConnector"
Cohesion: 0.12
Nodes (10): ICSBenchConnector, Отправка best-effort со счётчиком ошибок и разрежённым логом. Windows отдаёт…, → True если отправлено. Исключение наружу не выпускается., Мост к стенду: JSON поверх UDP, адрес стенда определяется из входящего пакета., Приём телеметрии стенда. Адрес отправителя определяется автоматически., Зафиксировать и разобрать один уже принятый UDP payload., Отправка управления на стенд. → отправлено ли (исключение наружу не…, Число последовательных best-effort ошибок текущего sender. (+2 more)

### Community 5 - "test_refactoring_contracts.py"
Cohesion: 0.11
Nodes (39): approach_control_from_dict(), approach_control_to_dict(), _copy_approach(), dump_scenario(), _finite_tree(), ground_control_from_dict(), ground_control_to_dict(), _legacy_ground() (+31 more)

### Community 6 - "SimInterface"
Cohesion: 0.10
Nodes (5): BaseException, StartMode, Минимальный lifecycle, одинаковый для стенда и X-Plane., SimInterface, Protocol

### Community 7 - "ControlsState"
Cohesion: 0.05
Nodes (67): _pid_from_colleague(), Загрузка настроек из JSON коллеги (`config/ics_clear_weather_pid.json`). Секции…, `PIDConfig` коллеги → аргументы нашего `PIDController`. Предел интегратора у…, ControlsState, Обнуляет все органы управления. Отправку делает вызывающий через `ICSSim.step`.…, Совместимое имя старого API; колёсные органы оно больше не обозначает., Разделяемая по тактам структура команд — и наземных, и воздушных. Аннотации…, Сброс к нейтральным командам — новый эпизод начинается с чистого состояния.… (+59 more)

### Community 8 - "Scenario"
Cohesion: 0.08
Nodes (35): match_conditions(), _profile_name(), AircraftProfile, FailureMode, FlightSegment, WeatherState, Нормированная дистанция сцепления, ветра, осадков и видимости двух условий., Сравнить ожидаемые условия участка с одним фактическим кадром backend. (+27 more)

### Community 10 - "Telemetry"
Cohesion: 0.07
Nodes (30): LateralDiagnostics, LongitudinalDiagnostics, FailureState, Эффективности исполнительных органов. Аннотации типов обязательны: без них…, ActuatorFeedback, ActuatorVector, AllocationDiagnostics, _clamp() (+22 more)

### Community 11 - ".from_dict"
Cohesion: 0.17
Nodes (8): _materialize_override(), Any, Применить одноуровневый sparse patch и вернуть полный неизменяемый config., Материализовать базовую ветку и sparse override выбранной строки., Serialize only the canonical profile- and matrix-aware schema v3., Прочитать schema v3 либо явно мигрируемую v1/v2 конфигурацию., test_preset_roundtrips_through_dict(), test_external_profile_controls_survive_scenario_v2_roundtrip()

### Community 13 - "pid.py"
Cohesion: 0.29
Nodes (4): Типы и порядок коэффициентов пяти наземных PID-регуляторов. Модуль намеренно не…, PIDDiagnostics, Пропорционально-интегрально-дифференциальный регулятор. Класс сохраняет прежнюю…, Типизированный снимок последнего такта регулятора.

### Community 14 - "test_ics_connector.py"
Cohesion: 0.10
Nodes (25): GearState, ICSOutputs, Разбор телеметрии стенда с совместимостью вперёд. Асимметрия намеренная (JSON-…, Команды и mode flags, сериализуемые ровно в ожидаемый стендом JSON., Сериализовать enums и 14 reserved zeros в точные UTF‑8 bytes wire contract., Дискретное положение стойки в кодировке ICSInputs., _connector(), _FakeSocket (+17 more)

### Community 15 - "test_run_matrix.py"
Cohesion: 0.10
Nodes (22): Разрешить только полный ``<шифр>/<номер>`` и вернуть точную строку JSON., resolve_matrix_run(), compose_matrix_scenario(), _install_through_scenarios(), Собрать сценарий из конкретных строк APPROACH/ROLLOUT/TAXI.…, Одна строка каталога → минимальный сценарий нужного участка или сквозной пары., Перенести накопленные overrides одного шифра на следующее условие этого же…, Собрать Б.4 из первой строки и заранее определённой пары законов. (+14 more)

### Community 16 - "AircraftProfile"
Cohesion: 0.10
Nodes (10): AircraftProfile, clamp(), Преобразовать воздушные команды ICD в нормированные DataRef X-Plane., Преобразовать нормированные команды пробега в DataRef X-Plane., Расширение реестра будущим профилем МС-21 без правки XPlaneSim., Проводка и масштабы конкретного планера X-Plane., Общая идентичность ЛА и необязательная привязка к X-Plane. Профиль нужен и…, Command refs retained under the historical public name. (+2 more)

### Community 17 - "test_full_flight.py"
Cohesion: 0.06
Nodes (59): IntFlag, ControlValid, Биты `ControlValidMask`: какие каналы несёт команда. **Один бит на одно…, initial_segment(), is_airborne(), FlightSegment, Окончен ли воздушный участок. Два независимых признака, любой достаточен:…, Сообщает ли стенд, что ВС в воздухе и достаточно высоко для приёма захода.… (+51 more)

### Community 18 - "ApproachController"
Cohesion: 0.13
Nodes (23): ApproachLimits, ApproachTelemetry, Предел крена по высоте: чем ниже, тем меньше запас до касания законцовкой.…, roll_limit_deg(), ApproachController, ApproachResult, clamp(), ApproachConfig (+15 more)

### Community 19 - "DashboardServer"
Cohesion: 0.24
Nodes (5): DashboardServer, Loopback-only HTTP lifecycle вокруг одного ``DashboardState``., Фактически привязанные host/port, включая ephemeral port 0 в тестах., Идемпотентно запустить daemon HTTP thread., Отклонить pending tuning, остановить thread и закрыть listening socket.

### Community 20 - "weather.py"
Cohesion: 0.05
Nodes (54): Фактические погодные условия со стенда (ветер, сцепление, осадки, видимость)., compose_wind(), decompose_wind(), Any, Enum, Погодные условия эпизода: описание, шкала сцепления и разбор ветра. Модуль **не…, Погодные условия. Поля — ровно то, что сообщает стенд (см. `from_ics`).…, `ICSInputs` → `WeatherState`. Единственный источник фактической погоды. Стенд… (+46 more)

### Community 21 - "XPlaneSim"
Cohesion: 0.06
Nodes (17): ApproachSetup, Результат безусловного best-effort отключения backend., ShutdownReport, AircraftProfile, ControlsState, FailureMode, FlightSegment, Path (+9 more)

### Community 23 - "PIDController"
Cohesion: 0.11
Nodes (28): PIDController, _legacy_reference(), Опциональная численность PID (шаг 5): каждый флаг проверяется на том дефекте,…, Если применено ровно то, что выдал PID, коррекции быть не должно., Уставка прыгает, объект стоит на месте — D-составляющая не должна реагировать.…, Выход ИЗ насыщения должен разрешаться всегда, иначе регулятор залипнет. kp…, Если насыщает уже пропорциональная часть, интегрировать нельзя вообще — и это…, Независимая реализация ПРЕЖНЕЙ численности — эталон для проверки парити. (+20 more)

### Community 25 - "DashboardState"
Cohesion: 0.15
Nodes (9): _allocator_stage(), DashboardState, _first_present(), HTTP читает только immutable recorder objects; controller меняет control-thread., Вернуть только новые recorder updates; смена run_id принудительно сбрасывает…, JSON-ready форма ``snapshot`` для ``GET /api/state``., Вызывается runtime ровно в начале control tick., Сохранить фактически записанный effective config, не изменяя SCENARIOS. (+1 more)

### Community 26 - "test_xplane_backend.py"
Cohesion: 0.08
Nodes (25): ApproachConfig, Параметры воздушного контура. Значения по умолчанию — настроенные на стенде.…, ApproachSetup, Начальные условия захода X-Plane на продолжении оси и глиссады., Начальные условия быстрого старта непосредственно с пробега., Детерминированно seeded шум/пропуски, применяемые только resettable backend., SensorNoise, TouchdownSetup (+17 more)

### Community 27 - "engaged_sim"
Cohesion: 0.12
Nodes (16): engaged_sim(), (sim, connector) с завершённым рукопожатием: стенд подтвердил `AgentIsActive =…, Регресс: расширение структуры не должно протащить руль высоты в маску пробега., test_ground_frame_still_declares_only_the_ground_channels(), Разделение органов из таблицы Заказчика: тиллер — на рулении, педальный пост —…, Базовый контур на стенде: `control_step` сам читает телеметрию и сам отправляет., На стенде каждый лишний `read_telemetry` — лишний приём UDP. Каждый такт явно…, Замолчать нельзя: последнее отклонение осталось бы приложенным до сторожа на… (+8 more)

### Community 29 - "IcsEngagement"
Cohesion: 0.05
Nodes (27): EngagementInputs, IcsEngagement, Автомат включения. `step(inputs)` вызывается каждый такт до формирования…, Полный сброс — новый эпизод начинается с невключённого состояния., Подхватить уже включённый извне пробег: шлём `ControlMode = Rollout`.…, Войти в пробег самостоятельно: шлём `ControlMode = Rollout`. Это же — передача…, Перейти `Approach → Landing` без нового рукопожатия. Закон остаётся воздушным., Войти в заход самостоятельно: шлём `ControlMode = Approach`. Обычно вызывать не… (+19 more)

### Community 30 - "ConditionMatch"
Cohesion: 0.25
Nodes (5): ConditionMatch, Сверка ожидаемых условий с фактической телеметрией backend., Истина, если набор фактических отказов совпал ровно., Истина при практически нулевой нормированной дистанции погоды., Погода остаётся отчётной; неверный отказ делает прогон недопустимым.

### Community 31 - "RunRecorder"
Cohesion: 0.19
Nodes (7): Exception, _mode_for(), Append-only writer; ошибка диска помечает прогон, но не выходит в control-loop., Поставить запись без блокировки control thread; переполнение инвалидирует run., Сохранить полный effective config; канонические config-файлы не затрагиваются., RunEvent, RunRecorder

### Community 32 - "._should_go_around"
Cohesion: 0.29
Nodes (5): above_decision_height(), ВС выше высоты решения ухода на второй круг (30 м по ТЗ 5.1.1.2). → уход…, Реверс убран: команды обратной тяги нулевые. В воздухе реверс не выдаётся…, Нужно ли уходить на второй круг по этому такту. → причина или `None`. Только…, ToleranceReport

### Community 33 - "Graphify Pipeline"
Cohesion: 0.08
Nodes (29): Folder Watcher, URL Ingestion, Extra Graph Exports, MCP Graph Server, Confidence Audit Trail, Deterministic Node IDs, Semantic Extraction Contract, Cross-Repository Graph Merge (+21 more)

### Community 34 - "XPlaneConnector"
Cohesion: 0.06
Nodes (22): DataRefSample, Атомарно снять все свежие значения без раскрытия внутреннего mutable cache., Discard pre-reload values so readiness cannot use stale telemetry., Повторять RREF requests до получения всех значений либо подробного timeout., Отправить один нативный 509-byte DREF packet., Последнее значение DataRef и monotonic timestamp его UDP-пакета., Отправить один нативный CMND packet., Перезагрузить текущий самолёт без открытия aircraft chooser. (+14 more)

### Community 35 - ".from_preset"
Cohesion: 0.11
Nodes (25): Скопировать канонический preset и заменить только запрошенные условия запуска., Готовый кадр `Telemetry` для прямых вызовов `control_step(dt, telemetry,…, telemetry(), Без `begin_flight` участок остаётся пробегом — среда обучения на это и…, test_the_rollout_default_keeps_the_existing_ground_behaviour(), Кадр без пакета стенда: пустой `faults` значит «сообщать некому», а не «всё…, Fallback работает лишь когда профиль ВПП явно приложен к кадру., Раньше неподвижное ВС завершало пробег на первом такте — до рукопожатия.… (+17 more)

### Community 36 - "ControllingSystem"
Cohesion: 0.10
Nodes (30): ControllingSystem, Связать сценарий с контуром; PID активируются после определения участка., Разорвать D-history после пропуска устаревшей UDP-очереди, не трогая интегралы., Оркестратор классического контура поверх стенда (`envs.ics_sim.ICSSim`).…, Аварийная остановка: обнулить органы и **снять заявку каналов**. Именно…, _lost_engagement(), Scenario, Снял ли стенд активность посреди прогона. → пора останавливаться. Без этой… (+22 more)

### Community 37 - "test_ics_engagement.py"
Cohesion: 0.10
Nodes (49): _Clock, _engine(), _pump(), Автомат включения управления на стенде. Два раздельных предмета проверки: *…, По ICD стенд должен два секунды ПОЛУЧАТЬ ModeAIReady=1. Если считать одно лишь…, Обратная защита: 30 кадров можно выпалить за 0.1 с — время тоже обязано пройти., Срыв предусловия обнуляет и время, и счётчик кадров., Требование ICD — непрерывность: пропуск готовности рвёт серию. (+41 more)

### Community 38 - "RunReader"
Cohesion: 0.10
Nodes (17): _apply_recorded_gains(), _equal(), main(), _number(), _parse_cell(), ControllingSystem, Path, Типизированный поток новых и legacy-строк с синтетическими ID для старых CSV. (+9 more)

### Community 39 - "sft.py"
Cohesion: 0.13
Nodes (23): GuardResult, Фактически разрешённые gains и причина ограничений/fallback., apply_gain_vector(), controller_gain_vector(), _feature_value(), feature_vector(), gain_vector_from_row(), _number() (+15 more)

### Community 40 - ".enqueue_gain_update"
Cohesion: 0.25
Nodes (4): _finite(), _jsonable(), Проверить HTTP-запрос и поставить полный PID triplet в control-thread queue., Поставить восстановление gains начала запуска для активного участка.

### Community 41 - "HandshakeBench"
Cohesion: 0.07
Nodes (18): flight_sim(), HandshakeBench, kinematic_sim(), KinematicBench, Стенд, включающий управление только после корректного рукопожатия. Ждёт…, Стенд, проигрывающий заход и касание **по сценарию**, а не по нашим командам.…, (sim, bench) на сценарном заходе. Рукопожатие ещё не выполнено., Мини-модель стенда: замедление ~ команде тормоза/реверса, ход вдоль осевой ВПП.… (+10 more)

### Community 43 - "ICSInputs"
Cohesion: 0.11
Nodes (31): ControlResult, ControlModeState, ICSInputs, IntEnum, UDP-мост к стенду заказчика (порт 3030) — транспорт пути поставки. `ICSInputs`…, Неизвестные поля исходного JSON; они доступны аудиту, но не закону управления., Режим управления/индикации, передаваемый в каждом ICSOutputs., Состояние створок реверса; величину задаёт отрицательный throttle rate. (+23 more)

### Community 45 - "3. Этапы реализации"
Cohesion: 0.09
Nodes (21): 1. Подтверждённые проблемы и целевое состояние, 2. Ключевые интерфейсы, 3. Этапы реализации, 4. Тестирование и критерии готовности, 5. Зафиксированные допущения, 6.1. Один dashboard вместо двух, 6.2. Единый источник данных, 6.3. Представления (+13 more)

### Community 46 - "test_sft_regressors.py"
Cohesion: 0.13
Nodes (18): feature_schema_hash(), GainGuard, Минимальная SFT-модель абсолютных коэффициентов PID и общий runtime guard., Стабильный hash порядка признаков; перестановка является сменой контракта., Проверяет prediction и ограничивает скорость изменения до записи в PID., checkpoint_metadata(), Path, Сформировать audit metadata загруженного файла, включая SHA-256 содержимого. (+10 more)

### Community 47 - "main"
Cohesion: 0.12
Nodes (15): compose_scenario(), Сценарий по имени либо шифру матрицы, без различия раскладки А/B., Собрать сценарий из независимых источников участков., resolve_scenario(), cli(), main(), Точка входа: подключиться к стенду, выбрать пресет и провести полёт.…, Единственная production CLI-точка для ICS и явного тестового X-Plane backend. (+7 more)

### Community 49 - "_Clock"
Cohesion: 0.15
Nodes (19): _air(), _Clock, _pump(), Ниже 400 футов стенд управление не отдаёт — гнать туда стимул бессмысленно., Необъявленная радиовысота — «стенд не сообщил», а не «ноль футов». Иначе ВС в…, После касания режим меняется на пробег — но не раньше: смена режима на глиссаде…, Ниже 80 футов потеря `AgentIsActive` не повод бросать органы: до земли секунды., Окно только удерживает подтверждение. Само оно включения не даёт. (+11 more)

### Community 50 - "test_go_around.py"
Cohesion: 0.16
Nodes (23): _armed_controller(), _drive(), _frame(), Уход на второй круг (fallback в воздухе): условия срабатывания и передача…, На пробеге ухода нет — segment guard (козление удерживает защёлка сегмента,…, Если реверс уже включён — взлёт невозможен, ухода нет., Устойчивый набор (прирост высоты + положительная верт. скорость) завершает…, После установившегося набора цикл снимает заявку каналов (ControlMode=Off,… (+15 more)

### Community 51 - "Hybrid Neural PID Controller"
Cohesion: 0.70
Nodes (5): Hybrid Neural PID Controller, Neural PID Gain Scheduler, PPO Training Loop, Preset-Anchored Deterministic Shield, SFT Behavioral-Cloning Warm Start

### Community 52 - "test_approach_criteria.py"
Cohesion: 0.07
Nodes (27): CompletionRule, GuidanceState, angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, Отдельный монитор критерия А.1.1 (не участвует в go-around). (+19 more)

### Community 53 - "._approach_step"
Cohesion: 0.11
Nodes (12): at_lateral_alignment_gate(), ils_blocker(), in_terminal_window(), Последние футы перед касанием, где прерывать заход опаснее, чем доработать.…, Полоса подхода к гейту совмещения с осью ± 5 м: `(30 м, 30 м + band]`. Только в…, Почему нельзя продолжать заход по этому кадру. `None` — можно. Закон читает…, Такт воздушного участка. → True, если управлять больше нечем. Касание…, Зафиксировать `Approach → Landing` на 25 ft без смены воздушного закона. (+4 more)

### Community 54 - "run_artifacts.py"
Cohesion: 0.16
Nodes (18): Вернуть одно свежее значение; stale/missing представлены ``None``., controller_pids(), _csv_value(), default_runs_root(), _effective_configs(), gains_snapshot(), _git_state(), _jsonable() (+10 more)

### Community 55 - "RunwayTracker"
Cohesion: 0.07
Nodes (21): find_earth_nav_dat(), ILSStation, parse_ils_station(), Path, Точка на продолжении оси; положительное расстояние — до порога., Найти LOC (тип 4) без хардкода частоты., GuidanceState, Решить прямую геодезическую задачу на сферической Земле. (+13 more)

### Community 56 - "RomanLogImporter"
Cohesion: 0.15
Nodes (13): _number(), Path, Импорт и проверка внешних CSV-прогонов roman_aviacia_ics., Потоково нормализует основной и authority CSV Романа., RomanLogImporter, verify_manifest(), Converts, Преобразовать координату из градусов, минут и секунд в signed degrees. (+5 more)

### Community 57 - "working_ics/approach_criteria.py"
Cohesion: 0.21
Nodes (7): angular_error_deg(), ApproachCriteriaConfig, ApproachCriteriaMonitor, ApproachCriteriaSample, ApproachCriteriaVerdict, ICSInputs, Evaluate the A.1.1 approach segment and stop at a radio-altitude floor.

### Community 58 - "test_dashboard.py"
Cohesion: 0.20
Nodes (13): _live(), _post(), parametrize, test_active_pid_is_editable_in_classical_and_shadow(), test_gain_change_is_queued_bumpless_and_records_full_event(), test_http_api_is_incremental_pending_and_loopback_only(), test_incremental_snapshot_uses_recorder_objects_and_stays_small_when_idle(), test_live_and_replay_use_the_same_dashboard_snapshot() (+5 more)

### Community 59 - "pretrain.py"
Cohesion: 0.09
Nodes (38): _condition_key(), _fit_feature_normalization(), load_offline_dataset(), _normalized_mse(), _physical_bounds(), _predict(), ndarray, Path (+30 more)

### Community 60 - "_load_updates"
Cohesion: 0.25
Nodes (5): _load_updates(), RunReader, Закрыть tuning и записать отказ для каждого неисполненного запроса., После recorder.finish держать полный run доступным, но только для чтения., RunEvent

### Community 61 - "test_control_parity.py"
Cohesion: 0.11
Nodes (19): CompletionRule, Enum, Генератор эталонной кривой скорости пробега. Два закона замедления: колокол…, Как активный наземный сценарий заканчивает управление., Генератор эталонной кривой скорости (Колокол Гаусса)., Начать профиль с фактической скорости текущего участка., То же без лишнего round-trip м/с → узлы → м/с на касании., Возвращает идеальную скорость (м/с) для текущей точки пути. (+11 more)

### Community 62 - "Project Dependencies"
Cohesion: 0.29
Nodes (7): Optional Gymnasium, NumPy, Pandas, Project Dependencies, Pytest, Termcolor, Optional PyTorch

### Community 64 - "PidGainRegressor"
Cohesion: 0.12
Nodes (15): device, PidGainRegressor, Any, Предсказать gains по последнему hidden state окна ``(B,T,F)``., Сохранить веса вместе с полным train↔runtime контрактом., Загрузить модель только после проверки полного train↔runtime контракта., Краткая форма ``load_checkpoint`` для потребителя, которому не нужна metadata., Восстановить и строго проверить normalization из checkpoint. (+7 more)

### Community 66 - "dashboard_core.py"
Cohesion: 0.14
Nodes (13): DashboardSnapshot, GainChange, main(), _mean(), Один локальный dashboard для live RunRecorder и read-only replay., Запустить локальный read-only replay dashboard до ``Ctrl+C``., Отображаемое имя, PID source и физическая фаза одной панели графика., Immutable запрос HTTP-thread, ожидающий применения control-thread. (+5 more)

### Community 67 - "GoAroundManeuver"
Cohesion: 0.33
Nodes (5): GoAroundManeuver, Начать уход: зафиксировать состояние манёвра и высоту входа., Состояние идущего ухода на второй круг. Пока он активен, заход не ведётся., Если набор не состоялся и стойка обжалась, воздушный закон на полосе не…, test_touchdown_also_wins_over_an_already_started_go_around()

### Community 68 - "test_working_ics_dashboard.py"
Cohesion: 0.35
Nodes (10): ClearWeatherILSController, DashboardState, _controller(), _inputs(), Characterization tests for the bench-validated ``working_ics`` dashboard., _record(), test_dashboard_records_four_airborne_views_and_diagnostics(), test_gain_updates_are_immediate_validated_and_share_pitch_with_flare() (+2 more)

### Community 70 - "ics_engagement.py"
Cohesion: 0.50
Nodes (4): Enum, EngagementState, Автомат включения управления на стенде заказчика. Стенд принимает наши команды…, Состояние **исходящего стимула** (что мы шлём стенду), а не факта включения.…

### Community 71 - "Unified Profile-Aware Scenario System"
Cohesion: 0.33
Nodes (6): Technical-Specification Acceptance Gates, Forward-Only Flight Segment Supervisor, Longitudinal and Lateral Ground Channels, PID Run Matrix, Unified Profile-Aware Scenario System, Legacy Scenario Preset Model

### Community 72 - "Interactive PID Dashboard"
Cohesion: 0.25
Nodes (9): Nine-View PID Dashboard, Run Recording Artifacts, buildTabs, draw, Gain Tuning and Snapshot Export, Interactive PID Dashboard, refresh, render (+1 more)

### Community 73 - "MatrixRun"
Cohesion: 0.06
Nodes (12): MatrixCase, MatrixCondition, MatrixRun, _number(), Any, FailureMode, FlightSegment, WeatherState (+4 more)

### Community 75 - "FailureManager"
Cohesion: 0.28
Nodes (5): FailureManager, FailureMode, Enum, Проецирует набор дискретных отказов в эффективности исполнительных органов., Привести состояние ровно к набору `modes` (то, что сообщил стенд). Пересборка с…

### Community 76 - "ICSInterface.cs"
Cohesion: 0.36
Nodes (7): External.Systems.ICS, ControlModeState, GearState, ICSInputs, ICSOutputs, ReverseEngineType, UInt64

### Community 77 - "План исправления"
Cohesion: 0.12
Nodes (15): 1. Handshake не повторяет рабочую последовательность, 2. Runtime работает с другой частотой и другой топологией, 3. RunRecorder находится в управляющем потоке, 4. Go-around имеет две отдельные ошибки, 5. Production entrypoint сейчас загрязнён debug-путём, ElevatorCmd действительно отправлялся, Найденные причины, План исправления (+7 more)

### Community 78 - "SftTrainConfig"
Cohesion: 0.22
Nodes (10): cli(), PretrainRunConfig, Последовательно обучить выбранные участки из одного каталога принятых прогонов., CLI офлайн-обучения; сеть никогда не открывает UDP и не сбрасывает X-Plane., Численные параметры одного воспроизводимого запуска обучения., Пути и участки для CLI, обучающего независимые air/ground checkpoints., Итог обучения участка и данные, необходимые для автоматической проверки gate., run_pretrain() (+2 more)

### Community 79 - "promote_candidate.py"
Cohesion: 0.33
Nodes (15): _gain_patch(), main(), promote_candidate(), PromotionError, Path, Проверяемое продвижение dashboard candidate в sparse scenario override., Пересчитать matrix/config hashes, а не доверять двум согласованно изменённым…, Проверить run и записать новый scenario JSON; registry исходников не меняется. (+7 more)

### Community 80 - "ICS PID Monitor"
Cohesion: 0.22
Nodes (9): Bench-Validated ILS Approach Channel, Tolerance-Gated Go-Around, buildControls, draw, formatTime, Four-Loop PID Tuning, ICS PID Monitor, Live and Historical Timeline (+1 more)

### Community 81 - "VlaydRolloutBridge"
Cohesion: 0.17
Nodes (11): FlightSegment, Enum, str, Участок, для которого выбираются закон управления и условия сценария., ICSInputs, socket, Hand the validated airborne session to Vlayd's existing rollout loop. The…, Keep Vlayd's engagement latch synchronized during the approach. (+3 more)

### Community 82 - "Autonomous Landing Controller"
Cohesion: 0.25
Nodes (8): Autonomous Landing Controller, Fourteen-Bit ControlValidMask Layout, Two-Factor ICS Engagement Handshake, ICS UDP JSON Protocol, Repository Guidance for Codex, Telemetry SI Unit Boundary, Autonomous Landing Controller, Repository Guidance for Claude Code

### Community 83 - "X-Plane Dashboard and Runtime Guide"
Cohesion: 0.43
Nodes (7): Dual-Backend SimInterface, ICS-Only Backend Guidance, Aircraft-Profile Checkpoint Isolation, Live A330 Acceptance Checklist, Profile-Aware Flight Scenarios, X-Plane Dashboard and Runtime Guide, X-Plane Resettable Runtime

### Community 84 - "test_working_ics_golden.py"
Cohesion: 0.26
Nodes (11): Касание: обжата **любая основная** стойка. Носовая не участвует — она…, _assert_numeric_result(), ICSInputs, Characterization baseline of the bench-validated ``working_ics`` approach., Канонический контур и формирователь пакета совпадают с эталоном до 1e-12., _replay(), _rows(), _state() (+3 more)

### Community 86 - "test_evaluate.py"
Cohesion: 0.16
Nodes (29): _check(), Criterion, evaluate_tz(), _range_check(), Чистые функции приёмки телеметрии по ТЗ и строкам матрицы. Каждый критерий…, Преобразовать наземные метрики запуска в вердикты раздела 5 ТЗ., Вернуть ``FAIL``, если провален хотя бы один применимый критерий., Один пункт ТЗ: предел, измеренное значение, вердикт и его причина. (+21 more)

### Community 87 - "scenarios.py"
Cohesion: 0.13
Nodes (22): ControlProfile, _copy_approach(), _copy_ground(), _ground_matrix_drafts(), _ground_segments_for_spec(), _GroundPresetSpec, _install_approach_scenarios(), _matrix_draft() (+14 more)

### Community 88 - "import_workbook"
Cohesion: 0.39
Nodes (8): import_workbook(), main(), Any, Path, Одноразовый импорт исходной Excel-матрицы в runtime-каталог JSON., Прочитать книгу целиком; функция не используется production runtime., _scalar(), write_catalog()

### Community 89 - "test_approach_channel.py"
Cohesion: 0.07
Nodes (37): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+29 more)

### Community 90 - "runs_for_code"
Cohesion: 0.50
Nodes (4): normalize_code(), Нормализовать латинские A/B и регистр к шифрам книги ``А/Б``., Вернуть строки одного шифра в исходном порядке книги., runs_for_code()

### Community 91 - "test_campaign.py"
Cohesion: 0.21
Nodes (19): campaign_phase(), campaign_rows(), campaign_summary(), _config_status(), main(), next_campaign_row(), Path, Порядок и фактический статус кампании из 280 матричных прогонов. (+11 more)

### Community 92 - "static_sim"
Cohesion: 0.10
Nodes (19): decode_outputs(), _integrate_throttle(), Отправленные команды в нормированном виде — для сравнения траекторий.…, `ICSOutputs` → (brake_l, brake_r, thr_l_rate, thr_r_rate, steer), всё…, Ход рычага РУД за такт: интеграл команды-скорости, зажатый физическим…, Доля обратной тяги по фактическому углу РУД: 0 в положительном секторе, 1 на…, (sim, connector) с неизменным кадром у порога ВПП. Скорость задаётся в **м/с**.…, Замедление считается по **фактическому** углу РУД, а не по команде. Тягой… (+11 more)

### Community 93 - "ICSSim"
Cohesion: 0.05
Nodes (31): ConditionMatch, FailureMode, ICSOutputs, _clamp(), ICSSim, FlightSegment, Обмен со стендом заказчика: телеметрия внутрь, команды наружу. Управление…, Принимает ли стенд наши команды. До включения любой `step` уходит вхолостую. (+23 more)

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
Cohesion: 0.06
Nodes (48): FakeConnector, make_ics_inputs(), on_ground(), Статический стенд: всегда один и тот же кадр, отправленное — в `sent_outputs`., Полный пакет стенда: нули по умолчанию + заданные поля., Кадр «ВС на полосе»: обжаты все стойки, курс/координаты у порога UUEE 06R., _cold_sim(), Тесты стенда (`ICSSim`) и подбора сценария — без реального стенда. (+40 more)

### Community 116 - "Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 3 плана [plan.md](docs/plan.md)., Source Nodes

### Community 124 - "_faults_from_inputs"
Cohesion: 0.40
Nodes (4): ICSInputs, _faults_from_inputs(), Отказы, о которых сообщает борт — **единственный** источник истины об отказах.…, Сигналы отказов со стенда → наши `FailureMode`. Отказы шасси…

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

### Community 131 - "control.py"
Cohesion: 0.36
Nodes (5): Полностью пересобрать наземные каналы controller этой конфигурацией., apply_ground_control(), build_pids(), Сборка классического контура из неизменяемой конфигурации., Фабрики stateful-объектов; config-модули хранят только данные.

### Community 135 - "Q: Приступай к выполнению этапа 2 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 2 плана docs/plan.md, Source Nodes

### Community 137 - "LandingFlapConfiguration"
Cohesion: 0.26
Nodes (13): alpha_prot_deg(), approach_limits(), ApproachLimits, _ceiling_weight_index(), detect_landing_flaps(), LandingFlapConfiguration, _linear_interpolate(), measured_landing_flaps() (+5 more)

### Community 142 - "pid_controller.py"
Cohesion: 0.08
Nodes (23): DashboardServer, DashboardState, Any, ICSInputs, Exact package port of the ICS approach contour validated in ``aviacia_v2``. The…, clamp(), ClearWeatherILSController, ControllerConfig (+15 more)

### Community 154 - "Normalization"
Cohesion: 0.10
Nodes (17): ArrayLike, Dataset, float32, float64, Normalization, NDArray, Выполнить deterministic inference и вернуть физические gains плюс OOD flag., Проверить prediction и ограничить его относительно accepted preset/предыдущего… (+9 more)

### Community 155 - "ics_sim.py"
Cohesion: 0.05
Nodes (56): AircraftProfile, ICSBenchConnector, IntEnum, get_aircraft_profile(), Профили преобразования команд ИСМПУ в органы управления X-Plane., Настройки воздушного участка: заход по ILS, выравнивание, управление скоростью.…, Глобальные константы контура управления (перенесены из main.ipynb)., FlightPhase (+48 more)

### Community 158 - "Q: Приступай к выполнению этапа 4 плана docs/plan.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 4 плана docs/plan.md, Source Nodes

### Community 167 - "Q: Приступай к выполнению этапа 8 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 8 плана [plan.md](docs/plan.md)., Source Nodes

### Community 181 - "Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md)."
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Приступай к выполнению этапа 7 плана [plan.md](docs/plan.md)., Source Nodes

### Community 183 - "ApproachRefused"
Cohesion: 0.21
Nodes (10): approach_blocker(), ApproachRefused, Воздушный участок начинать нельзя — с названной причиной. Отдельное исключение,…, Можно ли вообще судить об участке по этому кадру. Кадр без пакета стенда…, Почему нельзя вести заход по этому кадру. `None` — можно. Пока проверка одна,…, segment_is_decidable(), FlightSegment, Пересобрать stateful PID и уведомить backend до первого такта участка. (+2 more)

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

### Community 237 - "FrictionProfile"
Cohesion: 0.22
Nodes (5): FrictionProfile, Ступенчатый профиль сцепления по дистанции пробега., Компактные перцентили миллисекунд без зависимости в критическом пути., _timing_summary(), test_runtime_timing_reports_requested_percentiles_in_milliseconds()

### Community 244 - "ControlModeState"
Cohesion: 0.40
Nodes (3): ControlModeState, Сообщить автомату, что кадр **фактически ушёл** на стенд. Вызывается…, Значение `ControlMode` для исходящей команды (стимул). Во время выдержки —…

## Ambiguous Edges - Review These
- `Unified Profile-Aware Scenario System` → `Legacy Scenario Preset Model`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to
- `Dual-Backend SimInterface` → `ICS-Only Backend Guidance`  [AMBIGUOUS]
  CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **110 isolated node(s):** `ismpu`, `Answer`, `Outcome`, `Source Nodes`, `Answer` (+105 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **120 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `MatrixRun` (3× useful, score=2.979183365)
- `XPlaneSim` (3× useful, score=2.965617417)
- `PidGainRegressor` (2× useful, score=1.988230885)
- `rollout_bridge.py` (2× useful, score=1.988230885)
- `loop.py` (2× useful, score=1.96699511)
- `LateralChannel` (2× useful, score=1.929964048) _(code changed — re-verify)_

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Unified Profile-Aware Scenario System` and `Legacy Scenario Preset Model`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Dual-Backend SimInterface` and `ICS-Only Backend Guidance`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `ControllingSystem` connect `ControllingSystem` to `.control_step`, `control.py`, `test_refactoring_contracts.py`, `SimInterface`, `Scenario`, `Telemetry`, `test_run_matrix.py`, `test_full_flight.py`, `ApproachController`, `PIDController`, `test_xplane_backend.py`, `ics_sim.py`, `engaged_sim`, `ConditionMatch`, `._should_go_around`, `XPlaneConnector`, `.from_preset`, `sft.py`, `HandshakeBench`, `ICSInputs`, `test_sft_regressors.py`, `main`, `test_go_around.py`, `test_approach_criteria.py`, `._approach_step`, `ApproachRefused`, `test_dashboard.py`, `test_control_parity.py`, `GoAroundManeuver`, `VlaydRolloutBridge`, `scenarios.py`, `test_campaign.py`, `static_sim`, `.__init__`, `test_ics_sim.py`?**
  _High betweenness centrality (0.127) - this node is a cross-community bridge._
- **Why does `Telemetry` connect `Telemetry` to `.control_step`, `test_tolerance.py`, `test_refactoring_contracts.py`, `ControlsState`, `Scenario`, `test_full_flight.py`, `ApproachController`, `weather.py`, `XPlaneSim`, `test_xplane_backend.py`, `ics_sim.py`, `IcsEngagement`, `ConditionMatch`, `._should_go_around`, `.from_preset`, `ControllingSystem`, `HandshakeBench`, `ICSInputs`, `_Clock`, `test_go_around.py`, `test_approach_criteria.py`, `._approach_step`, `ApproachRefused`, `test_control_parity.py`, `GoAroundManeuver`, `VlaydRolloutBridge`, `test_working_ics_golden.py`, `scenarios.py`, `test_approach_channel.py`, `static_sim`, `ICSSim`, `test_ics_sim.py`, `_faults_from_inputs`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Why does `ICSSim` connect `ICSSim` to `XPlaneConnector`, `test_refactoring_contracts.py`, `ControlsState`, `engaged_sim`, `HandshakeBench`, `ICSInputs`, `test_sft_regressors.py`, `VlaydRolloutBridge`, `test_full_flight.py`, `test_ics_sim.py`, `_Clock`, `test_go_around.py`, `test_working_ics_golden.py`, `ics_sim.py`, `IcsEngagement`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `ControllingSystem` (e.g. with `ApproachSetup` and `ConditionMatch`) actually correct?**
  _`ControllingSystem` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 43 inferred relationships involving `Telemetry` (e.g. with `ApproachSetup` and `ConditionMatch`) actually correct?**
  _`Telemetry` has 43 INFERRED edges - model-reasoned connections that need verification._