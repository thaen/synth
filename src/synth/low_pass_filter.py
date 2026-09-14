"""This module models a one-control low-pass filter on the synth board."""

from math import cos, exp, log2, pi, sqrt

from synth.controls import Knob
from synth.patch import InputJack, OutputJack, VoltageRole


class LowPassFilter:
    """This module passes lower frequencies more readily than higher frequencies."""

    display_name = "LOW-PASS FILTER"
    minimum_cutoff_hz = 200.0
    maximum_cutoff_hz = 12_000.0

    def __init__(self, sample_rate: int, cutoff_hz: float = maximum_cutoff_hz) -> None:
        """Create a one-pole filter with a cutoff control and no resonance control."""
        if sample_rate <= 0:
            raise ValueError("The sample rate must be positive.")

        self.sample_rate = sample_rate
        self.cutoff_knob = Knob(
            "Cutoff", self.minimum_cutoff_hz, self.maximum_cutoff_hz, cutoff_hz, "Hz"
        )
        self.audio_input = InputJack("Audio input", VoltageRole.AUDIO)
        self.audio_output = OutputJack("Audio output", VoltageRole.AUDIO)
        self._previous_output = 0.0

    @property
    def cutoff_hz(self) -> float:
        """Return the cutoff frequency in hertz."""
        return self.cutoff_knob.value

    @property
    def signal_level(self) -> float:
        """Return the current output magnitude as a normalized meter level."""
        return min(1.0, abs(self.audio_output.voltage))

    def shift_cutoff(self, semitones: int) -> None:
        """Move cutoff by equal-tempered semitone ratios and keep it in range."""
        self.cutoff_knob.set_value(self.cutoff_hz * 2 ** (semitones / 12.0))

    def response_at(self, frequency_hz: float) -> float:
        """Return the one-pole filter's magnitude response at a frequency."""
        if frequency_hz < 0:
            raise ValueError("The response frequency cannot be negative.")
        pole = self._pole
        angle = 2.0 * pi * frequency_hz / self.sample_rate
        denominator = sqrt(1.0 - 2.0 * pole * cos(angle) + pole * pole)
        return (1.0 - pole) / denominator

    def ascii_response_trace(self, width: int = 15, height: int = 5) -> tuple[str, ...]:
        """Return a deterministic response graph from 200 Hz through 12 kHz."""
        if width < 2 or height < 2:
            raise ValueError("An ASCII trace needs at least two columns and two rows.")

        rows = [[" "] * width for _ in range(height)]
        previous_row: int | None = None
        span_octaves = self._octave_span
        for column in range(width):
            frequency_hz = self.minimum_cutoff_hz * 2 ** (span_octaves * column / (width - 1))
            response = max(0.0, min(1.0, self.response_at(frequency_hz)))
            row = round((1.0 - response) * (height - 1))
            if previous_row is not None:
                start, stop = sorted((previous_row, row))
                for trace_row in range(start, stop + 1):
                    rows[trace_row][column] = "*"
            rows[row][column] = "*"
            previous_row = row
        return tuple("".join(row) for row in rows)

    def advance(self) -> None:
        """Filter the incoming sample and write the result to the output jack."""
        pole = self._pole
        self._previous_output = (
            (1.0 - pole) * self.audio_input.read_voltage() + pole * self._previous_output
        )
        self.audio_output.voltage = self._previous_output

    def reset(self) -> None:
        """Clear the delay state so reset starts the filter from silence."""
        self._previous_output = 0.0
        self.audio_output.voltage = 0.0

    def input_jacks(self) -> list[InputJack]:
        """Return the audio input that appears on the module panel."""
        return [self.audio_input]

    def all_input_jacks(self) -> list[InputJack]:
        """Return every physical input jack on this module."""
        return [self.audio_input]

    def output_jacks(self) -> list[OutputJack]:
        """Return the filtered audio output that appears on the module panel."""
        return [self.audio_output]

    def controls(self) -> list[Knob]:
        """Return the cutoff control, which is the filter's only control."""
        return [self.cutoff_knob]

    def display_state(self) -> list[str]:
        """Return module-owned values for generic visual adapters."""
        return [
            f"cutoff: {self.cutoff_hz:.0f} Hz",
            f"signal: {self.audio_output.voltage:+.5f}",
        ]

    @property
    def _pole(self) -> float:
        """Return the one-pole coefficient for the current cutoff frequency."""
        return exp(-2.0 * pi * self.cutoff_hz / self.sample_rate)

    @property
    def _octave_span(self) -> float:
        """Return the displayed response range as a count of octaves."""
        return log2(self.maximum_cutoff_hz / self.minimum_cutoff_hz)
