"""This module models front-panel knobs on physical-style synth modules."""


class Knob:
    """This knob stores one adjustable value within a fixed physical range."""

    def __init__(self, name: str, minimum: float, maximum: float, value: float, unit: str) -> None:
        """Create a named knob with a range, value, and displayed unit."""
        self.name = name
        self.minimum = minimum
        self.maximum = maximum
        self.unit = unit
        self.value = value

    def set_value(self, value: float) -> None:
        """Turn the knob to a value within its allowed range."""
        self.value = max(self.minimum, min(self.maximum, value))
