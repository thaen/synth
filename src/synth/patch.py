"""This module models the jacks and cables on a physical synth board."""


class OutputJack:
    """This jack holds the voltage that a module sends through a cable."""

    def __init__(self, name: str) -> None:
        """Create a named output jack with zero volts at first."""
        self.name = name
        self.voltage = 0.0


class InputJack:
    """This jack reads voltage from the cable plugged into it."""

    def __init__(self, name: str) -> None:
        """Create a named input jack with no cable connected."""
        self.name = name
        self.cable: PatchCable | None = None

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
        self.source = source
        self.destination = destination
        destination.cable = self
