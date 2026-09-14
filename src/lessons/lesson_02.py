"""This module configures Lesson 2's pitch-control board."""

from synth.lesson import Lesson, ModulePresentation, VisibleControl
from synth.pitch_control import PitchControl
from lessons.lesson_01 import SAMPLE_RATE, mount_base_board


def build() -> Lesson:
    """Mount pitch control, oscillator, and speaker output with two patch cables."""
    board, oscillator, audio_output = mount_base_board()
    pitch_control = PitchControl(pitch_volts=0.0)
    board.mount(pitch_control)
    board.patch(pitch_control.pitch_output, oscillator.pitch_input)
    oscillator.pitch_input.visible = True
    return Lesson(
        2,
        "Pitch control changes a sine wave.",
        board,
        SAMPLE_RATE,
        [pitch_control, oscillator, audio_output],
        [(80, 190), (460, 190), (840, 190)],
        panels=[
            ModulePresentation(
                pitch_control,
                "Pitch Control",
                (
                    "This control sends a pitch signal to the oscillator.",
                    "One volt raises pitch by one octave in this lesson's module model.",
                ),
                (VisibleControl(pitch_control.pitch_knob, "Pitch", 1 / 12, "One semitone per step."),),
            ),
            ModulePresentation(
                oscillator,
                "Sine Wave Creator",
                (
                    "This source turns its pitch input into a smooth repeating audio signal.",
                    "Its displayed frequency changes when the pitch control changes.",
                ),
            ),
            ModulePresentation(
                audio_output,
                "Audio Output",
                (
                    "This boundary sends the completed signal to the selected computer output device.",
                    "The output is not itself a speaker.",
                ),
            ),
        ],
    )
