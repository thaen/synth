# This Course Builds a Reusable Instrument One Module at a Time.

This course uses digital code to model the signal flow of an analog modular synthesizer. Each lesson adds one idea, preserves the earlier lesson programs, and moves reusable behavior into the `src/synth/` package only after the lesson has made that behavior clear.

## The Project Uses Stable Module Boundaries.

An audio module produces normalized samples between `-1.0` and `1.0`. Its public operation is `next_sample()`, which returns one new sample each time it is called. A later mixer, filter, amplifier, and effect can use that same operation without knowing which oscillator produced the sample.

The `synth.audio_output` module is an output adapter. It converts completed samples into a WAV file and gives that file to macOS. It does not contain instrument behavior. A later real-time adapter can replace it while leaving the audio modules unchanged.

Each lesson program is a short patch that connects the modules introduced so far. A lesson program may set parameters and collect samples, but it should not duplicate module logic from an earlier lesson.

## The Course Adds These Modules in Order.

1. Lesson 1 makes one fixed sine-wave tone from the sample equation.
2. Lesson 2 turns that equation into a reusable sine oscillator with frequency, phase, and sample rate.
3. Lesson 3 will map note names to oscillator frequencies.
4. Lesson 4 will mix two oscillators into one signal.
5. Lesson 5 will add a gain stage and safe level handling.
6. Lesson 6 will use an envelope to control a gain stage over time.
7. Lesson 7 will add a low-pass filter.
8. Lesson 8 will add an LFO that controls another module.
9. Lesson 9 will assemble one playable voice from the modules.
10. Lesson 10 will schedule control events with a sequencer.
11. Later lessons will add polyphony, looping, delay, and other effects.

The output adapter remains outside the instrument signal path throughout the course.
