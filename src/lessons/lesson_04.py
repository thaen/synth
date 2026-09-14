"""This module configures Lesson 4's waveform-controlled oscillator board."""

from lessons.lesson_03 import build as build_lesson_03
from synth.lesson import Lesson, ModulePresentation, VisibleControl


def build() -> Lesson:
    """Expose waveform selection while retaining Lesson 3's pitch and gain path."""
    lesson_three = build_lesson_03()
    board = lesson_three.board
    pitch, oscillator, gain, audio_output = [panel.module for panel in lesson_three.visible_panels]

    return Lesson(
        4,
        "Waveform changes timbre.",
        board,
        lesson_three.sample_rate,
        [pitch, oscillator, gain, audio_output],
        [(50, 190), (320, 190), (590, 190), (860, 190)],
        panels=[
            ModulePresentation(
                pitch,
                "Pitch",
                (
                    "Pitch is the musical perception associated with frequency for this steady tone.",
                    "The comparison starts at A4, 440.00 Hz, and this control can still select semitone steps.",
                ),
                (VisibleControl(pitch.pitch_knob, "Semitones", 1.0, "Changes in steps of one semitone."),),
                readout=lambda: f"{pitch.note_name}  {pitch.frequency_hz:.2f} Hz",
                inactive_state="ready",
                active_state="controlling pitch",
            ),
            ModulePresentation(
                oscillator,
                "Oscillator",
                (
                    "An oscillator repeats a waveform. The trace shows one cycle of the selected shape.",
                    "Timbre is the sound quality that changes when pitch and level stay fixed.",
                ),
                (
                    VisibleControl(
                        oscillator.waveform_knob,
                        "Waveform",
                        1.0,
                        "Changes among Sine, Triangle, Square, and Sawtooth.",
                        value_formatter=lambda: oscillator.waveform_name,
                    ),
                ),
                readout=lambda: f"{oscillator.waveform_name}  {oscillator.frequency_hz:.2f} Hz",
                inactive_state="idle",
                active_state="active",
                trace=oscillator.ascii_trace,
            ),
            ModulePresentation(
                gain,
                "Gain",
                (
                    "Gain multiplies the waveform amplitude after the oscillator makes the signal.",
                    "It starts at 0.50, so waveform selection keeps the gain value unchanged.",
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
        audio_instruction="Press b to start or stop the selected waveform.",
        audio_active_message="The selected waveform is active. Use Oscillator to change its shape.",
        audio_inactive_message="The selected waveform is silent. Press b to start it.",
        key_summary="b starts or stops the selected waveform",
        reference_lines=(
            "Waveform: the repeated shape made by an oscillator.",
            "Timbre: the sound quality that differs when pitch and level stay fixed.",
            "A sine wave has one frequency component. Square and sawtooth waves have harmonics.",
            "Harmonics are frequency components above the fundamental frequency.",
            "Brightness is an informal description for sound with more high-frequency energy.",
        ),
    )
