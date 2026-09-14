"""This module contains repeating audio signal sources."""

from math import pi, sin


class SineOscillator:
    """This oscillator produces one normalized sine-wave sample at a time."""

    def __init__(self, frequency_hz: float, sample_rate: int) -> None:
        """Create an oscillator at the given frequency and sample rate."""
        if frequency_hz < 0:
            raise ValueError("The frequency cannot be negative.")
        if sample_rate <= 0:
            raise ValueError("The sample rate must be positive.")

        self.frequency_hz = frequency_hz
        self.sample_rate = sample_rate
        self.phase_cycles = 0.0

    def next_sample(self) -> float:
        """Return the next sample and advance the oscillator by one sample period."""
        sample = sin(2 * pi * self.phase_cycles)
        phase_step = self.frequency_hz / self.sample_rate
        self.phase_cycles = (self.phase_cycles + phase_step) % 1.0
        return sample

    def reset(self) -> None:
        """Return the oscillator to the start of its waveform cycle."""
        self.phase_cycles = 0.0
