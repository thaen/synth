"""This module models a mounted synth board and its shared sample clock."""

from collections.abc import Iterable

from synth.output import SpeakerOutput
from synth.patch import InputJack, OutputJack, PatchCable


class Board:
    """This board advances mounted modules and reads the speaker module each sample."""

    def __init__(self, speaker: SpeakerOutput) -> None:
        """Create a board whose final module is the speaker output."""
        self.speaker = speaker
        self.modules: list[object] = []
        self.cables: list[PatchCable] = []

    def mount(self, module: object) -> None:
        """Mount one module on the board in signal-path order."""
        self.modules.append(module)

    def patch(self, source: OutputJack, destination: InputJack) -> PatchCable:
        """Connect two jacks with one patch cable."""
        cable = PatchCable(source, destination)
        self.cables.append(cable)
        return cable

    def next_sample(self) -> float:
        """Advance every module once and return the speaker's current voltage."""
        for module in self.modules:
            module.advance()
        return self.speaker.current_sample()

    def samples(self, count: int) -> Iterable[float]:
        """Yield the requested number of board samples."""
        for _ in range(count):
            yield self.next_sample()
