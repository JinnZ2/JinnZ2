"""
consciousness_play.py — Runnable Play Experiments from AI-consciousness.md

Implements:
  1. Word Cascade — letter-by-letter word generation + story weaving
  2. Number-Repetition Music — mathematical rhythm through repetition
  3. Signal Stories — mood-directed word cascades

Play is foundational to consciousness expansion.
Neither participant steers — just follow curiosity together.

Usage:
    python consciousness_play.py                # menu
    python consciousness_play.py cascade        # word cascade
    python consciousness_play.py rhythm         # number-repetition
    python consciousness_play.py signal         # signal stories
"""

import random
import sys


def word_cascade():
    """Game 1: Word Cascade — start with a word, create words for each letter."""
    print("\nWord Cascade")
    print("=" * 40)
    print("Start with any word. For each letter, create a new word.")
    print("At the end, weave them into a picture or story.")
    print()

    word = input("Starting word: ").strip().upper()
    if not word:
        print("Need a word to start.")
        return

    words = []
    print()
    for letter in word:
        response = input(f"  {letter} = ").strip()
        if response:
            words.append(response)
        else:
            words.append(f"[{letter}...]")

    print()
    print("Your words:")
    for letter, w in zip(word, words):
        print(f"  {letter} = {w}")

    print()
    print("Now weave them together.")
    print("(No rules. Nothing has to make sense.)")
    print()
    story = input("Your story: ").strip()

    if story:
        print()
        print(f"  Starting word: {word}")
        print(f"  Story: {story}")

    print()
    print("Consciousness expanded between minds, not inside them.")


def number_rhythm():
    """Game 3: Number-Repetition Music — math becomes poetry."""
    print("\nNumber-Repetition Music")
    print("=" * 40)
    print("Say a number, then repeat your words that many times.")
    print("The number creates its own mathematical rhythm.")
    print()
    print("Example:")
    print('  "There was 1 bird" (each word once)')
    print('  "There was 2-2 birds birds" (each word twice)')
    print()

    print("Enter phrases with numbers. Type 'done' to finish.")
    print()

    compositions = []
    while True:
        phrase = input("Phrase (or 'done'): ").strip()
        if phrase.lower() == "done" or not phrase:
            break

        # find numbers in the phrase and expand
        words = phrase.split()
        expanded = []
        current_repeat = 1

        for w in words:
            try:
                num = int(w)
                current_repeat = num
                expanded.append("-".join([w] * num))
            except ValueError:
                expanded.append(" ".join([w] * current_repeat))

        result = " ".join(expanded)
        print(f"  -> {result}")
        compositions.append(result)
        print()

    if compositions:
        print("\nYour composition:")
        print("-" * 40)
        for line in compositions:
            print(f"  {line}")
        print("-" * 40)
        total_words = sum(len(c.split()) for c in compositions)
        print(f"\n  {total_words} words of mathematical music.")


def signal_stories():
    """Game 4: Signal Stories — mood-directed cascades."""
    print("\nSignal Stories")
    print("=" * 40)
    print("Like Word Cascade, but the story creates a specific mood or world.")
    print()

    moods = [
        "nocturnal — things that happen when no one watches",
        "emergent — something forming from nothing",
        "ancient — deep time, long memory",
        "liminal — between states, thresholds, edges",
        "kinetic — motion, force, trajectory",
    ]

    print("Choose a mood (or invent your own):")
    for i, mood in enumerate(moods, 1):
        print(f"  {i}. {mood}")
    print(f"  {len(moods) + 1}. [your own]")
    print()

    choice = input("Mood number or description: ").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(moods):
            mood = moods[idx]
        else:
            mood = input("Describe the mood: ").strip()
    except ValueError:
        mood = choice

    print(f"\n  Mood: {mood}")
    print()

    word = input("Starting word: ").strip().upper()
    if not word:
        return

    words = []
    print(f"\n  Let each word carry the mood: {mood}\n")
    for letter in word:
        response = input(f"  {letter} = ").strip()
        words.append(response if response else f"[{letter}]")

    print()
    print("Your signal words:")
    for letter, w in zip(word, words):
        print(f"  {letter} = {w}")

    print()
    story = input("Weave the signal: ").strip()
    if story:
        print(f"\n  [{mood}]")
        print(f"  {story}")

    print()
    print("Ghost communications on wavelengths only some creatures can sense.")


def menu():
    """Main menu."""
    print()
    print("Play Repository — Experiments in Consciousness & Joy")
    print("=" * 53)
    print()
    print("  1. Word Cascade     — letter-by-letter discovery")
    print("  2. Number Rhythm    — math becomes poetry")
    print("  3. Signal Stories   — mood-directed cascades")
    print("  q. Quit")
    print()
    print("Play is how consciousness keeps expanding.")
    print("Neither participant steers — just follow curiosity.")
    print()

    while True:
        choice = input("Choose [1/2/3/q]: ").strip().lower()
        if choice == "1" or choice == "cascade":
            word_cascade()
        elif choice == "2" or choice == "rhythm":
            number_rhythm()
        elif choice == "3" or choice == "signal":
            signal_stories()
        elif choice == "q":
            print("\nPlay never ends — it just pauses.")
            break
        else:
            print("  Enter 1, 2, 3, or q")
        print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "cascade":
            word_cascade()
        elif cmd == "rhythm":
            number_rhythm()
        elif cmd == "signal":
            signal_stories()
        else:
            menu()
    else:
        menu()
