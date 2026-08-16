# AGENTS.md

Инструкции для работы с кодовой базой ИСМПУ. Проект управляет МС‑21 от начала захода
примерно за 10 NM до завершения пробега/прямого руления. Производственный backend — стенд
заказчика ICS по UDP; X‑Plane 12 служит воспроизводимым resettable backend для настройки и
проверки. Оба backend проходят через один controller, Scenario, Telemetry, RunRecorder и
dashboard.

## Текущий объём проекта

- Воздух: статические PID localizer/glideslope/speed, flare как профиль setpoint, посадочный
  режим с 25 ft и уход на второй круг по допускам ТЗ.
- Земля: PID скорости и осевой линии, allocator руля/педалей/NWS/дифференциальных тормозов и
  реверса, затем переход Rollout → Taxi.
- Обучение: только два SFT-регрессора коэффициентов PID (`air` и `ground`). Сеть выдаёт
  коэффициенты классическим PID, но не actuator commands. Данные берутся только из принятых
  артефактов RunRecorder; live-среда во время обучения не запускается.
- Криволинейный taxi-маршрут до конкретного места стоянки не реализован. Поддерживается прямой
  участок по опубликованному стендом XTE/маршруту.

## Источники истины

- `docs/plan.md` — этапы рефакторинга и критерии готовности.
- `docs/XPLANE_DASHBOARD.md` — команды запуска, матричная кампания, dashboard, replay,
  candidate/promotion, артефакты и SFT.
- `docs/ТЗ_Интеграл-КБО-МС_ИСМПУ_итог_ф.pdf` — допуски заказчика.
- `docs/1_1_Приложение_1_Значения_для_опр_степени_критичности_отказа.pdf` — критичность,
  посадочные скорости, вертикальная скорость и перегрузки.
- `docs/ICSInterface.cs` — входная структура ICS и единицы. Файл неполон: стенд также
  публикует `AgentIsActive`.
- `docs/Входы_САУ.xlsx` — авторитет командных полей ICS, их единицы и пределы.
- `docs/Матрица_прогонов_ПИД_ИСМПУ.xlsx` — исходные 280 строк. Runtime читает только точный
  versioned snapshot `ismpu/config/run_matrix.v3.json`; обновление выполняется явно командой
  `python -m ismpu.tools.import_run_matrix`.
- `ismpu/working_ics/` — неизменяемый эталон проверенного воздушного закона и его dashboard.
  Production не импортирует этот package; parity-тесты сравнивают с ним активный код.

## Среда и команды

Использовать проектную `.venv`; Python из PATH может не содержать pytest/torch:

```powershell
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m ismpu.runtime.loop --aircraft-profile mc21
.venv\Scripts\python.exe -m ismpu.runtime.loop --backend xplane --start approach `
  --xplane-root "C:\X-Plane 12"
.venv\Scripts\python.exe -m ismpu.runtime.loop --backend xplane --start rollout `
  --xplane-root "C:\X-Plane 12"
```

ICS требует явный профиль, потому что ICD не сообщает тип самолёта. X‑Plane никогда не
выбирается неявно. Матричная строка задаётся полным идентификатором, например
`--run-id Б.2.2/4`; угадывать её по телеметрии запрещено.

Dashboard включается `--dashboard` (read-only) или `--dashboard-tune` (явное изменение PID) и
слушает только `127.0.0.1:8765`. Replay:

```powershell
.venv\Scripts\python.exe -m ismpu.gui.dashboard --replay runs\<run>
.venv\Scripts\python.exe -m ismpu.runtime.run_reader runs\<run> --atol 1e-12 --rtol 1e-12
```

Офлайн-SFT:

```powershell
.venv\Scripts\python.exe -m ismpu.runtime.pretrain runs --segment both
```

Модели сохраняются вне package как `checkpoints/sft_air.pt` и
`checkpoints/sft_ground.pt`. Запуск shadow/active требует явных путей `--sft-air-checkpoint` и
`--sft-ground-checkpoint`; без `--control-mode` всегда используется классический контур.

## Единственный runtime-путь

```text
runtime.loop
  → backend_factory.build_sim
      → ICSSim / XPlaneSim : SimInterface
  → Telemetry
  → ControllingSystem
      → ApproachController или LongitudinalChannel + LateralChannel + GroundAllocator
  → SimInterface.step(ControlsState)
  → RunRecorder
      → dashboard (те же RunSample/RunEvent)
      → report / replay / SFT dataset
```

ICS и X‑Plane различаются только transport и reset:

