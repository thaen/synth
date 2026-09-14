# Lesson 2 Controls an Oscillator's Pitch.

Lesson 2 keeps the sine oscillator, audio output, and audio cable from Lesson 1. It adds one new physical part: a pitch-control module. This module makes a voltage whose job is to set the oscillator's pitch.

```text
+------------------+  control cable  +---------------------------+   audio cable   +------------------+
| PITCH CONTROL    |---------------->| SINE OSCILLATOR           |---------------->| AUDIO OUTPUT     |
| Pitch knob       |  pitch voltage  | Pitch input               | audio voltage  | Audio input      |
| Pitch output     |                 | Sine output               |                | Monitor level    |
+------------------+                 +---------------------------+                +------------------+
```

The control cable carries control voltage. The audio cable carries audio voltage. Both are changing electrical values, but they have different jobs on this board. Control voltage sets a module parameter. Audio voltage travels toward the audio output and becomes sound.

## An Octave Doubles or Halves Frequency.

An octave is the interval between two tones whose frequencies have a ratio of two. A tone at 880 Hz is one octave above a tone at 440 Hz because 880 is twice 440. A tone at 220 Hz is one octave below 440 Hz because 220 is half 440.

The pitch-control module uses a common analog-synthesizer convention called one volt per octave. Its pitch knob produces control voltage. Raising the knob by one volt doubles the oscillator frequency. Lowering it by one volt halves the oscillator frequency.

```text
-1 V → 220 Hz → A3
 0 V → 440 Hz → A4
+1 V → 880 Hz → A5
```

The oscillator starts with a base frequency of 440 Hz. It calculates its current frequency with this rule:

```text
frequency = 440 × 2^(pitch voltage)
```

## The New Cable Changes the Oscillator Before It Makes Audio.

At every sample time, the pitch-control module places its knob voltage on `Pitch output`. The control cable carries that voltage to the oscillator's `Pitch input`. The oscillator reads the control voltage, calculates its frequency, and places a sine-wave voltage on `Sine output`. The retained audio cable then carries that voltage to the audio-output module.

The board derives this evaluation order from the direction of the two cables. The physical position of a module in the viewer therefore does not decide when its voltage is calculated.

## The Code Extends the Existing Board.

The [Lesson 2 configuration](../src/lessons/lesson_02.py) starts with the Lesson 1 board, mounts a `PitchControl` module, and patches one control cable to the existing oscillator. The [pitch-control code](../src/synth/pitch_control.py) owns the knob and output jack. The existing [oscillator code](../src/synth/oscillator.py) reads the new input jack.

The [generic viewer](../src/view.py) reads only module-provided jacks, controls, and panel state. It does not contain Lesson 2-specific drawing code.

## You Can See the Larger Board.

Run this command from the project directory:

```sh
python3 src/view.py --lesson 2
```

The command starts the same `view.py` program used by Lesson 1. The Lesson 2 configuration supplies one extra module and one extra cable, so the board has three visible modules and two visible cables. Drag or click the Pitch knob to change its voltage. The oscillator panel then shows the frequency that the control voltage produces.

## You Can Hear the Lesson 2 Board.

Run this command from the project directory:

```sh
python3 src/lesson_02_oscillator.py
```

The program loads the same Lesson 2 configuration and plays its default zero-volt setting, which is A4 at 440 Hz.

The next lesson will add a musical control that produces the pitch voltages for named notes.
