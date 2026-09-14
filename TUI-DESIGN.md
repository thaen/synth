# The terminal course builds one synthesizer in public.

This document defines the next prototype for the synthesizer course. It replaces the Pygame board with a terminal user interface, while keeping the current lesson configurations, modules, jacks, cables, and signal evaluation model. It gives implementation agents one target for the first five lessons.

The course has two goals. A learner can hear each new part change the signal, and the learner can name the term that appears on a synthesizer panel. The application does not teach circuit design in these lessons. It teaches what a sound signal does as it moves through a small instrument.

## The prototype has a clear boundary.

The terminal application is the current product. A lesson uses one full terminal screen, and it has a board across the upper part and a teaching panel along the bottom. It is not a browser port, a graphical rack, or an open-ended modular environment.

The existing Python model remains canonical.

- The `Board` object remains responsible for cable order and produces one audio sample at a time.
- A lesson configuration remains responsible for mounting modules, declaring cables, setting default control values, and placing panels.
- A module remains responsible for its state, its controls, its jacks, and its signal rule.
- The terminal view reads module data. It does not branch on a lesson number or put oscillator, gain, or filter math in view code.
- The audio adapter pulls samples from the configured board. It is outside the displayed signal path.

The present Pygame view and offline WAV writer are reference adapters. The terminal prototype does not remove them until its first five lessons have equivalent tests and observable behavior.

## The screen makes the signal path visible.

The first lesson presents this layout, with a cable that crosses the open space between two compact panels.

```text
Lesson 1: A sine wave becomes sound.

┌───────────────────┐                                      ┌──────────────────┐
│ SINE WAVE CREATOR │══════════════════════════════════════│ AUDIO OUTPUT     │
│ Frequency  440 Hz │          audio signal                │ To system sound  │
│ State      idle   │                                      │ State  silent    │
└───────────────────┘                                      └──────────────────┘

Selected: Sine wave creator — It makes a smooth signal that repeats 440 times each second.
Keys: ←/→ select a module   ↑/↓ change its control   b start or stop the tone   r reset   q quit
```

The interface calls the right-hand panel `Audio Output` because it is the boundary that sends the completed signal to the computer's selected output device. A speaker is one physical device after that boundary. The panel may show `speaker` as its destination when that is the active device, but it must not teach that the module itself is a speaker.

The view has these steady rules.

1. A cable runs from an output on the left to an input on the right. It has an arrow or moving pulse that shows signal direction, while the source is active.
2. The selected module has a high-contrast border and a single accent color. The same color identifies its name in the teaching panel.
3. Every visible module has a name, its current state, and only the controls introduced in the current lesson.
4. The teaching panel names the selected module, gives a two-sentence plain-language explanation, and lists the keys that affect it.
5. A compact status line states whether audio is ready, active, muted, or unavailable. An audio failure never makes the terminal view stop responding.
6. The application redraws the active pulse and state indicator at a fixed rate that is separate from audio sample production.

The first lesson uses a short pulse animation that travels along the cable while the tone is active. The animation is evidence that the source, cable, and output are participating in the current signal path. It does not claim to depict electricity at physical speed.

## The keyboard has two distinct roles.

The arrows navigate the board rather than play notes. Left and right move selection among the visible modules. Up and down change the selected module's one exposed control by a lesson-defined step. The application ignores an adjustment when the selected module has no exposed control, then states why in the status line.

The `b` key toggles the Lesson 1 tone on and off. It is a start and stop control, not a note that must remain held. The first screen states this directly: `b: start or stop A4`.

Most terminal emulators deliver key presses, but they do not provide portable key-release events. A usual piano-like rule, where sound stops when a physical laptop key rises, cannot be the base behavior for a terminal course. Later playable lessons therefore use a documented latch rule at first: pressing a mapped note key starts or selects a note, and pressing that key again stops it. A future optional input adapter can use a terminal that reports release events or a native keyboard API, but that adapter must not change the lesson model.

