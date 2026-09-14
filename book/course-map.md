# This Course Grows One Physical-Style Synth Board.

The course keeps one board visible from the first tone through the finished instrument. A lesson adds a module, a front-panel control, or a patch cable to that board. It does not replace the board with a separate program.

The digital model uses numbers as sampled voltages. A module writes a voltage to an output jack, a cable carries that voltage, and another module reads the voltage at its input jack. The sound-output adapter sits after the speaker-output module and delivers the final voltage stream to macOS.

## The First Board Has One Signal Path.

```text
[Sine oscillator at 440 Hz] ── patch cable ──> [Speaker output] ──> speaker
```

The oscillator produces the audio voltage. The cable carries it. The speaker-output module receives it. This path remains in place as the board grows.

## The Board Will Grow in This Order.

1. Lesson 1 mounts the fixed 440 Hz sine oscillator and patches it to the speaker output.
2. Lesson 2 makes the oscillator's frequency setting visible and adjustable.
3. Lesson 3 adds a musical pitch controller that sets oscillator frequency from note names.
4. Lesson 4 mounts a second oscillator and adds a mixer module with two input jacks and one output jack.
5. Lesson 5 adds a level-control module between the mixer and speaker output.
6. Lesson 6 adds an envelope generator and patches its control voltage to the level-control module.
7. Lesson 7 adds a filter module to the audio cable path.
8. Lesson 8 adds a low-frequency oscillator and patches its control voltage to another module's setting.
9. Lesson 9 turns the board into one playable voice with pitch and gate controls.
10. Lesson 10 adds a sequencer that creates timed pitch and gate signals.
11. Later boards add more voices, loops, delay, and other effects with the same modules, jacks, and cables.

## The Code Preserves the Physical Boundaries.

Each physical part has a small corresponding file. `patch.py` contains jacks and cables. `oscillator.py` contains the sine oscillator. `output.py` contains the speaker-output module. `board.py` contains the mounted board and its sample clock. `first_board.py` records the current physical patch.

Lesson programs configure the current board and ask it for samples. The display reads that same board and draws its mounted modules, front-panel settings, jacks, and cables.
