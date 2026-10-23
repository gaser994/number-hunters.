
import random
import time
import os
import json
from datetime import datetime

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle

Window.clearcolor = (0, 0, 0, 1)

PANEL = (0.075, 0.09, 0.16, 1)
BLUE = (0.12, 0.42, 0.95, 1)
CYAN = (0.0, 0.85, 0.95, 1)
GREEN = (0.1, 0.8, 0.48, 1)
RED = (0.95, 0.12, 0.2, 1)
WHITE = (0.95, 0.97, 1, 1)
GRAY = (0.62, 0.68, 0.78, 1)

MEDALS = [
    ("first_blood", "First Blood", "Win your first game"),
    ("rising_hunter", "Rising Hunter", "Win 5 games"),
    ("number_hunter", "Number Hunter", "Win 10 games"),
    ("veteran", "Veteran", "Win 25 games"),
    ("champion", "Champion", "Win 50 games"),
    ("legend", "Legend", "Win 100 games"),
    ("warm_up", "Warm Up", "Win in the 1-100 range"),
    ("getting_serious", "Getting Serious", "Win in the 1-500 range"),
    ("hard_target", "Hard Target", "Win in the 1-1000 range"),
    ("impossible_hunter", "Impossible Hunter", "Win in the 1-10000 range"),
    ("classic_mind", "Classic Mind", "Win Classic Mode"),
    ("against_clock", "Against the Clock", "Win Time Challenge"),
    ("duelist", "Duelist", "Win with 2 players"),
    ("party_master", "Party Master", "Win with 4 players"),
    ("sharp_shooter", "Sharp Shooter", "Win in 5 guesses or fewer in range 100"),
    ("precision_expert", "Precision Expert", "Win in 7 guesses or fewer in range 500"),
    ("master_strategist", "Master Strategist", "Win in 10 guesses or fewer in range 1000"),
    ("extreme_precision", "Extreme Precision", "Win in 14 guesses or fewer in range 10000"),
    ("persistent", "Persistent", "Make 100 guesses"),
    ("unstoppable", "Unstoppable", "Make 500 guesses"),
]


def label(text, size=18, color=WHITE, height=dp(42)):
    return Label(
        text=text,
        font_size=sp(size),
        color=color,
        size_hint_y=None,
        height=height,
        halign="center",
        valign="middle"
    )


def button(text, callback, color=BLUE, height=dp(50)):
    b = Button(
        text=text,
        font_size=sp(16),
        bold=True,
        color=WHITE,
        background_normal="",
        background_down="",
        background_color=color,
        size_hint_y=None,
        height=height
    )
    b.bind(on_release=callback)
    return b


def field(hint):
    return TextInput(
        hint_text=hint,
        multiline=False,
        font_size=sp(17),
        foreground_color=WHITE,
        hint_text_color=GRAY,
        background_normal="",
        background_active="",
        background_color=PANEL,
        cursor_color=CYAN,
        padding=[dp(12), dp(12)],
        size_hint_y=None,
        height=dp(48)
    )


class MainScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(16))
        root.add_widget(label("NUMBER HUNTERS", 30, CYAN, dp(65)))
        root.add_widget(label("THINK FAST. GUESS SMART.", 15, GRAY))
        root.add_widget(label("Find the secret number!", 16, WHITE, dp(60)))
        root.add_widget(button("START NEW GAME", self.setup, GREEN, dp(58)))
        root.add_widget(button("LEADERBOARD", self.leaderboard, CYAN, dp(52)))
        root.add_widget(button("ACHIEVEMENTS", self.achievements, BLUE, dp(52)))
        root.add_widget(button("HOW TO PLAY", self.help, BLUE, dp(52)))
        root.add_widget(label("VERSION 2.5", 12, GRAY))
        self.add_widget(root)

    def setup(self, *_):
        self.manager.current = "setup"

    def leaderboard(self, *_):
        self.manager.current = "leaderboard"

    def achievements(self, *_):
        self.manager.current = "achievements"

    def help(self, *_):
        self.manager.current = "help"


class HelpScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12))
        root.add_widget(label("HOW TO PLAY", 26, CYAN, dp(55)))
        instructions = (
            "1. Choose the number of players.\n\n"
            "2. Enter player names.\n\n"
            "3. Choose a difficulty level.\n\n"
            "4. Choose Classic or Time Challenge.\n\n"
            "5. The computer selects a secret number.\n\n"
            "6. Players take turns guessing.\n\n"
            "7. TOO HIGH or TOO LOW gives you a hint.\n\n"
            "8. The first correct guess wins!\n\n"
            "9. In Time Challenge, guess before time runs out.\n\n"
            "10. Winning results are saved automatically."
        )
        text = Label(
            text=instructions,
            font_size=sp(17),
            color=WHITE,
            halign="left",
            valign="top",
            size_hint_y=None
        )
        text.bind(width=lambda obj, w: setattr(obj, "text_size", (w, None)))
        text.bind(texture_size=lambda obj, size: setattr(obj, "height", size[1] + dp(20)))
        scroll = ScrollView()
        scroll.add_widget(text)
        root.add_widget(scroll)
        root.add_widget(button("BACK TO MENU", self.back, BLUE))
        self.add_widget(root)

    def back(self, *_):
        self.manager.current = "menu"


class SetupScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.count = 1
        self.maximum = 100
        self.inputs = []
        self.mode = "classic"
        self.time_limit = 60
        root = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(7))
        root.add_widget(label("NEW GAME SETUP", 25, CYAN, dp(48)))
        root.add_widget(label("NUMBER OF PLAYERS", 15, WHITE, dp(28)))
        row = GridLayout(cols=4, spacing=dp(7), size_hint_y=None, height=dp(42))
        self.player_buttons = {}
        for n in range(1, 5):
            b = button(str(n), lambda _, v=n: self.choose_count(v), BLUE if n == 1 else PANEL, dp(42))
            self.player_buttons[n] = b
            row.add_widget(b)
        root.add_widget(row)
        root.add_widget(label("DIFFICULTY", 15, WHITE, dp(28)))
        row = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(88))
        self.level_buttons = {}
        for value, title in [
            (100, "EASY\n1 - 100"),
            (500, "NORMAL\n1 - 500"),
            (1000, "HARD\n1 - 1,000"),
            (10000, "EXTREME\n1 - 10,000")
        ]:
            b = button(title, lambda _, v=value: self.choose_level(v), BLUE if value == 100 else PANEL, dp(42))
            self.level_buttons[value] = b
            row.add_widget(b)
        root.add_widget(row)
        root.add_widget(label("GAME MODE", 15, WHITE, dp(28)))
        row = GridLayout(cols=2, spacing=dp(7), size_hint_y=None, height=dp(42))
        self.mode_buttons = {}
        for value, title in [("classic", "CLASSIC MODE"), ("time", "TIME CHALLENGE")]:
            b = button(title, lambda _, v=value: self.choose_mode(v), GREEN if value == self.mode else PANEL, dp(42))
            self.mode_buttons[value] = b
            row.add_widget(b)
        root.add_widget(row)
        root.add_widget(label("TIME LIMIT", 14, WHITE, dp(25)))
        row = GridLayout(cols=4, spacing=dp(5), size_hint_y=None, height=dp(38))
        self.time_buttons = {}
        for seconds, title in [(30, "30 SEC"), (60, "60 SEC"), (120, "2 MIN"), (180, "3 MIN")]:
            b = button(title, lambda _, s=seconds: self.choose_time(s), BLUE if seconds == 60 else PANEL, dp(38))
            self.time_buttons[seconds] = b
            row.add_widget(b)
        root.add_widget(row)
        root.add_widget(label("PLAYER NAMES", 15, WHITE, dp(28)))
        self.names_box = BoxLayout(orientation="vertical", spacing=dp(7), size_hint_y=None)
        self.names_box.bind(minimum_height=self.names_box.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.names_box)
        root.add_widget(scroll)
        root.add_widget(button("START GAME", self.start, GREEN, dp(46)))
        root.add_widget(button("BACK", self.back, PANEL, dp(38)))
        self.add_widget(root)
        self.refresh_names()

    def on_pre_enter(self, *_):
        self.refresh_names()

    def choose_count(self, n):
        self.count = n
        for value, b in self.player_buttons.items():
            b.background_color = BLUE if value == n else PANEL
        self.refresh_names()

    def choose_level(self, value):
        self.maximum = value
        for number, b in self.level_buttons.items():
            b.background_color = BLUE if number == value else PANEL

    def choose_mode(self, mode):
        self.mode = mode
        for value, b in self.mode_buttons.items():
            b.background_color = GREEN if value == mode else PANEL

    def choose_time(self, seconds):
        self.time_limit = seconds
        for value, b in self.time_buttons.items():
            b.background_color = BLUE if value == seconds else PANEL

    def refresh_names(self):
        old = [x.text for x in self.inputs]
        self.names_box.clear_widgets()
        self.inputs = []
        for i in range(self.count):
            name = old[i] if i < len(old) and old[i].strip() else f"Player {i + 1}"
            f = field(f"Player {i + 1} name")
            f.text = name
            self.inputs.append(f)
            self.names_box.add_widget(f)

    def start(self, *_):
        names = [x.text.strip() or f"Player {i + 1}" for i, x in enumerate(self.inputs)]
        game = self.manager.get_screen("game")
        limit = self.time_limit if self.mode == "time" else None
        game.start_game([n[:24] for n in names], self.maximum, limit)
        self.manager.current = "game"

    def back(self, *_):
        self.manager.current = "menu"


class GameScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.players = []
        self.current = 0
        self.finished = False
        self.total = 0
        self.timer_event = None
        self.deadline = None
        self.time_limit = None
        self.maximum = 100
        root = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(8))
        root.add_widget(label("NUMBER HUNTERS", 24, CYAN, dp(42)))
        self.turn = label("PLAYER'S TURN", 19, WHITE)
        root.add_widget(self.turn)
        self.range = label("Guess a number", 15, GRAY, dp(30))
        root.add_widget(self.range)
        self.timer_label = label("TIME LEFT: NO LIMIT", 17, CYAN, dp(35))
        root.add_widget(self.timer_label)
        self.guess = field("Enter your guess")
        self.guess.input_filter = "int"
        self.guess.bind(on_text_validate=self.submit)
        root.add_widget(self.guess)
        root.add_widget(button("SUBMIT GUESS", self.submit, GREEN, dp(46)))
        self.feedback = label("Good luck!", 18, CYAN, dp(55))
        root.add_widget(self.feedback)
        self.counter = label("Total guesses: 0", 14, GRAY, dp(28))
        root.add_widget(self.counter)
        root.add_widget(label("PLAYER SCORES", 15, WHITE, dp(28)))
        self.scores = BoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=None)
        self.scores.bind(minimum_height=self.scores.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.scores)
        root.add_widget(scroll)
        root.add_widget(button("RESTART GAME", self.restart, BLUE, dp(40)))
        root.add_widget(button("MAIN MENU", self.menu, PANEL, dp(38)))
        self.add_widget(root)

    def start_game(self, names, maximum, time_limit=None):
        self.stop_timer()
        self.maximum = maximum
        self.secret = random.randint(1, maximum)
        self.players = [{"name": n, "guesses": 0} for n in names]
        self.current = 0
        self.total = 0
        self.finished = False
        self.time_limit = time_limit
        self.deadline = time.monotonic() + time_limit if time_limit is not None else None
        self.guess.text = ""
        self.feedback.text = "Find the secret number!"
        self.feedback.color = CYAN
        self.range.text = f"Secret number: 1 - {maximum}"
        if self.deadline is not None:
            self.update_timer(0)
            if not self.finished:
                self.timer_event = Clock.schedule_interval(self.update_timer, 0.1)
        else:
            self.timer_label.text = "TIME LEFT: NO LIMIT"
        self.update_screen()

    def update_timer(self, dt):
        if self.finished or self.deadline is None:
            return False
        remaining = max(0, int(self.deadline - time.monotonic() + 0.999))
        minutes, seconds = divmod(remaining, 60)
        self.timer_label.text = f"TIME LEFT: {minutes:02d}:{seconds:02d}"
        if time.monotonic() >= self.deadline:
            self.time_up()
            return False
        return True

    def stop_timer(self):
        if self.timer_event is not None:
            self.timer_event.cancel()
            self.timer_event = None

    def time_up(self):
        if self.finished:
            return
        self.finished = True
        self.stop_timer()
        self.timer_label.text = "TIME LEFT: 00:00"
        Clock.schedule_once(self.show_lose_screen, 0)

    def show_lose_screen(self, dt):
        if self.manager:
            self.manager.current = "lose"

    def update_screen(self):
        if not self.players:
            return
        self.turn.text = f"{self.players[self.current]['name']}'S TURN"
        self.counter.text = f"Total guesses: {self.total}"
        self.scores.clear_widgets()
        for i, p in enumerate(self.players):
            self.scores.add_widget(label(f"{p['name']}: {p['guesses']} guesses", 14, CYAN if i == self.current else WHITE, dp(30)))

    def submit(self, *_):
        if self.finished or not self.players:
            return
        if self.deadline is not None and time.monotonic() >= self.deadline:
            self.time_up()
            return
        raw = self.guess.text.strip()
        if not raw:
            self.feedback.text = "Enter a number first!"
            self.feedback.color = RED
            return
        try:
            guess = int(raw)
        except ValueError:
            self.feedback.text = "Enter a valid number!"
            self.feedback.color = RED
            return
        if not 1 <= guess <= self.maximum:
            self.feedback.text = f"Choose a number from 1 to {self.maximum}."
            self.feedback.color = RED
            return
        p = self.players[self.current]
        p["guesses"] += 1
        self.total += 1
        App.get_running_app().record_guess()
        if guess == self.secret:
            self.finished = True
            self.stop_timer()
            self.feedback.text = f"CORRECT! {p['name']} WINS!"
            self.feedback.color = GREEN
            self.update_screen()
            mode = "Time Challenge" if self.time_limit is not None else "Classic"
            app = App.get_running_app()
            app.save_result(
                winner=p["name"],
                winner_guesses=p["guesses"],
                total_guesses=self.total,
                maximum=self.maximum,
                mode=mode,
                player_count=len(self.players)
            )
            results = self.manager.get_screen("results")
            results.show_results(self.players, p["name"], self.total, self.secret)
            self.manager.current = "results"
            return
        if guess < self.secret:
            self.feedback.text = "TOO LOW! Try higher."
            self.feedback.color = CYAN
        else:
            self.feedback.text = "TOO HIGH! Try lower."
            self.feedback.color = RED
        self.guess.text = ""
        self.current = (self.current + 1) % len(self.players)
        self.update_screen()

    def restart(self, *_):
        self.stop_timer()
        self.manager.current = "setup"

    def menu(self, *_):
        self.stop_timer()
        self.manager.current = "menu"


class LoseScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)
        root = BoxLayout(orientation="vertical", padding=dp(25), spacing=dp(20))
        root.add_widget(Label())
        root.add_widget(label("YOU LOSE", 38, RED, dp(80)))
        root.add_widget(label("TIME'S UP!", 20, GRAY, dp(45)))
        root.add_widget(Label())
        root.add_widget(button("RETURN TO MAIN MENU", self.menu, BLUE, dp(55)))
        self.add_widget(root)

    def update_bg(self, *_):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def menu(self, *_):
        self.manager.current = "menu"


class ResultsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12))
        root.add_widget(label("GAME OVER", 28, CYAN, dp(55)))
        self.winner = label("WINNER", 23, GREEN, dp(55))
        root.add_widget(self.winner)
        self.secret = label("Secret number", 17, WHITE, dp(38))
        root.add_widget(self.secret)
        self.total = label("Total guesses", 15, GRAY, dp(32))
        root.add_widget(self.total)
        root.add_widget(label("FINAL LEADERBOARD", 18, CYAN, dp(40)))
        self.board = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        self.board.bind(minimum_height=self.board.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.board)
        root.add_widget(scroll)
        root.add_widget(button("PLAY AGAIN", self.play_again, GREEN))
        root.add_widget(button("MAIN MENU", self.menu, BLUE))
        self.add_widget(root)

    def show_results(self, players, winner, total, secret):
        self.winner.text = f"WINNER: {winner}"
        self.winner.color = GREEN
        self.secret.text = f"Secret number: {secret}"
        self.total.text = f"Total guesses: {total}"
        self.board.clear_widgets()
        ranked = sorted(players, key=lambda p: p["guesses"])
        for i, p in enumerate(ranked, 1):
            is_winner = p["name"] == winner
            self.board.add_widget(label(f"{i}. {p['name']} | {p['guesses']} guesses", 16, GREEN if is_winner else WHITE, dp(42)))

    def play_again(self, *_):
        self.manager.current = "setup"

    def menu(self, *_):
        self.manager.current = "menu"


class LeaderboardScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(10))
        root.add_widget(label("LEADERBOARD", 28, CYAN, dp(55)))
        root.add_widget(label("BEST SAVED WINNING RESULTS", 13, GRAY, dp(30)))
        self.entries = BoxLayout(orientation="vertical", spacing=dp(7), size_hint_y=None)
        self.entries.bind(minimum_height=self.entries.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.entries)
        root.add_widget(scroll)
        root.add_widget(button("CLEAR ALL RESULTS", self.confirm_clear, RED, dp(44)))
        root.add_widget(button("BACK TO MENU", self.back, BLUE, dp(44)))
        self.add_widget(root)

    def on_pre_enter(self, *_):
        self.refresh()

    def refresh(self):
        self.entries.clear_widgets()
        app = App.get_running_app()
        records = app.records
        if not records:
            self.entries.add_widget(label("No saved results yet.\nWin a game to appear here!", 17, GRAY, dp(90)))
            return
        for rank, record in enumerate(records, 1):
            date_text = record.get("date", "")
            if len(date_text) > 10:
                date_text = date_text[:10]
            text = (
                f"{rank}. {record.get('winner', 'Player')}\n"
                f"Guesses: {record.get('winner_guesses', '?')} | "
                f"Range: 1-{record.get('maximum', '?')}\n"
                f"{record.get('mode', '')} | {date_text}"
            )
            self.entries.add_widget(label(text, 14, GREEN if rank == 1 else WHITE, dp(76)))

    def confirm_clear(self, *_):
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(12))
        content.add_widget(label("Delete all saved results?", 16, WHITE, dp(50)))
        row = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(44))
        popup = Popup(title="CONFIRM", content=content, size_hint=(0.85, 0.35), auto_dismiss=True)
        row.add_widget(button("DELETE", lambda *_: self.clear_records(popup), RED))
        row.add_widget(button("CANCEL", lambda *_: popup.dismiss(), BLUE))
        content.add_widget(row)
        popup.open()

    def clear_records(self, popup):
        app = App.get_running_app()
        app.records = []
        app.save_records()
        popup.dismiss()
        self.refresh()

    def back(self, *_):
        self.manager.current = "menu"


class AchievementsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(10))
        root.add_widget(label("ACHIEVEMENTS", 27, CYAN, dp(55)))
        self.progress = label("", 15, GREEN, dp(35))
        root.add_widget(self.progress)
        self.entries = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        self.entries.bind(minimum_height=self.entries.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.entries)
        root.add_widget(scroll)
        root.add_widget(button("BACK TO MENU", self.back, BLUE))
        self.add_widget(root)

    def on_pre_enter(self, *_):
        self.refresh()

    def refresh(self):
        app = App.get_running_app()
        unlocked = app.achievements.get("unlocked", [])
        self.progress.text = f"UNLOCKED: {len(unlocked)} / {len(MEDALS)}"
        self.entries.clear_widgets()
        for medal_id, title, description in MEDALS:
            is_unlocked = medal_id in unlocked
            status = "[UNLOCKED]" if is_unlocked else "[LOCKED]"
            color = GREEN if is_unlocked else GRAY
            self.entries.add_widget(label(f"{status} {title}\n{description}", 15, color, dp(68)))

    def back(self, *_):
        self.manager.current = "menu"


