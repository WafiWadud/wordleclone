import random
import subprocess
from colorama import Fore, Style, init


# fjord gucks nymph vibex waltz
class WordGuessGame:
    def __init__(self):
        # Initialize colorama
        init()

        # Load the dictionary into a set for faster lookups
        self._five_letter_words = {
            word.lower()
            for word in subprocess.check_output(
                ["aspell", "dump", "-d", "en_US", "master"]
            )
            .decode("utf-8")
            .splitlines()
            if len(word) == 5 and "'" not in word
        }

    def get_random_word(self) -> str:
        """Get a random 5-letter word from the cached list."""
        return random.choice(list(self._five_letter_words))

    def is_valid_word(self, word: str) -> bool:
        """Check if the word is valid using the cached set."""
        return word in self._five_letter_words

    def check_guess(self, guess: str, target: str) -> str:
        result: list[str] = []
        for g, t in zip(guess, target):
            if g == t:
                result.append(Fore.GREEN + g)  # Correct letter in the correct position
            elif g in target:
                result.append(Fore.YELLOW + g)  # Correct letter in the wrong position
            else:
                result.append(Fore.BLACK + g)  # Incorrect letter
        return "".join(result) + Style.RESET_ALL

    def play_game(self) -> None:
        target_word: str = self.get_random_word()
        attempts: int = 0
        while attempts < 6:
            guess: str = input("Enter your guess: ").lower()
            if not self.is_valid_word(guess):
                print("That's not a valid word. Please try again.")
                continue
            result: str = self.check_guess(guess, target_word)
            print(result)
            attempts += 1
            if guess == target_word:
                print("Congratulations You guessed the word.")
                break
        else:
            print(f"Game over. The word was {target_word}.")


# Create an instance of the game and start playing
game = WordGuessGame()
game.play_game()
