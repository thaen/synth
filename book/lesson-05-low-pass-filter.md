# Lesson 5 changes brightness with a low-pass filter.

Lesson 5 keeps the Pitch, Oscillator, Gain, and Audio Output panels from Lesson 4. It places a Low-Pass Filter after Gain and before Audio Output. The Oscillator starts as a sawtooth at A4, `440.00 Hz`, because its harmonics make the filter change easy to hear.

## You can change the cutoff.

Press `b` to start the sawtooth. Use the right arrow until Low-Pass Filter is selected, then use the up and down arrows to change Cutoff. The control starts at `12000 Hz` and reaches `200 Hz` at its lowest setting. Each key press changes the cutoff by one equal-tempered semitone ratio, so the frequency changes by a fixed musical proportion instead of a fixed number of hertz.

| Pitch A4 440 Hz |   | Sawtooth 440 Hz |   | Gain 0.50 |   | Cutoff 12000 Hz |   | To system sound |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

The filter panel has a response trace. Its left side represents lower frequencies, and its right side represents higher frequencies. A higher trace means that more of that frequency can pass through the filter. Lower cutoff settings move the falling part of the trace to the left.

## A filter changes components that already exist.

A waveform can contain several frequency components. The lowest repeating component of this sawtooth is its fundamental at `440 Hz`. Its harmonics are components above that fundamental.

The Low-Pass Filter changes the balance of those components after Gain has made the signal. Frequencies below cutoff pass more readily. Frequencies above cutoff become quieter. At `12000 Hz`, the sawtooth is close to its open state. At `200 Hz`, many of its harmonics have been reduced, and the sound is darker.

Brightness and darkness are listening descriptions for this change in frequency balance. They are not separate physical controls. Cutoff is the boundary frequency that controls where the reduction begins.

## The board evaluates the filter after Gain.

At each sample time, Pitch writes its control value. Oscillator reads it and makes a sawtooth sample. Gain scales that sample, Low-Pass Filter processes it, and Audio Output receives the result.

```text
oscillator -> gain -> low-pass filter -> audio output
```

The [Lesson 5 configuration](../src/lessons/lesson_05.py) declares the panels, controls, cables, and response trace. The [Low-Pass Filter module](../src/synth/low_pass_filter.py) owns the cutoff mapping and one-pole filtering rule. The [terminal view](../src/synth/terminal.py) reads the declared panel data, so it has no filter-specific drawing or control rule.

This filter has one control: cutoff. Resonance changes behavior near cutoff, so the course introduces it in a later lesson. Press `r` to stop audio and restore Sawtooth, A4 at `440.00 Hz`, Gain at `0.50`, and Cutoff at `12000 Hz`.
