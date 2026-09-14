# Terminal Lesson Authoring

The terminal view reads a `Lesson` configuration and has no lesson-number branches. A lesson author adds `ModulePresentation` objects to the `panels` field in the same order as the visible modules. Each presentation has the module object, a learner-facing label, and two sentences of prose.

The `visible_controls` field contains only controls that the lesson introduces. A `VisibleControl` has the existing `Knob`, its label, and an adjustment step. The terminal uses the first declared control for the selected module, so early lessons should expose one control per panel. The module remains responsible for the control range and signal rule.

Each `ModulePresentation` can declare a `readout`, `inactive_state`, and `active_state`. The terminal renders these values without checking a lesson number or module type. A readout can be text or a function that returns current module data.

`Lesson` records every mounted control value after construction. Its `reset()` method calls module `reset()` methods and restores those values according to `ResetBehavior`. The terminal stops audio before this reset when `ResetBehavior.stop_audio` is true. A module with time-dependent state must provide a `reset()` method.

The lesson can declare its audio instruction, active and inactive messages, key summary, and `reference_lines`. Those values let a lesson explain its latch and terminology while the terminal input code remains shared.

The terminal adapter reads `Board.samples()` in the sound callback. Terminal input only changes the lesson state and requests a short output gain ramp; it never runs inside the callback. Tests should use `DeterministicAudioCollector`, which has `collect(count)` and needs no audio device.
