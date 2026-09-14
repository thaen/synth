"""This module models the board's connection to a speaker or audio device."""

from synth.controls import Knob
from synth.patch import InputJack, OutputJack, SignalKind


class AudioOutput:
    """This module receives audio voltage and presents a monitored output voltage."""

    display_name = "AUDIO OUTPUT"

    def __init__(self) -> None:
        """Create the audio output with one input jack and one monitor-level knob."""
        self.audio_input = InputJack("Audio input", (SignalKind.AUDIO,))
        self.monitor_level = Knob("Monitor level", 0.0, 1.0, 0.25, "")

    def advance(self) -> None:
        """Keep the audio output on the board's shared sample clock."""

    def current_sample(self) -> float:
        """Return the monitored voltage that the output adapter receives."""
        return self.monitor_level.value * self.audio_input.read_voltage()

    def input_jacks(self) -> list[InputJack]:
        """Return the audio input jack."""
        return [self.audio_input]

    def all_input_jacks(self) -> list[InputJack]:
        """Return every physical input jack on the audio output."""
        return [self.audio_input]

    def output_jacks(self) -> list[OutputJack]:
        """Return the audio output's panel output jacks, of which it has none."""
        return []

    def controls(self) -> list[Knob]:
        """Return the monitor-level control."""
        return [self.monitor_level]

    def display_state(self) -> list[str]:
        """Return the state that belongs on the audio-output panel."""
        return [f"output voltage: {self.current_sample():+.5f}"]
