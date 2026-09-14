"""Write and play three seconds of a 440 Hz sine wave."""

from pathlib import Path

from synth.audio_output import play_wav_file, write_mono_wav_file
from synth.first_board import make_first_board


SAMPLE_RATE = 44_100
FREQUENCY = 440.0
DURATION_SECONDS = 3.0
AMPLITUDE = 0.25

PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_DIRECTORY / "output" / "lesson-01-a4.wav"


def main() -> None:
    """Mount the first board, write its signal, and play it."""
    instrument = make_first_board(FREQUENCY, SAMPLE_RATE)
    number_of_samples = round(SAMPLE_RATE * DURATION_SECONDS)
    samples = (AMPLITUDE * instrument.next_sample() for _ in range(number_of_samples))
    write_mono_wav_file(samples, SAMPLE_RATE, OUTPUT_PATH)

    print(f"Wrote {OUTPUT_PATH}")
    print("Playing the tone.")
    play_wav_file(OUTPUT_PATH)


if __name__ == "__main__":
    main()
