"""These tests protect the physical board rules used by every lesson."""

import math
import unittest

from lessons.lesson_01 import mount_base_board
from synth.gain import Gain
from synth.patch import PatchCable
from synth.pitch_control import PitchControl


class BoardTests(unittest.TestCase):
    """These tests check cables, topology, pitch control, and reset behavior."""

    def test_pitch_control_runs_before_the_oscillator_when_mounted_last(self) -> None:
        """The cable direction determines order rather than the order of mounting."""
        board, oscillator, _audio_output = mount_base_board()
        pitch_control = PitchControl(pitch_volts=1.0)
        board.mount(pitch_control)
        board.patch(pitch_control.pitch_output, oscillator.pitch_input)

        board.next_sample()

        self.assertEqual(board.evaluation_order()[0], pitch_control)
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


if __name__ == "__main__":
    unittest.main()
