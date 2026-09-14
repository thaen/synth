"""This module scales an audio signal by a front-panel gain control."""

from synth.controls import Knob
from synth.patch import InputJack, OutputJack, VoltageRole


class Gain:
    """This module multiplies its audio input by a value from zero through one."""

    display_name = "GAIN"

    def __init__(self, value: float = 0.50) -> None:
        """Create a gain stage with a half-sized signal as its documented default."""
        self.gain_knob = Knob("Gain", 0.0, 1.0, value, "")
        self.audio_input = InputJack("Audio input", VoltageRole.AUDIO)
        self.audio_output = OutputJack("Audio output", VoltageRole.AUDIO)

    @property
    def signal_level(self) -> float:
        """Return the current output magnitude as a normalized meter level."""
        return min(1.0, abs(self.audio_output.voltage))

    def advance(self) -> None:
        """Scale the incoming sample and place the result on the output jack."""
        self.audio_output.voltage = self.audio_input.read_voltage() * self.gain_knob.value

    def input_jacks(self) -> list[InputJack]:
        """Return the audio input that appears on the module panel."""
        return [self.audio_input]

    def all_input_jacks(self) -> list[InputJack]:
        """Return every physical input jack on this module."""
        return [self.audio_input]

    def output_jacks(self) -> list[OutputJack]:
        """Return the scaled audio output that appears on the module panel."""
        return [self.audio_output]

    def controls(self) -> list[Knob]:
        """Return the gain multiplier that this module owns."""
        return [self.gain_knob]

    def display_state(self) -> list[str]:
        """Return module-owned values for generic visual adapters."""
        return [f"signal: {self.audio_output.voltage:+.5f}"]
