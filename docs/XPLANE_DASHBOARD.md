# X‑Plane 12, журналирование и PID‑дашборд

ICS остаётся производственным backend по умолчанию. X‑Plane выбирается только явно и предназначен для
воспроизводимых reset-сценариев, настройки и обучения.

## Профильные сценарии

Канонический реестр — `ismpu.config.scenarios.SCENARIOS`; его значения являются готовыми объектами
`Scenario`. Сценарий содержит настройки `APPROACH / ROLLOUT / TAXI` отдельно для `mc21` и `a330-300`,
условия каждого участка и provenance источников составного сценария. Для произвольной сборки по
участкам используется:

```python
from ismpu.config.scenarios import compose_scenario

scenario = compose_scenario(
    "engine-then-reverse",
    approach="a_4_1_engine_out_high",
    rollout="left_reverse_fail",
)
```

Для матрицы стендовых прогонов удобнее выбирать строки листов А и Б напрямую:

```python
from ismpu.config.scenarios import compose_matrix_scenario

scenario = compose_matrix_scenario(
    "full",
    approach_run="А.4.1/1",
    rollout_run="Б.3.1/1",
)
```

Все строки листа А для `mc21` используют один проверенный воздушный пресет
`ics_clear_weather`, перенесённый из `roman_aviacia_ics/config/ics_clear_weather_pid.json`.
Они различаются условиями испытания, а не копиями наземного PID-пресета. Отказы листа А
сохраняются после касания; совпадающие отказы А и Б объединяются один раз.

`taxi_run=None` наследует источник пробега. Повторяющийся отказ хранится один раз в `frozenset`, поэтому
X‑Plane не вводит его повторно; неизменная погода также не переустанавливается. ICS не меняет среду:
он сверяет телеметрию с `SegmentConditions` и сохраняет `ConditionMatch` в `report.json`.

Для ICS профиль обязателен (`mc21` — канонический стендовый профиль). X‑Plane по умолчанию использует
`a330-300` и отклоняет профиль без X‑Plane-привязки. Воздушная ветка A330 остаётся `draft` до живой
приёмки; `draft` проверяется отдельно для профиля и участка.

Сценарии сериализуются в JSON schema v3 с конкретными `matrix_runs`, статусами профилей и sparse overrides.
Schema v1/v2 читаются миграторами; для старого A330-файла нужен
`legacy_aircraft_profile="a330-300"`.

NPGS-артефакты разделены по профилям:

```text
checkpoints/
├── mc21/
│   ├── npgs_sft.pt
│   └── npgs_final.pt
└── a330-300/
    ├── npgs_sft.pt
    └── npgs_final.pt
```

Чекпоинт другого профиля или с несовпадающим снимком `GainSpace` не загружается. Старый чекпоинт без
профиля мигрируется только при явном `legacy_aircraft_profile` и совпадении сохранённых диапазонов.

## Запуск

Стенд ICS:

```powershell
.venv\Scripts\python.exe -m ismpu.runtime.loop --aircraft-profile mc21
```

Матричный прогон ICS запускается только по полной строке, например
`--run-id Б.2.2/4`; шифр по телеметрии не угадывается.

Полный заход в X‑Plane:

```powershell
.venv\Scripts\python.exe -m ismpu.runtime.loop `
  --backend xplane `
  --start approach `
  --xplane-root "C:\X-Plane 12"
```

Быстрый старт с пробега:

```powershell
.venv\Scripts\python.exe -m ismpu.runtime.loop `
  --backend xplane `
  --start rollout `
  --xplane-root "C:\X-Plane 12"
```

`--xplane-root` обязателен для захода: частота ILS не зашита в код, а находится в установленном
`Custom Data\earth_nav.dat` или `Resources\default data\earth_nav.dat`. До снятия паузы NAV1
настраивается и проверяется.

## Дашборд

Безопасный режим наблюдения:

```powershell
.venv\Scripts\python.exe -m ismpu.runtime.loop --aircraft-profile mc21 --dashboard
```

Live-настройка разрешается отдельным флагом:

```powershell
.venv\Scripts\python.exe -m ismpu.runtime.loop --aircraft-profile mc21 --dashboard-tune
```

Сервер слушает только `127.0.0.1:8765`. Девять представлений — `Roll`, `Pitch`, `Flare`,
`Air Speed`, `Steer`, `Brake L/R`, `Reverse L/R`; `Pitch` и `Flare` используют один PID.
Live и replay используют один поток `RunSample`/`RunEvent`: API отдаёт только изменения после
`sequence`, а timeline позволяет перейти к прошлому кадру и вернуться в Live с окнами
30/60/120 секунд или Full run. В режиме `sft-active` коэффициенты доступны только для чтения;
в `classical` и `sft-shadow` изменение активного участка ставится в очередь и применяется на
следующем такте с bumpless-переносом состояния PID. После завершения dashboard остаётся доступен
300 секунд; интервал меняется через `--dashboard-hold-seconds`, `0` отключает удержание.

Replay общего лога или CSV Романа:

```powershell
.venv\Scripts\python.exe -m ismpu.gui.dashboard `
  --replay "runs\20260726T120000.000000Z"
```

Детерминированная проверка самого контроллера без UDP/X-Plane:

```powershell
.venv\Scripts\python.exe -m ismpu.runtime.run_reader `
  "runs\20260726T120000.000000Z" --atol 1e-12 --rtol 1e-12
```

`Save candidate` сохраняет полный effective config, но не меняет канонический сценарий. После
успешного прогона кандидат проверяется и превращается в sparse override своей строки матрицы:

```powershell
.venv\Scripts\python.exe -m ismpu.runtime.promote_candidate `
  "runs\20260726T120000.000000Z\candidates\rollout-1.json"
