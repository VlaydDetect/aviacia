---
type: "codebase_analysis"
date: "2026-08-16T20:37:16.238327+00:00"
question: "Проанализировать три неудачных production-прогона против working_ics и составить план исправления"
contributor: "graphify"
outcome: "useful"
source_nodes: ["ismpu/io/ics_engagement.py:L338", "ismpu/envs/ics_sim.py:L599", "ismpu/runtime/loop.py:L41", "ismpu/control/system.py:L494", "ismpu/runtime/run_artifacts.py:L460", "ismpu/io/ics_connector.py:L348", "ismpu/working_ics/runner.py:L304", "ismpu/working_ics/runner.py:L390"]
---

# Q: Проанализировать три неудачных production-прогона против working_ics и составить план исправления

## Answer

Expanded query: approach engagement runtime recorder telemetry elevator aileron handshake outputs pid control around. Численный PID-порт совпадает с эталоном с max error 0.0. Расхождение находится в runtime: engagement может стать true до фактической отправки фронта; первый пакет с маской 31 сразу содержит PID-команды вместо эталонных 0.2 s нейтрали. Production обрабатывает 17.6-18.1 Hz против 21.7 Hz эталона из-за polling, синхронной записи и одного recv на такт, что создаёт запаздывание. В raw TX ElevatorCmd присутствует и достигает +0.5 вместе с тягой +8, но в двух прогонах обратная связь почти отсутствует. Таймаут ухода ошибочно объявляется установленным набором. runtime.loop также импортирует working_ics вопреки единому production path.

## Outcome

- Signal: useful

## Source Nodes

- ismpu/io/ics_engagement.py:L338
- ismpu/envs/ics_sim.py:L599
- ismpu/runtime/loop.py:L41
- ismpu/control/system.py:L494
- ismpu/runtime/run_artifacts.py:L460
- ismpu/io/ics_connector.py:L348
- ismpu/working_ics/runner.py:L304
- ismpu/working_ics/runner.py:L390