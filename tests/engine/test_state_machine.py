"""Tests de la máquina de estados del agente."""

import pytest

from engine.runtime.state_machine import AgentState, StateMachine


def test_initial_state_is_idle():
    sm = StateMachine(agent_id="test")
    assert sm.state == AgentState.IDLE


def test_valid_transition_idle_to_planning():
    sm = StateMachine(agent_id="test")
    sm.transition(AgentState.PLANNING, reason="test")
    assert sm.state == AgentState.PLANNING


def test_invalid_transition_raises():
    """IDLE → EXECUTING no es válido (hay que planificar primero)."""
    sm = StateMachine(agent_id="test")
    with pytest.raises(ValueError):
        sm.transition(AgentState.EXECUTING)


def test_history_records_transitions():
    sm = StateMachine(agent_id="test")
    sm.transition(AgentState.PLANNING, reason="r1")
    sm.transition(AgentState.EXECUTING, reason="r2")
    assert len(sm.history) == 2
    assert sm.history[0].to_state == "planning"
    assert sm.history[1].to_state == "executing"


def test_is_terminal():
    sm = StateMachine(agent_id="test")
    assert not sm.is_terminal()
    sm.transition(AgentState.PLANNING)
    sm.transition(AgentState.EXECUTING)
    sm.transition(AgentState.REFLECTING)
    sm.transition(AgentState.COMPLETED)
    assert sm.is_terminal()


def test_reset_returns_to_idle():
    sm = StateMachine(agent_id="test")
    sm.transition(AgentState.PLANNING)
    sm.transition(AgentState.EXECUTING)
    sm.transition(AgentState.REFLECTING)
    sm.transition(AgentState.COMPLETED)
    sm.reset()
    assert sm.state == AgentState.IDLE
