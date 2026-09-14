"""This module configures Lesson 3's pitch-controlled oscillator board."""

from lessons.lesson_02 import build as build_lesson_02
from synth.lesson import Lesson, ModulePresentation, VisibleControl
from synth.pitch_control import PitchControl


def build() -> Lesson:
    """Add a semitone pitch control while retaining Lesson 2's audio path."""
    lesson_two = build_lesson_02()
    board = lesson_two.board
    oscillator, gain, audio_output = [panel.module for panel in lesson_two.visible_panels]
    pitch = PitchControl()
    oscillator.pitch_input.visible = True
    board.mount(pitch)
    board.patch(pitch.pitch_output, oscillator.pitch_input)

    return Lesson(
        3,
        "Pitch selects the rate of repetition.",
        board,
        lesson_two.sample_rate,
        [pitch, oscillator, gain, audio_output],
        [(50, 190), (320, 190), (590, 190), (860, 190)],
        panels=[
            ModulePresentation(
                pitch,
                "Pitch",
                (
                    "Pitch is the musical perception associated with frequency for this steady tone.",
                    "Each step is one semitone from A4, and the panel names the selected note and frequency.",
                ),
                (VisibleControl(pitch.pitch_knob, "Semitones", 1.0, "Changes in steps of one semitone."),),
                readout=lambda: f"{pitch.note_name}  {pitch.frequency_hz:.2f} Hz",
                inactive_state="ready",
                active_state="controlling pitch",
            ),
            ModulePresentation(
                oscillator,
                "Sine Wave Creator",
                (
                    "This source repeats at the frequency selected by its Pitch input.",
                    "The audio signal still travels through Gain before it reaches Audio Output.",
                ),
                readout=lambda: f"Pitch input  {pitch.note_name}  {oscillator.frequency_hz:.2f} Hz",
                inactive_state="idle",
                active_state="active",
            ),
            ModulePresentation(
                gain,
                "Gain",
                (
                    "Gain still multiplies the sine-wave amplitude after the oscillator makes the signal.",
                    "It remains at 0.50 while Pitch changes the frequency.",
                ),
                (VisibleControl(gain.gain_knob, "Gain", 0.05, "Changes in steps of 0.05."),),
                readout="Multiplies the signal",
                meter=lambda: gain.signal_level,
                inactive_state="waiting",
                active_state="passing signal",
            ),
            ModulePresentation(
                audio_output,
                "Audio Output",
                (
                    "This boundary sends the completed signal to the selected computer output device.",
                    "The module is an output boundary, while a speaker can be one device after it.",
                ),
                readout="To system sound",
                inactive_state="silent",
                active_state="active",
            ),
        ],
        audio_instruction="Press b to start or stop the sine tone.",
        audio_active_message="The sine tone is active. Use Pitch to change its frequency.",
        audio_inactive_message="The sine tone is silent. Press b to start it.",
        key_summary="b starts or stops the sine tone",
        reference_lines=(
            "Pitch: the musical perception associated with frequency for a steady repeating tone.",
            "Frequency: the number of repeating cycles each second, measured in hertz.",
            "A4 is 440 Hz. A5 is 880 Hz, and A3 is 220 Hz.",
            "A semitone is one of twelve equal pitch steps in an octave.",
            "The pitch module sends one volt per octave to the oscillator's Pitch input.",
        ),
    )
