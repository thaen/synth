# Lesson 1 Explains How a Program Produces a Tone.

Sound is a change in air pressure over time. A speaker moves back and forth in response to a stream of numbers, which makes those pressure changes. A digital instrument begins by preparing that stream.

This lesson makes concert A, called A4, at 440 hertz. Hertz means cycles per second, so the speaker moves through 440 complete back-and-forth cycles each second. A tone at 40 Hz would be much lower; it is close to the low end of human hearing and is not the usual musical A reference.

## The Primitive Is a Sine Wave.

The program uses a sine wave. A sine wave has one smooth cycle, and it is the simplest useful model of a pure tone. Its sample value at time `t` is:

```
sample(t) = amplitude × sin(2π × frequency × t)
```

The frequency is 440. The amplitude is 0.25, which keeps the generated samples well below the format's largest value. The program uses a sample rate of 44,100 samples per second, so it evaluates the formula 44,100 times for every second of sound.

For sample number `n`, the time is `n / 44100`. The first 3 seconds therefore have 132,300 samples. Each resulting decimal is scaled into a 16-bit signed integer, because the WAV file stores integers rather than Python decimal values.

## The Signal Path Moves Samples to the Speaker.

```
frequency and duration
          |
          v
sine-wave equation for each sample
          |
          v
16-bit PCM values in a WAV file
          |
          v
afplay and the selected macOS output device
          |
          v
speaker motion and an audible 440 Hz tone
```

The WAV file is a container around the PCM values. PCM, or pulse-code modulation, is a direct list of speaker positions measured at fixed times. In this lesson there is one channel, so the same simple stream represents one mono sound source. The `synth.audio_output` module now holds WAV writing and macOS playback, so later lessons can focus on instrument modules.

## You Can Run the Program.

From the project directory, run:

```sh
python3 src/lesson_01_tone.py
```

The program writes the audio data, then starts `afplay`. That macOS program opens the sound device that macOS has selected and plays the WAV file. Headphones or speakers must be connected, and the system output volume must be audible.

The program uses a file instead of a pipe in this lesson because the file makes the PCM data inspectable and reusable. A later real-time lesson can keep an audio buffer in memory and send buffers continuously to an audio engine.

## These Experiments Change the Tone.

Change `FREQUENCY` from `440.0` to `220.0`. The result is A3, one octave lower, because halving a frequency lowers a note by one octave. Change it to `880.0` for A5, one octave higher.

Change `AMPLITUDE` between `0.0` and `1.0`. This number is the source level, not necessarily the perceived loudness, because human hearing and the sound device both affect perceived loudness. Values above `1.0` would exceed the 16-bit range after scaling, so later lessons will explain safe mixing and clipping.

## This Lesson Has Deliberate Limits.

This program does not respond to a keyboard, schedule notes, retain a loop, or run continuously. It makes a fixed buffer before playback. Those limits keep the first primitive visible: a digital sound is a sequence of samples.

The next lesson will combine several sample streams, which is the basis for chords and many layers of an instrument.