The application reserves these keys from the first lesson.

| Key | The application does this. |
| --- | --- |
| `b` | The application starts or stops the current default A4 tone. |
| Left and right arrows | The application selects the previous or next visible module. |
| Up and down arrows | The application raises or lowers the selected control by its stated step. |
| `r` | The application returns the current lesson to its documented defaults and stops sound. |
| `?` | The application opens or closes a key and terminology reference. |
| `q` | The application stops the audio adapter and exits. |

Mapped musical keys begin only after the course introduces pitch. The initial map is `a w s e d f t g y h u j k`, which follows the familiar white-key and black-key rows. Its lesson text calls the map a computer-keyboard convention rather than a property of synthesis.

## The audio adapter produces sound without owning the lesson.

The prototype uses a real-time output stream, not repeated calls to `afplay` or WAV-file creation. The implementation uses `sounddevice.OutputStream` with a mono callback at 44,100 samples per second and a small device-selected block size. The callback requests the required count of samples from the configured board and writes them into the output buffer.

The audio callback must not render the terminal view, allocate lesson objects, write files, print output, or wait on terminal input. The terminal event loop changes control state through a small thread-safe command queue or lock. It requests a safe gain ramp whenever a control changes in a way that could click, including start, stop, reset, or a large gain change.

The adapter has a start-up check that reports the selected device, sample rate, and any failure. The first `b` press starts the adapter if it is not already ready. The `q` and `r` paths stop active sound before they close or reset the board. Tests replace this adapter with a deterministic sample collector.

## The first five lessons have one audible question each.

Each lesson retains every earlier panel and cable. A lesson adds one part or one exposed control that changes the learner's answer to one question. The board is therefore a growing instrument rather than five unrelated screens.

### Lesson 1 shows that a source needs an output.

**The learner hears:** A4, a steady 440 Hz sine tone, after pressing `b`.

**The board contains:** A `Sine Wave Creator` panel and an `Audio Output` panel. The sine output has one cable to the audio input.

**The learner learns:** A source makes a signal. A sine wave is a smooth repeating pattern. Frequency is the number of cycles per second, and hertz means cycles per second. A4 at 440 Hz is a conventional reference pitch. The audio output sends the completed signal to the selected computer device.

**The interaction proves:** Pressing `b` changes the source from idle to active, starts the cable pulse, and produces the tone. Pressing it again stops the tone and the pulse.

**The code path is:** `lesson_01` configuration → `SineOscillator.advance()` → `PatchCable` → `AudioOutput.current_sample()` → real-time audio adapter.

### Lesson 2 shows that gain changes signal size.

**The learner hears:** The same A4 tone at different levels.

**The board adds:** A `Gain` panel between the sine-wave creator and audio output. The older cable becomes `oscillator → gain`, and a new cable becomes `gain → audio output`.

**The learner learns:** Amplitude is the size of a signal's value. Gain is a multiplier that changes amplitude. A gain of `1.00` leaves the signal unchanged, `0.50` halves it, and `0.00` makes it silent. Loudness is what a person perceives, and volume is a practical listening control; both relate to amplitude but are not interchangeable terms.

**The interaction proves:** Select Gain with the arrows, then use up and down to change a `0.00–1.00` gain control in `0.05` steps. The panel shows `Gain: 0.50`, and a small signal meter becomes shorter as the value falls.

**The model rule is:** `output sample = oscillator sample × gain`. The gain module must be named `Gain`, while the teaching panel explains amplitude before it uses the word gain without a definition.

### Lesson 3 shows that pitch selects the rate of repetition.

**The learner hears:** The same sine tone become higher or lower without becoming louder at a fixed gain.

**The board adds:** A `Pitch` panel with an output cable to the sine-wave creator's visible `Pitch input`. The audio cable path from Lesson 2 stays unchanged.

**The learner learns:** Pitch is the musical perception associated with frequency. An octave doubles frequency, so A5 is 880 Hz and A3 is 220 Hz. A semitone is one of twelve equal pitch steps in an octave. The project uses the common one-volt-per-octave control convention inside the module model, but the terminal panel presents pitch as semitones first.

