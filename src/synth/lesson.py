"""This module defines the board and terminal presentation that every lesson supplies."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from synth.board import Board
from synth.controls import Knob


@dataclass(frozen=True)
class VisibleControl:
    """This object declares one learner-adjustable control on a terminal panel."""

    control: Knob
    label: str
    step: float
    description: str = ""

    def format_value(self) -> str:
        """Return the current value in the form that belongs on a terminal panel."""
        suffix = f" {self.control.unit}" if self.control.unit else ""
        return f"{self.control.value:.2f}{suffix}"


@dataclass(frozen=True)
class ModulePresentation:
    """This object gives a mounted module its lesson-facing terminal content."""

    module: object
    label: str
    prose: tuple[str, str]
    visible_controls: tuple[VisibleControl, ...] = ()
    readout: str | Callable[[], str] | None = None
    meter: Callable[[], float] | None = None
    inactive_state: str = "idle"
    active_state: str = "active"

    def format_readout(self) -> str:
        """Return the panel's declared readout without teaching module details to the view."""
        if callable(self.readout):
            return self.readout()
        if self.readout is not None:
            return self.readout
        state = self.module.display_state()
        return state[0] if state else ""

    def format_meter(self, width: int = 8) -> str:
        """Return a compact meter from a lesson-declared normalized signal level."""
        if self.meter is None:
            return ""
        level = max(0.0, min(1.0, self.meter()))
        filled = int(level * width + 0.5)
        return "Signal [" + "#" * filled + "." * (width - filled) + "]"


@dataclass(frozen=True)
class ResetBehavior:
    """This object declares how a lesson returns to its documented starting state."""

    reset_modules: bool = True
    restore_control_values: bool = True
    stop_audio: bool = True


@dataclass
class Lesson:
    """This object names one lesson and provides its board and terminal contract."""

    number: int
    title: str
    board: Board
    sample_rate: int
    panel_modules: list[object]
    panel_positions: list[tuple[int, int]]
    panels: list[ModulePresentation] = field(default_factory=list)
    reset_behavior: ResetBehavior = field(default_factory=ResetBehavior)
    audio_instruction: str = "Use b to start or stop audio."
    audio_active_message: str = "Audio is active."
    audio_inactive_message: str = "Audio is muted."
    key_summary: str = "b starts or stops audio."
    reference_lines: tuple[str, ...] = ()
    _initial_control_values: dict[int, float] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Record control defaults after the lesson configuration has mounted its board."""
        self._initial_control_values = {
            id(control): control.value
            for module in self.board.modules
            for control in module.controls()
        }

    @property
    def visible_panels(self) -> list[ModulePresentation]:
        """Return terminal panels, with a compatibility view for older configurations."""
        if self.panels:
            return self.panels
        return [
            ModulePresentation(
                module=module,
                label=getattr(module, "display_name", type(module).__name__),
                prose=("This module participates in the current signal path.", ""),
                visible_controls=tuple(
                    VisibleControl(control, control.name, 0.01) for control in module.controls()
                ),
            )
            for module in self.panel_modules
        ]

    def reset(self) -> None:
        """Return module state and controls to the values declared by this lesson."""
        if self.reset_behavior.reset_modules:
            for module in self.board.modules:
                reset = getattr(module, "reset", None)
                if callable(reset):
                    reset()
        if self.reset_behavior.restore_control_values:
            for module in self.board.modules:
                for control in module.controls():
                    control.set_value(self._initial_control_values[id(control)])
