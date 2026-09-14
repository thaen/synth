"""Show the state and output of the Lesson 2 sine oscillator with Pygame."""

from dataclasses import dataclass
import pygame

from synth.first_board import make_first_board


SAMPLE_RATE = 44_100
DEFAULT_FREQUENCY_HZ = 440.0
WINDOW_WIDTH = 920
WINDOW_HEIGHT = 610
ANIMATION_DELAY_MILLISECONDS = 35
SAMPLES_PER_VISIBLE_STEP = 10
MINIMUM_FREQUENCY_HZ = 20.0
MAXIMUM_FREQUENCY_HZ = 1_000.0

BACKGROUND = (248, 245, 238)
INK = (23, 47, 59)
MUTED_INK = (74, 89, 96)
MODULE_FILL = (220, 232, 231)
MODULE_BORDER = (23, 47, 59)
SIGNAL = (181, 74, 54)
SIGNAL_DARK = (143, 54, 39)
GRID = (169, 183, 183)
BUTTON_FILL = (232, 221, 200)
BUTTON_ACTIVE_FILL = (213, 231, 215)


@dataclass
class Button:
    """This object describes one clickable rectangle in the visual lab."""

    label: str
    rectangle: pygame.Rect


class OscillatorView:
    """This window shows one oscillator and the waveform it produces."""

    def __init__(self) -> None:
        """Create the Pygame drawing surface and oscillator state."""
        pygame.init()
        pygame.display.set_caption("Lesson 2: The Sine Oscillator")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont("Helvetica", 22, bold=True)
        self.heading_font = pygame.font.SysFont("Helvetica", 17, bold=True)
        self.body_font = pygame.font.SysFont("Helvetica", 15)
        self.small_font = pygame.font.SysFont("Helvetica", 12)

        self.instrument = make_first_board(DEFAULT_FREQUENCY_HZ, SAMPLE_RATE)
        self.oscillator = self.instrument.oscillator
        self.speaker = self.instrument.speaker
        self.last_sample = 0.0
        self.is_running = False
        self.is_open = True
        self.elapsed_milliseconds = 0
        self.is_dragging_frequency = False

        self.run_button = Button("Run", pygame.Rect(480, 510, 110, 42))
        self.step_button = Button("Request 10 samples", pygame.Rect(602, 510, 170, 42))
        self.reset_button = Button("Reset phase", pygame.Rect(784, 510, 110, 42))
        self.slider_track = pygame.Rect(54, 466, 330, 8)

    def run(self) -> None:
        """Process input, advance the oscillator, and redraw until the window closes."""
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
        """Respond to window, button, and frequency-slider events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_open = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_mouse_down(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.is_dragging_frequency = False
            elif event.type == pygame.MOUSEMOTION and self.is_dragging_frequency:
                self.set_frequency_from_x(event.pos[0])

    def handle_mouse_down(self, position: tuple[int, int]) -> None:
        """Apply the action associated with a click."""
        if self.run_button.rectangle.collidepoint(position):
            self.is_running = not self.is_running
            self.elapsed_milliseconds = 0
        elif self.step_button.rectangle.collidepoint(position):
            self.advance_visible_step()
        elif self.reset_button.rectangle.collidepoint(position):
            self.oscillator.reset()
            self.last_sample = 0.0
        elif self.slider_hitbox().collidepoint(position):
            self.is_dragging_frequency = True
            self.set_frequency_from_x(position[0])

    def set_frequency_from_x(self, x_position: int) -> None:
        """Set frequency from a horizontal position on the slider track."""
        fraction = (x_position - self.slider_track.left) / self.slider_track.width
        fraction = max(0.0, min(1.0, fraction))
        frequency = MINIMUM_FREQUENCY_HZ + fraction * (
            MAXIMUM_FREQUENCY_HZ - MINIMUM_FREQUENCY_HZ
        )
        self.oscillator.frequency_hz = round(frequency)

    def advance_visible_step(self) -> None:
        """Advance the mounted board enough to make phase movement easy to see."""
        for _ in range(SAMPLES_PER_VISIBLE_STEP):
            self.last_sample = self.instrument.next_sample()

    def slider_hitbox(self) -> pygame.Rect:
        """Return a generous clickable region around the frequency slider."""
        return self.slider_track.inflate(0, 32)

    def draw(self) -> None:
        """Draw the mounted board and its patch cable."""
        self.screen.fill(BACKGROUND)
        self.draw_title()
        self.draw_module()
        self.draw_connection()
        self.draw_speaker()
        self.draw_frequency_control()
        self.draw_buttons()
        pygame.display.flip()

    def draw_title(self) -> None:
        """Draw the title and the meaning of the phase marker."""
        self.draw_text(
            "The first board sends a sine-wave voltage through one patch cable.",
            self.title_font,
            INK,
            (30, 25),
        )
        self.draw_text(
            "The board advances once per sample, and the speaker reads the cable's voltage.",
            self.body_font,
            MUTED_INK,
            (30, 56),
        )

    def draw_module(self) -> None:
        """Draw the oscillator as a physical instrument part."""
        rectangle = pygame.Rect(35, 116, 350, 320)
        pygame.draw.rect(self.screen, MODULE_FILL, rectangle)
        pygame.draw.rect(self.screen, MODULE_BORDER, rectangle, width=2)
        self.draw_text("SINE OSCILLATOR", self.heading_font, INK, (58, 141))
        pygame.draw.line(self.screen, MUTED_INK, (55, 174), (365, 174), width=1)

        phase_step = self.oscillator.frequency_hz / self.oscillator.sample_rate
        visible_step = SAMPLES_PER_VISIBLE_STEP * phase_step
        rows = [
            ("INPUT", f"frequency: {self.oscillator.frequency_hz:.0f} Hz"),
            ("INPUT", f"sample rate: {self.oscillator.sample_rate:,} samples each second"),
            ("STATE", f"phase: {self.oscillator.phase_cycles:.5f} cycles"),
            ("OUTPUT", f"last sample: {self.last_sample:+.5f}"),
            ("STEP", f"one request advances: {phase_step:.5f} cycles"),
            ("VIEW", f"10 requests advance: {visible_step:.5f} cycles"),
        ]
        y = 197
        for label, value in rows:
            self.draw_text(label, self.small_font, MUTED_INK, (58, y))
            self.draw_text(value, self.body_font, INK, (58, y + 15))
            y += 37

    def draw_connection(self) -> None:
        """Draw the physical-style cable from the oscillator to the speaker module."""
        start, end, y = 385, 440, 276
        pygame.draw.line(self.screen, SIGNAL, (start, y), (end, y), width=4)
        pygame.draw.polygon(self.screen, SIGNAL, [(end, y), (end - 12, y - 7), (end - 12, y + 7)])
        self.draw_text("patch cable", self.small_font, SIGNAL_DARK, (390, 246))
        self.draw_text("audio voltage", self.small_font, SIGNAL_DARK, (390, 262))

    def draw_speaker(self) -> None:
        """Draw the physical-style output module that reads the patch cable."""
        left, top, width, height = 455, 116, 420, 320
        rectangle = pygame.Rect(left, top, width, height)

        pygame.draw.rect(self.screen, MODULE_FILL, rectangle)
        pygame.draw.rect(self.screen, MODULE_BORDER, rectangle, width=2)
        self.draw_text("SPEAKER OUTPUT", self.heading_font, INK, (480, 141))
        pygame.draw.line(self.screen, MUTED_INK, (475, 174), (850, 174), width=1)
        input_x, input_y = left, 276
        pygame.draw.circle(self.screen, SIGNAL_DARK, (input_x, input_y), 13)
        pygame.draw.circle(self.screen, BACKGROUND, (input_x, input_y), 7)
        self.draw_text("Audio input jack", self.body_font, INK, (480, 248))
        self.draw_text(
            f"incoming voltage: {self.speaker.current_sample():+.5f}",
            self.body_font,
            INK,
            (480, 278),
        )
        self.draw_text("speaker", self.heading_font, INK, (690, 222))
        pygame.draw.circle(self.screen, INK, (745, 290), 72, width=3)
        pygame.draw.circle(self.screen, SIGNAL, (745, 290), 32)
        pygame.draw.line(self.screen, INK, (710, 250), (780, 330), width=3)
        self.draw_text("The output adapter sends this voltage stream to macOS.", self.small_font, MUTED_INK, (480, 391))

    def draw_frequency_control(self) -> None:
        """Draw the slider that changes the oscillator's frequency input."""
        self.draw_text("Frequency input", self.heading_font, INK, (35, 462))
        self.draw_text(
            f"{self.oscillator.frequency_hz:.0f} Hz",
            self.heading_font,
            SIGNAL_DARK,
            (262, 462),
        )
        pygame.draw.rect(self.screen, GRID, self.slider_track, border_radius=4)
        fraction = (self.oscillator.frequency_hz - MINIMUM_FREQUENCY_HZ) / (
            MAXIMUM_FREQUENCY_HZ - MINIMUM_FREQUENCY_HZ
        )
        knob_x = round(self.slider_track.left + fraction * self.slider_track.width)
        pygame.draw.circle(self.screen, SIGNAL, (knob_x, self.slider_track.centery), 10)
        self.draw_text("20 Hz", self.small_font, MUTED_INK, (54, 483))
        self.draw_text("1,000 Hz", self.small_font, MUTED_INK, (326, 483))

    def draw_buttons(self) -> None:
        """Draw the controls that request samples and reset oscillator state."""
        buttons = [self.run_button, self.step_button, self.reset_button]
        for button in buttons:
            is_active = button is self.run_button and self.is_running
            fill = BUTTON_ACTIVE_FILL if is_active else BUTTON_FILL
            pygame.draw.rect(self.screen, fill, button.rectangle, border_radius=5)
            pygame.draw.rect(self.screen, INK, button.rectangle, width=1, border_radius=5)
            label = "Pause" if button is self.run_button and self.is_running else button.label
            text = self.body_font.render(label, True, INK)
            text_rectangle = text.get_rect(center=button.rectangle.center)
            self.screen.blit(text, text_rectangle)

    def draw_text(
        self, text: str, font: pygame.font.Font, color: tuple[int, int, int], position: tuple[int, int]
    ) -> None:
        """Draw text at the given position."""
        self.screen.blit(font.render(text, True, color), position)


def main() -> None:
    """Open the oscillator view."""
    OscillatorView().run()


if __name__ == "__main__":
    main()