**The interaction proves:** Select Pitch and use up or down to move in one-semitone steps from A4. The pitch panel shows both the note name and the frequency, while the oscillator panel shows the frequency that its input now selects.

**The model rule is:** `frequency = 440 × 2^(semitones / 12)`. The pitch module may convert its displayed semitone value into the existing one-volt-per-octave input value at its output jack.

### Lesson 4 shows that waveform changes timbre.

**The learner hears:** A sine, triangle, square, and sawtooth tone at the same pitch and gain, with different character.

**The board changes:** The sine-wave creator becomes an `Oscillator` panel and receives one new `Waveform` control. It remains the same source module in the configuration and does not add a cable. Its options are Sine, Triangle, Square, and Sawtooth.

**The learner learns:** A waveform is the repeated shape made by an oscillator. Timbre is the quality that distinguishes sounds at the same pitch and level. A sine wave has one frequency component. Square and sawtooth waves have added frequency components, called harmonics. Brightness is an informal description for sound with more high-frequency energy; it is not a separate physical quantity or a universal knob.

**The interaction proves:** Select Oscillator and use up or down to choose a waveform. The panel shows an ASCII trace of one cycle and the selected waveform name. The lesson keeps pitch and gain fixed during the first comparison.

**The model rule is:** The oscillator has one phase clock and one selected waveform function. Changing waveform does not change the oscillator's frequency or the gain value.

### Lesson 5 shows that a filter changes brightness after the source.

**The learner hears:** A sawtooth become darker as a low-pass filter closes, then brighter as it opens.

**The board adds:** A `Low-Pass Filter` panel between Gain and Audio Output. The older output cable becomes `gain → filter`, and a new cable becomes `filter → audio output`. The lesson sets the oscillator to Sawtooth so that the filter has audible high-frequency content to remove.

**The learner learns:** A filter changes the balance of frequency components in an existing sound. A low-pass filter lets frequencies below its cutoff pass more readily and makes frequencies above it quieter. Cutoff is that boundary frequency. The words bright and dark describe the result of the changed frequency balance. Resonance is not introduced yet, because it changes the behavior near cutoff and deserves its own later lesson.

**The interaction proves:** Select Low-Pass Filter and use up or down to move the cutoff between 200 Hz and 12 kHz on a musical, logarithmic scale. The panel displays the cutoff in hertz and a small response trace. At 12 kHz, the sawtooth is near its unfiltered state; at 200 Hz, it is much darker.

**The model rule is:** The filter processes the incoming sample after the gain module and before the audio output. The initial filter implementation has one cutoff parameter and no resonance control.

## The course makes later vocabulary predictable.

The next groups extend the same voice after Lesson 5. They are an order for design, not a request to implement them in the first terminal prototype.

| Lessons | The new idea is this. | The learner can then define this term. |
| --- | --- | --- |
| 6–7 | A gate marks the start and end of a note, then an attack-decay envelope shapes gain over time. | A gate, envelope, attack, and decay are separate things. |
| 8 | The envelope gains sustain and release stages. | ADSR describes a level shape, while sustain is a level and release is a time. |
| 9 | An LFO changes a chosen control repeatedly at a non-audio rate. | Movement is an informal result of modulation, and an LFO is one repeated modulator. |
| 10 | Filter resonance changes the range near cutoff. | Resonance is not brightness, although it can make a sound feel brighter. |
| 11 | A delay stores samples and feeds delayed copies back into the path. | Delay is a time-based repeat effect, and feedback controls repeat decay. |
| 12 | A reverb uses many dense short delays. | Reverb suggests acoustic space; it is not one audible echo. |
| 13–14 | A clock creates regular events, then a sequencer turns events into stored pitch and gate steps. | Tempo, pulse, step, pattern, and sequence describe musical time. |

