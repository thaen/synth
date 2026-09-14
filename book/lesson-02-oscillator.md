# Lesson 2 Makes the Oscillator's Frequency Setting Visible.

Lesson 2 keeps the first board's two modules and its one patch cable. The board still has one sine oscillator connected directly to one speaker-output module. This lesson focuses on the oscillator's frequency setting, which determines how quickly its voltage repeats.

```text
+---------------------------+       patch cable       +---------------------------+
| SINE OSCILLATOR           |------------------------>| SPEAKER OUTPUT            |
| Frequency: 440 Hz         |      audio voltage      | Audio input               |
| Sine output jack          |                         | Speaker                   |
+---------------------------+                         +---------------------------+
```

The cable carries audio voltage. The frequency setting is a front-panel setting on the oscillator itself. It changes the voltage made by the oscillator before that voltage enters the cable.

## A Sine Oscillator Repeats One Shape.

A sine wave rises smoothly from zero to a positive peak, returns to zero, falls to a negative peak, and returns to zero. One complete rise and fall is a cycle. The shape made during one cycle is called a waveform.

The frequency tells the oscillator how many cycles to make each second. A 440 Hz setting makes 440 cycles in one second. A 220 Hz setting makes 220 cycles in one second, so its tone is one octave lower. An 880 Hz setting makes 880 cycles in one second, so its tone is one octave higher.

## The Oscillator Remembers Its Position.

The oscillator must remember where it is in the current cycle between sample times. That remembered position is called phase. A phase of `0.0` is the start of the cycle. A phase of `0.5` is halfway through the cycle. After a phase reaches one complete cycle, it returns to `0.0`.

The board uses 44,100 sample times each second. At a frequency of 440 Hz, the oscillator moves forward by this fraction of a cycle for every sample:

```text
440 / 44100 = 0.00998 cycles per sample
```

The `SineOscillator.advance()` operation places the voltage for its current phase on the sine-output jack, then advances phase by that amount. The cable always carries the voltage currently on its source jack.

## The Board Has a Physical-Style Code Model.

The [oscillator code](../src/synth/oscillator.py) has a `sine_output` jack. The [speaker-output code](../src/synth/output.py) has an `audio_input` jack. The [patch code](../src/synth/patch.py) connects those two jacks with a `PatchCable`. The [board code](../src/synth/board.py) advances the mounted modules and reads the voltage at the speaker module.

```text
SineOscillator.advance()
        |
        v
Sine output jack holds the current voltage
        |
        v
PatchCable carries that voltage
        |
        v
Speaker output reads its Audio input jack
```

The audio program and the board display use the same mounted-board setup from [first_board.py](../src/synth/first_board.py). The audio program asks the board for 132,300 samples and plays them. The board display advances the same board in groups of ten samples so its phase movement is visible.

## You Can Hear the Board at Different Frequencies.

Run this command from the project directory:

```sh
python3 src/lesson_02_oscillator.py
```

Change `FREQUENCY_HZ` in `src/lesson_02_oscillator.py` from `440.0` to `220.0`, then run the program again. The board retains the same modules and cable while the oscillator repeats more slowly.

## You Can See the Mounted Board.

Run these commands from the project directory:

```sh
python3 -m pip install --user -r requirements.txt
python3 src/lesson_02_view.py
```

The display shows the oscillator module, the speaker-output module, and the cable between their jacks. Its frequency control changes the oscillator setting. The Run control advances the board at a visible speed, Request 10 Samples advances it once, and Reset Phase returns the oscillator to the start of its cycle.

The next lesson will add a musical pitch control to the same board.
