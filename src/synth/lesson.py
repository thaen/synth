"""This module defines the small configuration object that every lesson supplies."""

from dataclasses import dataclass

from synth.board import Board


@dataclass
class Lesson:
    """This object names one lesson and provides its fully mounted board."""

    number: int
    title: str
    board: Board
    sample_rate: int
    panel_modules: list[object]
    panel_positions: list[tuple[int, int]]
