"""This module models a sine-wave source mounted on a synth board."""

from math import pi, sin

from synth.patch import OutputJack


class SineOscillator:
    """This module places a sine-wave voltage on its output jack each sample."""

    def __init__(self, frequency_hz: float, sample_rate: int) -> None:
        """Create an oscillator at the given frequency and sample rate."""
        if frequency_hz < 0:
            raise ValueError("The frequency cannot be negative.")
        if sample_rate <= 0:
            raise ValueError("The sample rate must be positive.")

        self.frequency_hz = frequency_hz
        self.sample_rate = sample_rate
        self.phase_cycles = 0.0
        self.sine_output = OutputJack("Sine output")

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
