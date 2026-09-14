"""Write three seconds of a 440 Hz sine wave to a mono WAV file."""

from math import pi, sin
from pathlib import Path
import struct
import subprocess
import wave


SAMPLE_RATE = 44_100
FREQUENCY = 440.0
DURATION_SECONDS = 3.0
AMPLITUDE = 0.25
MAX_16_BIT_SAMPLE = 32_767

PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_DIRECTORY / "output" / "lesson-01-a4.wav"


def make_sample(sample_number: int) -> int:
    """Return one signed 16-bit PCM sample for the configured sine wave."""
    time_seconds = sample_number / SAMPLE_RATE
    wave_position = 2 * pi * FREQUENCY * time_seconds
    return round(AMPLITUDE * sin(wave_position) * MAX_16_BIT_SAMPLE)


def write_wav_file() -> None:
    """Write the complete sample stream in the WAV format."""
    number_of_samples = round(SAMPLE_RATE * DURATION_SECONDS)
    pcm_samples = (make_sample(number) for number in range(number_of_samples))
    pcm_bytes = b"".join(struct.pack("<h", sample) for sample in pcm_samples)

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    with wave.open(str(OUTPUT_PATH), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(pcm_bytes)

    print(f"Wrote {OUTPUT_PATH}")


def play_wav_file() -> None:
    """Ask macOS to play the WAV file through its selected sound device."""
    print("Playing the tone.")
    subprocess.run(["afplay", str(OUTPUT_PATH)], check=True)


def main() -> None:
    """Write the WAV file and play it."""
    write_wav_file()
    play_wav_file()


if __name__ == "__main__":
    main()
