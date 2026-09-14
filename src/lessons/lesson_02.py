"""This module configures Lesson 2's oscillator-to-gain-to-output board."""

from synth.lesson import Lesson, ModulePresentation, VisibleControl
from synth.gain import Gain
from lessons.lesson_01 import SAMPLE_RATE, mount_base_board


def build() -> Lesson:
    """Mount gain between the Lesson 1 source and its audio output."""
    board, oscillator, audio_output = mount_base_board()
    board.unpatch(board.cables[0])
    gain = Gain()
    board.mount(gain)
    board.patch(oscillator.sine_output, gain.audio_input)
    board.patch(gain.audio_output, audio_output.audio_input)
    audio_output.monitor_level.set_value(1.0)
    return Lesson(
        2,
        "Gain changes a signal's size.",
        board,
        SAMPLE_RATE,
        [oscillator, gain, audio_output],
        [(80, 190), (460, 190), (840, 190)],
        panels=[
            ModulePresentation(
                oscillator,
                "Sine Wave Creator",
                (
                    "This source makes the same smooth signal from Lesson 1.",
                    "Its frequency remains 440 Hz while this lesson changes the signal size.",
                ),
                readout=lambda: f"Frequency  {oscillator.frequency_hz:.0f} Hz",
                inactive_state="idle",
                active_state="active",
            ),
            ModulePresentation(
                gain,
                "Gain",
                (
                    "Amplitude is the size of a signal value. A larger amplitude carries the sine wave farther from zero.",
                    "Gain is a multiplier that changes amplitude. A setting of 0.50 halves this signal.",
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
        audio_instruction="Press b to start or stop A4 at 440 Hz.",
        audio_active_message="A4 at 440 Hz is active. Use Gain to change its signal size.",
        audio_inactive_message="A4 at 440 Hz is silent. Press b to start it.",
        key_summary="b starts or stops A4",
        reference_lines=(
            "Signal: a changing sequence of numbers that represents audio in this model.",
            "Amplitude: the size of a signal value or wave.",
            "Gain: a multiplier that changes amplitude. 1.00 leaves the signal unchanged.",
            "A gain of 0.50 halves the signal, and 0.00 makes it silent.",
            "Loudness is what a person perceives. Volume is a listening control.",
        ),
    )
