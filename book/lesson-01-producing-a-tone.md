# Lesson 1 shows how a source reaches an output.

Lesson 1 has one source, one cable, and one output boundary. Press `b` to hear A4, a steady sine tone at 440 Hz.

Run the terminal lesson from the project directory.

```sh
python3 -m pip install --user -r requirements.txt
python3 src/terminal_view.py --lesson 1
```

The terminal starts with the Sine Wave Creator selected. Its panel reads `Frequency  440 Hz` and `State: idle`. The Audio Output panel reads `To system sound` and `State: silent`.

## The source makes the signal.

The Sine Wave Creator is the source in this board. It makes a sine wave, which is a smooth repeating signal. In the digital model, the signal is a changing sequence of numbers that represents audio.

Frequency tells how many cycles of the repeating pattern occur each second. Hertz, written `Hz`, means cycles each second. The source runs at 440 Hz, so the pattern completes 440 cycles each second.

A4 is the reference pitch at 440 Hz. It gives the lesson one fixed tone, so the connection between source and output is easy to hear.

## The output sends the completed signal to the computer.

The cable runs from the Sine Wave Creator to Audio Output. The Audio Output module is the boundary between the board and the computer's selected sound device. A speaker can be the physical device after that boundary, but the module itself is Audio Output.

The moving mark on the cable begins when the tone is active. It moves from the source toward the output. The mark shows that the current signal path is in use. It is an interface animation, so it does not show electricity moving at physical speed.

## The `b` key uses a latch.

Press `b` once to start A4. The source changes from `idle` to `active`, the output changes from `silent` to `active`, and the cable begins to pulse. Press `b` again to stop the tone. The source returns to `idle`, the output returns to `silent`, and the cable stops pulsing.

This start and stop rule is a latch. The tone stays on after a press, then changes state on the next press. Terminal programs receive key presses reliably, but portable terminals do not provide one common way to report when a key is released.

The arrow keys select a panel. Lesson 1 does not expose a control to change, so up and down leave the board unchanged and state why in the status line. Press `?` to read the short definitions for signal, sine wave, frequency, hertz, A4, and Audio Output.

Press `r` to stop audio and return the lesson to its defaults. The Sine Wave Creator becomes selected, the tone becomes silent, and the oscillator returns to the start of its sine-wave cycle. Press `q` to stop the audio adapter and exit.

## The code keeps the view separate from the signal path.

The [Lesson 1 configuration](../src/lessons/lesson_01.py) declares the two panels, their labels, their state words, the 440 Hz text, the latch messages, and the terminology reference. The [board](../src/synth/board.py) advances the source, follows the patch cable, and reads Audio Output. The [terminal adapter](../src/synth/terminal.py) renders the lesson data without oscillator or output rules of its own.

The real-time adapter requests board samples only while the latch is active. Its [deterministic collector](../src/synth/realtime_audio.py) has no sound device and returns a repeatable sequence of samples during tests. The [terminal tests](../tests/test_terminal.py) check the latch, panel states, reset, and the 440 Hz sample stream without requiring an audio device.
