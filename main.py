import random
import subprocess
from colorama import Fore, Style, init

# Initialize colorama
init()

# Load the dictionary into a set for faster lookups
words = (
    subprocess.check_output(["aspell", "dump", "-d", "en_US", "master"])
    .decode("utf-8")
    .splitlines()
)
five_letter_words = {
    word.lower() for word in words if len(word) == 5 and "'" not in word
}


def get_random_word():
    """Get a random 5-letter word from the cached list."""
    return random.choice(list(five_letter_words))


def is_valid_word(word):
    """Check if the word is valid using the cached set."""
    return word in five_letter_words


def check_guess(guess, target):
    result = []
    for g, t in zip(guess, target):
        if g == t:
            result.append(Fore.GREEN + g)  # Correct letter in the correct position
        elif g in target:
            result.append(Fore.YELLOW + g)  # Correct letter in the wrong position
        else:
            result.append(Fore.BLACK + g)  # Incorrect letter
    return "".join(result) + Style.RESET_ALL


def play_game():
    target_word = get_random_word()
    attempts = 0
    while attempts < 6:
        guess = input("Enter your guess: ").lower()
        if not is_valid_word(guess):
            print("That's not a valid word. Please try again.")
            continue
        result = check_guess(guess, target_word)
        print(result)
        attempts += 1
        if guess == target_word:
            print("Congratulations! You guessed the word.")
            break
    else:
        print(f"Game over. The word was {target_word}.")


play_game()
