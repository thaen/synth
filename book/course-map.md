# This Course Grows One Board Through Lesson Configurations.

The course has one board viewer: `python3 src/view.py --lesson NUMBER`. Each lesson has one configuration file in `src/lessons/`. A configuration mounts modules, sets their front-panel controls, and patches their jacks. The viewer reads that configuration and draws its board without lesson-specific display code.

The digital model uses numbers as sampled voltages. A module writes a voltage to an output jack, a cable carries that voltage, and another module reads the voltage at its input jack. The sound-output adapter sits after the audio-output module and sends the final voltage stream to macOS.

## The First Board Has One Signal Path.

```text
[Sine oscillator at 440 Hz] ── audio cable ──> [Audio output] ──> speaker
```

Lesson 1 supplies this two-module configuration. The oscillator produces audio voltage, and the audio-output module receives it.

## Each Lesson Adds One Physical Part.

1. Lesson 1 adds the sine oscillator and its audio cable to the audio output.
2. Lesson 2 adds the pitch-control module and its control-voltage cable to the oscillator.
3. Lesson 3 will add a musical pitch-control module that produces voltages for named notes.
4. Lesson 4 will add a second oscillator and a mixer module.
5. Lesson 5 will add a level-control module between the mixer and audio output.
6. Lesson 6 will add an envelope generator and its control-voltage cable.
7. Lesson 7 will add a filter module to the audio cable path.
8. Lesson 8 will add a low-frequency oscillator and its control cable.
9. Lesson 9 will add a gate-control module and form one playable voice.
10. Lesson 10 will add a sequencer module that creates timed pitch and gate voltages.

## The Code Keeps the Physical Parts Separate.

`patch.py` contains jacks and cables. `controls.py` contains front-panel knobs. `oscillator.py`, `pitch_control.py`, and `output.py` contain the current physical modules. `board.py` advances a mounted board on its sample clock. Each file in `src/lessons/` provides one completed board configuration. `view.py` displays every configuration with the same interface.
