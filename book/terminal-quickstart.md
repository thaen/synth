# The terminal synth has a quick start.

The terminal synth has five lessons that build one board. Each lesson draws its configured modules and cables, then can send the board's samples to the selected audio device.

## You can install and run a lesson.

Run these commands from the repository root.

```sh
python3 -m pip install --user -r requirements.txt
python3 src/terminal_view.py --lesson 1
```

The `--lesson` argument accepts `1` through `5`. For example, Lesson 5 starts the board with Pitch, Oscillator, Gain, Low-Pass Filter, and Audio Output.

```sh
python3 src/terminal_view.py --lesson 2
python3 src/terminal_view.py --lesson 3
python3 src/terminal_view.py --lesson 4
python3 src/terminal_view.py --lesson 5
```

The full-screen program needs a terminal with curses support. Press `b` after the screen opens to request audio.

## The controls have these effects.

| Key | The terminal does this. |
| --- | --- |
| Left and right arrows | The terminal selects the previous or next visible module. |
| Up and down arrows | The terminal changes the selected module's exposed control by the lesson's stated step. |
| `b` | The terminal starts or stops the lesson tone. The first press also starts the audio adapter. |
| `r` | The terminal stops audio and restores the lesson's documented module and control defaults. |
| `?` | The terminal opens or closes the keyboard and terminology reference. |
| `q` | The terminal stops the audio adapter and exits. |

Some visible modules have no exposed control in a lesson. The terminal leaves their state unchanged and explains that choice on the status line.

## The code follows this path.

`src/terminal_view.py` calls `synth.terminal.main()`. That entry point loads `lessons.lesson_NN`, whose `build()` function creates a `Board`, mounts modules, patches their jacks, selects the Audio Output module, and returns a `Lesson`. The lesson also supplies the visible panel order, learner-facing text, and exposed controls.

`TerminalLessonState` gives that configured board and its sample rate to the audio adapter. `TerminalLessonApp` is the curses view. It reads the lesson's panels, controls, and board cables to draw the screen, while its event loop translates the control keys into state changes. The view has no oscillator, gain, or filter signal rules.

When audio is active, `SoundDeviceAudioAdapter` asks the board for one sample at a time from its output-stream callback. `Board.next_sample()` derives the module order from its `PatchCable` connections, advances each module, and reads `AudioOutput.current_sample()`. The adapter writes those samples to a mono `sounddevice.OutputStream` at the lesson's sample rate. The adapter is outside the board's displayed signal path.

## Audio has this fallback.

The adapter imports `sounddevice` only after `b` requests audio. If the package is missing or the selected device cannot open, the terminal reports audio as unavailable and keeps the lesson open. The terminal does not switch to WAV-file output or `afplay`; you can still inspect the board, change controls, reset the lesson, or quit.
