"""These tests protect the generic terminal lesson state and audio seam."""

import unittest

from lessons.lesson_01 import build as build_lesson_01
from lessons.lesson_02 import build as build_lesson_02
from synth.realtime_audio import DeterministicAudioCollector, SoundDeviceAudioAdapter
from synth.terminal import TerminalLessonState


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
        """The terminal changes the configured pitch knob by its declared step."""
        lesson = build_lesson_02()
        state = TerminalLessonState(lesson, DeterministicAudioCollector())

        state.dispatch("up")

        self.assertAlmostEqual(lesson.visible_panels[0].visible_controls[0].control.value, 1 / 12)
        self.assertIn("Pitch", state.status_message)

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
        state.dispatch("up")
        state.dispatch("b")
        samples = collector.collect(4)

        self.assertTrue(collector.is_active)
        self.assertEqual(len(samples), 4)
        state.dispatch("?")
        self.assertTrue(state.help_is_visible)
        state.dispatch("r")
        self.assertFalse(collector.is_active)
        self.assertEqual(lesson.visible_panels[0].visible_controls[0].control.value, 0.0)
        state.dispatch("q")
        self.assertFalse(state.is_open)


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


if __name__ == "__main__":
    unittest.main()
