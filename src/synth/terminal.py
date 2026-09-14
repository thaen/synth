"""This module contains the generic full-screen terminal lesson interface."""

from __future__ import annotations

import argparse
import curses
import importlib
import time

from synth.lesson import Lesson, ModulePresentation
from synth.realtime_audio import AudioAdapter, SoundDeviceAudioAdapter


class TerminalLessonState:
    """This object applies terminal commands without placing terminal work in audio callbacks."""

    def __init__(self, lesson: Lesson, audio: AudioAdapter) -> None:
        """Create state for one lesson and configure its output adapter."""
        self.lesson = lesson
        self.audio = audio
        self.audio.configure(lesson.board, lesson.sample_rate)
        self.selected_index = 0
        self.help_is_visible = False
        self.is_open = True
        self.status_message = "Use b to start or stop the lesson tone."

    @property
    def selected_panel(self) -> ModulePresentation:
        """Return the presentation selected by the learner."""
        return self.lesson.visible_panels[self.selected_index]

    def dispatch(self, command: str) -> None:
        """Apply one normalized terminal command to generic lesson data."""
        if command == "left":
            self._move_selection(-1)
        elif command == "right":
            self._move_selection(1)
        elif command == "up":
            self._adjust_selected(1)
        elif command == "down":
            self._adjust_selected(-1)
        elif command == "b":
            self._toggle_audio()
        elif command == "r":
            self._reset()
        elif command == "?":
            self.help_is_visible = not self.help_is_visible
            self.status_message = "Keyboard reference is visible." if self.help_is_visible else "Keyboard reference is closed."
        elif command == "q":
            self.audio.stop()
            self.is_open = False
            self.status_message = "The terminal lesson has stopped."

    def _move_selection(self, direction: int) -> None:
        """Move among visible lesson panels and keep selection within that list."""
        panel_count = len(self.lesson.visible_panels)
        self.selected_index = (self.selected_index + direction) % panel_count
        self.status_message = f"Selected {self.selected_panel.label}."

    def _adjust_selected(self, direction: int) -> None:
        """Adjust the selected lesson-declared control, if it has one."""
        controls = self.selected_panel.visible_controls
        if not controls:
            self.status_message = f"{self.selected_panel.label} has no exposed control in this lesson."
            return
        control = controls[0]
        self.audio.apply_terminal_change(
            lambda: control.control.set_value(control.control.value + direction * control.step)
        )
        self.status_message = f"{control.label}: {control.format_value()}."

    def _toggle_audio(self) -> None:
        """Start the adapter when needed and toggle its output state."""
        if not self.audio.is_active and not self.audio.start():
            self.status_message = self.audio.status.message
            return
        self.audio.set_active(not self.audio.is_active)
        self.status_message = self.audio.status.message

    def _reset(self) -> None:
        """Stop audio before the lesson restores module state and control defaults."""
        if self.lesson.reset_behavior.stop_audio:
            self.audio.stop()
        self.audio.apply_terminal_change(self.lesson.reset)
        self.status_message = "The lesson has returned to its documented defaults."


