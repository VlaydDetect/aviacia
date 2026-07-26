# X‑Plane 12, журналирование и PID‑дашборд

ICS остаётся производственным backend по умолчанию. X‑Plane выбирается только явно и предназначен для
воспроизводимых reset-сценариев, настройки и обучения.

## Запуск

Стенд ICS:

```powershell
.venv\Scripts\python.exe -m ismpu.runtime.loop
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
.venv\Scripts\python.exe -m ismpu.runtime.loop --dashboard
```

Live-настройка разрешается отдельным флагом:

```powershell
.venv\Scripts\python.exe -m ismpu.runtime.loop --dashboard-tune
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