The sequencer begins a second board only when the voice has a gate and pitch input that it can control. The first board remains a playable voice, while a later sequencer board has clearly labeled output cables that feed that voice. This separation prevents a clock or sequencer from looking like a sound source.

## The terminology has rules.

The teaching panel defines a term before it relies on the term. It keeps these distinctions stable.

| The term is this. | The course uses the term in this way. |
| --- | --- |
| Signal | A changing sequence of numbers in the digital model that represents the audio or control quantity. |
| Amplitude | The size of a signal value or wave. |
| Gain | A multiplier that changes amplitude. |
| Volume or loudness | A listening result or user-facing level idea, rather than the gain operation itself. |
| Pitch | The musical perception that follows frequency for a steady periodic tone. |
| Frequency | The number of repeating cycles each second, measured in hertz. |
| Timbre | The sound quality that differs when pitch and level stay fixed. |
| Brightness | An informal description that often means more high-frequency content. |
| Modulation | One signal or rule changes a parameter of another part over time. |
| Movement | An informal listening description that often results from modulation. |

The application shows a definition in the current lesson, a short definition in the `?` reference, and a longer explanation in the matching Markdown lesson. The text does not use marketing labels such as `warm`, `fat`, or `analog` as if they have fixed technical meanings.

## The implementation has a bounded first increment.

The first implementation increment ends after Lesson 1. It has the following completion conditions.

1. Running `python3 -m synth_tui --lesson 1` opens a terminal application that fits a standard 80-by-24 terminal, with a documented wider layout for 100 columns or more.
2. The application shows the two panels, the cable, the selected-module teaching panel, and the complete key reference.
3. Pressing `b` starts and stops a real 440 Hz sine tone through the selected audio device, and it changes the source and cable animation state.
4. Pressing left or right moves the selection between the source and the audio output. Pressing up or down on either panel has a clear no-control status message.
5. Pressing `r` stops sound and restores the initial state. Pressing `q` stops the stream before the terminal closes.
6. Unit tests verify the fixed oscillator frequency, the audio path, the start and stop state machine, selected-module movement, and the adapter's behavior when no audio device is available.
7. A short Lesson 1 Markdown page uses the same terms and key behavior as the running program.

The second increment adds only the Gain module and Lesson 2. It must not introduce waveform selection, musical-key mapping, envelopes, or filters.

## The Ableton site is a reference, not a source dependency.

Ableton Learning Synths has a useful course structure. Its current course begins with amplitude and pitch, then presents envelopes, LFOs, oscillators, filters, recipes, and a playground. Its filter lesson connects brightness with high-frequency content, and its envelope lesson describes envelopes as modulators. Those teaching choices support the proposed order, but the terminal course has its own screen, terminology, source model, interaction model, and text.

The 2026-09-14 review found that the Ableton site delivers a minified `musiclab.js` bundle and a license file that identifies third-party components. No public Learning Synth source repository appeared in Ableton's public GitHub organization during that review. The project must not copy, deminify, or treat that bundle as reusable source without express permission from Ableton and the relevant rights holders. The site is a behavior and teaching reference only.

The implementation agents can consult these sources when a detail needs confirmation.

- [Ableton Learning Synths course map](https://learningsynths.ableton.com/en/) records the lesson families and the Playground scope.
- [Ableton's filter lesson](https://learningsynths.ableton.com/en/filters/filters-in-synthesizers) defines a low-pass filter in terms of lower and higher sound components and links brightness to high-frequency content.
- [Ableton's envelope lesson](https://learningsynths.ableton.com/en/envelopes/synthesizer-envelopes) distinguishes an envelope from the parameter that it changes.
- [Textual's keyboard-input documentation](https://textual.textualize.io/guide/input/) documents key events and terminal key limitations for the proposed view library.
- [python-sounddevice stream documentation](https://python-sounddevice.readthedocs.io/en/latest/api/streams.html) documents the callback output-stream adapter.

The first terminal lesson has one source, one cable, one output boundary, and one 440 Hz sine tone.
