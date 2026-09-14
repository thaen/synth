"""This module configures Lesson 1's fixed oscillator-to-output board."""

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
                readout=lambda: f"Frequency  {oscillator.frequency_hz:.0f} Hz",
                inactive_state="idle",
                active_state="active",
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
        audio_instruction="Press b to start or stop A4 at 440 Hz.",
        audio_active_message="A4 at 440 Hz is active. Press b to stop it.",
        audio_inactive_message="A4 at 440 Hz is silent. Press b to start it.",
        key_summary="b starts or stops A4",
        reference_lines=(
            "Signal: a changing sequence of numbers that represents audio in this model.",
            "Sine wave: a smooth repeating pattern.",
            "Frequency: cycles each second. Hertz, written Hz, means cycles each second.",
            "A4: the reference pitch at 440 Hz. Audio Output sends the signal to the selected device.",
        ),
    )
