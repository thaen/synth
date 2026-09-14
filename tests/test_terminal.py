"""These tests protect the generic terminal lesson state and audio seam."""

import math
import unittest

from lessons.lesson_01 import build as build_lesson_01
from lessons.lesson_02 import build as build_lesson_02
from lessons.lesson_03 import build as build_lesson_03
from lessons.lesson_04 import build as build_lesson_04
from lessons.lesson_05 import build as build_lesson_05
from synth.realtime_audio import DeterministicAudioCollector, SoundDeviceAudioAdapter
from synth.terminal import TerminalLessonApp, TerminalLessonState


class TerminalLessonStateTests(unittest.TestCase):
    """These tests exercise commands through lesson presentation data."""

    def test_selection_wraps_between_visible_panels(self) -> None:
        """The right command selects the next generic presentation panel."""
        state = TerminalLessonState(build_lesson_01(), DeterministicAudioCollector())

        state.dispatch("right")

        self.assertEqual(state.selected_panel.label, "Audio Output")
        state.dispatch("right")
        self.assertEqual(state.selected_panel.label, "Sine Wave Creator")

    def test_adjustment_uses_the_lesson_declared_visible_control(self) -> None:
        """The terminal changes the configured gain knob by its declared step."""
        lesson = build_lesson_02()
        state = TerminalLessonState(lesson, DeterministicAudioCollector())

        state.dispatch("right")
        state.dispatch("up")

        self.assertAlmostEqual(lesson.visible_panels[1].visible_controls[0].control.value, 0.55)
        self.assertIn("Gain", state.status_message)

    def test_adjustment_reports_a_panel_without_an_exposed_control(self) -> None:
        """The terminal keeps responding when a selected module has no lesson control."""
        state = TerminalLessonState(build_lesson_01(), DeterministicAudioCollector())

        state.dispatch("up")

        self.assertIn("no exposed control", state.status_message)

    def test_audio_toggle_reset_help_and_quit_change_terminal_state(self) -> None:
        """The reserved commands change generic state and stop audio before reset or quit."""
        lesson = build_lesson_02()
        collector = DeterministicAudioCollector()
        state = TerminalLessonState(lesson, collector)
        state.dispatch("right")
        state.dispatch("up")
        state.dispatch("b")
        samples = collector.collect(4)

        self.assertTrue(collector.is_active)
        self.assertEqual(len(samples), 4)
        state.dispatch("?")
        self.assertTrue(state.help_is_visible)
        state.dispatch("r")
        self.assertFalse(collector.is_active)
        self.assertEqual(lesson.visible_panels[1].visible_controls[0].control.value, 0.50)
        state.dispatch("q")
        self.assertFalse(state.is_open)

    def test_lesson_one_declares_its_panels_and_inactive_states(self) -> None:
        """Lesson 1 supplies panel text and states without terminal lesson branches."""
        state = TerminalLessonState(build_lesson_01(), DeterministicAudioCollector())

        source, output = state.lesson.visible_panels

        self.assertEqual(source.label, "Sine Wave Creator")
        self.assertEqual(source.format_readout(), "Frequency  440 Hz")
        self.assertEqual(state.panel_state(source), "idle")
        self.assertEqual(output.label, "Audio Output")
        self.assertEqual(output.format_readout(), "To system sound")
        self.assertEqual(state.panel_state(output), "silent")

    def test_lesson_one_latch_emits_a_deterministic_440_hz_signal(self) -> None:
        """The b command starts A4, and its next press mutes collection without a device."""
        lesson = build_lesson_01()
        collector = DeterministicAudioCollector()
        state = TerminalLessonState(lesson, collector)

        state.dispatch("b")
        samples = collector.collect(256)

        expected = [
            0.25 * math.sin(2 * math.pi * index * 440.0 / lesson.sample_rate)
            for index in range(256)
        ]
        self.assertTrue(collector.is_active)
        self.assertEqual(state.panel_state(lesson.visible_panels[0]), "active")
        self.assertEqual(state.panel_state(lesson.visible_panels[1]), "active")
        for sample, expected_sample in zip(samples, expected):
            self.assertAlmostEqual(sample, expected_sample, places=12)
        self.assertIn("440 Hz is active", state.status_message)

        state.dispatch("b")

        self.assertFalse(collector.is_active)
        self.assertEqual(state.panel_state(lesson.visible_panels[0]), "idle")
        self.assertEqual(state.panel_state(lesson.visible_panels[1]), "silent")
        self.assertEqual(collector.collect(8), [0.0] * 8)
        self.assertIn("440 Hz is silent", state.status_message)

    def test_lesson_one_reset_stops_audio_and_returns_to_its_starting_state(self) -> None:
        """The reset command restores the selected source and the first A4 sample."""
        lesson = build_lesson_01()
        collector = DeterministicAudioCollector()
        state = TerminalLessonState(lesson, collector)
        state.dispatch("right")
        state.dispatch("?")
        state.dispatch("b")
        collector.collect(64)

        state.dispatch("r")

        self.assertFalse(collector.is_active)
        self.assertFalse(state.help_is_visible)
        self.assertEqual(state.selected_panel.label, "Sine Wave Creator")
        self.assertEqual(collector.collect(4), [0.0] * 4)
        state.dispatch("b")
        self.assertEqual(collector.collect(1), [0.0])

    def test_lesson_one_cable_pulse_moves_only_while_the_latch_is_active(self) -> None:
        """The generic renderer changes the configured cable from a still rail to a moving pulse."""
        class RecordingScreen:
            """This replacement records terminal output without a terminal emulator."""

            def __init__(self) -> None:
                self.calls: list[tuple[int, int, str]] = []

            def getmaxyx(self) -> tuple[int, int]:
                return (20, 80)

            def erase(self) -> None:
                self.calls = []

            def addnstr(
                self, row: int, column: int, text: str, count: int, _attribute: int
            ) -> None:
                self.calls.append((row, column, text[:count]))

            def refresh(self) -> None:
                return None

        state = TerminalLessonState(build_lesson_01(), DeterministicAudioCollector())
        app = TerminalLessonApp(state)
        screen = RecordingScreen()

        app.pulse_frame = 3
        app._draw(screen)
        inactive_cable = next(
            text for row, _column, text in screen.calls if row == 6 and set(text) == {"-"}
        )
        self.assertGreater(len(inactive_cable), 0)

        state.dispatch("b")
        app._draw(screen)
        first_active_cable = next(
            text for row, _column, text in screen.calls if row == 6 and ">" in text
        )
        self.assertEqual(first_active_cable.count(">"), 1)

        app.pulse_frame = 4
        app._draw(screen)
        second_active_cable = next(
            text for row, _column, text in screen.calls if row == 6 and ">" in text
        )
        self.assertNotEqual(first_active_cable, second_active_cable)

    def test_lesson_two_places_gain_between_the_original_panels(self) -> None:
        """Lesson 2 retains the source and output while it inserts the gain stage."""
        lesson = build_lesson_02()
        source, gain, output = lesson.visible_panels

        self.assertEqual([panel.label for panel in lesson.visible_panels], [
            "Sine Wave Creator",
            "Gain",
            "Audio Output",
        ])
        self.assertEqual(gain.visible_controls[0].control.minimum, 0.0)
        self.assertEqual(gain.visible_controls[0].control.maximum, 1.0)
        self.assertEqual(gain.visible_controls[0].step, 0.05)
        self.assertEqual(len(lesson.board.cables), 2)
        self.assertIs(lesson.board.cables[0].source.owner, source.module)
        self.assertIs(lesson.board.cables[0].destination.owner, gain.module)
        self.assertIs(lesson.board.cables[1].source.owner, gain.module)
        self.assertIs(lesson.board.cables[1].destination.owner, output.module)

    def test_lesson_two_gain_scales_samples_and_its_meter(self) -> None:
        """The lesson has a deterministic multiplier and a meter from the scaled signal."""
        lesson = build_lesson_02()
        collector = DeterministicAudioCollector()
        state = TerminalLessonState(lesson, collector)
        gain_panel = lesson.visible_panels[1]

        state.dispatch("b")
        samples_at_half_gain = collector.collect(26)
        expected_at_half_gain = [
            0.50 * math.sin(2 * math.pi * index * 440.0 / lesson.sample_rate)
            for index in range(26)
        ]
        for sample, expected_sample in zip(samples_at_half_gain, expected_at_half_gain):
            self.assertAlmostEqual(sample, expected_sample, places=12)
        self.assertEqual(gain_panel.format_meter(), "Signal [####....]")

        state.dispatch("right")
        for _ in range(5):
            state.dispatch("down")
        collector.collect(1)

        self.assertAlmostEqual(gain_panel.visible_controls[0].control.value, 0.25)
        self.assertEqual(gain_panel.format_meter(), "Signal [##......]")

    def test_lesson_two_draws_the_declared_signal_meter_without_lesson_branches(self) -> None:
        """The generic terminal renderer reads the configured meter from the gain panel."""
        class RecordingScreen:
            """This replacement records terminal output without a terminal emulator."""

            def __init__(self) -> None:
                self.calls: list[tuple[int, int, str]] = []

            def getmaxyx(self) -> tuple[int, int]:
                return (20, 80)

            def erase(self) -> None:
                self.calls = []

            def addnstr(
                self, row: int, column: int, text: str, count: int, _attribute: int
            ) -> None:
                self.calls.append((row, column, text[:count]))

            def refresh(self) -> None:
                return None

        collector = DeterministicAudioCollector()
        state = TerminalLessonState(build_lesson_02(), collector)
        state.dispatch("b")
        collector.collect(26)
        screen = RecordingScreen()

        TerminalLessonApp(state)._draw(screen)

        self.assertTrue(
            any("Signal [####....]" in text for _row, _column, text in screen.calls)
        )

    def test_lesson_three_adds_pitch_without_changing_the_gain_audio_path(self) -> None:
        """Lesson 3 places pitch before the source and retains the Lesson 2 audio cables."""
        lesson = build_lesson_03()
        pitch, oscillator, gain, output = lesson.visible_panels

        self.assertEqual(
            [panel.label for panel in lesson.visible_panels],
            ["Pitch", "Sine Wave Creator", "Gain", "Audio Output"],
        )
        self.assertTrue(oscillator.module.pitch_input.visible)
        self.assertEqual(pitch.visible_controls[0].label, "Semitones")
        self.assertEqual(pitch.visible_controls[0].step, 1.0)
        self.assertEqual(len(lesson.board.cables), 3)
        self.assertIs(lesson.board.cables[0].source.owner, oscillator.module)
        self.assertIs(lesson.board.cables[0].destination.owner, gain.module)
        self.assertIs(lesson.board.cables[1].source.owner, gain.module)
        self.assertIs(lesson.board.cables[1].destination.owner, output.module)
        self.assertIs(lesson.board.cables[2].source.owner, pitch.module)
        self.assertIs(lesson.board.cables[2].destination.owner, oscillator.module)

    def test_lesson_three_semitone_steps_change_note_frequency_and_keep_gain(self) -> None:
        """A deterministic collector receives the selected frequency at Lesson 2's gain."""
        lesson = build_lesson_03()
        collector = DeterministicAudioCollector()
        state = TerminalLessonState(lesson, collector)

        for _ in range(3):
            state.dispatch("up")
        state.dispatch("b")
        samples = collector.collect(4)

        frequency_hz = 440.0 * 2 ** (3.0 / 12.0)
        expected = [
            0.50 * math.sin(2 * math.pi * index * frequency_hz / lesson.sample_rate)
            for index in range(4)
        ]
        for sample, expected_sample in zip(samples, expected):
            self.assertAlmostEqual(sample, expected_sample, places=12)
        self.assertEqual(lesson.visible_panels[0].format_readout(), "C5  523.25 Hz")
        self.assertEqual(lesson.visible_panels[1].format_readout(), "Pitch input  C5  523.25 Hz")
        self.assertEqual(lesson.visible_panels[2].visible_controls[0].control.value, 0.50)

    def test_lesson_three_reset_restores_a4_and_the_first_sample(self) -> None:
        """Reset returns pitch to A4, stops audio, and resets oscillator phase."""
        lesson = build_lesson_03()
        collector = DeterministicAudioCollector()
        state = TerminalLessonState(lesson, collector)
        state.dispatch("up")
        state.dispatch("b")
        collector.collect(4)

        state.dispatch("r")
        state.dispatch("b")

        self.assertTrue(collector.is_active)
        self.assertEqual(lesson.visible_panels[0].format_readout(), "A4  440.00 Hz")
        self.assertEqual(collector.collect(1), [0.0])

    def test_lesson_four_changes_waveform_without_changing_pitch_or_gain(self) -> None:
        """The waveform control changes the source shape while the earlier control values stay fixed."""
        lesson = build_lesson_04()
        collector = DeterministicAudioCollector()
        state = TerminalLessonState(lesson, collector)
        pitch, oscillator, gain, output = lesson.visible_panels

        self.assertEqual(
            [panel.label for panel in lesson.visible_panels],
            ["Pitch", "Oscillator", "Gain", "Audio Output"],
        )
        self.assertEqual(len(lesson.board.cables), 3)
        self.assertIs(lesson.board.cables[0].source.owner, oscillator.module)
        self.assertIs(lesson.board.cables[0].destination.owner, gain.module)
        self.assertIs(lesson.board.cables[1].source.owner, gain.module)
        self.assertIs(lesson.board.cables[1].destination.owner, output.module)
        self.assertIs(lesson.board.cables[2].source.owner, pitch.module)
        self.assertIs(lesson.board.cables[2].destination.owner, oscillator.module)

        state.dispatch("right")
        state.dispatch("up")
        state.dispatch("up")

        self.assertEqual(oscillator.visible_controls[0].format_value(), "Square")
        self.assertEqual(oscillator.format_readout(), "Square  440.00 Hz")
        self.assertEqual(pitch.visible_controls[0].control.value, 0.0)
        self.assertEqual(gain.visible_controls[0].control.value, 0.50)
        self.assertNotEqual(oscillator.format_trace(), build_lesson_04().visible_panels[1].format_trace())

        state.dispatch("b")
        self.assertEqual(collector.collect(1), [0.50])

    def test_lesson_four_trace_uses_the_generic_terminal_panel_data(self) -> None:
        """The terminal draws a lesson-declared trace without waveform display rules."""
        class RecordingScreen:
            """This replacement records terminal output without a terminal emulator."""

            def __init__(self) -> None:
                self.calls: list[tuple[int, int, str]] = []

            def getmaxyx(self) -> tuple[int, int]:
                return (30, 100)

            def erase(self) -> None:
                self.calls = []

            def addnstr(
                self, row: int, column: int, text: str, count: int, _attribute: int
            ) -> None:
                self.calls.append((row, column, text[:count]))

            def refresh(self) -> None:
                return None

        state = TerminalLessonState(build_lesson_04(), DeterministicAudioCollector())
        screen = RecordingScreen()
        TerminalLessonApp(state)._draw(screen)

        trace = state.lesson.visible_panels[1].format_trace()
        for trace_line in trace:
            self.assertTrue(any(trace_line.rstrip() in text for _row, _column, text in screen.calls))

    def test_lesson_four_reset_restores_sine_pitch_gain_and_phase(self) -> None:
        """The reset command restores each Lesson 4 comparison value and stops audio."""
        lesson = build_lesson_04()
        collector = DeterministicAudioCollector()
        state = TerminalLessonState(lesson, collector)

        state.dispatch("up")
        state.dispatch("right")
        state.dispatch("up")
        state.dispatch("right")
        state.dispatch("up")
        state.dispatch("b")
        collector.collect(4)
        state.dispatch("r")

        pitch, oscillator, gain, _output = lesson.visible_panels
        self.assertFalse(collector.is_active)
        self.assertEqual(pitch.visible_controls[0].control.value, 0.0)
        self.assertEqual(oscillator.visible_controls[0].format_value(), "Sine")
        self.assertEqual(gain.visible_controls[0].control.value, 0.50)
        self.assertEqual(oscillator.module.phase_cycles, 0.0)

    def test_lesson_five_inserts_a_low_pass_filter_and_starts_with_sawtooth(self) -> None:
        """Lesson 5 keeps the earlier path and places its filter before Audio Output."""
        lesson = build_lesson_05()
        pitch, oscillator, gain, low_pass_filter, output = lesson.visible_panels

        self.assertEqual(
            [panel.label for panel in lesson.visible_panels],
            ["Pitch", "Oscillator", "Gain", "Low-Pass Filter", "Audio Output"],
        )
        self.assertEqual(oscillator.format_readout(), "Sawtooth  440.00 Hz")
        self.assertEqual(oscillator.visible_controls, ())
        self.assertEqual(len(low_pass_filter.visible_controls), 1)
        self.assertEqual(low_pass_filter.visible_controls[0].label, "Cutoff")
        self.assertEqual(low_pass_filter.visible_controls[0].format_value(), "12000 Hz")
        self.assertEqual(len(lesson.board.cables), 4)
        self.assertIs(lesson.board.cables[0].source.owner, oscillator.module)
        self.assertIs(lesson.board.cables[0].destination.owner, gain.module)
        self.assertIs(lesson.board.cables[2].source.owner, gain.module)
        self.assertIs(lesson.board.cables[2].destination.owner, low_pass_filter.module)
        self.assertIs(lesson.board.cables[3].source.owner, low_pass_filter.module)
        self.assertIs(lesson.board.cables[3].destination.owner, output.module)
        self.assertIs(lesson.board.cables[1].source.owner, pitch.module)
        self.assertIs(lesson.board.cables[1].destination.owner, oscillator.module)

    def test_lesson_five_cutoff_changes_by_a_semitone_and_reset_restores_the_open_filter(self) -> None:
        """The generic terminal adjusts cutoff logarithmically and reset restores the lesson default."""
        lesson = build_lesson_05()
        collector = DeterministicAudioCollector()
        state = TerminalLessonState(lesson, collector)

        for _ in range(3):
            state.dispatch("right")
        state.dispatch("down")

        cutoff = lesson.visible_panels[3].visible_controls[0]
        self.assertAlmostEqual(cutoff.control.value, 12_000.0 * 2 ** (-1.0 / 12.0))
        self.assertEqual(cutoff.format_value(), "11326 Hz")
        self.assertIn("Cutoff", state.status_message)

        state.dispatch("b")
        collector.collect(32)
        state.dispatch("r")

        self.assertFalse(collector.is_active)
        self.assertEqual(state.selected_panel.label, "Pitch")
        self.assertEqual(cutoff.format_value(), "12000 Hz")
        self.assertEqual(lesson.visible_panels[1].format_readout(), "Sawtooth  440.00 Hz")
        self.assertEqual(lesson.visible_panels[1].module.phase_cycles, 0.0)

    def test_lesson_five_response_trace_uses_generic_terminal_panel_data(self) -> None:
        """The terminal draws the filter response trace from the presentation contract."""
        class RecordingScreen:
            """This replacement records terminal output without a terminal emulator."""

            def __init__(self) -> None:
                self.calls: list[tuple[int, int, str]] = []

            def getmaxyx(self) -> tuple[int, int]:
                return (30, 120)

            def erase(self) -> None:
                self.calls = []

            def addnstr(
                self, row: int, column: int, text: str, count: int, _attribute: int
            ) -> None:
                self.calls.append((row, column, text[:count]))

            def refresh(self) -> None:
                return None

        state = TerminalLessonState(build_lesson_05(), DeterministicAudioCollector())
        screen = RecordingScreen()
        TerminalLessonApp(state)._draw(screen)

        trace = state.lesson.visible_panels[3].format_trace()
        for trace_line in trace:
            self.assertTrue(any(trace_line.rstrip() in text for _row, _column, text in screen.calls))


