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
        self.status_message = lesson.audio_instruction

    @property
    def selected_panel(self) -> ModulePresentation:
        """Return the presentation selected by the learner."""
        return self.lesson.visible_panels[self.selected_index]

    def panel_state(self, panel: ModulePresentation) -> str:
        """Return the lesson-declared state text for one panel."""
        return panel.active_state if self.audio.is_active else panel.inactive_state

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
        self.status_message = (
            self.lesson.audio_active_message
            if self.audio.is_active
            else self.lesson.audio_inactive_message
        )

    def _reset(self) -> None:
        """Stop audio before the lesson restores module state and control defaults."""
        if self.lesson.reset_behavior.stop_audio:
            self.audio.stop()
        self.audio.apply_terminal_change(self.lesson.reset)
        self.selected_index = 0
        self.help_is_visible = False
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
        panel_width = self._panel_width(width, len(panels))
        panel_lefts = self._panel_lefts(width, panel_width, len(panels))
        panel_top = 2
        for index, panel in enumerate(panels):
            self._draw_panel(
                screen,
                panel_top,
                panel_lefts[index],
                panel_width,
                panel,
                index == self.state.selected_index,
            )
        self._draw_cables(screen, panel_top + 4, panel_width, panels, panel_lefts)
        teaching_top = panel_top + 8
        if self.state.help_is_visible:
            lines = [
                "Keyboard reference: left/right select a module; up/down change its exposed control.",
                f"{self.state.lesson.key_summary}. r restores defaults and stops audio. ? closes this reference. q quits.",
                *self.state.lesson.reference_lines,
            ]
        else:
            selected = self.state.selected_panel
            lines = [f"Selected: {selected.label}. {selected.prose[0]}", selected.prose[1]]
        for offset, line in enumerate(lines):
            self._write(screen, teaching_top + offset, 0, line, curses.A_BOLD if offset == 0 else 0)
        status_row = height - 2
        self._write(
            screen,
            status_row - 1,
            0,
            f"Keys: {self.state.lesson.key_summary}; left/right select; up/down change a control; r reset; ? help; q quit",
        )
        self._write(screen, status_row, 0, f"Audio {self.state.audio.status.state}: {self.state.audio.status.message}")
        self._write(screen, height - 1, 0, self.state.status_message)
        screen.refresh()

    def _draw_panel(self, screen: curses.window, top: int, left: int, width: int, panel: ModulePresentation, selected: bool) -> None:
        """Draw one compact module panel from presentation and module-owned state."""
        attribute = curses.A_REVERSE if selected else 0
        self._write(screen, top, left, "+" + "-" * (width - 2) + "+", attribute)
        self._write(screen, top + 1, left, "|" + self._fit(panel.label, width - 2).center(width - 2) + "|", attribute)
        self._write(screen, top + 2, left, "|" + self._fit(panel.format_readout(), width - 2).ljust(width - 2) + "|", attribute)
        control_text = ""
        if panel.visible_controls:
            control = panel.visible_controls[0]
            control_text = f"{control.label} {control.format_value()}"
        self._write(screen, top + 3, left, "|" + self._fit(control_text, width - 2).ljust(width - 2) + "|", attribute)
        self._write(screen, top + 4, left, "|" + self._fit("State: " + self.state.panel_state(panel), width - 2).ljust(width - 2) + "|", attribute)
        self._write(screen, top + 5, left, "|" + self._fit(panel.format_meter(), width - 2).ljust(width - 2) + "|", attribute)
        self._write(screen, top + 6, left, "+" + "-" * (width - 2) + "+", attribute)

    @staticmethod
    def _fit(text: str, width: int) -> str:
        """Keep a terminal line within the current screen width."""
        return text[: max(0, width)]

    @staticmethod
    def _panel_width(screen_width: int, panel_count: int) -> int:
        """Return a compact width that leaves open space for visible patch cables."""
        if panel_count <= 0:
            return 18
        drawable_width = max(1, screen_width - 1)
        minimum_gap = 4 * max(0, panel_count - 1)
        return max(18, min(30, (drawable_width - minimum_gap) // panel_count))

    @staticmethod
    def _panel_lefts(screen_width: int, panel_width: int, panel_count: int) -> list[int]:
        """Place panels across the screen with an even cable space between neighbors."""
        if panel_count <= 1:
            return [0]
        drawable_width = max(1, screen_width - 1)
        remaining_width = max(0, drawable_width - panel_width * panel_count)
        gap = remaining_width // (panel_count - 1)
        return [index * (panel_width + gap) for index in range(panel_count)]

    def _draw_cables(
        self,
        screen: curses.window,
        row: int,
        panel_width: int,
        panels: list[ModulePresentation],
        panel_lefts: list[int],
    ) -> None:
        """Draw each configured cable with a moving pulse only while audio is active."""
        left_by_module = {id(panel.module): panel_lefts[index] for index, panel in enumerate(panels)}
        for cable in self.state.lesson.board.cables:
            source_left = left_by_module.get(id(cable.source.owner))
            destination_left = left_by_module.get(id(cable.destination.owner))
            if source_left is None or destination_left is None:
                continue
            if source_left < destination_left:
                start = source_left + panel_width
                stop = destination_left
                direction = ">"
            else:
                start = destination_left + panel_width
                stop = source_left
                direction = "<"
            length = max(0, stop - start)
            if length == 0:
                continue
            cable_text = "=" * length if self.state.audio.is_active else "-" * length
            if self.state.audio.is_active:
                pulse_index = self.pulse_frame % length
                if direction == "<":
                    pulse_index = length - pulse_index - 1
                cable_text = cable_text[:pulse_index] + direction + cable_text[pulse_index + 1 :]
            self._write(screen, row, start, cable_text)

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
