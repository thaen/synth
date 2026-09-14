"""This module models the board's connection to a speaker or audio device."""

from synth.patch import InputJack


class SpeakerOutput:
    """This module receives one audio voltage and presents it to the output adapter."""

    def __init__(self) -> None:
        """Create the speaker module with one audio input jack."""
        self.audio_input = InputJack("Audio input")

    def advance(self) -> None:
        """Keep the speaker module on the board's shared sample clock."""

    def current_sample(self) -> float:
        """Return the voltage arriving at the speaker input."""
        return self.audio_input.read_voltage()
