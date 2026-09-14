# Lesson 2 Turns a Tone Formula into an Oscillator.

An oscillator is a module that produces a repeating signal. Lesson 1 evaluated the sine-wave equation directly for every sample. This lesson puts the same rule inside `SineOscillator`, which provides one sample whenever another part of the instrument asks for one.

## The Oscillator Has Three Pieces of State.

The oscillator has a frequency, a sample rate, and a phase. The frequency says how many waveform cycles occur each second. The sample rate says how many opportunities the program has to describe those cycles each second. The phase says where the current sample lies within the waveform's cycle.

At 440 Hz and a 44,100 Hz sample rate, the oscillator advances by `440 / 44100` of one cycle for each sample. It then wraps phase back into the range from zero up to one cycle. This wrapping is why the output repeats.

```text
frequency and sample rate → phase step
phase → sine function → next normalized sample
phase plus phase step → next phase
```

The oscillator produces samples from `-1.0` through `1.0`. It does not set loudness. That separation matches the instrument model: an oscillator produces a signal, and a later amplifier module controls the signal's level.

## The Reusable Module Has a Small Interface.

`SineOscillator(frequency_hz, sample_rate)` creates the module. `next_sample()` returns one sample and advances its phase. `reset()` returns the phase to the start of the waveform.

The lesson program creates an oscillator, calls `next_sample()` 132,300 times, and sends those samples to the output adapter. The program contains no sine-wave calculation because that behavior belongs to the oscillator module.

## You Can Run the Oscillator Lesson.

Run this command from the project directory:

```sh
python3 src/lesson_02_oscillator.py
```

The program writes and plays three seconds of A4. Change `FREQUENCY_HZ` to `220.0` or `880.0` to hear the oscillator at one octave below or above A4.

## The Next Lesson Will Name Frequencies as Notes.

The oscillator only understands hertz. A musical interface needs a translation between a note name and a frequency, so the next lesson will add that translation without changing the oscillator.
