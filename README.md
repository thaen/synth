# This Project Builds Digital Instruments from First Principles.

This project builds one digital instrument board from small modules, jacks, and patch cables. Each lesson has a runnable Python program and a chapter that explains the board in plain terms.

Python is the teaching language because its standard library can make a WAV file without installing a package. On macOS, `afplay` sends that file to the selected sound output device. The physical-style instrument modules live in `src/synth/`, while `synth.audio_output` keeps the device boundary separate from the board. The board display uses Pygame, which is listed in `requirements.txt`.

## The Lessons Build One Instrument Layer at a Time.

1. [Lesson 1: Producing a Tone](book/lesson-01-producing-a-tone.md) generates A4, the 440 Hz concert A.
2. [Lesson 2: Adding Pitch Control](book/lesson-02-oscillator.md) mounts a pitch-control module and its control-voltage cable.
3. [The course map](book/course-map.md) records the module, jack, and cable order for the growing board.

The Pygame board display is `src/view.py`. The terminal board is `src/terminal_view.py`. Each view loads the requested configuration from `src/lessons/` and reads the modules, jacks, cables, and front-panel controls that the configuration supplies.

## You Can Run the Lesson Programs.

Run the program from this directory.

```sh
python3 -m pip install --user -r requirements.txt
python3 src/lesson_01_tone.py
python3 src/lesson_02_oscillator.py
python3 src/view.py --lesson 1
python3 src/view.py --lesson 2
python3 src/terminal_view.py --lesson 1
```

The two audio programs write three seconds of A4 to `output/` and start `afplay`, which plays the file through macOS's selected sound output device. The board display loads the same lesson configuration as the matching audio program. The WAV files are derived output and are not stored in Git.

The terminal program uses `sounddevice` only after `b` requests audio. A missing device leaves the terminal interface open and reports its status. The terminal controls are `Left` and `Right` for selection, `Up` and `Down` for the selected lesson control, `b` for audio, `r` for reset, `?` for help, and `q` for quit.
