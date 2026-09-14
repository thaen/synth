# Lesson 2 Builds a Repeating Sound Source.

Lesson 1 made one tone by calculating every number in advance. The program knew that it needed three seconds of A4, calculated all 132,300 sample values, saved them in a file, and played the file. This lesson focuses on the repeating source that makes those sample values.

This lesson changes one part of the first program. Instead of asking, "What is sample number 57?", the program keeps track of a repeating wave and answers a different question repeatedly: "What sample comes next?"

## A Sound Source Repeats a Pattern.

A sound source is anything that produces sound. In this program, a sound source is code that produces a sequence of numbers for a speaker over time. A sine wave is one particular sequence. Its values rise smoothly from zero to a positive peak, return to zero, fall to a negative peak, and return to zero. That complete rise and fall is one cycle. The shape made by the values during a cycle is called a waveform.

For a sine wave at 440 hertz, the cycle happens 440 times each second. The same pattern repeats, but the program must remember where it is in the current cycle. The position within one cycle is called phase.

Imagine a much slower wave that has four sample positions in each cycle. Its positions could look like this:

```text
phase in the cycle:   start   one quarter   halfway   three quarters   start again
sample value:           0          1           0          -1             0
```

Each request for a sample moves the wave forward by one position. A real 440 Hz sine wave has many more positions than this example, but it follows the same rule: use the current position, then move forward a small amount.

## A Module Is One Small Part with One Job.

An electronic synthesizer has separate physical parts. One part creates a repeating electrical signal. Another part changes its level. Another part can remove some of its high-frequency content. Musicians connect these parts with cables.

The program uses the word *module* for one small, named part that has one job and a clear connection to other parts. The `SineOscillator` module makes the next value of a sine wave. Its connection is the `next_sample()` operation: another part asks for one value, and the oscillator supplies it.

This separation keeps the connection simple. Code that needs a sound value asks for the next sample. The oscillator handles the phase calculation needed to supply that value.

## The Oscillator Remembers Its Position.

The `SineOscillator` code has three stored pieces of information.

`frequency_hz` is the number of cycles per second. The lesson uses 440.0, which is A4.

`sample_rate` is the number of samples made per second. The lesson uses 44,100.

`phase_cycles` is the current position in the waveform. A phase of `0.0` means the start of a cycle. A phase of `0.5` means halfway through it. A phase of `1.0` means the next cycle has begun, so the program wraps it back to `0.0`.

For every sample, the oscillator advances phase by this amount:

```text
frequency / sample rate
```

At 440 Hz and 44,100 samples per second, the amount is `440 / 44100`, or about 0.00998 of a cycle. The oscillator turns its present phase into a sine-wave value, adds that amount to the phase, wraps around after one whole cycle, and waits for the next request.

## The Program Uses the Oscillator One Sample at a Time.

The important line in the lesson program is:

```python
oscillator.next_sample()
```

That line asks the oscillator for one number. The lesson calls it 132,300 times because three seconds at 44,100 samples per second require 132,300 numbers.

The oscillator produces values from `-1.0` to `1.0`. The lesson program multiplies each value by `MONITOR_LEVEL`, which is 0.25, before it sends the values to the output code. This keeps playback at a restrained level.

## You Can Read the Complete Signal Path.

```text
SineOscillator
    makes one new sample when asked
            |
            v
lesson program
    asks for 132,300 samples and applies a fixed monitoring level
            |
            v
audio output code
    writes the samples to a WAV file and asks macOS to play it
            |
            v
speaker
    moves back and forth and makes a 440 Hz tone
```

The audio output code moves completed samples to the Mac's sound device. The oscillator supplies the values that begin the signal path.

## You Can Run and Change the Lesson.

Run this command from the project directory:

```sh
python3 src/lesson_02_oscillator.py
```

Change `FREQUENCY_HZ` from `440.0` to `220.0`, then run the program again. The waveform now repeats 220 times per second, so the sound is one octave lower. Change it to `880.0` for one octave higher.

## You Can Watch the Oscillator Work.

Run this command from the project directory:

```sh
python3 src/lesson_02_view.py
```

The window shows the oscillator module, its input values, its current phase, its most recent sample, and the waveform that those samples follow. The Run button advances the oscillator one audio sample at a time at a visible speed. The Step button advances it once, and the Reset button returns phase to the start of the cycle.

The next lesson will give musicians a way to name these frequencies without changing the oscillator itself.
