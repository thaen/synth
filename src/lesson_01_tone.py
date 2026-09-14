"""Write and play three seconds of a 440 Hz sine wave."""

from math import pi, sin
from pathlib import Path

from synth.audio_output import play_wav_file, write_mono_wav_file


SAMPLE_RATE = 44_100
FREQUENCY = 440.0
DURATION_SECONDS = 3.0
AMPLITUDE = 0.25

PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_DIRECTORY / "output" / "lesson-01-a4.wav"


def make_sample(sample_number: int) -> float:
    """Return one normalized sample for the configured sine wave."""
    time_seconds = sample_number / SAMPLE_RATE
    wave_position = 2 * pi * FREQUENCY * time_seconds
    return AMPLITUDE * sin(wave_position)


def main() -> None:
    """Write the complete sample stream and play it."""
    number_of_samples = round(SAMPLE_RATE * DURATION_SECONDS)
    samples = (make_sample(number) for number in range(number_of_samples))
    write_mono_wav_file(samples, SAMPLE_RATE, OUTPUT_PATH)

    print(f"Wrote {OUTPUT_PATH}")
    print("Playing the tone.")
    play_wav_file(OUTPUT_PATH)


if __name__ == "__main__":
    main()
