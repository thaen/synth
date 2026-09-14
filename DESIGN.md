# This document directs an interactive book about modular synthesis.

The book teaches sound and digital instruments by building one small modular synthesizer from a blank board. A reader hears a result, sees the physical model that makes it, reads a short explanation, and can inspect the same code that drives the board. The work begins with one sine oscillator at A4, which is 440 Hz, and ends with a playable instrument that can sequence, shape, mix, and repeat sound.

This document defines the educational and product requirements for the agent that writes the book. It does not prescribe classes, file names, rendering libraries, or audio-engine internals.

## The book has one teaching goal.

The book teaches how instruments turn changing signals into sound. Programming serves that goal, but it is not the subject. Code must therefore be short, direct, and available for inspection without forcing a reader to learn software architecture before learning an oscillator.

The book models familiar modular-synth hardware in a deliberately small digital simulation. A module is a self-contained circuit or program unit with a particular job. Jacks are its connection points. A patch cable connects an output jack to an input jack. A control changes a module's behavior. The board is the physical-looking surface that holds the modules and cables.

The book must say when its model is digital rather than analog. A digital audio engine represents a changing signal as a sequence of numbers at sample times. An analog circuit has a continuously changing electrical signal. The lesson must use the simpler model without claiming that it reproduces every detail of physical hardware.

## Each written lesson follows textbook rules.

Each lesson begins with an observable result, such as a tone that the reader can hear or a control that the reader can move. The lesson then introduces the objects and ideas that explain that result in the order that a new reader needs them.

Every technical term must have a plain-language definition before the text relies on it. A definition needs an example in the current board where possible. The text must not use unexplained words such as module, oscillator, sample, voltage, frequency, gate, envelope, filter, or sequence.

The prose uses complete sentences and ordinary textbook language. It states what the present board does. It does not interrupt the explanation with apologies for omitted features, comparisons with an unfinished future system, or comments about the lesson's own construction. A short final section may name the single thing that the next lesson adds.

The text must distinguish a fact from a design choice. For example, 1 volt per octave is a common convention for pitch control, not a law of all electronic instruments. A WAV file and a browser audio context are delivery methods, not synthesizer modules. An audio device is a boundary between the simulated board and the physical world.

Each lesson contains the following elements.

1. The lesson states the audible or visible result first.
2. The lesson gives a diagram of the current board and its signal path.
3. The lesson defines only the concepts needed to understand that board.
4. The lesson explains one concrete experiment that changes a control, makes a patch, or listens for a result.
5. The lesson gives an inspection path from board configuration to module behavior to sound output.
6. The lesson ends with one sentence about the next lesson.

Diagrams are part of the explanation rather than decoration. A diagram must identify the modules, visible controls, jacks, cables, and direction of the present signal path. When a relationship changes over time, such as an envelope or a sequence, the lesson needs a time diagram or a simple trace as well as the board diagram.

## The board follows physical patching rules.

The companion board is one growing surface, not a separate application for each lesson. Lesson 1 starts with a mostly empty board and two modest panels: a sine oscillator and an audio-output module. Each later lesson retains the existing board, then places one new panel or makes one small, visible change to its patch.

The empty area must remain visible. Panels do not stretch to fill the window, and a larger lesson does not replace the board with a new dashboard. Cables cross open space between small panels. The configuration decides the position of each module, while the execution of sound follows cable connections rather than screen position.

A cable has no intrinsic audio, control, or gate identity. It carries a changing electrical quantity, which the digital model represents as values. The output circuit produces the values, and the input circuit decides how to interpret them. A pitch input can interpret a voltage as a frequency offset, while an audio input can interpret a changing voltage as sound to send to an output device. The introductory board may use labels or a visual legend to help a reader follow a patch, but it must not imply that different cable colors are different kinds of wire.

The board presents only the modules, jacks, controls, cables, and meters introduced by the current lesson. Its stable operations are starting and stopping sound, changing an exposed control, and inspecting the current patch. Direct cable patching may appear when a lesson introduces patching as an action. A module browser, arbitrary module collection, and unrelated controls do not belong on the early board.

The audio-output module is an output boundary, not a speaker. The output boundary passes the completed signal to an adapter, and the adapter sends it to the chosen sound device. A speaker is one possible physical device after that boundary.

## The book preserves one reusable instrument model.

