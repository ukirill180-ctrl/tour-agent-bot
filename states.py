"""Машина состояний клиента"""
from enum import Enum


class ClientState(str, Enum):
    NEW = "new"
    GREETING = "greeting"
    QUALIFYING = "qualifying"
    SEARCHING = "searching"
    PRESENTING = "presenting"
    ESCALATED = "escalated"
    CLOSED = "closed"


VALID_TRANSITIONS = {
    ClientState.NEW: {ClientState.GREETING},
    ClientState.GREETING: {ClientState.QUALIFYING},
    ClientState.QUALIFYING: {ClientState.SEARCHING, ClientState.PRESENTING, ClientState.ESCALATED},
    ClientState.SEARCHING: {ClientState.PRESENTING, ClientState.ESCALATED},
    ClientState.PRESENTING: {ClientState.ESCALATED, ClientState.CLOSED},
    ClientState.ESCALATED: {ClientState.GREETING, ClientState.CLOSED},
    ClientState.CLOSED: {ClientState.GREETING},
}


def can_transition(current: ClientState, target: ClientState) -> bool:
    return target in VALID_TRANSITIONS.get(current, set())


def next_state(current: ClientState) -> ClientState:
    transitions = VALID_TRANSITIONS.get(current, set())
    if not transitions:
        return current
    order = [
        ClientState.NEW, ClientState.GREETING, ClientState.QUALIFYING,
        ClientState.SEARCHING, ClientState.PRESENTING, ClientState.ESCALATED,
        ClientState.CLOSED,
    ]
    idx = order.index(current)
    for s in order[idx + 1:]:
        if s in transitions:
            return s
    return current
