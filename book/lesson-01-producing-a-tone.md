# Lesson 1 Mounts a Board That Makes One Tone.

An instrument board is a surface that holds the electronic parts of an instrument. A single part on that board is called a module. A module has connection points called jacks, and a cable plugs one jack into another.

The first instrument board has two modules and one cable. A sine oscillator produces a repeating voltage, and a speaker-output module receives that voltage and sends it to the Mac's sound device.

```text
+---------------------------+       patch cable       +---------------------------+
| SINE OSCILLATOR           |------------------------>| SPEAKER OUTPUT            |
| Frequency: 440 Hz         |      audio voltage      | Audio input               |
| Sine output jack          |                         | Speaker                   |
+---------------------------+                         +---------------------------+
```

This board makes A4, the musical A at 440 Hz. A tone at 40 Hz would be much lower and would not be the usual A reference.

## A Module Is a Physical Part of the Board.

A module is one physical unit mounted on a synthesizer board. It has a particular job, front-panel controls, and connection points called jacks. The sine oscillator's job is to produce a voltage that follows the shape of a sine wave. The speaker-output module's job is to receive a voltage at its audio-input jack and pass it to a speaker.

The program uses classes to represent those physical parts. `SineOscillator` represents the oscillator module. `SpeakerOutput` represents the speaker-output module. The code keeps the two modules separate for the same reason that the physical board keeps them separate: each part has one job and a visible connection.

## A Cable Carries a Voltage.

A patch cable plugs from an output jack on one module into an input jack on another module. The oscillator has a jack named `Sine output`. The speaker module has a jack named `Audio input`. The cable connects those two jacks.

At every sample time, the oscillator places one number on its output jack. That number represents the voltage present on the physical output jack at that instant. The cable carries the number to the speaker module's input jack. The speaker module reads that number.

The program uses 44,100 sample times each second. At a 440 Hz setting, the oscillator repeats its sine-wave cycle 440 times during one second.

## The Board Runs on a Shared Clock.

The board advances once for each sample. First, the oscillator places its next voltage on the sine-output jack. Then, the speaker module reads the cable connected to its audio-input jack. That voltage becomes the next value sent to the sound device.

```text
sample 1: oscillator output voltage → cable → speaker input voltage
sample 2: oscillator output voltage → cable → speaker input voltage
sample 3: oscillator output voltage → cable → speaker input voltage
```

The sound device receives 44,100 such values per second. It converts those values to an electrical signal, and its speaker converts the changing electrical signal into physical motion and then into changing air pressure.

## The Program Mounts and Patches the Board.

The code in `synth/first_board.py` assembles the first board in the same order that a person would assemble hardware: create the modules, mount them, and connect a cable.

```python
oscillator = SineOscillator(frequency_hz, sample_rate)
speaker = SpeakerOutput()
board = Board(speaker)
board.mount(oscillator)
board.mount(speaker)
board.patch(oscillator.sine_output, speaker.audio_input)
```

The lesson program asks this completed board for 132,300 samples. Three seconds at 44,100 samples per second require 132,300 samples. The output adapter writes those samples into a WAV file and asks macOS to play the file.

## You Can Hear the First Board.

Run this command from the project directory:

```sh
python3 src/lesson_01_tone.py
```

The program writes three seconds of A4 to `output/lesson-01-a4.wav` and plays it through the selected macOS sound device.

The next lesson keeps the same cable and speaker module while making the oscillator's frequency setting visible on the board.
