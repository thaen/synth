"""This module configures Lesson 1's fixed oscillator-to-speaker board."""

from synth.board import Board
from synth.lesson import Lesson
from synth.oscillator import SineOscillator
from synth.output import AudioOutput


SAMPLE_RATE = 44_100


def mount_base_board() -> tuple[Board, SineOscillator, AudioOutput]:
    """Mount the fixed A4 oscillator and audio output with their audio cable."""
    oscillator = SineOscillator(base_frequency_hz=440.0, sample_rate=SAMPLE_RATE)
    audio_output = AudioOutput()
    board = Board()
    board.mount(oscillator)
    board.mount(audio_output)
    board.patch(oscillator.sine_output, audio_output.audio_input)
    board.use_audio_output(audio_output)
    return board, oscillator, audio_output


def build() -> Lesson:
    """Supply Lesson 1's base board to the generic programs."""
    board, oscillator, audio_output = mount_base_board()
    return Lesson(
        1,
        "One sine oscillator patched to one audio output",
        board,
        SAMPLE_RATE,
        [oscillator, audio_output],
    )
