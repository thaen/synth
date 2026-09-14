"""This module models a mounted synth board and its shared sample clock."""

from collections.abc import Iterable

from synth.output import AudioOutput
from synth.patch import InputJack, OutputJack, PatchCable


class Board:
    """This board advances mounted modules and reads the audio-output module each sample."""

    def __init__(self) -> None:
        """Create an empty board with no selected audio-output module."""
        self.audio_output: AudioOutput | None = None
        self.modules: list[object] = []
        self.cables: list[PatchCable] = []

    def mount(self, module: object) -> None:
        """Mount one module on the board in signal-path order."""
        for jack in module.all_input_jacks() + module.output_jacks():
            jack.owner = module
        self.modules.append(module)

    def use_audio_output(self, module: AudioOutput) -> None:
        """Select one mounted audio-output module as the board's final endpoint."""
        if module not in self.modules:
            raise ValueError("The selected audio output must be mounted on the board.")
        self.audio_output = module

    def patch(self, source: OutputJack, destination: InputJack) -> PatchCable:
        """Connect two jacks with one patch cable."""
        if source.owner not in self.modules or destination.owner not in self.modules:
            raise ValueError("Both cable endpoints must belong to mounted modules.")
        cable = PatchCable(source, destination)
        self.cables.append(cable)
        return cable

    def unpatch(self, cable: PatchCable) -> None:
        """Remove one cable from the board and unplug its destination jack."""
        self.cables.remove(cable)
        cable.disconnect()

    def next_sample(self) -> float:
        """Advance modules in cable order and return the audio-output voltage."""
        if self.audio_output is None:
            raise ValueError("The board has no selected audio-output module.")
        for module in self.evaluation_order():
            module.advance()
        return self.audio_output.current_sample()

    def samples(self, count: int) -> Iterable[float]:
        """Yield the requested number of board samples."""
        for _ in range(count):
            yield self.next_sample()

    def evaluation_order(self) -> list[object]:
        """Return module order derived from connected cable directions."""
        dependencies = {module: set() for module in self.modules}
        dependents = {module: set() for module in self.modules}
        for cable in self.cables:
            source_module = cable.source.owner
            destination_module = cable.destination.owner
            if source_module is not destination_module:
                dependencies[destination_module].add(source_module)
                dependents[source_module].add(destination_module)

        ready = [module for module in self.modules if not dependencies[module]]
        order = []
        while ready:
            module = ready.pop(0)
            order.append(module)
            for dependent in dependents[module]:
                dependencies[dependent].remove(module)
                if not dependencies[dependent]:
                    ready.append(dependent)

        if len(order) != len(self.modules):
            raise ValueError("The board has a cable cycle and needs an explicit feedback model.")
        return order
