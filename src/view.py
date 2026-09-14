"""Display any lesson board from its module-and-cable configuration."""

import argparse
import importlib
from typing import Type, Union

import pygame

from synth.controls import Knob
from synth.lesson import Lesson
from synth.patch import InputJack, OutputJack


WINDOW_WIDTH = 1_140
WINDOW_HEIGHT = 650
MODULE_WIDTH = 190
MODULE_HEIGHT = 270
BOARD_RECTANGLE = pygame.Rect(24, 108, WINDOW_WIDTH - 48, 412)
SAMPLES_PER_VISIBLE_STEP = 10
ANIMATION_DELAY_MILLISECONDS = 35

BACKGROUND = (248, 245, 238)
INK = (23, 47, 59)
MUTED_INK = (74, 89, 96)
MODULE_FILL = (220, 232, 231)
MODULE_BORDER = (23, 47, 59)
CABLE = (181, 74, 54)
INPUT_JACK = (78, 94, 99)
OUTPUT_JACK = (37, 68, 79)
BOARD_FILL = (234, 226, 211)
BOARD_BORDER = (171, 154, 130)
BUTTON_FILL = (232, 221, 200)
BUTTON_ACTIVE_FILL = (213, 231, 215)


def load_lesson(number: int) -> Lesson:
    """Import one lesson configuration and return its newly mounted board."""
    module_name = f"lessons.lesson_{number:02d}"
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as error:
        if error.name == module_name:
            raise ValueError(f"Lesson {number} has no board configuration.") from error
        raise
    return module.build()


