"""This module contains the output boundary between the instrument and macOS."""

from collections.abc import Iterable
from pathlib import Path
import struct
import subprocess
import wave


MAX_16_BIT_SAMPLE = 32_767


def write_mono_wav_file(
    samples: Iterable[float], sample_rate: int, output_path: Path
) -> None:
    """Write normalized mono samples to a 16-bit PCM WAV file."""
    pcm_bytes = bytearray()
    for sample in samples:
        if not -1.0 <= sample <= 1.0:
            raise ValueError("Every sample must be between -1.0 and 1.0.")
        pcm_bytes.extend(struct.pack("<h", round(sample * MAX_16_BIT_SAMPLE)))

    output_path.parent.mkdir(exist_ok=True)
    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_bytes)


def play_wav_file(output_path: Path) -> None:
    """Ask macOS to play a WAV file through its selected sound device."""
    subprocess.run(["afplay", str(output_path)], check=True)
