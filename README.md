# This Project Builds Digital Instruments from First Principles.

This project builds small digital instruments from generated audio samples. Each lesson has a runnable Python program and a chapter that explains the program in plain terms.

Python is the teaching language because its standard library can make a WAV file without installing a package. On macOS, `afplay` sends that file to the selected sound output device. The instrument modules live in `src/synth/`, while `synth.audio_output` keeps the device boundary separate from the instrument. The visual laboratories use Pygame, which is listed in `requirements.txt`.

## The Lessons Build One Instrument Layer at a Time.

1. [Lesson 1: Producing a Tone](book/lesson-01-producing-a-tone.md) generates A4, the 440 Hz concert A.
2. [Lesson 2: Creating an Oscillator](book/lesson-02-oscillator.md) turns that tone rule into a reusable module.
3. [The course map](book/course-map.md) records the module order and code boundaries for the growing instrument.

The Lesson 2 view is in `src/lesson_02_view.py`. It shows the oscillator's inputs, stored phase, output sample, and waveform while using the same oscillator code as the audio lesson.

## You Can Run the Lesson Programs.

Run the program from this directory.

```sh
python3 -m pip install --user -r requirements.txt
python3 src/lesson_01_tone.py
python3 src/lesson_02_oscillator.py
python3 src/lesson_02_view.py
```

The two audio programs write three seconds of A4 to `output/` and start `afplay`, which plays the file through macOS's selected sound output device. The Lesson 2 view displays the same oscillator's state and waveform. The WAV files are derived output and are not stored in Git.