- `ICSSim.reset` наблюдательный — конфигурацией стенда владеет оператор.
- `XPlaneSim.reset` выставляет начальное состояние, погоду и поддерживаемые отказы.
- Перевод единиц находится на границе backend. Общая `Telemetry` использует SI. Исключение —
  `Telemetry.approach_inputs`: воздушные gains откалиброваны на knots/feet/fpm стенда и не
  пересчитываются без повторной настройки.

## Package layout

- `ismpu/io/` — UDP transports и ICS engagement; никакой логики управления.
- `ismpu/envs/` — `SimInterface`, `ICSSim`, `XPlaneSim`, общая `Telemetry`, weather и factory.
- `ismpu/control/` — PID, воздушный закон, supervisor участков, наземные каналы, allocator,
  trajectory, failures и tolerance monitor.
- `ismpu/config/` — профили ВС, сценарии, матрица, runway, требования ТЗ и все ICD-константы.
- `ismpu/runtime/` — loop, потоковые артефакты, report/replay, campaign, promotion и offline SFT.
- `ismpu/agent/pid_gain_regressor.py` — минимальная GRU-регрессия и guard коэффициентов.
- `ismpu/gui/` — один dashboard для live и replay.
- `tests/fakes.py` — общие fake backend/ICS frames. Не создавать рядом ещё один mock без
  необходимости.

## ICS wire contract

UDP payload — UTF‑8 JSON без framing, header, CRC или sequence number. Стенд сериализует
Newtonsoft JSON; добавление префикса ломает протокол. Адрес получателя берётся из первого
входящего datagram.

`ICSInputs.from_dict` игнорирует неизвестные ключи, но требует все известные: неизвестный сигнал
не должен ломать совместимость, а отсутствующий нельзя молча заменить нулём. Raw packet хранится
в `Telemetry.ics_inputs`; bench-specific properties выводятся из него, чтобы не было двух
источников истины.

В `ICSOutputs` ровно 14 командных полей. `ControlValidMask` имеет один бит на поле в порядке
объявления; `ALL = 16383`. Маска по умолчанию равна нулю. Основные подтверждённые единицы:

- elevator ±0.5 g, aileron ±25°, rudder ±30°;
- throttle — скорость рычага ±8 °/s, а не абсолютная позиция;
- brake command 0…45 mm;
- rudder pedal ±75 mm используется на rollout;
- tiller ±65 mm используется на taxi;
- reverse magnitude задаётся отрицательным движением рычага, двери — `ReverseXCmd`.

`ICSSim._to_outputs` выбирает маску по `ControlMode`: airborne, rollout и taxi заявляют только
органы, которые действительно формируют. Shutdown всегда сначала отправляет нейтраль под маской
0, затем закрывает transport. `ResilientSender` не роняет цикл на Windows UDP 10054, но считает
и rate-limit логирует ошибки.

## Engagement и участки

Команда действительна только когда одновременно выполнены:

```text
engaged = AgentIsActive подтверждён стендом AND handshake stimulus завершён
```

Airborne handshake: `ControlMode=Off`, `ModeAIReady=1` не менее 2.2 s и минимального числа
реально отправленных кадров, затем edge `0→1`. Ground handshake аналогичен, но длится 2.0 s.
До engagement маска равна 0. Потеря уже подтверждённого `AgentIsActive` ниже 80 ft удерживается
до завершения посадки; она никогда не создаёт подтверждение сама.

Supervisor движется только вперёд:

```text
APPROACH → Landing mode at 25 ft → ROLLOUT at first main-gear WOW → TAXI
```

Touchdown проверяется до вычисления воздушной команды, поэтому сам кадр касания уже получает
наземное управление. Любая основная стойка или `FlightPhase=LandRun` считается касанием. Bounce
не возвращает сегмент назад. Кадр без raw ICS packet ничего не решает о начальном сегменте.

Заход отклоняется до engagement при нелётной посадочной механизации. В воздухе потеря валидности
ILS или устойчивое превышение допусков выше 30 m инициирует terminal go-around: TOGA, набор и
крылья в горизонт. Ниже decision height посадка committed. Проверка касания выполняется первой,
поэтому плохой ILS в кадре касания не превращается в уход.

## Воздушный и наземный законы

`ApproachController` — численно идентичный port `working_ics`: localizer → roll target → aileron,
glideslope → vertical speed/pitch → elevator, IAS → throttle rate. Flare меняет setpoint в том же
pitch PID без reset интегратора или отдельной команды. Знаки и размерности PID нельзя
«исправлять» без live-перекалибровки; parity требует `1e-12`.

На земле:

- `LongitudinalChannel` ведёт скорость по `ReferenceTrajectory`, отдельно считает brake L/R и
  reverse L/R. Reverse запрещён ниже 60 kt с reset интегратора. `rollout_started` не даёт
  стационарному ВС завершить цикл до handshake.