class NumberHuntersApp(App):
    def build(self):
        self.title = "NUMBER HUNTERS"
        self.records_file = os.path.join(self.user_data_dir, "leaderboard.json")
        self.achievements_file = os.path.join(self.user_data_dir, "achievements.json")
        self.records = []
        self.achievements = {"unlocked": [], "total_guesses": 0, "total_wins": 0}
        self.load_records()
        self.load_achievements()
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="menu"))
        sm.add_widget(SetupScreen(name="setup"))
        sm.add_widget(GameScreen(name="game"))
        sm.add_widget(LoseScreen(name="lose"))
        sm.add_widget(ResultsScreen(name="results"))
        sm.add_widget(HelpScreen(name="help"))
        sm.add_widget(LeaderboardScreen(name="leaderboard"))
        sm.add_widget(AchievementsScreen(name="achievements"))
        return sm

    def load_records(self):
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            if os.path.exists(self.records_file):
                with open(self.records_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.records = data if isinstance(data, list) else []
            else:
                self.records = []
        except Exception as e:
            print("Could not load leaderboard:", e)
            self.records = []

    def save_records(self):
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            temporary_file = self.records_file + ".tmp"
            with open(temporary_file, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
            os.replace(temporary_file, self.records_file)
        except Exception as e:
            print("Could not save leaderboard:", e)

    def load_achievements(self):
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            if os.path.exists(self.achievements_file):
                with open(self.achievements_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self.achievements.update(data)
            if not isinstance(self.achievements.get("unlocked"), list):
                self.achievements["unlocked"] = []
            if not isinstance(self.achievements.get("total_guesses"), int):
                self.achievements["total_guesses"] = 0
            if not isinstance(self.achievements.get("total_wins"), int):
                self.achievements["total_wins"] = 0
        except Exception as e:
            print("Could not load achievements:", e)

    def save_achievements(self):
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            temporary_file = self.achievements_file + ".tmp"
            with open(temporary_file, "w", encoding="utf-8") as f:
                json.dump(self.achievements, f, ensure_ascii=False, indent=2)
            os.replace(temporary_file, self.achievements_file)
        except Exception as e:
            print("Could not save achievements:", e)

    def record_guess(self):
        self.achievements["total_guesses"] += 1
        self.check_achievements()
        self.save_achievements()

    def unlock_medals(self, medal_ids):
        unlocked = self.achievements["unlocked"]
        new_medals = []
        for medal_id in medal_ids:
            if medal_id not in unlocked:
                unlocked.append(medal_id)
                medal = next((m for m in MEDALS if m[0] == medal_id), None)
                if medal:
                    new_medals.append(medal[1])
        if new_medals:
            self.save_achievements()
            content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
            content.add_widget(label("MEDAL UNLOCKED!", 21, GREEN, dp(45)))
            content.add_widget(label("\n".join(new_medals), 16, CYAN, dp(90)))
            popup = Popup(title="ACHIEVEMENT", content=content, size_hint=(0.85, 0.45))
            content.add_widget(button("CONTINUE", lambda *_: popup.dismiss(), BLUE))
            popup.open()

    def check_achievements(self, maximum=None, mode=None, winner_guesses=None, player_count=None):
        a = self.achievements
        wins = a["total_wins"]
        guesses = a["total_guesses"]
        medals = []
        if wins >= 1:
            medals.append("first_blood")
        if wins >= 5:
            medals.append("rising_hunter")
        if wins >= 10:
            medals.append("number_hunter")
        if wins >= 25:
            medals.append("veteran")
        if wins >= 50:
            medals.append("champion")
        if wins >= 100:
            medals.append("legend")
        if guesses >= 100:
            medals.append("persistent")
        if guesses >= 500:
            medals.append("unstoppable")
        if maximum is not None and winner_guesses is not None:
            if maximum == 100:
                medals.append("warm_up")
                if winner_guesses <= 5:
                    medals.append("sharp_shooter")
            elif maximum == 500:
                medals.append("getting_serious")
                if winner_guesses <= 7:
                    medals.append("precision_expert")
            elif maximum == 1000:
                medals.append("hard_target")
                if winner_guesses <= 10:
                    medals.append("master_strategist")
            elif maximum == 10000:
                medals.append("impossible_hunter")
                if winner_guesses <= 14:
                    medals.append("extreme_precision")
            if mode == "Classic":
                medals.append("classic_mind")
            elif mode == "Time Challenge":
                medals.append("against_clock")
            if player_count == 2:
                medals.append("duelist")
            if player_count == 4:
                medals.append("party_master")
        self.unlock_medals(medals)

    def save_result(self, winner, winner_guesses, total_guesses, maximum, mode, player_count):
        record = {
            "winner": winner,
            "winner_guesses": winner_guesses,
            "total_guesses": total_guesses,
            "maximum": maximum,
            "mode": mode,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.records.append(record)
        self.records.sort(key=lambda r: (int(r.get("winner_guesses", 999999)), -int(r.get("maximum", 0))))
        self.records = self.records[:50]
        self.save_records()
        self.achievements["total_wins"] += 1
        self.check_achievements(
            maximum=maximum,
            mode=mode,
            winner_guesses=winner_guesses,
            player_count=player_count
        )
        self.save_achievements()


if __name__ == "__main__":
    NumberHuntersApp().run()
