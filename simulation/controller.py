"""Educational control logic only: no physical I/O or machine safety functions."""

from dataclasses import dataclass
from enum import Enum


class State(str, Enum):
    STOPPED = "STOPPED"
    READY = "READY"
    FEED = "FEED"
    ACCEPT = "ACCEPT"
    EXTEND = "EXTEND"
    RETRACT = "RETRACT"
    FAULT = "FAULT"


@dataclass(frozen=True)
class Inputs:
    start: bool = False
    reset: bool = False
    stop: bool = False
    permissive_ok: bool = True
    station: bool = False
    metal: bool = False
    accepted: bool = False
    rejected: bool = False
    pusher_home: bool = True
    pusher_extended: bool = False


@dataclass(frozen=True)
class Outputs:
    conveyor: bool = False
    extend: bool = False
    alarm: bool = False
    ready: bool = False


@dataclass(frozen=True)
class Config:
    scan_ms: int = 20
    feed_timeout_ms: int = 5000
    accept_timeout_ms: int = 3000
    extend_timeout_ms: int = 1000
    retract_timeout_ms: int = 1000

    def __post_init__(self):
        for name, value in vars(self).items():
            if type(value) is not int or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        for name, value in vars(self).items():
            if name != "scan_ms" and value % self.scan_ms:
                raise ValueError(f"{name} must be a multiple of scan_ms")


class Controller:
    """One part per Start edge; each tick advances one configured logical scan."""

    def __init__(self, config=None):
        self.config = config or Config()
        self.state = State.STOPPED
        self.fault = None
        self.accepted_count = 0
        self.rejected_count = 0
        self.elapsed_ms = 0
        self._start_previous = False
        self._reset_previous = False
        self._accepted_seen = False
        self._rejected_seen = False

    @staticmethod
    def _clear(i):
        return (
            not (i.station or i.accepted or i.rejected)
            and i.pusher_home
            and not i.pusher_extended
        )

    def _enter(self, state):
        self.state = state
        self.elapsed_ms = 0

    def _trip(self, reason):
        if self.state != State.FAULT:
            self.fault = reason  # Preserve the first fault until an eligible reset.
            self._enter(State.FAULT)

    def _outputs(self, i):
        return Outputs(
            conveyor=self.state in (State.FEED, State.ACCEPT),
            extend=self.state == State.EXTEND,
            alarm=self.state == State.FAULT,
            ready=self.state == State.READY and self._clear(i),
        )

    def tick(self, i):
        start_edge = i.start and not self._start_previous
        reset_edge = i.reset and not self._reset_previous
        self._start_previous = i.start
        self._reset_previous = i.reset

        if not i.permissive_ok:
            self._trip("INTERLOCK_OPEN")
        elif i.pusher_home and i.pusher_extended:
            self._trip("LIMIT_CONFLICT")
        elif i.accepted and i.rejected:
            self._trip("EXIT_CONFLICT")

        if self.state == State.FAULT:
            if (
                reset_edge and not i.start and not i.stop
                and i.permissive_ok and self._clear(i)
            ):
                self.fault = None
                self._enter(State.READY)
            return self._outputs(i)

        if i.stop:
            self._enter(State.STOPPED)
            return self._outputs(i)

        if self.state == State.STOPPED:
            if reset_edge and not i.start and self._clear(i):
                self._enter(State.READY)
            return self._outputs(i)

        if self.state == State.READY:
            if start_edge:
                if not self._clear(i):
                    self._trip("START_NOT_CLEAR")
                else:
                    self._accepted_seen = False
                    self._rejected_seen = False
                    self._enter(State.FEED)
            return self._outputs(i)

        self.elapsed_ms += self.config.scan_ms
        timeout = {
            State.FEED: self.config.feed_timeout_ms,
            State.ACCEPT: self.config.accept_timeout_ms,
            State.EXTEND: self.config.extend_timeout_ms,
            State.RETRACT: self.config.retract_timeout_ms,
        }[self.state]
        # A success arriving on the deadline scan is late; timeout wins.
        if self.elapsed_ms >= timeout:
            self._trip(f"{self.state.value}_TIMEOUT")
            return self._outputs(i)

        if self.state in (State.FEED, State.ACCEPT) and not i.pusher_home:
            self._trip("PUSHER_NOT_HOME")
        elif (
            (self.state == State.FEED and (i.accepted or i.rejected))
            or (self.state == State.ACCEPT and i.rejected)
            or (self.state in (State.EXTEND, State.RETRACT) and i.accepted)
        ):
            self._trip("UNEXPECTED_EXIT")
        elif self.state == State.FEED:
            if i.station:
                self._enter(State.EXTEND if i.metal else State.ACCEPT)
        elif self.state == State.ACCEPT:
            self._accepted_seen |= i.accepted
            if self._accepted_seen and not i.accepted and not i.station:
                self.accepted_count += 1
                self._enter(State.READY)
        else:
            self._rejected_seen |= i.rejected
            if self.state == State.EXTEND and i.pusher_extended:
                self._enter(State.RETRACT)
            elif (
                self.state == State.RETRACT and i.pusher_home
                and self._rejected_seen and not i.rejected and not i.station
            ):
                self.rejected_count += 1
                self._enter(State.READY)

        return self._outputs(i)