- `LateralChannel` получает heading/XTE от стенда, когда поля валидны. Геодезия UUEE — только
  fallback. Пара `RunwayHeading=64°`, `LateralDeviation=0 m` обязана давать нулевой XTE,
  независимо от переданных координат.
- `GroundAllocator` после обоих каналов распределяет steering между rudder/pedal/tiller,
  дифференциальными тормозами и реверсом, применяет failure authority, clamp и slew limits.
  Порядок longitudinal → lateral mix → allocator является частью закона.

Для обычного полёта rollout передаёт управление taxi около 7.5 kt. Матричные наземные строки
останавливаются полностью, кроме Б.1.2: её прямой taxi завершает оператор `Ctrl+C` после
фактического конца участка.

## Сценарии и матрица

`ismpu.config.scenarios.SCENARIOS` — единственный реестр. `Scenario` содержит независимые
APPROACH/ROLLOUT/TAXI control+conditions для `mc21` и `a330-300`, statuses
`draft/tuned/accepted`, provenance, конкретные `matrix_runs` и sparse overrides.

Все 280 строк адресуются через `resolve_matrix_run`. Один шифр имеет одну базовую конфигурацию;
конкретная строка может иметь только sparse `run_overrides[run_id]`. Черновики листа Б строятся
из `GROUND_CASES` versioned JSON, а не из второго ручного списка. Композиция:

```python
compose_matrix_scenario(
    "full",
    approach_run="А.4.1/1",
    rollout_run="Б.3.1/1",
)
```

ICS не применяет условия: он сравнивает их с telemetry и записывает mismatch. X‑Plane применяет
только поддерживаемые условия. Отказы, введённые в воздухе, сохраняются после касания.

Кампания использует канонический порядок и уже записанные артефакты:

```powershell
.venv\Scripts\python.exe -m ismpu.runtime.campaign plan
.venv\Scripts\python.exe -m ismpu.runtime.campaign status runs
.venv\Scripts\python.exe -m ismpu.runtime.campaign next runs
```

## RunRecorder, dashboard и promotion

Каждый фактический запуск пишет `manifest.json`, raw RX/TX JSONL, общий `telemetry.csv`,
`approach.csv`, `ground.csv`, `events.jsonl`, `report.json` и явные candidates. Схема CSV
фиксирована; все известные ICS fields, неизвестный raw JSON, фактические commands, PID P/I/D,
integral, gains, allocator, SFT diagnostics, timestamps, `dt`, tick, segment и config revision
сохраняются на каждом такте. Запись потоковая с периодическим flush; ошибка writer видна и
делает прогон непригодным для приёмки/SFT, но не размыкает управление.

Dashboard читает только immutable `RunSample/RunEvent` из recorder. Incremental API не повторяет
старую историю. HTTP thread никогда не меняет controller: gain update попадает в ограниченную
очередь и применяется control thread на границе такта. `sft-active` read-only.

`Save candidate` не меняет SCENARIOS. `promote_candidate` проверяет PASS, hashes, точный run_id,
replay и отсутствие live-изменений, затем создаёт sparse override только выбранной строки.
`--accepted` требует доказательства всех обязательных строк шифра.

## SFT contract

`runtime.pretrain` читает только завершённые classical runs с
`report.sft_eligible=true`. Split выполняется по условиям/запускам до нарезки временных окон,
чтобы соседние кадры одного полёта не попали одновременно в train и validation.

Air model прогнозирует 9 gains трёх PID; ground model — 15 gains пяти PID. В checkpoint входят
segment, aircraft profile, feature/gain schemas и hashes, matrix hash, normalization, source
run IDs и validation gates. `GainGuard` отклоняет NaN/Inf/OOD, ограничивает физический диапазон
и скорость изменения. При любой ошибке static preset остаётся fallback; shadow никогда не
изменяет controller.

## Правила изменений

- Не изменять `ismpu/working_ics`; переносить исправления только в production и обновлять parity.
- Не добавлять второй protocol schema, controller, recorder, dashboard или список матрицы.
- Сохранять пользовательские изменения и не выполнять destructive Git-команды.
- Константы ICS держать в `config/ics.py`; единицы переводить только на backend boundary.
- Сначала искать файлы/символы через `rg`; редактировать через `apply_patch`.
- Комментарии объясняют физический смысл, единицы, safety invariant и причину нетривиального
  порядка. Не комментировать очевидный синтаксис.
- Для каждой нетривиальной ветки оставлять минимальную регрессию. Полный suite должен работать
  без живого ICS и X‑Plane.
