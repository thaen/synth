"""This module assembles the first physical-style board used by the course."""

from dataclasses import dataclass

from synth.board import Board
from synth.oscillator import SineOscillator
from synth.output import SpeakerOutput


@dataclass
class FirstBoard:
    """This object keeps the mounted modules of the first board together."""

    board: Board
    oscillator: SineOscillator
    speaker: SpeakerOutput

    def next_sample(self) -> float:
        """Advance the mounted board once and return its speaker sample."""
        return self.board.next_sample()


def make_first_board(frequency_hz: float, sample_rate: int) -> FirstBoard:
    """Mount a sine oscillator, patch it to a speaker, and return the board."""
    oscillator = SineOscillator(frequency_hz, sample_rate)
    speaker = SpeakerOutput()
    board = Board(speaker)
    board.mount(oscillator)
    board.mount(speaker)
    board.patch(oscillator.sine_output, speaker.audio_input)
    return FirstBoard(board, oscillator, speaker)
