---
type: "query"
date: "2026-08-14T22:36:00.679819+00:00"
question: "Реализовать этап 0: baseline, golden replay и dashboard characterization"
contributor: "graphify"
outcome: "useful"
source_nodes: ["approach_blocker()", "ControllingSystem", "WeatherState", "ObservationBuilder", "DashboardState", "ICSOutputs"]
---

# Q: Реализовать этап 0: baseline, golden replay и dashboard characterization

## Answer

Expanded from original query via graph vocab: approach, blocker, tolerance, runway, weather, observation, dashboard, working, replay, pid, outputs, landing. Общие точки исправления: approach_blocker, ControllingSystem._approach_step, runway_condition_from_bench и ObservationBuilder. working_ics оставлен неизменным; его PID, wire JSON и dashboard API закреплены characterization-тестами. Полный pytest: 427 passed, 2 skipped.

## Outcome

- Signal: useful

## Source Nodes

- approach_blocker()
- ControllingSystem
- WeatherState
- ObservationBuilder
- DashboardState
- ICSOutputs