class TerminalLessonApp:
    """This object redraws a full-screen lesson at a rate separate from sample production."""

    def __init__(self, state: TerminalLessonState, refresh_rate: float = 30.0) -> None:
        """Create an application with a fixed display refresh rate."""
        self.state = state
        self.refresh_rate = refresh_rate
        self.pulse_frame = 0

    def run(self) -> None:
        """Run the curses screen until the learner quits."""
        curses.wrapper(self._run_screen)

    def _run_screen(self, screen: curses.window) -> None:
        """Poll keyboard input and redraw at the fixed configured rate."""
        screen.keypad(True)
        screen.nodelay(True)
        frame_period = 1.0 / self.refresh_rate
        next_frame = time.monotonic()
        while self.state.is_open:
            command = self._command_for_key(screen.getch())
            if command is not None:
                self.state.dispatch(command)
            now = time.monotonic()
            if now >= next_frame:
                self.pulse_frame += 1
                self._draw(screen)
                next_frame = now + frame_period
            else:
                time.sleep(min(0.01, next_frame - now))

    @staticmethod
    def _command_for_key(key: int) -> str | None:
        """Translate curses key values into the state object's portable command names."""
        mapping = {
            curses.KEY_LEFT: "left",
            curses.KEY_RIGHT: "right",
            curses.KEY_UP: "up",
            curses.KEY_DOWN: "down",
            ord("b"): "b",
            ord("r"): "r",
            ord("?"): "?",
            ord("q"): "q",
        }
        return mapping.get(key)

    def _draw(self, screen: curses.window) -> None:
        """Draw board panels, cable direction, teaching text, status, and key reference."""
        height, width = screen.getmaxyx()
        screen.erase()
        self._write(screen, 0, 0, f"Lesson {self.state.lesson.number}: {self.state.lesson.title}", curses.A_BOLD)
        panels = self.state.lesson.visible_panels
        panel_width = max(18, min(30, (width - max(0, len(panels) - 1) * 3) // len(panels)))
        panel_top = 2
        for index, panel in enumerate(panels):
            self._draw_panel(screen, panel_top, index * (panel_width + 3), panel_width, panel, index == self.state.selected_index)
        cable_row = panel_top + 7
        if cable_row < height:
            pulse = ">" if self.state.audio.is_active and self.pulse_frame % 2 == 0 else "-"
            labels = {id(panel.module): panel.label for panel in panels}
            cable_text = "   ".join(
                f"{labels.get(id(cable.source.owner), type(cable.source.owner).__name__)} "
                f"-{pulse}> {labels.get(id(cable.destination.owner), type(cable.destination.owner).__name__)}"
                for cable in self.state.lesson.board.cables
            )
            self._write(screen, cable_row, 0, cable_text)
        teaching_top = cable_row + 2
        if self.state.help_is_visible:
            lines = [
                "Keyboard reference: left/right select a module; up/down change its exposed control.",
                "b starts or stops the tone. r restores defaults and stops audio. ? closes this reference. q quits.",
            ]
        else:
            selected = self.state.selected_panel
            lines = [f"Selected: {selected.label}", *selected.prose]
        for offset, line in enumerate(lines):
            self._write(screen, teaching_top + offset, 0, line, curses.A_BOLD if offset == 0 else 0)
        status_row = height - 2
        self._write(screen, status_row, 0, f"Audio {self.state.audio.status.state}: {self.state.audio.status.message}")
        self._write(screen, height - 1, 0, self.state.status_message)
        screen.refresh()

    def _draw_panel(self, screen: curses.window, top: int, left: int, width: int, panel: ModulePresentation, selected: bool) -> None:
        """Draw one compact module panel from presentation and module-owned state."""
        attribute = curses.A_REVERSE if selected else 0
        self._write(screen, top, left, "+" + "-" * (width - 2) + "+", attribute)
        self._write(screen, top + 1, left, "|" + self._fit(panel.label, width - 2).center(width - 2) + "|", attribute)
        state = panel.module.display_state()
        self._write(screen, top + 2, left, "|" + self._fit(state[0] if state else "", width - 2).ljust(width - 2) + "|", attribute)
        control_text = ""
        if panel.visible_controls:
            control = panel.visible_controls[0]
            control_text = f"{control.label} {control.format_value()}"
        self._write(screen, top + 3, left, "|" + self._fit(control_text, width - 2).ljust(width - 2) + "|", attribute)
        self._write(screen, top + 4, left, "|" + self._fit("State: " + ("active" if self.state.audio.is_active else "idle"), width - 2).ljust(width - 2) + "|", attribute)
        self._write(screen, top + 5, left, "|" + " " * (width - 2) + "|", attribute)
        self._write(screen, top + 6, left, "+" + "-" * (width - 2) + "+", attribute)

    @staticmethod
    def _fit(text: str, width: int) -> str:
        """Keep a terminal line within the current screen width."""
        return text[: max(0, width)]

    @staticmethod
    def _write(screen: curses.window, row: int, column: int, text: str, attribute: int = 0) -> None:
        """Write one clipped line without failing in a small terminal window."""
        height, width = screen.getmaxyx()
        if 0 <= row < height and column < width:
            try:
                screen.addnstr(row, column, text, max(0, width - column - 1), attribute)
            except curses.error:
                pass


def load_lesson(number: int) -> Lesson:
    """Load the requested lesson configuration without encoding lesson behavior here."""
    module_name = f"lessons.lesson_{number:02d}"
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as error:
        if error.name == module_name:
            raise ValueError(f"Lesson {number} has no board configuration.") from error
        raise
    return module.build()


def main() -> None:
    """Start one generic terminal lesson screen."""
    parser = argparse.ArgumentParser(description="Run one terminal synthesizer lesson.")
    parser.add_argument("--lesson", type=int, required=True, help="The lesson number to run.")
    arguments = parser.parse_args()
    try:
        lesson = load_lesson(arguments.lesson)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    TerminalLessonApp(TerminalLessonState(lesson, SoundDeviceAudioAdapter())).run()


if __name__ == "__main__":
    main()
