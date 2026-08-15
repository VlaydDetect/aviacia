"""Contracts of the unified aircraft-profiled scenario model."""

from dataclasses import replace

import pytest

from ismpu.config.scenarios import (
    AircraftControlSet,
    SCENARIOS,
    Scenario,
    compose_scenario,
    select_scenario,
)
from ismpu.config.segments import FlightSegment
from ismpu.control.failures import FailureMode


def test_profile_controls_are_independent_and_draft_is_per_branch():
    scenario = SCENARIOS["default"]
    mc21 = scenario.aircraft_controls["mc21"]
    a330 = scenario.aircraft_controls["a330-300"]

    assert mc21 is not a330
    assert mc21.rollout is not a330.rollout
    assert mc21.rollout.brake_l is not a330.rollout.brake_l
    assert not scenario.is_draft("mc21", FlightSegment.APPROACH)
    assert scenario.is_draft("a330-300", FlightSegment.APPROACH)
    assert a330.approach.name == "xplane_a330_approach"


def test_automatic_selection_never_falls_back_to_a_draft_profile_branch():
    with pytest.raises(ValueError, match="нет допущенных сценариев"):
        select_scenario(
            aircraft_profile="a330-300",
            segment=FlightSegment.APPROACH,
        )
    assert select_scenario(
        aircraft_profile="a330-300",
        segment=FlightSegment.APPROACH,
        include_draft=True,
    ).scenario_id == "default"


def test_missing_profile_and_segment_fail_explicitly():
    scenario = SCENARIOS["default"]
    with pytest.raises(KeyError, match="missing"):
        scenario.control_for("missing", FlightSegment.ROLLOUT)

    incomplete = replace(
        scenario,
        scenario_id="incomplete",
        conditions={FlightSegment.ROLLOUT: scenario.conditions_for(
            FlightSegment.ROLLOUT)},
    )
    with pytest.raises(KeyError, match="approach"):
        incomplete.conditions_for(FlightSegment.APPROACH)


def test_composition_selects_each_phase_and_preserves_provenance():
    composed = compose_scenario(
        "engine-then-reverse",
        approach="a_4_1_engine_out_high",
        rollout="left_reverse_fail",
    )

    assert composed.provenance == {
        FlightSegment.APPROACH: "a_4_1_engine_out_high",
        FlightSegment.ROLLOUT: "left_reverse_fail",
        FlightSegment.TAXI: "left_reverse_fail",
    }
    assert composed.conditions_for(FlightSegment.APPROACH).failures == frozenset({
        FailureMode.ENGINE_OUT_LEFT,
    })
    assert composed.conditions_for(FlightSegment.ROLLOUT).failures == frozenset({
        FailureMode.REVERSE_LEFT_FAIL,
    })
    assert composed.control_for("mc21", FlightSegment.APPROACH).name == \
        "ics_clear_weather"
    assert composed.control_for("mc21", FlightSegment.ROLLOUT) == \
        SCENARIOS["left_reverse_fail"].control_for("mc21", FlightSegment.ROLLOUT)
    assert composed.control_for("mc21", FlightSegment.ROLLOUT) is not \
        SCENARIOS["left_reverse_fail"].control_for("mc21", FlightSegment.ROLLOUT)


def test_composition_keeps_repeated_failures_as_one_set_member():
    source = Scenario.from_preset(
        "default", failures=(FailureMode.ENGINE_OUT_LEFT,))
    composed = compose_scenario(
        "repeated", approach=source, rollout=source)

    for segment in FlightSegment:
        assert composed.conditions_for(segment).failures == frozenset({
            FailureMode.ENGINE_OUT_LEFT,
        })


def test_external_profile_controls_survive_scenario_v2_roundtrip():
    base = SCENARIOS["default"]
    experimental = replace(
        base.aircraft_controls["mc21"],
        rollout=replace(
            base.aircraft_controls["mc21"].rollout,
            brake_l={
                **base.aircraft_controls["mc21"].rollout.brake_l,
                "kp": 0.4321,
            },
        ),
    )
    scenario = replace(
        base,
        scenario_id="external-profile",
        aircraft_controls={"experimental": experimental},
    )

    document = scenario.to_dict()
    restored = Scenario.from_dict(document)
    assert document["schema_version"] == 3
    assert restored.control_for(
        "experimental", FlightSegment.ROLLOUT).brake_l["kp"] == 0.4321
    assert restored.to_dict() == document
