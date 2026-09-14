"""Show the state and output of the Lesson 2 sine oscillator."""

import tkinter as tk
from math import pi, sin

from synth.oscillator import SineOscillator


SAMPLE_RATE = 44_100
DEFAULT_FREQUENCY_HZ = 440.0
CANVAS_WIDTH = 900
CANVAS_HEIGHT = 560
GRAPH_LEFT = 390
GRAPH_TOP = 85
GRAPH_WIDTH = 460
GRAPH_HEIGHT = 300
ANIMATION_DELAY_MILLISECONDS = 35


class OscillatorView:
    """This window shows one oscillator and the waveform it produces."""

    def __init__(self, root: tk.Tk) -> None:
        """Create the window and its controls."""
        self.root = root
        self.root.title("Lesson 2: The Sine Oscillator")
        self.root.resizable(False, False)

        self.oscillator = SineOscillator(DEFAULT_FREQUENCY_HZ, SAMPLE_RATE)
        self.last_sample = 0.0
        self.is_running = False
        self.frequency_hz = tk.DoubleVar(value=DEFAULT_FREQUENCY_HZ)

        self.canvas = tk.Canvas(
            root,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            background="#f8f5ee",
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, columnspan=4, padx=18, pady=(18, 8))

        self.frequency_scale = tk.Scale(
            root,
            from_=20,
            to=1_000,
            resolution=1,
            orient=tk.HORIZONTAL,
            length=360,
            label="Frequency in hertz",
            variable=self.frequency_hz,
            command=self.change_frequency,
        )
        self.frequency_scale.grid(row=1, column=0, columnspan=2, padx=(18, 6), pady=8)

        self.run_button = tk.Button(root, text="Run", width=10, command=self.toggle_run)
        self.run_button.grid(row=1, column=2, padx=6, pady=8)
        tk.Button(root, text="Step one sample", width=16, command=self.step).grid(
            row=1, column=3, padx=(6, 18), pady=8
        )
        tk.Button(root, text="Reset phase", width=14, command=self.reset).grid(
            row=2, column=0, columnspan=2, pady=(0, 18)
        )
        tk.Label(
            root,
            text="The display advances one audio sample per visible step, so phase is easy to see.",
        ).grid(row=2, column=2, columnspan=2, padx=(6, 18), pady=(0, 18))

        self.draw()

    def change_frequency(self, _value: str) -> None:
        """Set the oscillator frequency from the frequency control."""
        self.oscillator.frequency_hz = self.frequency_hz.get()
        self.draw()

    def step(self) -> None:
        """Request one sample from the oscillator and redraw the window."""
        self.last_sample = self.oscillator.next_sample()
        self.draw()

    def reset(self) -> None:
        """Return the oscillator to the first position of its waveform."""
        self.oscillator.reset()
        self.last_sample = 0.0
        self.draw()

    def toggle_run(self) -> None:
        """Start or stop visible sample-by-sample motion."""
        self.is_running = not self.is_running
        self.run_button.configure(text="Pause" if self.is_running else "Run")
        if self.is_running:
            self.animate()

    def animate(self) -> None:
        """Advance the oscillator once and schedule the next visible step."""
        if not self.is_running:
            return
        self.step()
        self.root.after(ANIMATION_DELAY_MILLISECONDS, self.animate)

    def draw(self) -> None:
        """Draw the module, its signal connection, and its waveform."""
        self.canvas.delete("all")
        self.draw_title()
        self.draw_module()
        self.draw_connection()
        self.draw_waveform()

    def draw_title(self) -> None:
        """Draw the window title and the meaning of its visual language."""
        self.canvas.create_text(
            26,
            24,
            anchor="w",
            text="A sine oscillator makes one new sample whenever it receives a request.",
            font=("Helvetica", 18, "bold"),
            fill="#172f3b",
        )
        self.canvas.create_text(
            26,
            52,
            anchor="w",
            text="The dot marks the oscillator's present position in one waveform cycle.",
            font=("Helvetica", 11),
            fill="#4a5960",
        )

    def draw_module(self) -> None:
        """Draw the oscillator as a physical instrument part."""
        left, top, right, bottom = 35, 120, 330, 405
        self.canvas.create_rectangle(
            left, top, right, bottom, fill="#dce8e7", outline="#172f3b", width=2
        )
        self.canvas.create_text(
            (left + right) / 2,
            top + 34,
            text="SINE OSCILLATOR",
            font=("Helvetica", 16, "bold"),
            fill="#172f3b",
        )
        self.canvas.create_line(left + 18, top + 58, right - 18, top + 58, fill="#7d9292")

        phase_step = self.oscillator.frequency_hz / self.oscillator.sample_rate
        rows = [
            ("INPUT", f"frequency: {self.oscillator.frequency_hz:.0f} Hz"),
            ("INPUT", f"sample rate: {self.oscillator.sample_rate:,} per second"),
            ("STATE", f"phase: {self.oscillator.phase_cycles:.5f} cycles"),
            ("OUTPUT", f"last sample: {self.last_sample:+.5f}"),
            ("STEP", f"phase advance: {phase_step:.5f} cycles"),
        ]
        y = top + 84
        for label, value in rows:
            self.canvas.create_text(
                left + 20, y, anchor="w", text=label, font=("Helvetica", 9, "bold"), fill="#4a5960"
            )
            self.canvas.create_text(
                left + 20, y + 18, anchor="w", text=value, font=("Helvetica", 12), fill="#172f3b"
            )
            y += 42

    def draw_connection(self) -> None:
        """Draw the path from the oscillator output to the waveform display."""
        y = 262
        self.canvas.create_line(330, y, GRAPH_LEFT - 15, y, fill="#b54a36", width=3, arrow=tk.LAST)
        self.canvas.create_text(
            360,
            y - 18,
            text="one sample",
            font=("Helvetica", 10),
            fill="#8f3627",
        )

    def draw_waveform(self) -> None:
        """Draw two cycles of the sine-wave pattern and the current phase marker."""
        left, top = GRAPH_LEFT, GRAPH_TOP
        right, bottom = left + GRAPH_WIDTH, top + GRAPH_HEIGHT
        center_y = (top + bottom) / 2
        amplitude = GRAPH_HEIGHT * 0.37

        self.canvas.create_text(
            left,
            top - 20,
            anchor="w",
            text="The waveform that the oscillator follows",
            font=("Helvetica", 13, "bold"),
            fill="#172f3b",
        )
        self.canvas.create_rectangle(left, top, right, bottom, outline="#728487", width=1)
        self.canvas.create_line(left, center_y, right, center_y, fill="#a9b7b7", dash=(3, 3))

        points = []
        visible_cycles = 1
        for pixel in range(GRAPH_WIDTH + 1):
            cycle_position = visible_cycles * pixel / GRAPH_WIDTH
            x = left + pixel
            y = center_y - amplitude * sin(2 * pi * cycle_position)
            points.extend((x, y))
        self.canvas.create_line(points, fill="#b54a36", width=3, smooth=True)

        marker_x = left + (self.oscillator.phase_cycles % 1.0) * GRAPH_WIDTH
        marker_y = center_y - amplitude * sin(2 * pi * self.oscillator.phase_cycles)
        self.canvas.create_line(marker_x, top, marker_x, bottom, fill="#172f3b", dash=(4, 3))
        self.canvas.create_oval(
            marker_x - 7,
            marker_y - 7,
            marker_x + 7,
            marker_y + 7,
            fill="#172f3b",
            outline="#f8f5ee",
            width=2,
        )
        self.canvas.create_text(
            left + GRAPH_WIDTH / 2,
            bottom + 24,
            text="one complete waveform cycle",
            font=("Helvetica", 10),
            fill="#4a5960",
        )


def main() -> None:
    """Open the oscillator view."""
    root = tk.Tk()
    OscillatorView(root)
    root.mainloop()


if __name__ == "__main__":
    main()
