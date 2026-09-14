"""This module configures Lesson 2's pitch-control board."""

from synth.lesson import Lesson
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
        "Pitch control drives a sine oscillator",
        board,
        SAMPLE_RATE,
        [pitch_control, oscillator, audio_output],
        [(80, 190), (460, 190), (840, 190)],
    )
