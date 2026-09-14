"""This module models an oscillator mounted on a synth board."""

from math import pi, sin

from synth.controls import Knob
from synth.patch import InputJack, OutputJack, VoltageRole


class Oscillator:
    """This module places its selected repeating waveform on an output jack each sample."""

    display_name = "OSCILLATOR"
    waveform_names = ("Sine", "Triangle", "Square", "Sawtooth")

    def __init__(self, base_frequency_hz: float, sample_rate: int) -> None:
        """Create an oscillator whose pitch input starts at zero volts and whose waveform is sine."""
        if base_frequency_hz <= 0:
            raise ValueError("The base frequency must be positive.")
        if sample_rate <= 0:
            raise ValueError("The sample rate must be positive.")

        self.base_frequency_hz = base_frequency_hz
        self.sample_rate = sample_rate
        self.phase_cycles = 0.0
        self.pitch_input = InputJack("Pitch input", VoltageRole.CONTROL, visible=False)
        self.sine_output = OutputJack("Sine output", VoltageRole.AUDIO)
        self.audio_output = self.sine_output
        self.waveform_knob = Knob("Waveform", 0.0, 3.0, 0.0, "")

    @property
    def frequency_hz(self) -> float:
        """Return frequency after applying one volt per octave of pitch voltage."""
        return self.base_frequency_hz * 2 ** self.pitch_input.read_voltage()

    @property
    def waveform_index(self) -> int:
        """Return the selected waveform index from the discrete waveform control."""
        return round(self.waveform_knob.value)

    @property
    def waveform_name(self) -> str:
        """Return the learner-facing name of the selected waveform."""
        return self.waveform_names[self.waveform_index]

    def waveform_value(self, phase_cycles: float) -> float:
        """Return the selected waveform's voltage at one position in a cycle."""
        phase = phase_cycles % 1.0
        if self.waveform_index == 0:
            return sin(2 * pi * phase)
        if self.waveform_index == 1:
            return 1.0 - 4.0 * abs(phase - 0.5)
        if self.waveform_index == 2:
            return 1.0 if phase < 0.5 else -1.0
        return 2.0 * phase - 1.0

    def ascii_trace(self, width: int = 15, height: int = 5) -> tuple[str, ...]:
        """Return a deterministic ASCII graph of one cycle of the selected waveform."""
        if width < 2 or height < 2:
            raise ValueError("An ASCII trace needs at least two columns and two rows.")

        rows = [[" "] * width for _ in range(height)]
        previous_row: int | None = None
        for column in range(width):
            phase = column / (width - 1)
            value = self.waveform_value(phase)
            row = round((1.0 - value) * (height - 1) / 2.0)
            if previous_row is not None:
                start, stop = sorted((previous_row, row))
                for trace_row in range(start, stop + 1):
                    rows[trace_row][column] = "*"
            rows[row][column] = "*"
            previous_row = row
        return tuple("".join(row) for row in rows)

    def advance(self) -> None:
        """Place the next waveform voltage on the output jack and advance phase."""
        self.audio_output.voltage = self.waveform_value(self.phase_cycles)
        phase_step = self.frequency_hz / self.sample_rate
        self.phase_cycles = (self.phase_cycles + phase_step) % 1.0

    def next_sample(self) -> float:
        """Advance once and return the voltage for code that reads a source directly."""
        self.advance()
        return self.audio_output.voltage

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
        return [self.audio_output]

    def controls(self) -> list[Knob]:
        """Return the oscillator's exposed front-panel controls."""
        return [self.waveform_knob]

    def display_state(self) -> list[str]:
        """Return the state that belongs on the oscillator panel."""
        return [
            f"waveform: {self.waveform_name}",
            f"frequency: {self.frequency_hz:.2f} Hz",
            f"phase: {self.phase_cycles:.5f}",
        ]


SineOscillator = Oscillator
