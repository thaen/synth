"""Write and play a tone from the reusable sine-oscillator module."""

from pathlib import Path

from synth.audio_output import play_wav_file, write_mono_wav_file
from synth.oscillator import SineOscillator


SAMPLE_RATE = 44_100
FREQUENCY_HZ = 440.0
DURATION_SECONDS = 3.0
MONITOR_LEVEL = 0.25
PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_DIRECTORY / "output" / "lesson-02-oscillator-a4.wav"


def main() -> None:
    """Create one oscillator, collect its samples, and play them."""
    oscillator = SineOscillator(FREQUENCY_HZ, SAMPLE_RATE)
    number_of_samples = round(SAMPLE_RATE * DURATION_SECONDS)
    samples = (
        MONITOR_LEVEL * oscillator.next_sample()
        for _ in range(number_of_samples)
    )

    write_mono_wav_file(samples, SAMPLE_RATE, OUTPUT_PATH)
    print(f"Wrote {OUTPUT_PATH}")
    print("Playing the oscillator.")
    play_wav_file(OUTPUT_PATH)


if __name__ == "__main__":
    main()
