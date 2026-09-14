"""This module models a sine-wave source mounted on a synth board."""

from math import pi, sin

from synth.patch import InputJack, OutputJack, SignalKind


class SineOscillator:
    """This module places a sine-wave voltage on its output jack each sample."""

    display_name = "SINE OSCILLATOR"

    def __init__(self, base_frequency_hz: float, sample_rate: int) -> None:
        """Create an oscillator whose pitch input starts at zero volts."""
        if base_frequency_hz <= 0:
            raise ValueError("The base frequency must be positive.")
        if sample_rate <= 0:
            raise ValueError("The sample rate must be positive.")

        self.base_frequency_hz = base_frequency_hz
        self.sample_rate = sample_rate
        self.phase_cycles = 0.0
        self.pitch_input = InputJack("Pitch input", (SignalKind.CONTROL,), visible=False)
        self.sine_output = OutputJack("Sine output", SignalKind.AUDIO)

    @property
    def frequency_hz(self) -> float:
        """Return frequency after applying one volt per octave of pitch voltage."""
        return self.base_frequency_hz * 2 ** self.pitch_input.read_voltage()

    def advance(self) -> None:
        """Place the next sine-wave voltage on the output jack and advance phase."""
        self.sine_output.voltage = sin(2 * pi * self.phase_cycles)
        phase_step = self.frequency_hz / self.sample_rate
        self.phase_cycles = (self.phase_cycles + phase_step) % 1.0

    def next_sample(self) -> float:
        """Advance once and return the voltage for code that reads a source directly."""
        self.advance()
        return self.sine_output.voltage

    def reset(self) -> None:
        """Return the oscillator to the start of its waveform cycle."""
        self.phase_cycles = 0.0

    def input_jacks(self) -> list[InputJack]:
        """Return the currently visible input jacks on the oscillator panel."""
        return [jack for jack in [self.pitch_input] if jack.visible]

    def all_input_jacks(self) -> list[InputJack]:
        """Return every physical input jack, including jacks not yet revealed."""
        return [self.pitch_input]

    def output_jacks(self) -> list[OutputJack]:
        """Return the output jacks on the oscillator panel."""
        return [self.sine_output]

    def controls(self) -> list[object]:
        """Return the oscillator's exposed front-panel controls."""
        return []

    def display_state(self) -> list[str]:
        """Return the state that belongs on the oscillator panel."""
        return [f"frequency: {self.frequency_hz:.2f} Hz", f"phase: {self.phase_cycles:.5f}"]
