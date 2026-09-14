"""Write and play a tone from the reusable sine-oscillator module."""

from pathlib import Path

from lessons.lesson_02 import build
from synth.audio_output import play_wav_file, write_mono_wav_file


DURATION_SECONDS = 3.0
PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_DIRECTORY / "output" / "lesson-02-oscillator-a4.wav"


def main() -> None:
    """Mount the Lesson 2 board, collect its samples, and play them."""
    lesson = build()
    number_of_samples = round(lesson.sample_rate * DURATION_SECONDS)
    samples = (lesson.board.next_sample() for _ in range(number_of_samples))

    write_mono_wav_file(samples, lesson.sample_rate, OUTPUT_PATH)
    print(f"Wrote {OUTPUT_PATH}")
    print("Playing the oscillator.")
    play_wav_file(OUTPUT_PATH)


if __name__ == "__main__":
    main()
