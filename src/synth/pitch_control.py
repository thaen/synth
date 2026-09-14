"""This module models a front-panel control that produces pitch voltage."""

from synth.controls import Knob
from synth.patch import OutputJack, SignalKind


class PitchControl:
    """This module places one-volt-per-octave pitch voltage on its output jack."""

    display_name = "PITCH CONTROL"

    def __init__(self, pitch_volts: float = 0.0) -> None:
        """Create a pitch control centered at zero volts, which represents A4."""
        self.pitch_knob = Knob("Pitch", -2.0, 2.0, pitch_volts, "V")
        self.pitch_output = OutputJack("Pitch output", SignalKind.CONTROL)

    def advance(self) -> None:
        """Place the knob's pitch voltage on the output jack."""
        self.pitch_output.voltage = self.pitch_knob.value

    def controls(self) -> list[Knob]:
        """Return the front-panel controls that the generic board view can draw."""
        return [self.pitch_knob]

    def input_jacks(self) -> list[object]:
        """Return the pitch control's input jacks, of which it has none."""
        return []

    def all_input_jacks(self) -> list[object]:
        """Return every physical input jack, of which this module has none."""
        return []

    def output_jacks(self) -> list[OutputJack]:
        """Return the pitch control's output jack."""
        return [self.pitch_output]

    def display_state(self) -> list[str]:
        """Return the state that belongs on the pitch-control panel."""
        return ["1 V raises pitch by one octave"]