```

Флаг `--accepted` разрешён только при наличии успешных артефактов всех обязательных строк этого
кода; корень доказательств задаётся через `--evidence-root`.

## Кампания настройки матрицы

Канонический порядок этапа 7 и следующая незачтённая строка вычисляются из каталога и уже
записанных артефактов — отдельного редактируемого журнала нет:

```powershell
.venv\Scripts\python.exe -m ismpu.runtime.campaign plan
.venv\Scripts\python.exe -m ismpu.runtime.campaign status runs
.venv\Scripts\python.exe -m ismpu.runtime.campaign next runs
```

Порядок: `Б.1.1/1`, остальные Б.1.1, Б.1.2, Б.2.*, Б.3.*, А.1.*, А.2–А.4 и Б.4.*.
После promotion накопленные sparse overrides применяются к следующему условию того же шифра:

```powershell
.venv\Scripts\python.exe -m ismpu.runtime.loop `
  --aircraft-profile mc21 `
  --scenario-json "runs\...\candidates\rollout-1.tuned.scenario.json" `
  --run-id "Б.1.1/2" `
  --dashboard-tune
```

Перенос JSON на другой шифр запрещён. Для Б.1.2 контур не угадывает конец прямого участка:
оператор завершает зачётный taxi-прогон `Ctrl+C`, который записывается как
`operator_completed`; до первого управляющего такта это остаётся обычным `interrupted`.
`accepted` допускает разные effective config отдельных условий, но проверяет PASS каждой строки
шифра, её config/matrix hashes, отсутствие live-изменений и replay. PASS под `draft/tuned` служит
приёмочным доказательством, но получает `sft_eligible=true` только при повторной записи уже под
`accepted`-конфигурацией.

## Артефакты прогона

Каждый запуск `runtime.loop` создаёт:

```text
runs/<UTC timestamp>/
├── manifest.json
├── raw-rx.jsonl
├── raw-tx.jsonl
├── telemetry.csv
├── approach.csv
├── ground.csv
├── events.jsonl
├── candidates/                  # явные экспорты коэффициентов
└── report.json
```

`telemetry.csv` содержит весь полёт: raw/SI-входы, фактически сформированные выходы, timestamps,
`dt`, `tick_id`, участок, режим/маску и revision конфигурации. `approach.csv` и `ground.csv` —
потоковые срезы той же фиксированной схемы по участкам; P/I/D, состояние и коэффициенты всех восьми
PID сохраняются на каждом такте. Сырые ICS payload записываются до разбора и после успешной UDP-
отправки без повторной сериализации. CSV/JSONL дописываются по ходу полёта и flush-ятся не реже раза
в секунду; в памяти остаётся только ограниченное окно дашборда. Ошибка записи видна в manifest,
дашборде и делает результат непригодным для приёмки/SFT, но не размыкает управление.

Итоги выбранных строк матрицы собираются без Excel-зависимости:

```powershell
.venv\Scripts\python.exe -m ismpu.runtime.run_report aggregate runs `
  --output runs\matrix-results.csv

# эквивалентная команда кампании
.venv\Scripts\python.exe -m ismpu.runtime.campaign report runs `
  --output runs\matrix-results.csv
```

`matrix-results.csv` использует исходные 16 колонок книги, включая `Статус`,
`Факт. макс. отклонения` и `Комментарий`. `runs/` исключён из Git. Пустой экземпляр
`RunRecorder`, созданный в ноутбуке, каталог не создаёт до `start`, первой записи или `finish`.
Для матричного запуска `report.json` дополнительно содержит критерии конкретной строки,
touchdown distance/speed/sink/load, saturation по каналам, applied gains, наличие actuator
feedback, плавность стыка и ожидаемую/фактическую диагностику сцепления, ветра и риска
аквапланирования. Несовпадение погоды остаётся видимым `report_only`; несовпадение отказа делает
прогон `INVALID`.

Большие исходные логи Романа остаются в `roman_aviacia_ics`. Их целостность описана в
`docs/roman_logs_manifest.json`; `ismpu.runtime.roman_logs.verify_manifest` сообщает отсутствующие
и изменённые файлы, а `RomanLogImporter` потоково приводит обе его CSV-схемы к общей.

## Профили и безопасность

- Реализован штатный профиль `a330-300`. Неизвестный самолёт завершается явной ошибкой.
- Команды тяги пишутся в `ENGN_thro_use` под `override_throttles`; тормоза — под
  `override_toe_brakes`. Все команды проходят профильный clamp.
- `deactivate` и `close` сначала выдают нейтраль, затем освобождают roll/pitch/yaw/throttle/brake override.
- После reload старые samples удаляются, подписки RREF возобновляются, а freshness проверяется по timestamp.
- `Scenario` сериализует оба начальных состояния, sensor noise, порывы и переменный профиль сцепления.
- Стендовый и X‑Plane‑пресеты не являются одним объектом. Воздушный A330‑пресет X‑Plane имеет `draft=True`.

## Живая приёмка A330

Профиль нельзя переводить из `draft` до выполнения на установленном X‑Plane 12:

1. ILS UUEE 06R найден из фактической nav-базы, NAV1 подтверждён до снятия паузы.
2. Старт `approach` даёт примерно 2800 ft RA, FLAPS 3, выпущенное шасси и устойчивый цикл 20 Гц.
3. Заход проходит без рассогласования знаков roll/pitch/yaw и без stale telemetry.
4. Первое обжатие основной стойки переключает команды с воздушных на тормоза/реверс/путевое управление.
5. После достижения taxi speed органы нейтрализуются, override освобождаются.
6. Повторный `rollout` reset воспроизводим и не наследует повреждения/нагрев предыдущего эпизода.

Автономные mock/scripted-тесты проверяют протокол и переходы, но не заменяют этот аэродинамический прогон.