One board configuration must serve the written lesson, the interactive board, and the program that produces sound. A later configuration extends the earlier configuration by adding a module, a control setting, or a cable. It does not duplicate the older patch or rewrite older modules merely to make a new lesson.

The board viewer remains generic. It draws what a lesson configuration declares instead of branching on lesson numbers or module names. A module presents its own jacks, controls, and state in a common form. The viewer remains responsible for drawing the board, not for knowing how an oscillator or sequencer works.

The code has a visible reading order. A reader can start at the lesson configuration, see the modules and cables that it places, open one module to see its signal rule, and follow the finished signal through the output adapter. Each lesson identifies that path in its text.

The project retains tests for every completed lesson. A change to a later module must not alter the sound or patching behavior promised by an earlier lesson without an explicit correction to that earlier lesson. The agent must prefer extension over replacement, so that a reader can compare neighboring lessons and find a small, meaningful difference.

## The first lessons add one idea at a time.

The following sequence is the intended first course. A capability that would need two new modules must be split into two lessons, because the board should expose one new idea at a time.

1. Lesson 1 produces A4 with a fixed sine oscillator and an audio-output module. It introduces frequency, a cycle, a sine wave, samples, jacks, and a patch cable.
2. Lesson 2 adds a pitch-control module. It introduces pitch, octaves, and the 1 volt per octave convention by changing the oscillator's frequency.
3. Lesson 3 adds a note source, such as a small keyboard or note selector. It introduces named notes, semitones, and the conversion from a chosen note to pitch voltage.
4. Lesson 4 adds a second sine oscillator. It introduces two simultaneous sources, frequency ratios, beating, and detuning.
5. Lesson 5 adds a mixer. It introduces summing signals and the reason that a mixture can become too large for an output.
6. Lesson 6 adds a voltage-controlled amplifier, usually called a VCA. It introduces gain and makes volume a signal-controlled part of the patch rather than a hidden safety setting.
7. Lesson 7 adds a gate source. It introduces a gate as a voltage that represents a held or released event.
8. Lesson 8 adds an envelope generator and patches it to the VCA. It introduces attack, decay, sustain, release, and changes in level over time.
9. Lesson 9 adds a low-pass filter. It introduces harmonics, cutoff frequency, and resonance through a sound that the reader can hear change.
10. Lesson 10 adds a low-frequency oscillator. It introduces slow periodic modulation and routes it to one already familiar input.
11. Lesson 11 adds a clock. It introduces tempo, pulses, and discrete musical time.
12. Lesson 12 adds a sequencer. It introduces steps, repeated pitch patterns, and the connection between a clock, a pitch sequence, and a gate sequence.
13. Lesson 13 adds a delay or loop module. It introduces stored samples, time-based effects, feedback, and the difference between a repeated signal and a new sound source.

The earlier lessons can use a tone file as a simple output adapter while the board model is small. The output method must stay outside the educational signal path. The reader should be able to learn the board before needing to understand the operating system's audio API.

## The published form can use browser audio.

Existing work shows that the central form is established. [VCV Rack](https://vcvrack.com/manual/GettingStarted) provides a virtual modular rack with movable panels, patch cables, and an audio module that connects the virtual rack to a sound device. Its manual also states that signals are virtual voltages and that any output can connect to any input. [Ableton Learning Synths](https://learningsynths.ableton.com/) provides a browser-based environment for learning synthesis.

The book should move toward HTML, CSS, and JavaScript for its publishable interactive form. HTML and CSS can present the text and board in one page. SVG or canvas can draw panels, jacks, and cables. The browser's Web Audio API can send audio to the user's device, and an [AudioWorklet](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Using_AudioWorklet) can run custom audio processing away from the browser's main interface thread.

The browser runtime must remain an adapter around the book's module model. It must not replace the visible oscillator, mixer, VCA, or sequencer with an opaque built-in node that the lesson cannot explain. The next implementation agent must choose one canonical audio model before a browser migration. The project must not maintain two independent lesson engines that slowly disagree. The present Python prototype may remain as a reference until the browser board has feature parity for the completed lessons.

## The handoff has clear completion conditions.

The completed book has one persistent board, a lesson page for every board state, and a sound path that reaches a device through a separate adapter. A new reader can open Lesson 1, hear A4, name every visible part, and trace the signal to the audio boundary. A reader of any later lesson can identify exactly what changed from the prior board.

The completed book uses correct electrical language: cables carry voltage, and modules interpret voltage at their inputs. The completed book adds one understandable part at a time.
