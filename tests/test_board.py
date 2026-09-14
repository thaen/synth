"""These tests protect the physical board rules used by every lesson."""

import math
import unittest

from lessons.lesson_01 import mount_base_board
from synth.gain import Gain
from synth.low_pass_filter import LowPassFilter
from synth.oscillator import Oscillator
from synth.patch import OutputJack, PatchCable, VoltageRole
from synth.pitch_control import PitchControl


class BoardTests(unittest.TestCase):
    """These tests check cables, topology, pitch control, and reset behavior."""

    def test_pitch_control_converts_twelve_semitones_to_one_octave(self) -> None:
        """The pitch control sends one volt and selects A5 after twelve semitone steps."""
        board, oscillator, _audio_output = mount_base_board()
        pitch_control = PitchControl(semitones=12.0)
        board.mount(pitch_control)
        board.patch(pitch_control.pitch_output, oscillator.pitch_input)

        board.next_sample()

        self.assertEqual(board.evaluation_order()[0], pitch_control)
        self.assertEqual(pitch_control.note_name, "A5")
        self.assertEqual(pitch_control.pitch_output.voltage, 1.0)
        self.assertTrue(math.isclose(oscillator.frequency_hz, 880.0))

    def test_cable_can_connect_an_audio_output_to_a_pitch_input(self) -> None:
        """A cable carries voltage, while the destination module interprets that voltage."""
        board, oscillator, _audio_output = mount_base_board()
        board.patch(oscillator.sine_output, oscillator.pitch_input)

        self.assertIs(oscillator.pitch_input.cable.source, oscillator.sine_output)

    def test_input_jack_accepts_only_one_cable(self) -> None:
        """A second cable cannot occupy an already connected input jack."""
        board, oscillator, _audio_output = mount_base_board()
        pitch_control = PitchControl()
        board.mount(pitch_control)
        board.patch(pitch_control.pitch_output, oscillator.pitch_input)
        with self.assertRaises(ValueError):
            PatchCable(pitch_control.pitch_output, oscillator.pitch_input)

    def test_unpatch_frees_an_input_jack_for_a_new_cable(self) -> None:
        """Removing a cable frees its input jack for the next physical patch."""
        board, oscillator, _audio_output = mount_base_board()
        first_pitch_control = PitchControl()
        second_pitch_control = PitchControl()
        board.mount(first_pitch_control)
        board.mount(second_pitch_control)
        cable = board.patch(first_pitch_control.pitch_output, oscillator.pitch_input)

        board.unpatch(cable)
        board.patch(second_pitch_control.pitch_output, oscillator.pitch_input)

        self.assertIs(oscillator.pitch_input.cable.source, second_pitch_control.pitch_output)

    def test_reset_returns_the_oscillator_to_the_start_of_its_cycle(self) -> None:
        """Resetting phase makes the next oscillator voltage zero again."""
        board, oscillator, _audio_output = mount_base_board()
        board.next_sample()
        board.next_sample()
        oscillator.reset()
        self.assertTrue(math.isclose(board.next_sample(), 0.0, abs_tol=1e-12))

    def test_gain_multiplies_the_audio_signal_before_the_output(self) -> None:
        """A gain stage scales the oscillator sample before AudioOutput reads it."""
        board, oscillator, audio_output = mount_base_board()
        direct_cable = board.cables[0]
        board.unpatch(direct_cable)
        gain = Gain(0.50)
        board.mount(gain)
        board.patch(oscillator.sine_output, gain.audio_input)
        board.patch(gain.audio_output, audio_output.audio_input)
        audio_output.monitor_level.set_value(1.0)

        samples = [board.next_sample() for _ in range(4)]
        expected = [
            0.50 * math.sin(2 * math.pi * index * 440.0 / oscillator.sample_rate)
            for index in range(4)
        ]

        for sample, expected_sample in zip(samples, expected):
            self.assertAlmostEqual(sample, expected_sample, places=12)

    def test_oscillator_generates_each_waveform_from_one_phase_clock(self) -> None:
        """Each waveform has deterministic samples at the same four phase positions."""
        oscillator = Oscillator(base_frequency_hz=1.0, sample_rate=4)
        expected_by_waveform = {
            "Sine": [0.0, 1.0, 0.0, -1.0],
            "Triangle": [-1.0, 0.0, 1.0, 0.0],
            "Square": [1.0, 1.0, -1.0, -1.0],
            "Sawtooth": [-1.0, -0.5, 0.0, 0.5],
        }

        for index, (waveform, expected) in enumerate(expected_by_waveform.items()):
            oscillator.waveform_knob.set_value(float(index))
            oscillator.reset()
            samples = [oscillator.next_sample() for _ in range(4)]

            self.assertEqual(oscillator.waveform_name, waveform)
            for sample, expected_sample in zip(samples, expected):
                self.assertAlmostEqual(sample, expected_sample, places=12)

    def test_ascii_trace_covers_one_selected_waveform_cycle(self) -> None:
        """The waveform trace has stable dimensions and changes with its selected shape."""
        oscillator = Oscillator(base_frequency_hz=440.0, sample_rate=44_100)
        sine_trace = oscillator.ascii_trace()
        oscillator.waveform_knob.set_value(2.0)
        square_trace = oscillator.ascii_trace()

        self.assertEqual(len(sine_trace), 5)
        self.assertTrue(all(len(row) == 15 for row in sine_trace))
        self.assertNotEqual(sine_trace, square_trace)

    def test_low_pass_filter_has_one_cutoff_control_and_filters_high_frequency_changes(self) -> None:
        """The one-pole filter has no resonance control and attenuates an alternating signal."""
        source = OutputJack("Source", VoltageRole.AUDIO)
        low_cutoff = LowPassFilter(sample_rate=44_100, cutoff_hz=200.0)
        high_cutoff = LowPassFilter(sample_rate=44_100, cutoff_hz=12_000.0)
        PatchCable(source, low_cutoff.audio_input)
        PatchCable(source, high_cutoff.audio_input)

        low_samples = []
        high_samples = []
        for index in range(1_000):
            source.voltage = 1.0 if index % 2 == 0 else -1.0
            low_cutoff.advance()
            high_cutoff.advance()
            if index >= 900:
                low_samples.append(abs(low_cutoff.audio_output.voltage))
                high_samples.append(abs(high_cutoff.audio_output.voltage))

        self.assertEqual(len(low_cutoff.controls()), 1)
        self.assertEqual(low_cutoff.cutoff_knob.minimum, 200.0)
        self.assertEqual(low_cutoff.cutoff_knob.maximum, 12_000.0)
        self.assertGreater(sum(high_samples) / len(high_samples), 20 * sum(low_samples) / len(low_samples))

    def test_low_pass_filter_cutoff_moves_by_semitone_ratios_and_its_trace_changes(self) -> None:
        """The cutoff uses a logarithmic musical step and supplies a stable response trace."""
        low_pass_filter = LowPassFilter(sample_rate=44_100)
        open_trace = low_pass_filter.ascii_response_trace()

        low_pass_filter.shift_cutoff(-12)
        self.assertAlmostEqual(low_pass_filter.cutoff_hz, 6_000.0)
        low_pass_filter.shift_cutoff(12)
        self.assertAlmostEqual(low_pass_filter.cutoff_hz, 12_000.0)
        for _ in range(100):
            low_pass_filter.shift_cutoff(-1)

        closed_trace = low_pass_filter.ascii_response_trace()
        self.assertEqual(low_pass_filter.cutoff_hz, 200.0)
        self.assertEqual(len(open_trace), 5)
        self.assertTrue(all(len(row) == 15 for row in open_trace))
        self.assertNotEqual(open_trace, closed_trace)


if __name__ == "__main__":
    unittest.main()
