"""This module configures Lesson 1's fixed oscillator-to-speaker board."""

from synth.board import Board
from synth.lesson import Lesson, ModulePresentation
from synth.oscillator import SineOscillator
from synth.output import AudioOutput


SAMPLE_RATE = 44_100


def mount_base_board() -> tuple[Board, SineOscillator, AudioOutput]:
    """Mount the fixed A4 oscillator and audio output with one patch cable."""
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
        "A sine wave becomes sound.",
        board,
        SAMPLE_RATE,
        [oscillator, audio_output],
        [(190, 190), (760, 190)],
        panels=[
            ModulePresentation(
                oscillator,
                "Sine Wave Creator",
                (
                    "This source makes a smooth signal that repeats 440 times each second.",
                    "Frequency is the number of cycles each second, measured in hertz.",
                ),
            ),
            ModulePresentation(
                audio_output,
                "Audio Output",
                (
                    "This boundary sends the completed signal to the selected computer output device.",
                    "The module is an output boundary, while a speaker can be one device after it.",
                ),
            ),
        ],
    )
