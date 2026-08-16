---
type: "architecture"
date: "2026-08-16T21:22:40.425048+00:00"
question: "Почему production-заход терял паритет с working_ics и как это исправлено?"
contributor: "graphify"
outcome: "useful"
source_nodes: ["IcsEngagement", "ICSSim", "ControllingSystem", "RunRecorder", "PIDController", "ICSOutputs"]
---

# Q: Почему production-заход терял паритет с working_ics и как это исправлено?

## Answer

PID-математика совпадала; ломался замкнутый контур. Исправлены фактическое завершение handshake и 0.2 с нейтрального Approach, receive-driven обработка каждого RX с эталонным TX gate, сброс UDP backlog после пауз, асинхронный RunRecorder и отделение go-around от windup. Production entrypoint очищен. Проверка: 373 passed, 2 skipped; working_ics не изменён.

## Outcome

- Signal: useful

## Source Nodes

- IcsEngagement
- ICSSim
- ControllingSystem
- RunRecorder
- PIDController
- ICSOutputs