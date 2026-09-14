# Lesson 2 Builds a Repeating Sound Source.

Lesson 1 made one tone by calculating every number in advance. The program knew that it needed three seconds of A4, calculated all 132,300 sample values, saved them in a file, and played the file. That method works, but it does not yet describe a useful instrument. An instrument needs to keep making sound while a player changes the pitch, holds a key, or turns a knob.

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

The program uses the word *module* for one small, named part that has one job and a clear connection to other parts. The `SineOscillator` module has one job: it makes the next value of a sine wave. It does not know about WAV files, speakers, note names, filters, or loudness controls.

This separation has a practical result. A later sound-combining part can ask any sound-source module for its next sample. It will not need to know whether that source is a sine wave, a square wave, or something else. The modules can change inside, as long as they keep the same simple connection.

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

The oscillator produces values from `-1.0` to `1.0`. The lesson program multiplies each value by `MONITOR_LEVEL`, which is 0.25, before it sends the values to the output code. This keeps the first playback at a restrained level. It is not yet a modeled amplifier; a later lesson will make level control into its own module.

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

The audio output code is separate because it is not part of the synthesizer lesson. Its job is only to move completed samples to the Mac's sound device. The oscillator is the new instrument part in this lesson.

## You Can Run and Change the Lesson.

Run this command from the project directory:

```sh
python3 src/lesson_02_oscillator.py
```

Change `FREQUENCY_HZ` from `440.0` to `220.0`, then run the program again. The waveform now repeats 220 times per second, so the sound is one octave lower. Change it to `880.0` for one octave higher.

The next lesson will give musicians a way to name these frequencies without changing the oscillator itself.