class AudioAdapterTests(unittest.TestCase):
    """These tests keep physical-device failures outside terminal state handling."""

    def test_sounddevice_failure_reports_unavailable_without_raising(self) -> None:
        """A failed output stream has an unavailable status that the interface can show."""
        class UnavailableSoundDevice:
            """This replacement raises the same way an unavailable device can raise."""

            class OutputStream:
                """This replacement fails during stream creation."""

                def __init__(self, **_arguments: object) -> None:
                    raise RuntimeError("No output device")

        lesson = build_lesson_01()
        adapter = SoundDeviceAudioAdapter(sounddevice_module=UnavailableSoundDevice())
        adapter.configure(lesson.board, lesson.sample_rate)

        self.assertFalse(adapter.start())
        self.assertEqual(adapter.status.state, "unavailable")
        adapter.stop()
        self.assertEqual(adapter.status.state, "ready")

    def test_unavailable_audio_leaves_the_terminal_state_open(self) -> None:
        """An unavailable device reports its failure without ending the terminal lesson."""
        class UnavailableSoundDevice:
            """This replacement has no usable output stream."""

            class OutputStream:
                """This replacement fails during stream creation."""

                def __init__(self, **_arguments: object) -> None:
                    raise RuntimeError("No output device")

        lesson = build_lesson_01()
        adapter = SoundDeviceAudioAdapter(sounddevice_module=UnavailableSoundDevice())
        state = TerminalLessonState(lesson, adapter)

        state.dispatch("b")

        self.assertTrue(state.is_open)
        self.assertIn("unavailable", state.status_message.lower())

    def test_sounddevice_adapter_pulls_samples_and_stops_an_injected_stream(self) -> None:
        """The real-time seam can be exercised with a stream replacement and no device."""
        class CapturingStream:
            """This replacement records callback and shutdown operations."""

            def __init__(self, **arguments: object) -> None:
                self.callback = arguments["callback"]
                self.device = "test output"
                self.started = False
                self.stopped = False
                self.closed = False

            def start(self) -> None:
                self.started = True

            def stop(self) -> None:
                self.stopped = True

            def close(self) -> None:
                self.closed = True

        class CapturingSoundDevice:
            """This replacement provides one capturable output stream."""

            OutputStream = CapturingStream

        lesson = build_lesson_01()
        adapter = SoundDeviceAudioAdapter(
            sounddevice_module=CapturingSoundDevice(), ramp_samples=1
        )
        adapter.configure(lesson.board, lesson.sample_rate)

        self.assertTrue(adapter.start())
        adapter.set_active(True)
        stream = adapter._stream
        output = [[0.0] for _ in range(4)]
        stream.callback(output, 4, None, None)
        adapter.stop()

        self.assertTrue(any(frame[0] != 0.0 for frame in output))
        self.assertTrue(stream.started)
        self.assertTrue(stream.stopped)
        self.assertTrue(stream.closed)
        self.assertEqual(adapter._gain, 0.0)


if __name__ == "__main__":
    unittest.main()
