# Lesson 3 selects pitch with semitone steps.

Lesson 2 sends the sine wave through Gain before Audio Output. Lesson 3 keeps that audio path and adds a Pitch panel. Its control cable reaches the Sine Wave Creator's Pitch input.

Run the terminal lesson from the project directory.

```sh
python3 src/terminal_view.py --lesson 3
```

Press `b` to start the sine tone. The Pitch panel is selected first. Use the up and down arrows to move one semitone at a time. The panel starts at A4, `440.00 Hz`. Three upward steps select C5, `523.25 Hz`. Use the arrows to select Gain when you want to change the signal size.

```text
+-----------------+   +-----------------------+   +----------------+   +------------------+
| PITCH           |-->| SINE WAVE CREATOR     |-->| GAIN           |-->| AUDIO OUTPUT     |
| A4  440.00 Hz   |   | Pitch input A4 440 Hz |   | Gain 0.50      |   | To system sound  |
| Semitones 0 st  |   | State: active         |   | State: active  |   | State: active    |
+-----------------+   +-----------------------+   +----------------+   +------------------+
```

## Pitch and frequency describe related parts of the tone.

Frequency is the number of repeating cycles each second. Hertz, written Hz, is the unit for that rate. Pitch is the musical perception associated with frequency for a steady repeating tone.

The Sine Wave Creator repeats faster when the frequency rises. The tone then has a higher pitch. The Gain control stays at `0.50`, so the lesson changes the repetition rate while the gain remains fixed.

## A semitone is one equal step.

An octave has twelve equal semitone steps. Moving up twelve semitones doubles the frequency. A4 is `440 Hz`, A5 is `880 Hz`, and A3 is `220 Hz`.

The pitch control follows this rule, where the step count is measured from A4.

```text
frequency = 440 × 2^(semitones / 12)
```

One upward step from A4 selects A#4 at about `466.16 Hz`. Three upward steps select C5 at about `523.25 Hz`. The note name and frequency appear together so that each semitone step has a musical name and a measured rate.

## The control path changes the oscillator.

The Pitch panel turns semitone steps into a one-volt-per-octave control voltage. Twelve semitones become one volt, which makes the oscillator double its base frequency. This control cable carries pitch information. It does not carry the audio signal.

The audio cables remain `oscillator -> gain -> audio output`. At each sample time, the pitch control writes its voltage first. The oscillator reads that voltage, makes its sine-wave sample, and Gain multiplies the sample before Audio Output receives it.

The [Lesson 3 configuration](../src/lessons/lesson_03.py) declares the four panels and three cables. The [Pitch control](../src/synth/pitch_control.py) converts semitones into voltage and names the selected note. The [terminal view](../src/synth/terminal.py) reads the lesson data without Lesson 3 rules.

Press `r` to stop audio and return to A4 at `440.00 Hz`. The reset also restores Gain to `0.50` and the oscillator phase to the start of its cycle.
