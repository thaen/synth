"""This module models the jacks and cables on a physical synth board."""

from enum import Enum


class SignalKind(Enum):
    """This enumeration names the intended role of voltage on a jack."""

    AUDIO = "audio"
    CONTROL = "control"
    GATE = "gate"


class OutputJack:
    """This jack holds the voltage that a module sends through a cable."""

    def __init__(self, name: str, signal_kind: SignalKind) -> None:
        """Create a named output jack with a voltage role and zero volts at first."""
        self.name = name
        self.signal_kind = signal_kind
        self.voltage = 0.0
        self.owner: object | None = None


class InputJack:
    """This jack reads voltage from the cable plugged into it."""

    def __init__(
        self, name: str, accepted_kinds: tuple[SignalKind, ...], visible: bool = True
    ) -> None:
        """Create a named input jack with accepted voltage roles and no cable."""
        self.name = name
        self.accepted_kinds = accepted_kinds
        self.visible = visible
        self.cable: PatchCable | None = None
        self.owner: object | None = None

    def read_voltage(self) -> float:
        """Return the connected cable's voltage, or zero volts without a cable."""
        if self.cable is None:
            return 0.0
        return self.cable.source.voltage


class PatchCable:
    """This cable connects one output jack to one input jack."""

    def __init__(self, source: OutputJack, destination: InputJack) -> None:
        """Plug the source output into the destination input."""
        if destination.cable is not None:
            raise ValueError(f"The {destination.name} input already has a cable.")
        if source.signal_kind not in destination.accepted_kinds:
            raise ValueError(
                f"The {destination.name} input does not accept {source.signal_kind.value} voltage."
            )
        self.source = source
        self.destination = destination
        destination.cable = self

    def disconnect(self) -> None:
        """Unplug this cable from its destination input jack."""
        if self.destination.cable is self:
            self.destination.cable = None
