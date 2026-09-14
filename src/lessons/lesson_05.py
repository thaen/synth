"""This module configures Lesson 5's low-pass-filtered sawtooth board."""

from lessons.lesson_04 import build as build_lesson_04
from synth.lesson import Lesson, ModulePresentation, VisibleControl
from synth.low_pass_filter import LowPassFilter


def build() -> Lesson:
    """Add a low-pass filter after Gain and start the source as a sawtooth."""
    lesson_four = build_lesson_04()
    board = lesson_four.board
    pitch, oscillator, gain, audio_output = [panel.module for panel in lesson_four.visible_panels]
    oscillator.waveform_knob.set_value(3.0)
    board.unpatch(next(cable for cable in board.cables if cable.destination.owner is audio_output))
    low_pass_filter = LowPassFilter(lesson_four.sample_rate)
    board.mount(low_pass_filter)
    board.patch(gain.audio_output, low_pass_filter.audio_input)
    board.patch(low_pass_filter.audio_output, audio_output.audio_input)

    return Lesson(
        5,
        "A low-pass filter changes brightness.",
        board,
        lesson_four.sample_rate,
        [pitch, oscillator, gain, low_pass_filter, audio_output],
        [(30, 190), (240, 190), (450, 190), (660, 190), (870, 190)],
        panels=[
            ModulePresentation(
                pitch,
                "Pitch",
                (
                    "Pitch is the musical perception associated with frequency for this steady tone.",
                    "The source starts at A4, 440.00 Hz, and this control still moves by semitones.",
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
                    "This oscillator starts with a sawtooth waveform, which has high-frequency harmonics.",
                    "The filter receives the signal after Gain, so changing cutoff does not change the oscillator.",
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
                    "Gain multiplies the waveform amplitude before the signal reaches the filter.",
                    "It starts at 0.50 while cutoff changes the balance of frequency components.",
                ),
                (VisibleControl(gain.gain_knob, "Gain", 0.05, "Changes in steps of 0.05."),),
                readout="Multiplies the signal",
                meter=lambda: gain.signal_level,
                inactive_state="waiting",
                active_state="passing signal",
            ),
            ModulePresentation(
                low_pass_filter,
                "Low-Pass Filter",
                (
                    "A low-pass filter lets lower frequency components pass more readily than higher ones.",
                    "Cutoff is the boundary frequency. Lower settings make this sawtooth darker.",
                ),
                (
                    VisibleControl(
                        low_pass_filter.cutoff_knob,
                        "Cutoff",
                        1.0,
                        "Changes by one semitone between 200 Hz and 12 kHz.",
                        value_formatter=lambda: f"{low_pass_filter.cutoff_hz:.0f} Hz",
                        adjustment=low_pass_filter.shift_cutoff,
                    ),
                ),
                readout="Passes lower frequencies",
                meter=lambda: low_pass_filter.signal_level,
                inactive_state="waiting",
                active_state="filtering",
                trace=low_pass_filter.ascii_response_trace,
            ),
            ModulePresentation(
                audio_output,
                "Audio Output",
                (
                    "This boundary sends the filtered signal to the selected computer output device.",
                    "The module is an output boundary, while a speaker can be one device after it.",
                ),
                readout="To system sound",
                inactive_state="silent",
                active_state="active",
            ),
        ],
        audio_instruction="Press b to start or stop the filtered sawtooth.",
        audio_active_message="The filtered sawtooth is active. Use Low-Pass Filter to change its brightness.",
        audio_inactive_message="The filtered sawtooth is silent. Press b to start it.",
        key_summary="b starts or stops the filtered sawtooth",
        reference_lines=(
            "Filter: a module that changes the balance of frequency components in an existing sound.",
            "Low-pass filter: a filter that passes lower frequencies more readily than higher frequencies.",
            "Cutoff: the boundary frequency where the filter begins reducing higher frequency components.",
            "Brightness and darkness describe the changed balance of frequency components.",
            "This filter has cutoff only. Resonance changes behavior near cutoff and belongs to a later lesson.",
        ),
    )
