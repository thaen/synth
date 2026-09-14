# Lesson 2 changes a signal's size.

Lesson 1 made a sine wave at A4, which repeats 440 times each second. This lesson keeps that source and the Audio Output panel. It puts a Gain module between them, so the same tone can have a smaller or larger signal.

Run the terminal lesson from the project directory.

```sh
python3 src/terminal_view.py --lesson 2
```

Press `b` to start A4. Use the right arrow to select Gain, then use the up and down arrows to change its control. The control starts at `0.50` and moves from `0.00` through `1.00` in steps of `0.05`.

```text
+-------------------+      +-------------------+      +------------------+
| SINE WAVE CREATOR |----->| GAIN              |----->| AUDIO OUTPUT     |
| Frequency  440 Hz |      | Gain  0.50        |      | To system sound  |
| State: active     |      | Signal [####....] |      | State: active    |
+-------------------+      +-------------------+      +------------------+
```

## The signal has amplitude.

The digital model represents sound as a sequence of numbers. A sine wave moves above and below zero. Its amplitude is the size of each value, or how far the wave reaches from zero.

The oscillator in this lesson still makes the same wave at the same frequency. The Gain module changes the size of that wave after the oscillator makes it. The signal meter shows the magnitude of the signal leaving Gain at the current sample time.

## Gain multiplies amplitude.

Gain is a multiplier that changes amplitude. A gain of `1.00` leaves every signal value unchanged. A gain of `0.50` makes each value half as large, and `0.00` changes every value to zero.

For one sample, the lesson follows this rule.

```text
gain output sample = oscillator sample × gain
```

For example, an oscillator sample of `0.80` becomes `0.40` when gain is `0.50`. The same sample becomes `0.00` when gain is `0.00`.

The signal meter becomes shorter as the gain setting falls, although it also moves with the sine wave. A sine wave reaches zero twice during each cycle, so the meter briefly reaches zero even when the gain setting is above zero.

## Listening has related words.

Amplitude describes the size of a signal value in the model. Gain describes the multiplication that changes that size. Loudness is what a person perceives, and volume is a listening control. These words are related, but they describe different parts of the lesson.

The Audio Output module still sends the completed signal to the computer's selected output device. A speaker can be one device after that boundary.

## The board evaluates the new path in order.

At each sample time, the oscillator writes a sine-wave value to its output jack. The first cable carries that value to Gain. Gain multiplies the value, writes the result to its output jack, and the second cable carries the result to Audio Output.

The [Lesson 2 configuration](../src/lessons/lesson_02.py) declares the three panels and both cables. The [Gain module](../src/synth/gain.py) owns the control and multiplication rule. The [terminal view](../src/synth/terminal.py) reads the meter that the lesson declares, so it has no Lesson 2-specific signal code.

Press `r` to restore gain to `0.50` and stop the tone. The reset returns the oscillator phase to its starting point and restores the gain control to `0.50`.
