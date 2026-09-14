# Lesson 4 changes waveform and timbre.

Lesson 4 keeps the Pitch, Gain, and Audio Output panels from Lesson 3. The source panel is now named Oscillator, and it has a Waveform control.

Run the terminal lesson from the project directory.

```sh
python3 src/terminal_view.py --lesson 4
```

The Pitch panel is selected when the lesson opens. Its setting is A4 at `440.00 Hz`. Select Oscillator with the right arrow, then use the up and down arrows to choose Sine, Triangle, Square, or Sawtooth. The panel shows the waveform name, the selected frequency, and an ASCII trace of one cycle.

```text
+----------------+  +----------------+  +----------------+  +----------------+
| PITCH          |  | OSCILLATOR     |  | GAIN           |  | AUDIO OUTPUT   |
| A4  440.00 Hz  |  | Square 440 Hz  |  | Multiplies ... |  | To system sound|
| Semitones 0 st |  | Waveform Square|  | Gain 0.50      |  |                |
| State: ready   |  | State: idle    |  | State: waiting |  | State: silent  |
|                |  |********      * |  | Signal [...]   |  |                |
|                |  |       *      * |  |                |  |                |
|                |  |       *      * |  |                |  |                |
|                |  |       *      * |  |                |  |                |
|                |  |       ******** |  |                |  |                |
+----------------+  +----------------+  +----------------+  +----------------+
```

## A waveform is one repeated shape.

An oscillator repeats a waveform. The sine wave from the earlier lessons is smooth. A triangle rises and falls in straight lines. A square stays high, then low. A sawtooth rises in a ramp and returns to its starting level.

The trace is a small graph of one cycle. It shows shape rather than elapsed sound time. The oscillator uses one phase clock for every waveform, so waveform selection does not change the selected frequency.

## Timbre describes the difference in sound quality.

Pitch and level can stay fixed while the waveform changes. Timbre is the sound quality that lets those tones sound different.

A sine wave has one frequency component. Square and sawtooth waves have added frequency components called harmonics. Those extra components can make a sound seem brighter. Brightness is an informal description for more high-frequency energy, rather than a separate physical quantity.

The first comparison uses A4 at `440.00 Hz` and Gain at `0.50`. Waveform selection keeps both values unchanged. You can still use Pitch and Gain after comparing the four waveform choices.

At each sample time, Pitch writes its control value, Oscillator reads it and makes the selected waveform sample, Gain multiplies that sample, and Audio Output receives the result. The audio path remains `oscillator -> gain -> audio output`.

The [Lesson 4 configuration](../src/lessons/lesson_04.py) declares the Oscillator control and trace. The [oscillator](../src/synth/oscillator.py) owns the phase clock and waveform functions. The [terminal view](../src/synth/terminal.py) reads the declared trace without waveform rules.

Press `r` to stop audio and restore Sine, A4 at `440.00 Hz`, Gain at `0.50`, and the oscillator phase at the start of its cycle.
