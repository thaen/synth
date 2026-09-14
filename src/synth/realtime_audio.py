"""This module keeps sounddevice output separate from terminal input and drawing."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from threading import RLock
from typing import Protocol

from synth.board import Board


@dataclass(frozen=True)
class AudioStatus:
    """This object reports the adapter state without raising terminal-facing errors."""

    state: str
    message: str


class AudioAdapter(Protocol):
    """This protocol is the boundary used by the terminal lesson state."""

    @property
    def status(self) -> AudioStatus:
        """Return the current device and activity state."""

    @property
    def is_active(self) -> bool:
        """Return whether the adapter is emitting board samples."""

    def configure(self, board: Board, sample_rate: int) -> None:
        """Associate one configured lesson board with the adapter."""

    def start(self) -> bool:
        """Prepare the output device and return whether it is ready."""

    def set_active(self, active: bool) -> None:
        """Start or mute signal emission through a short output-gain ramp."""

    def apply_terminal_change(self, change: Callable[[], None]) -> None:
        """Apply one board mutation while excluding the real-time callback."""

    def stop(self) -> None:
        """Stop the output device without changing the lesson board."""


class DeterministicAudioCollector:
    """This adapter collects board samples deterministically for tests and examples."""

    def __init__(self) -> None:
        """Create an adapter that has no dependency on a physical output device."""
        self.board: Board | None = None
        self.sample_rate: int | None = None
        self._active = False
        self._started = False
        self._status = AudioStatus("ready", "Test audio collector is ready.")

    @property
    def status(self) -> AudioStatus:
        """Return the collector state."""
        return self._status

    @property
    def is_active(self) -> bool:
        """Return whether collection is active."""
        return self._active

    def configure(self, board: Board, sample_rate: int) -> None:
        """Associate one board with this deterministic collector."""
        self.board = board
        self.sample_rate = sample_rate

    def start(self) -> bool:
        """Mark the collector ready after configuration."""
        if self.board is None:
            self._status = AudioStatus("unavailable", "The collector has no configured board.")
            return False
        self._started = True
        self._status = AudioStatus("ready", "Test audio collector is ready.")
        return True

    def set_active(self, active: bool) -> None:
        """Change collection state without producing samples from terminal input."""
        if not self._started and not self.start():
            return
        self._active = active
        state = "active" if active else "muted"
        message = "Test audio collector is active." if active else "Test audio collector is muted."
        self._status = AudioStatus(state, message)

    def apply_terminal_change(self, change: Callable[[], None]) -> None:
        """Apply a test-side lesson mutation synchronously."""
        if not callable(change):
            raise TypeError("A terminal change must be callable.")
        change()

    def collect(self, count: int) -> list[float]:
        """Return exactly ``count`` board samples when the collector is active."""
        if count < 0:
            raise ValueError("The sample count cannot be negative.")
        if not self._active or self.board is None:
            return [0.0] * count
        return list(self.board.samples(count))

    def stop(self) -> None:
        """Stop collection while keeping the collector available for another start."""
        self._active = False
        if self.board is not None:
            self._status = AudioStatus("ready", "Test audio collector stopped safely.")


class SoundDeviceAudioAdapter:
    """This adapter sends a configured board to one sounddevice output stream."""

    def __init__(self, sounddevice_module: object | None = None, ramp_samples: int = 128) -> None:
        """Create an adapter that imports sounddevice only when audio is requested."""
        self._sounddevice_module = sounddevice_module
        self._ramp_samples = max(1, ramp_samples)
        self._board: Board | None = None
        self._sample_rate: int | None = None
        self._stream: object | None = None
        self._lock = RLock()
        self._active = False
        self._gain = 0.0
        self._target_gain = 0.0
        self._status = AudioStatus("ready", "Audio has not started.")

    @property
    def status(self) -> AudioStatus:
        """Return a thread-safe snapshot of the output state."""
        with self._lock:
            return self._status

    @property
    def is_active(self) -> bool:
        """Return whether board samples are currently emitted."""
        with self._lock:
            return self._active

    def configure(self, board: Board, sample_rate: int) -> None:
        """Set the board that the callback may pull from after the stream starts."""
        with self._lock:
            self._board = board
            self._sample_rate = sample_rate

    def _sounddevice(self) -> object:
        """Return the injected module or import the optional runtime dependency."""
        if self._sounddevice_module is not None:
            return self._sounddevice_module
        import sounddevice

        return sounddevice

    def start(self) -> bool:
        """Open the stream and preserve a readable unavailable state on failure."""
        with self._lock:
            if self._board is None or self._sample_rate is None:
                self._status = AudioStatus("unavailable", "Audio has no configured lesson board.")
                return False
            if self._stream is not None:
                return True
            try:
                sounddevice = self._sounddevice()
                self._stream = sounddevice.OutputStream(
                    samplerate=self._sample_rate,
                    channels=1,
                    callback=self._callback,
                )
                self._stream.start()
                device = getattr(self._stream, "device", "the selected output device")
                self._status = AudioStatus(
                    "ready", f"Audio is ready on {device} at {self._sample_rate} Hz."
                )
                return True
            except Exception as error:
                self._stream = None
                self._status = AudioStatus("unavailable", f"Audio unavailable: {error}")
                return False

    def set_active(self, active: bool) -> None:
        """Request a short gain ramp, which the callback applies without terminal work."""
        with self._lock:
            if active and self._stream is None and not self.start():
                return
            self._active = active
            self._target_gain = 1.0 if active else 0.0
            state = "active" if active else "muted"
            message = "Audio is active." if active else "Audio is muted."
            self._status = AudioStatus(state, message)

    def request_gain_ramp(self) -> None:
        """Request a gain ramp after a terminal-side control change."""
        with self._lock:
            self._gain = 0.0 if self._active else self._gain

    def apply_terminal_change(self, change: Callable[[], None]) -> None:
        """Apply a terminal-side board mutation under the callback's shared lock."""
        if not callable(change):
            raise TypeError("A terminal change must be callable.")
        with self._lock:
            change()
            self.request_gain_ramp()

    def _callback(self, outdata: object, frames: int, _time: object, status: object) -> None:
        """Pull samples only; this callback does not read terminal events or draw frames."""
        with self._lock:
            board = self._board
            active = self._active
            target_gain = self._target_gain
            gain = self._gain
            if status:
                self._status = AudioStatus("active" if active else "muted", str(status))
            for frame in range(frames):
                if gain != target_gain:
                    difference = target_gain - gain
                    gain += difference / min(self._ramp_samples, max(1, frames - frame))
                should_render = active or gain > 0.0
                sample = board.next_sample() if should_render and board is not None else 0.0
                outdata[frame][0] = sample * gain
            self._gain = gain

    def stop(self) -> None:
        """Mute, stop, and close the stream so reset and quit leave no callback running."""
        with self._lock:
            self._active = False
            self._gain = 0.0
            self._target_gain = 0.0
            stream = self._stream
            self._stream = None
        if stream is not None:
            try:
                stream.stop()
                stream.close()
            except Exception as error:
                with self._lock:
                    self._status = AudioStatus("unavailable", f"Audio stop failed: {error}")
                return
        with self._lock:
            self._status = AudioStatus("ready", "Audio stopped safely.")
