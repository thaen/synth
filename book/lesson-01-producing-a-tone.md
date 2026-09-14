# Lesson 1 Produces a Steady Tone.

The first board produces a steady A4 tone, which repeats 440 times each second. A4 is the musical A at 440 Hz. A tone at 40 Hz would be much lower and would not be the usual A reference.

An instrument board is a surface that holds electronic parts. Each part is a module. A module has connection points called jacks, and a patch cable plugs an output jack into an input jack.

The first board has a sine oscillator, an audio-output module, and one patch cable.

```text
+---------------------------+       patch cable       +---------------------------+
| SINE OSCILLATOR           |------------------------>| AUDIO OUTPUT              |
| Base frequency: 440 Hz    |   changing voltage      | Audio input               |
| Sine output jack          |                         | Monitor level: 0.25       |
+---------------------------+                         +---------------------------+
```

## The Oscillator Produces a Repeating Voltage.

The sine oscillator produces a repeating electrical pattern called a sine wave. The pattern rises smoothly from zero to a positive peak, returns to zero, falls to a negative peak, and returns to zero. One complete rise and fall is one cycle.

The oscillator's base frequency is 440 Hz, so it makes 440 cycles each second. In this digital model, one number represents the voltage at one instant. At every sample time, the oscillator places its next voltage on the jack named `Sine output`.

The board has 44,100 sample times each second. The audio adapter converts the resulting stream of numbers to an electrical signal, and a speaker converts that changing electrical signal to motion and air pressure.

## The Cable Carries Voltage Between the Modules.

The cable plugs from the oscillator's `Sine output` jack to the audio-output module's `Audio input` jack. A physical patch cable is a conductor. It does not determine the meaning of the voltage that it carries.

The oscillator makes a voltage that changes at an audio rate. The audio-output module interprets the voltage at its input as a signal to send toward the audio adapter. Those module roles make this cable part of an audio path.

The audio-output module has a monitor-level control set to 0.25. It multiplies the incoming voltage by 0.25 before the audio adapter receives it. That visible control keeps the first tone at a restrained level.

```text
oscillator output voltage → patch cable → audio-output voltage → audio adapter → speaker
```

## The Code Follows the Board.

The [Lesson 1 configuration](../src/lessons/lesson_01.py) mounts the sine oscillator and audio output, then patches their two jacks. The [board code](../src/synth/board.py) follows the cable direction when it advances modules at each sample time. The [audio program](../src/lesson_01_tone.py) loads the configuration, asks the board for samples, and sends the final samples to the audio adapter.

The configuration, board, and audio program are the three files to read in that order. Each file has one role: describe the physical patch, advance the mounted modules, and deliver completed audio samples.

## The Generic Viewer Loads This Board.

The board viewer is one program for the whole course. It imports a lesson configuration by number, then draws the modules, jacks, cables, controls, and panel state that the configuration supplies.

Run these commands from the project directory:

```sh
python3 -m pip install --user -r requirements.txt
python3 src/view.py --lesson 1
```

The viewer shows the first board's two modules and one patch cable on a board with open space around them. The Run control advances the complete board in groups of ten samples, and the audio-output voltage display shows the voltage currently arriving through the cable.

## You Can Hear the First Board.

Run this command from the project directory:

```sh
python3 src/lesson_01_tone.py
```

The program loads the same Lesson 1 configuration, requests 132,300 samples from its board, writes three seconds of A4 to `output/lesson-01-a4.wav`, and plays the file through the selected macOS sound device.

The next lesson adds a pitch-control module and one patch cable to this board.
