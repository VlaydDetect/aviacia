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
    approach_case="А.4.1",
    ground_case="Б.3.1",
)
```

Все строки листа А для `mc21` используют один проверенный воздушный пресет
`ics_clear_weather`, перенесённый из `roman_aviacia_ics/config/ics_clear_weather_pid.json`.
Они различаются условиями испытания, а не копиями наземного PID-пресета. Отказы листа А
сохраняются после касания; совпадающие отказы А и Б объединяются один раз.

`taxi=None` наследует источник пробега. Повторяющийся отказ хранится один раз в `frozenset`, поэтому
X‑Plane не вводит его повторно; неизменная погода также не переустанавливается. ICS не меняет среду:
он сверяет телеметрию с `SegmentConditions` и сохраняет `ConditionMatch` в `report.json`.

Для ICS профиль обязателен (`mc21` — канонический стендовый профиль). X‑Plane по умолчанию использует
`a330-300` и отклоняет профиль без X‑Plane-привязки. Воздушная ветка A330 остаётся `draft` до живой
приёмки; `draft` проверяется отдельно для профиля и участка.

Сценарии сериализуются только в JSON schema v2. Чтение schema v1 относит старые стендовые настройки к
`mc21`; старый A330-файл нужно читать с `legacy_aircraft_profile="a330-300"`.

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
При активном NPGS наземные коэффициенты должны передаваться в `DashboardState(npgs_active=True)`:
в этом режиме они доступны только для чтения. Экспорт создаёт новый JSON-снимок и не меняет пресет.

Replay общего лога или CSV Романа:

```powershell
.venv\Scripts\python.exe -m ismpu.gui.dashboard `
  --replay "runs\20260726T120000.000000Z\telemetry.csv"
```

## Артефакты прогона

Каждый запуск `runtime.loop` создаёт:

```text
runs/<UTC timestamp>/
├── metadata.json
├── telemetry.csv
├── gains-<UTC timestamp>.json   # только после явного экспорта
└── report.json
```

`telemetry.csv` содержит общую телеметрию, команды, участок полёта и для каждого из восьми PID:
value, setpoint, error, output, P/I/D, saturation и Kp/Ki/Kd. `runs/` исключён из Git.
Во время прогона снимки накапливаются в памяти, а CSV записывается один раз при штатном завершении
или обработанном прерывании (`Ctrl-C` / Interrupt). Пустой экземпляр `RunRecorder`, созданный в
ноутбуке, каталог не создаёт.

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
