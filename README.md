# This Project Builds Digital Instruments from First Principles.

This project builds small digital instruments from generated audio samples. Each lesson has a runnable Python program and a chapter that explains the program in plain terms.

Python is the teaching language because its standard library can make a WAV file without installing a package. On macOS, `afplay` sends that file to the selected sound output device. Later lessons can keep the sound rules and exchange this file-based output path for a real-time audio path.

## The Lessons Build One Instrument Layer at a Time.

1. [Producing a Tone](book/lesson-01-producing-a-tone.md) generates A4, the 440 Hz concert A.
2. Multiple notes will mix several generated waves into one stream.
3. Level control will scale sample values and introduce clipping.
4. A note envelope will control attack, sustain, and release.
5. A sequencer will schedule notes against a clock.
6. Loops and effects will transform the generated stream.

## You Can Run the First Lesson.

Run the program from this directory.

```sh
python3 src/lesson_01_tone.py
```

The program writes three seconds of A4 to `output/lesson-01-a4.wav` and starts `afplay`, which plays the file through macOS's selected sound output device. The WAV file is derived output and is not stored in Git.
