"""This module models a front-panel control that produces pitch voltage."""

from synth.controls import Knob
from synth.patch import OutputJack, VoltageRole


class PitchControl:
    """This module converts semitone steps into one-volt-per-octave pitch voltage."""

    display_name = "PITCH CONTROL"
    _NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")

    def __init__(self, semitones: float = 0.0) -> None:
        """Create a pitch control centered on A4 at zero semitones."""
        self.pitch_knob = Knob("Semitones", -24.0, 24.0, semitones, "st")
        self.pitch_output = OutputJack("Pitch output", VoltageRole.CONTROL)

    @property
    def semitones(self) -> float:
        """Return the number of equal-tempered steps from A4."""
        return self.pitch_knob.value

    @property
    def pitch_volts(self) -> float:
        """Return the control voltage for the current semitone setting."""
        return self.semitones / 12.0

    @property
    def frequency_hz(self) -> float:
        """Return the A4-relative frequency selected by the control."""
        return 440.0 * 2 ** (self.semitones / 12.0)

    @property
    def note_name(self) -> str:
        """Return the nearest equal-tempered note name for the current setting."""
        midi_note = 69 + round(self.semitones)
        name = self._NOTE_NAMES[midi_note % len(self._NOTE_NAMES)]
        octave = midi_note // len(self._NOTE_NAMES) - 1
        return f"{name}{octave}"

    def advance(self) -> None:
        """Place the knob's pitch voltage on the output jack."""
        self.pitch_output.voltage = self.pitch_volts

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
        return [f"{self.note_name}  {self.frequency_hz:.2f} Hz"]
