import random
import subprocess
from textual.app import App, ComposeResult
from textual.widgets import Static, Input, Label
from textual.containers import Horizontal, Vertical
from textual import on


def load_words() -> set[str]:
    return {
        word.lower()
        for word in subprocess.check_output(["aspell", "dump", "-d", "en_US", "master"])
        .decode("utf-8")
        .splitlines()
        if len(word) == 5 and "'" not in word
    }


class LetterTile(Static):
    def update(self, letter: str) -> None:  # type: ignore[override]
        super().update(letter)


class WordleGrid(Vertical):
    def compose(self) -> ComposeResult:
        for row in range(6):
            with Horizontal(id=f"row-{row}", classes="grid-row"):
                for col in range(5):
                    yield LetterTile(
                        "", id=f"tile-{row}-{col}", classes="tile tile-empty"
                    )


class Keyboard(Vertical):
    ROWS = [list("QWERTYUIOP"), list("ASDFGHJKL"), list("ZXCVBNM")]

    def compose(self) -> ComposeResult:
        for row in self.ROWS:
            with Horizontal(classes="kb-row"):
                for letter in row:
                    yield Static(letter, id=f"kb-{letter}", classes="kb-key")


class WordleApp(App):
    CSS = """
    Screen {
        background: #121213;
        align: center top;
    }
 
    #game-container {
        width: 45;
        height: auto;
        align: center top;
        padding: 1 2;
    }
 
    #title {
        text-align: center;
        color: #ffffff;
        text-style: bold;
        width: 100%;
        padding: 0 0 1 0;
        border-bottom: solid #3a3a3c;
        margin-bottom: 1;
    }
 
    #subtitle {
        text-align: center;
        color: #818384;
        width: 100%;
        margin-bottom: 1;
    }
 
    WordleGrid {
        width: 100%;
        height: auto;
        align: center top;
    }
 
    .grid-row {
        width: 100%;
        height: 5;
        align: center middle;
    }
 
    LetterTile {
        width: 7;
        height: 5;
        content-align: center middle;
        text-style: bold;
        color: #ffffff;
        margin: 0;
    }
 
    .tile-empty   { background: #121213; border: solid #3a3a3c; }
    .tile-filled  { background: #121213; border: solid #999;    color: #ffffff; }
    .tile-correct { background: #538d4e; border: solid #538d4e; color: #ffffff; }
    .tile-present { background: #b59f3b; border: solid #b59f3b; color: #ffffff; }
    .tile-absent  { background: #3a3a3c; border: solid #3a3a3c; color: #818384; }
 
    #input-area {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 1;
    }
 
    #guess-input {
        width: 37;
        background: #1a1a1b;
        color: #ffffff;
        border: solid #565758;
        padding: 0 1;
        text-style: bold;
    }
 
    #guess-input:focus { border: solid #818384; }
 
    #error-message {
        text-align: center;
        color: #ff6b6b;
        width: 100%;
        height: 1;
    }
 
    #message {
        text-align: center;
        color: #ffffff;
        text-style: bold;
        width: 100%;
        height: 1;
    }
 
    Keyboard {
        width: 100%;
        height: auto;
        align: center top;
        margin-top: 1;
    }
 
    .kb-row {
        width: 100%;
        height: 3;
        align: center middle;
    }
 
    .kb-key {
        width: 5;
        height: 2;
        background: #818384;
        color: #ffffff;
        text-style: bold;
        content-align: center middle;
        margin: 0;
    }
 
    .kb-correct { background: #538d4e; }
    .kb-present { background: #b59f3b; }
    .kb-absent  { background: #3a3a3c; color: #565758; }
 
    #stats-bar {
        text-align: center;
        color: #565758;
        width: 100%;
        margin-top: 1;
    }
    """

    def __init__(self):
        super().__init__()
        self._words = load_words()
        self.target_word = random.choice(list(self._words))
        self.current_row = 0
        self.game_over = False

    def compose(self) -> ComposeResult:
        with Vertical(id="game-container"):
            yield Label("W O R D L E", id="title")
            yield Label("Guess the 5-letter word in 6 tries", id="subtitle")
            yield WordleGrid()
            with Vertical(id="input-area"):
                yield Input(
                    placeholder="Type your guess and press Enter",
                    id="guess-input",
                    max_length=5,
                )
            yield Label("", id="error-message")
            yield Label("", id="message")
            yield Keyboard()
            yield Label("Attempt 1 of 6", id="stats-bar")

    def on_mount(self) -> None:
        self.query_one("#guess-input").focus()

    @on(Input.Changed, "#guess-input")
    def on_input_changed(self, event: Input.Changed) -> None:
        guess = event.value.lower()
        row = self.current_row
        if self.game_over or row >= 6:
            return
        for col in range(5):
            tile = self.query_one(f"#tile-{row}-{col}", LetterTile)
            if col < len(guess):
                tile.update(guess[col].upper())
                tile.remove_class("tile-empty")
                tile.add_class("tile-filled")
            else:
                tile.update("")
                tile.remove_class("tile-filled")
                tile.add_class("tile-empty")
        self.query_one("#error-message", Label).update("")

    @on(Input.Submitted, "#guess-input")
    def handle_guess(self, event: Input.Submitted) -> None:
        if self.game_over:
            return
        guess = event.value.lower().strip()
        error_label = self.query_one("#error-message", Label)
        error_label.update("")

        if len(guess) != 5:
            error_label.update("⚠  Word must be exactly 5 letters")
            return
        if not guess.isalpha():
            error_label.update("⚠  Letters only please!")
            return
        if guess not in self._words:
            error_label.update(f"⚠  '{guess.upper()}' is not in the word list")
            return

        result = self._check_guess(guess, self.target_word)
        self._update_grid(guess, result)
        self._update_keyboard(guess, result)
        self.current_row += 1

        if guess == self.target_word:
            self.game_over = True
            emojis = [
                "🧠 Genius!",
                "🌟 Magnificent!",
                "💥 Impressive!",
                "😎 Splendid!",
                "👍 Great!",
                "😅 Phew!",
            ]
            msg = emojis[min(self.current_row - 1, 5)]
            self.query_one("#message", Label).update(
                f"{msg}  [{self.target_word.upper()}]"
            )
            self.query_one("#stats-bar", Label).update(
                "Restart to play again  •  Ctrl+C to quit"
            )
            event.input.disabled = True
        elif self.current_row >= 6:
            self.game_over = True
            self.query_one("#message", Label).update(
                f"💀  Game over! The word was {self.target_word.upper()}"
            )
            self.query_one("#stats-bar", Label).update("Better luck next time!")
            event.input.disabled = True
        else:
            self.query_one("#stats-bar", Label).update(
                f"Attempt {self.current_row + 1} of 6"
            )

        event.input.clear()

    def _check_guess(self, guess: str, target: str) -> list[str]:
        result = ["absent"] * 5
        target_chars: list[str | None] = list(target)
        guess_chars: list[str | None] = list(guess)
        for i in range(5):
            if guess_chars[i] == target_chars[i]:
                result[i] = "correct"
                target_chars[i] = None
                guess_chars[i] = None
        for i in range(5):
            if guess_chars[i] is not None and guess_chars[i] in target_chars:
                result[i] = "present"
                target_chars[target_chars.index(guess_chars[i])] = None
        return result

    def _update_grid(self, guess: str, result: list[str]) -> None:
        row = self.current_row
        for col, (letter, state) in enumerate(zip(guess, result)):
            tile = self.query_one(f"#tile-{row}-{col}", LetterTile)
            tile.update(letter.upper())
            tile.remove_class(
                "tile-empty",
                "tile-filled",
                "tile-correct",
                "tile-present",
                "tile-absent",
            )
            tile.add_class(f"tile-{state}")

    def _update_keyboard(self, guess: str, result: list[str]) -> None:
        priority = {"correct": 3, "present": 2, "absent": 1}
        for letter, state in zip(guess, result):
            key = self.query_one(f"#kb-{letter.upper()}", Static)
            current_best = 0
            for cls_name, prio in priority.items():
                if f"kb-{cls_name}" in key.classes:
                    current_best = prio
            if priority[state] > current_best:
                key.remove_class("kb-correct", "kb-present", "kb-absent")
                key.add_class(f"kb-{state}")


if __name__ == "__main__":
    WordleApp().run()