class BoardView:
    """This unchanged viewer draws whichever board configuration a lesson supplies."""

    def __init__(self, lesson: Lesson) -> None:
        """Create one Pygame window for the lesson's mounted board."""
        pygame.init()
        pygame.display.set_caption(f"Synth Board: Lesson {lesson.number}")
        self.lesson = lesson
        self.module_height = MODULE_HEIGHT
        self.footer_top = 554
        self.window_height = WINDOW_HEIGHT
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, self.window_height))
        self.clock = pygame.time.Clock()
        self.last_sample = 0.0
        self.is_running = False
        self.is_open = True
        self.elapsed_milliseconds = 0
        self.jack_positions: dict[int, tuple[int, int]] = {}
        self.knob_areas: list[tuple[pygame.Rect, Knob]] = []
        self.run_button = pygame.Rect(770, self.footer_top, 100, 42)
        self.step_button = pygame.Rect(882, self.footer_top, 150, 42)
        self.reset_button = pygame.Rect(1_044, self.footer_top, 70, 42)

    def run(self) -> None:
        """Process input, advance the board, and draw until the window closes."""
        while self.is_open:
            elapsed = self.clock.tick(60)
            self.handle_events()
            if self.is_running:
                self.elapsed_milliseconds += elapsed
                while self.elapsed_milliseconds >= ANIMATION_DELAY_MILLISECONDS:
                    self.advance_visible_step()
                    self.elapsed_milliseconds -= ANIMATION_DELAY_MILLISECONDS
            self.draw()
        pygame.quit()

    def handle_events(self) -> None:
        """Respond to buttons and front-panel controls that the board exposes."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_open = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)
            elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
                self.adjust_knob_at(event.pos)

    def handle_click(self, position: tuple[int, int]) -> None:
        """Apply the action associated with a button or a front-panel control."""
        if self.run_button.collidepoint(position):
            self.is_running = not self.is_running
            self.elapsed_milliseconds = 0
        elif self.step_button.collidepoint(position):
            self.advance_visible_step()
        elif self.reset_button.collidepoint(position):
            self.reset_modules()
        else:
            self.adjust_knob_at(position)

    def adjust_knob_at(self, position: tuple[int, int]) -> None:
        """Turn a drawn front-panel control according to the horizontal click position."""
        for rectangle, knob in self.knob_areas:
            within_x = rectangle.left <= position[0] <= rectangle.right
            within_y = rectangle.top - 12 <= position[1] <= rectangle.bottom + 12
            if within_x and within_y:
                fraction = (position[0] - rectangle.left) / rectangle.width
                knob.set_value(knob.minimum + max(0.0, min(1.0, fraction)) * (knob.maximum - knob.minimum))

    def advance_visible_step(self) -> None:
        """Advance the shared board enough times for its state to visibly change."""
        for _ in range(SAMPLES_PER_VISIBLE_STEP):
            self.last_sample = self.lesson.board.next_sample()

    def reset_modules(self) -> None:
        """Return every module that has phase state to its initial position."""
        for module in self.lesson.panel_modules:
            reset = getattr(module, "reset", None)
            if reset is not None:
                reset()
        self.last_sample = 0.0

    def draw(self) -> None:
        """Draw the lesson title, mounted modules, cables, and shared controls."""
        self.screen.fill(BACKGROUND)
        self.jack_positions = {}
        self.knob_areas = []
        self.draw_title()
        pygame.draw.rect(self.screen, BOARD_FILL, BOARD_RECTANGLE, border_radius=8)
        pygame.draw.rect(self.screen, BOARD_BORDER, BOARD_RECTANGLE, width=2, border_radius=8)
        for index, module in enumerate(self.lesson.panel_modules):
            self.draw_module(module, index)
        self.draw_cables()
        self.draw_footer()
        pygame.display.flip()

    def draw_title(self) -> None:
        """Draw the lesson identity and the board's current output voltage."""
        title_font = pygame.font.SysFont("Helvetica", 22, bold=True)
        body_font = pygame.font.SysFont("Helvetica", 15)
        self.draw_text(f"BOARD {self.lesson.number}: {self.lesson.title}", title_font, INK, (28, 25))
        self.draw_text(
            f"Audio-output voltage: {self.lesson.board.audio_output.current_sample():+.5f}",
            body_font,
            MUTED_INK,
            (28, 58),
        )
        self.draw_text(
            "Every module and cable in this window comes from the lesson configuration.",
            body_font,
            MUTED_INK,
            (28, 82),
        )

    def draw_module(self, module: object, index: int) -> None:
        """Draw one mounted module from its jacks and exposed front-panel controls."""
        left, top = self.lesson.panel_positions[index]
        rectangle = pygame.Rect(left, top, MODULE_WIDTH, self.module_height)
        heading_font = pygame.font.SysFont("Helvetica", 18, bold=True)
        body_font = pygame.font.SysFont("Helvetica", 15)
        small_font = pygame.font.SysFont("Helvetica", 12)

        pygame.draw.rect(self.screen, MODULE_FILL, rectangle, border_radius=4)
        pygame.draw.rect(self.screen, MODULE_BORDER, rectangle, width=2, border_radius=4)
        name = getattr(module, "display_name", type(module).__name__.upper())
        self.draw_text(name, heading_font, INK, (left + 18, top + 20))
        pygame.draw.line(self.screen, MUTED_INK, (left + 16, top + 54), (left + MODULE_WIDTH - 16, top + 54))

        input_jacks = self.jacks(module, InputJack)
        output_jacks = self.jacks(module, OutputJack)
        for jack_index, jack in enumerate(input_jacks):
            y = top + 95 + jack_index * 42
            self.draw_jack(jack, (left, y))
            self.draw_text(jack.name, small_font, INK, (left + 22, y - 7))
        for jack_index, jack in enumerate(output_jacks):
            y = top + 95 + jack_index * 42
            self.draw_jack(jack, (left + MODULE_WIDTH, y))
            text = small_font.render(jack.name, True, INK)
            self.screen.blit(text, (left + MODULE_WIDTH - 22 - text.get_width(), y - 7))

        controls = self.controls(module)
        for control_index, knob in enumerate(controls):
            self.draw_knob(knob, left + 22, top + 220 + control_index * 58, MODULE_WIDTH - 44)

        self.draw_module_state(module, left + 18, top + 172, body_font)

    def draw_module_state(self, module: object, x: int, y: int, font: pygame.font.Font) -> None:
        """Draw the state that a module explicitly provides for its front panel."""
        for index, line in enumerate(module.display_state()):
            self.draw_text(line, font, INK, (x, y + index * 24))

    def draw_jack(self, jack: Union[InputJack, OutputJack], position: tuple[int, int]) -> None:
        """Draw one jack and remember its location for the corresponding patch cable."""
        color = OUTPUT_JACK if isinstance(jack, OutputJack) else INPUT_JACK
        pygame.draw.circle(self.screen, color, position, 12)
        pygame.draw.circle(self.screen, BACKGROUND, position, 6)
        self.jack_positions[id(jack)] = position

    def draw_knob(self, knob: Knob, left: int, top: int, width: int) -> None:
        """Draw one adjustable front-panel control and remember its hit area."""
        label_font = pygame.font.SysFont("Helvetica", 12, bold=True)
        body_font = pygame.font.SysFont("Helvetica", 13)
        self.draw_text(knob.name, label_font, INK, (left, top))
        self.draw_text(f"{knob.value:+.2f} {knob.unit}", body_font, INK, (left + width - 72, top))
        track = pygame.Rect(left, top + 27, width, 7)
        pygame.draw.rect(self.screen, MUTED_INK, track, border_radius=3)
        fraction = (knob.value - knob.minimum) / (knob.maximum - knob.minimum)
        knob_x = round(track.left + fraction * track.width)
        pygame.draw.circle(self.screen, OUTPUT_JACK, (knob_x, track.centery), 9)
        self.knob_areas.append((track, knob))

    def draw_cables(self) -> None:
        """Draw every cable after every jack has a known screen position."""
        for cable in self.lesson.board.cables:
            source = self.jack_positions[id(cable.source)]
            destination = self.jack_positions[id(cable.destination)]
            pygame.draw.line(self.screen, CABLE, source, destination, width=4)

    def draw_footer(self) -> None:
        """Draw controls that advance the board's shared sample clock."""
        body_font = pygame.font.SysFont("Helvetica", 14)
        self.draw_text(
            "Run and Request 10 Samples advance the entire mounted board on its shared clock.",
            body_font,
            MUTED_INK,
            (28, self.footer_top + 12),
        )
        self.draw_button(self.run_button, "Pause" if self.is_running else "Run", self.is_running)
        self.draw_button(self.step_button, "Request 10 samples", False)
        self.draw_button(self.reset_button, "Reset", False)

    def draw_button(self, rectangle: pygame.Rect, label: str, active: bool) -> None:
        """Draw one board-level control button."""
        fill = BUTTON_ACTIVE_FILL if active else BUTTON_FILL
        pygame.draw.rect(self.screen, fill, rectangle, border_radius=5)
        pygame.draw.rect(self.screen, INK, rectangle, width=1, border_radius=5)
        font = pygame.font.SysFont("Helvetica", 14)
        text = font.render(label, True, INK)
        self.screen.blit(text, text.get_rect(center=rectangle.center))

    def jacks(
        self, module: object, jack_type: Union[Type[InputJack], Type[OutputJack]]
    ) -> list[Union[InputJack, OutputJack]]:
        """Return the jacks that a module explicitly provides for its front panel."""
        return module.input_jacks() if jack_type is InputJack else module.output_jacks()

    def controls(self, module: object) -> list[Knob]:
        """Return the controls that one module asks the generic viewer to draw."""
        return module.controls()

    def draw_text(
        self, text: str, font: pygame.font.Font, color: tuple[int, int, int], position: tuple[int, int]
    ) -> None:
        """Draw text at the requested position."""
        self.screen.blit(font.render(text, True, color), position)


def parse_arguments() -> argparse.Namespace:
    """Read the lesson number that selects the board configuration to display."""
    parser = argparse.ArgumentParser(description="Display one synthesizer lesson board.")
    parser.add_argument("--lesson", type=int, required=True, help="The lesson number to display.")
    return parser.parse_args()


def main() -> None:
    """Load the selected lesson configuration and display its board."""
    arguments = parse_arguments()
    try:
        lesson = load_lesson(arguments.lesson)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    BoardView(lesson).run()


if __name__ == "__main__":
    main()
