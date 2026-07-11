import json
import random
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageOps


APP_DIR = Path(__file__).resolve().parent
BACKGROUND_IMAGE = APP_DIR / "assets" / "stars_space.png"
RES_DIR = APP_DIR / "res"
SETTINGS_FILE = RES_DIR / "settings.json"
COMMANDERS_DIR = RES_DIR / "commanders"
COMMANDER_TEXT_DIR = COMMANDERS_DIR / "commander_text"
COMMANDER_TEXT_FILE = COMMANDER_TEXT_DIR / "commander_text.txt"
MANA_DIR = RES_DIR / "mana"
PLANES_DIR = RES_DIR / "planes"
PLANES_LIST_FILE = PLANES_DIR / "planes.txt"
PLANES_CATALOG_FILE = PLANES_DIR / "planes.json"
CREATE_NEW_PROFILE = "Create New Player Profile"
CREATE_NEW_COMMANDER_PROFILE = "Create New Commander Profile"
APP_VERSION = "1.0"
MANA_COLORS = ["white", "blue", "red", "green", "black", "colorless"]


def resolve_app_path(path_value):
    path = Path(str(path_value))
    return path if path.is_absolute() else APP_DIR / path


def app_relative_path(path_value):
    if not path_value:
        return ""

    path = Path(str(path_value))
    if not path.is_absolute():
        return path.as_posix()

    try:
        return path.relative_to(APP_DIR).as_posix()
    except ValueError:
        return str(path)


class MagicApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(f"Magic Merna v{APP_VERSION}")
        self.geometry("520x420")
        self.minsize(360, 300)
        self.configure(bg="#0b1026")

        self.start_screen = None
        self.settings_screen = None
        self.settings_panel_window = None
        self.back_button_window = None
        self.back_button = None
        self.player_profile_screen = None
        self.player_profile_panel_window = None
        self.profile_selector_menu = None
        self.profile_selection = tk.StringVar(value=CREATE_NEW_PROFILE)
        self.profile_name = tk.StringVar()
        self.profile_total_wins = tk.IntVar(value=0)
        self.profile_commander_name = tk.StringVar()
        self.player_profiles = {}
        self.player_profile_wins = {}
        self.profile_commander_draft = []
        self.last_profile_name = ""
        self.profile_loaded_name = ""
        self.profile_commander_list = None
        self.player_profile_status = tk.StringVar()
        self.commander_profile_screen = None
        self.commander_profile_panel_window = None
        self.commander_profile_selector_menu = None
        self.commander_profile_selection = tk.StringVar(value=CREATE_NEW_COMMANDER_PROFILE)
        self.commander_profile_name = tk.StringVar()
        self.primary_commander_name = ""
        self.commander_total_wins = tk.IntVar(value=0)
        self.commander_attack_power = tk.IntVar(value=0)
        self.commander_defense_power = tk.IntVar(value=0)
        self.commander_image_path = tk.StringVar()
        self.commander_image_filename = tk.StringVar()
        self.commander_text = tk.StringVar()
        self.commander_text_widget = None
        self.second_commander_enabled = tk.BooleanVar(value=False)
        self.second_commander_name = tk.StringVar()
        self.second_commander_image_path = tk.StringVar()
        self.second_commander_image_filename = tk.StringVar()
        self.second_commander_text = tk.StringVar()
        self.second_commander_text_widget = None
        self.second_commander_attack_power = tk.IntVar(value=0)
        self.second_commander_defense_power = tk.IntVar(value=0)
        self.commander_profiles = {}
        self.commander_texts = {}
        self.last_commander_profile_name = ""
        self.commander_preview_image = None
        self.commander_preview_label = None
        self.commander_preview_canvas = None
        self.second_commander_preview_image = None
        self.second_commander_preview_canvas = None
        self.mana_icon_images = {}
        self.mana_icon_labels = {}
        self.second_mana_icon_labels = {}
        self.commander_profile_status = tk.StringVar()
        self.commander_color_vars = {
            color_name: tk.BooleanVar(value=False)
            for color_name in MANA_COLORS
        }
        self.second_commander_color_vars = {
            color_name: tk.BooleanVar(value=False)
            for color_name in MANA_COLORS
        }
        self.commander_color_cost_vars = {
            color_name: tk.IntVar(value=0)
            for color_name in MANA_COLORS
        }
        self.second_commander_color_cost_vars = {
            color_name: tk.IntVar(value=0)
            for color_name in MANA_COLORS
        }
        self.player_setup_screen = None
        self.player_setup_panel_window = None
        self.number_of_players = tk.IntVar(value=4)
        self.starting_life_total = tk.IntVar(value=40)
        self.game_type = tk.StringVar(value="Commander")
        self.planechase_enabled = tk.BooleanVar(value=False)
        self.player_names = []
        self.commander_names = []
        self.life_totals = []
        self.game_life_text_items = []
        self.game_pending_change_items = []
        self.game_commander_damage_flash_items = []
        self.pending_counter_changes = {}
        self.pending_counter_timers = {}
        self.commander_damage_flash_timers = {}
        self.commander_damage_totals = []
        self.commander_damage_mode_player = None
        self.commander_damage_summary_items = []
        self.poison_counters = []
        self.poison_mode_player = None
        self.planes = []
        self.plane_history = []
        self.current_plane_history_index = -1
        self.plane_background_image = None
        self.plane_canvas = None
        self.leaderboards_screen = None
        self.leaderboards_panel_window = None
        self.game_winner_index = None
        self.game_win_recorded = False
        self.game_background_images = {}
        self.hidden_commander_players = set()
        self.game_key_bindings = {
            "q": (0, 1),
            "a": (0, -1),
            "w": (1, 1),
            "s": (1, -1),
            "e": (2, 1),
            "d": (2, -1),
            "r": (3, 1),
            "f": (3, -1),
            "t": (4, 1),
            "g": (4, -1),
            "y": (5, 1),
            "h": (5, -1),
        }
        self._load_app_data()
        self._load_commander_texts()
        self.plane_canvas = None
        self._load_planes()
        self.protocol("WM_DELETE_WINDOW", self._quit_app)
        self.space_background = tk.PhotoImage(file=BACKGROUND_IMAGE)

        self._show_start_screen()

    def _show_start_screen(self):
        self._clear_window()
        self._maximize_window()

        self.start_screen = tk.Canvas(self, highlightthickness=0, bg="#0b1026")
        self.start_screen.pack(fill="both", expand=True)
        self.start_screen.bind("<Configure>", self._draw_start_screen)

    def _draw_start_screen(self, event=None):
        width = self.start_screen.winfo_width()
        height = self.start_screen.winfo_height()

        self.start_screen.delete("all")
        self.start_screen.create_image(
            width // 2,
            height // 2,
            image=self.space_background,
            anchor="center",
        )
        self.start_screen.create_text(
            width // 2,
            height * 0.28,
            text="Magic Merna",
            fill="#ffffff",
            font=("Arial", 42, "bold"),
        )

        self._create_main_menu_text(
            text="New Game",
            x=width // 2,
            y=height * 0.47,
            command=self._show_player_setup_screen,
        )
        self._create_main_menu_text(
            text="Settings",
            x=width // 2,
            y=height * 0.54,
            command=self._show_settings_screen,
        )
        self._create_main_menu_text(
            text="Player Profile",
            x=width // 2,
            y=height * 0.61,
            command=self._show_player_profile_screen,
        )
        self._create_main_menu_text(
            text="Commander Profile",
            x=width // 2,
            y=height * 0.68,
            command=self._show_commander_profile_screen,
        )
        self._create_main_menu_text(
            text="Leaderboards",
            x=width // 2,
            y=height * 0.75,
            command=self._show_leaderboards_screen,
        )
        self._create_main_menu_text(
            text="Quit",
            x=width // 2,
            y=height * 0.82,
            command=self._quit_app,
        )

    def _create_main_menu_text(self, text, x, y, command):
        item = self.start_screen.create_text(
            x,
            y,
            text=text,
            fill="#ffffff",
            activefill="#f7d046",
            font=("Arial", 24, "bold"),
            tags=("main_menu_action",),
        )
        self.start_screen.tag_bind(item, "<Enter>", lambda event: self.start_screen.config(cursor="hand2"))
        self.start_screen.tag_bind(item, "<Leave>", lambda event: self.start_screen.config(cursor=""))
        self.start_screen.tag_bind(item, "<Button-1>", lambda event: command())

    def _load_app_data(self):
        if not SETTINGS_FILE.exists():
            self._save_app_data()
            return

        try:
            with SETTINGS_FILE.open("r", encoding="utf-8") as settings_file:
                data = json.load(settings_file)
        except (OSError, json.JSONDecodeError):
            return

        settings = data.get("settings", {})
        self.number_of_players.set(
            self._clamp_plain_number(settings.get("number_of_players", 4), 2, 6)
        )
        self.starting_life_total.set(
            self._clamp_plain_number(settings.get("starting_life_total", 40), 1, 999)
        )
        game_type = settings.get("game_type", "Commander")
        self.game_type.set(game_type if game_type in {"Commander", "Standard"} else "Commander")
        self.planechase_enabled.set(bool(settings.get("planechase_enabled", False)))
        if self.planechase_enabled.get() and self.number_of_players.get() > 5:
            self.number_of_players.set(5)

        profiles = data.get("player_profiles", {})
        if isinstance(profiles, dict):
            self.player_profiles = {
                str(player_name): [
                    str(commander_name)
                    for commander_name in commanders
                    if str(commander_name).strip()
                ]
                for player_name, commanders in profiles.items()
                if isinstance(commanders, list)
            }

        profile_wins = data.get("player_profile_wins", {})
        if isinstance(profile_wins, dict):
            self.player_profile_wins = {
                str(player_name): self._clamp_plain_number(wins, 0, 999999)
                for player_name, wins in profile_wins.items()
            }

        self.last_profile_name = str(data.get("last_profile_name", ""))

        commander_profiles = data.get("commander_profiles", {})
        if isinstance(commander_profiles, dict):
            self.commander_profiles = {}
            for commander_name, profile in commander_profiles.items():
                if not isinstance(profile, dict):
                    continue

                colors = profile.get("colors", [])
                second_commander = self._clean_second_commander_profile(
                    profile.get("second_commander", {})
                )
                primary_name = str(profile.get("primary_name", "")).strip()
                if not primary_name:
                    primary_name = str(commander_name)
                    old_suffix = f" - {second_commander['name']}"
                    if (
                        second_commander["enabled"]
                        and second_commander["name"]
                        and primary_name.endswith(old_suffix)
                    ):
                        primary_name = primary_name[: -len(old_suffix)]
                    elif " / " in primary_name:
                        primary_name = primary_name.split(" / ", 1)[0]

                self.commander_profiles[str(commander_name)] = {
                    "primary_name": primary_name,
                    "image_path": str(profile.get("image_path", "")),
                    "text_path": str(profile.get("text_path", "")),
                    "total_wins": self._clamp_plain_number(
                        profile.get("total_wins", 0),
                        0,
                        999999,
                    ),
                    "attack_power": self._clamp_plain_number(
                        profile.get("attack_power", 0),
                        0,
                        99,
                    ),
                    "defense_power": self._clamp_plain_number(
                        profile.get("defense_power", 0),
                        0,
                        99,
                    ),
                    "colors": [
                        str(color)
                        for color in colors
                        if str(color) in self.commander_color_vars
                    ]
                    if isinstance(colors, list)
                    else [],
                    "color_cost": self._clean_color_cost(profile.get("color_cost", {})),
                    "second_commander": second_commander,
                }

        self.last_commander_profile_name = str(
            data.get("last_commander_profile_name", "")
        )

        setup = data.get("player_setup", {})
        player_names = setup.get("player_names", [])
        commander_names = setup.get("commander_names", [])
        if isinstance(player_names, list):
            self.player_names = [tk.StringVar(value=str(name)) for name in player_names[:6]]
        if isinstance(commander_names, list):
            self.commander_names = [
                tk.StringVar(value=str(name)) for name in commander_names[:6]
            ]
        self._ensure_player_fields()
        if self._backfill_commander_profiles_from_player_profiles():
            self._save_app_data()

    def _save_app_data(self):
        RES_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "settings": {
                "number_of_players": self._clamp_input(
                    self.number_of_players,
                    minimum=2,
                    maximum=6,
                ),
                "starting_life_total": self._clamp_input(
                    self.starting_life_total,
                    minimum=1,
                    maximum=999,
                ),
                "game_type": self.game_type.get(),
                "planechase_enabled": self.planechase_enabled.get(),
            },
            "player_profiles": self.player_profiles,
            "player_profile_wins": self.player_profile_wins,
            "last_profile_name": self.last_profile_name,
            "commander_profiles": self.commander_profiles,
            "last_commander_profile_name": self.last_commander_profile_name,
            "player_setup": {
                "player_names": [player_name.get() for player_name in self.player_names],
                "commander_names": [
                    commander_name.get() for commander_name in self.commander_names
                ],
            },
        }
        with SETTINGS_FILE.open("w", encoding="utf-8") as settings_file:
            json.dump(data, settings_file, indent=2)

    def _load_commander_texts(self):
        self.commander_texts = {}
        if not COMMANDER_TEXT_FILE.exists():
            return

        try:
            file_text = COMMANDER_TEXT_FILE.read_text(encoding="utf-8")
        except OSError:
            return

        current_commander = None
        current_lines = []
        for line in file_text.splitlines():
            if line.startswith("[") and line.endswith("]"):
                if current_commander is not None:
                    self.commander_texts[current_commander] = "\n".join(
                        current_lines
                    ).strip()
                current_commander = line[1:-1].strip()
                current_lines = []
            elif current_commander is not None:
                current_lines.append(line)

        if current_commander is not None:
            self.commander_texts[current_commander] = "\n".join(current_lines).strip()

    def _save_commander_texts(self):
        COMMANDER_TEXT_DIR.mkdir(parents=True, exist_ok=True)
        with COMMANDER_TEXT_FILE.open("w", encoding="utf-8") as text_file:
            for commander_name in sorted(self.commander_texts):
                text_file.write(f"[{commander_name}]\n")
                text_file.write(self.commander_texts[commander_name].strip())
                text_file.write("\n\n")

    def _load_planes(self):
        self.planes = []
        if not PLANES_CATALOG_FILE.exists():
            self._create_planes_catalog()
        if not PLANES_CATALOG_FILE.exists():
            return

        try:
            with PLANES_CATALOG_FILE.open("r", encoding="utf-8") as catalog_file:
                planes = json.load(catalog_file)
        except (OSError, json.JSONDecodeError):
            return

        if isinstance(planes, list):
            self.planes = [
                plane
                for plane in planes
                if isinstance(plane, dict)
                and str(plane.get("name", "")).strip()
                and str(plane.get("image_path", "")).strip()
            ]

    def _create_planes_catalog(self):
        if not PLANES_LIST_FILE.exists():
            return

        try:
            plane_names = [
                name.strip()
                for name in PLANES_LIST_FILE.read_text(encoding="utf-8").splitlines()
                if name.strip()
            ]
        except OSError:
            return

        image_paths = sorted(PLANES_DIR.glob("*.png"), key=lambda path: path.name.casefold())
        planes = []
        for plane_name, image_path in zip(plane_names, image_paths):
            planes.append(
                {
                    "name": plane_name,
                    "image_path": app_relative_path(image_path),
                    "planes_text": f"This is the planes text for the {image_path.name} image.",
                }
            )

        if planes:
            PLANES_DIR.mkdir(parents=True, exist_ok=True)
            with PLANES_CATALOG_FILE.open("w", encoding="utf-8") as catalog_file:
                json.dump(planes, catalog_file, indent=2)

    def _backfill_commander_profiles_from_player_profiles(self):
        created_profile = False

        for commanders in self.player_profiles.values():
            for commander_name in commanders:
                if commander_name not in self.commander_profiles:
                    self.commander_profiles[commander_name] = {
                        "primary_name": commander_name,
                        "image_path": "",
                        "text_path": "",
                        "total_wins": 0,
                        "attack_power": 0,
                        "defense_power": 0,
                        "colors": [],
                        "color_cost": self._empty_color_cost(),
                    }
                    created_profile = True

        return created_profile

    def _clean_second_commander_profile(self, profile):
        if not isinstance(profile, dict):
            profile = {}

        colors = profile.get("colors", [])
        return {
            "enabled": bool(profile.get("enabled", False)),
            "name": str(profile.get("name", "")),
            "image_path": str(profile.get("image_path", "")),
            "text_path": str(profile.get("text_path", "")),
            "attack_power": self._clamp_plain_number(
                profile.get("attack_power", 0),
                0,
                99,
            ),
            "defense_power": self._clamp_plain_number(
                profile.get("defense_power", 0),
                0,
                99,
            ),
            "colors": [
                str(color)
                for color in colors
                if str(color) in self.second_commander_color_vars
            ]
            if isinstance(colors, list)
            else [],
            "color_cost": self._clean_color_cost(profile.get("color_cost", {})),
        }

    def _clamp_plain_number(self, value, minimum, maximum):
        try:
            current_value = int(value)
        except (TypeError, ValueError):
            current_value = minimum

        return max(minimum, min(maximum, current_value))

    def _empty_color_cost(self):
        return {color_name: 0 for color_name in MANA_COLORS}

    def _clean_color_cost(self, color_cost):
        if not isinstance(color_cost, dict):
            color_cost = {}

        return {
            color_name: self._clamp_plain_number(
                color_cost.get(color_name, 0),
                0,
                99,
            )
            for color_name in MANA_COLORS
        }

    def _quit_app(self):
        self._save_settings()
        self._save_app_data()
        self.destroy()

    def _show_leaderboards_screen(self):
        self._clear_window()

        self.leaderboards_screen = tk.Canvas(
            self,
            highlightthickness=0,
            bg="#0b1026",
        )
        self.leaderboards_screen.pack(fill="both", expand=True)
        self._add_view_exit_button(self.leaderboards_screen)
        self.leaderboards_screen.bind(
            "<Configure>",
            self._draw_leaderboards_background,
        )

        panel = tk.Frame(self.leaderboards_screen, bg="#111827", padx=30, pady=24)
        self.leaderboards_panel_window = self.leaderboards_screen.create_window(
            260,
            230,
            window=panel,
            anchor="center",
            tags="leaderboards_panel",
        )

        title = tk.Label(
            panel,
            text="Leaderboards",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 28, "bold"),
        )
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        self._build_leaderboard_list(
            panel,
            "Top Players",
            self._top_player_profiles(),
            column=0,
        )
        self._build_leaderboard_list(
            panel,
            "Top Commanders",
            self._top_commander_profiles(),
            column=1,
        )

    def _draw_leaderboards_background(self, event=None):
        width = self.leaderboards_screen.winfo_width()
        height = self.leaderboards_screen.winfo_height()

        self.leaderboards_screen.delete("background")
        self.leaderboards_screen.create_image(
            width // 2,
            height // 2,
            image=self.space_background,
            anchor="center",
            tags="background",
        )
        self.leaderboards_screen.tag_lower("background")
        if self.leaderboards_panel_window is not None:
            self.leaderboards_screen.coords(
                self.leaderboards_panel_window,
                width // 2,
                height // 2,
            )

    def _build_leaderboard_list(self, parent, title, entries, column):
        section = tk.Frame(parent, bg="#111827", padx=18)
        section.grid(row=1, column=column, sticky="n", padx=12)

        heading = tk.Label(
            section,
            text=title,
            bg="#111827",
            fg="#f7d046",
            font=("Arial", 20, "bold"),
        )
        heading.grid(row=0, column=0, columnspan=3, pady=(0, 12))

        for index, (name, wins) in enumerate(entries, start=1):
            tk.Label(
                section,
                text=f"{index}.",
                bg="#111827",
                fg="#ffffff",
                font=("Arial", 12, "bold"),
            ).grid(row=index, column=0, sticky="e", padx=(0, 8), pady=4)
            tk.Label(
                section,
                text=name,
                bg="#111827",
                fg="#ffffff",
                font=("Arial", 12, "bold"),
                width=34,
                anchor="w",
            ).grid(row=index, column=1, sticky="w", pady=4)
            tk.Label(
                section,
                text=str(wins),
                bg="#111827",
                fg="#f7d046",
                font=("Arial", 12, "bold"),
                width=6,
                anchor="e",
            ).grid(row=index, column=2, sticky="e", pady=4)

    def _top_player_profiles(self):
        return sorted(
            (
                (player_name, self.player_profile_wins.get(player_name, 0))
                for player_name in self.player_profiles
            ),
            key=lambda entry: (-entry[1], entry[0].casefold()),
        )[:10]

    def _top_commander_profiles(self):
        return sorted(
            (
                (
                    commander_name,
                    self._clamp_plain_number(profile.get("total_wins", 0), 0, 999999),
                )
                for commander_name, profile in self.commander_profiles.items()
            ),
            key=lambda entry: (-entry[1], entry[0].casefold()),
        )[:10]

    def _show_player_profile_screen(self):
        self._clear_window()

        self.player_profile_screen = tk.Canvas(self, highlightthickness=0, bg="#0b1026")
        self.player_profile_screen.pack(fill="both", expand=True)
        self._add_view_exit_button(self.player_profile_screen)
        self.player_profile_screen.bind("<Configure>", self._draw_player_profile_background)
        self.profile_commander_list = None

        if self.last_profile_name in self.player_profiles:
            self.profile_selection.set(self.last_profile_name)
        else:
            self.profile_selection.set(CREATE_NEW_PROFILE)
        self._load_selected_player_profile()

        panel = tk.Frame(self.player_profile_screen, bg="#111827", padx=28, pady=22)
        self.player_profile_panel_window = self.player_profile_screen.create_window(
            260,
            230,
            window=panel,
            anchor="center",
            tags="player_profile_panel",
        )

        title = tk.Label(
            panel,
            text="Player Profile",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 26, "bold"),
        )
        title.grid(row=0, column=0, columnspan=3, pady=(0, 18))

        profile_label = tk.Label(
            panel,
            text="Player Profile",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
        )
        profile_label.grid(row=1, column=0, sticky="w", padx=(0, 14), pady=8)

        self.profile_selector_menu = ttk.Combobox(
            panel,
            textvariable=self.profile_selection,
            values=self._profile_options(),
            state="readonly",
            font=("Arial", 12, "bold"),
            width=30,
        )
        self.profile_selector_menu.bind(
            "<<ComboboxSelected>>",
            lambda event: self._load_selected_player_profile(),
        )
        self.profile_selector_menu.grid(row=1, column=1, columnspan=2, sticky="ew", pady=8)

        player_label = tk.Label(
            panel,
            text="Player Name",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
        )
        player_label.grid(row=2, column=0, sticky="w", padx=(0, 14), pady=8)

        player_input = tk.Entry(
            panel,
            textvariable=self.profile_name,
            width=28,
            font=("Arial", 13, "bold"),
        )
        player_input.grid(row=2, column=1, columnspan=2, sticky="ew", pady=8)
        player_input.bind("<KeyPress>", self._clear_player_profile_status)

        wins_label = tk.Label(
            panel,
            text="Total Wins",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
        )
        wins_label.grid(row=3, column=0, sticky="w", padx=(0, 14), pady=8)

        wins_input = tk.Entry(
            panel,
            textvariable=self.profile_total_wins,
            width=10,
            font=("Arial", 13, "bold"),
        )
        wins_input.grid(row=3, column=1, sticky="w", pady=8)
        wins_input.bind("<KeyPress>", self._clear_player_profile_status)

        commander_label = tk.Label(
            panel,
            text="Commander Name",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
        )
        commander_label.grid(row=4, column=0, sticky="w", padx=(0, 14), pady=8)

        commander_input = ttk.Combobox(
            panel,
            textvariable=self.profile_commander_name,
            values=sorted(self.commander_profiles),
            state="readonly",
            width=30,
            font=("Arial", 13, "bold"),
        )
        commander_input.grid(row=4, column=1, sticky="ew", pady=8)
        commander_input.bind(
            "<<ComboboxSelected>>",
            self._clear_player_profile_status,
        )

        add_button = tk.Button(
            panel,
            text="Add",
            command=self._add_profile_commander,
            bg="#f7d046",
            fg="#141414",
            activebackground="#ffe176",
            activeforeground="#141414",
            font=("Arial", 12, "bold"),
            padx=12,
            pady=5,
            relief="raised",
            bd=2,
            cursor="hand2",
        )
        add_button.grid(row=4, column=2, sticky="ew", padx=(10, 0), pady=8)

        delete_button = tk.Button(
            panel,
            text="Delete",
            command=self._delete_selected_profile_commander,
            bg="#f1f5f9",
            fg="#141414",
            activebackground="#ffffff",
            activeforeground="#141414",
            font=("Arial", 12, "bold"),
            padx=12,
            pady=5,
            relief="raised",
            bd=2,
            cursor="hand2",
        )
        delete_button.grid(row=4, column=3, sticky="ew", padx=(10, 0), pady=8)

        list_label = tk.Label(
            panel,
            text="Current Commanders",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
        )
        list_label.grid(row=5, column=0, columnspan=4, sticky="w", pady=(14, 6))

        self.profile_commander_list = tk.Listbox(
            panel,
            height=7,
            font=("Arial", 12, "bold"),
            bg="#f8fafc",
            fg="#141414",
            selectbackground="#f7d046",
            selectforeground="#141414",
        )
        self.profile_commander_list.grid(row=6, column=0, columnspan=4, sticky="nsew")
        self.profile_commander_list.bind("<Button-1>", self._clear_player_profile_status)
        self._refresh_profile_commander_list()

        button_area = tk.Frame(panel, bg="#111827")
        button_area.grid(row=7, column=0, columnspan=4, pady=(18, 0))

        back_button = tk.Button(
            button_area,
            text="Back",
            command=self._show_start_screen,
            bg="#f1f5f9",
            fg="#141414",
            activebackground="#ffffff",
            activeforeground="#141414",
            font=("Arial", 13, "bold"),
            padx=22,
            pady=7,
            relief="raised",
            bd=2,
            cursor="hand2",
        )
        back_button.pack(side="left", padx=(0, 12))

        save_button = tk.Button(
            button_area,
            text="Save Player",
            command=self._save_player_profile,
            bg="#f7d046",
            fg="#141414",
            activebackground="#ffe176",
            activeforeground="#141414",
            font=("Arial", 13, "bold"),
            padx=22,
            pady=7,
            relief="raised",
            bd=2,
            cursor="hand2",
        )
        save_button.pack(side="left")

        status_label = tk.Label(
            panel,
            textvariable=self.player_profile_status,
            bg="#111827",
            fg="#f7d046",
            font=("Arial", 12, "bold"),
        )
        status_label.grid(row=8, column=0, columnspan=4, pady=(12, 0))

    def _draw_player_profile_background(self, event=None):
        width = self.player_profile_screen.winfo_width()
        height = self.player_profile_screen.winfo_height()

        self.player_profile_screen.delete("background")
        self.player_profile_screen.create_image(
            width // 2,
            height // 2,
            image=self.space_background,
            anchor="center",
            tags="background",
        )
        self.player_profile_screen.tag_lower("background")

        if self.player_profile_panel_window is not None:
            self.player_profile_screen.coords(
                self.player_profile_panel_window,
                width // 2,
                height // 2,
            )

    def _profile_options(self):
        return [CREATE_NEW_PROFILE, *sorted(self.player_profiles)]

    def _load_selected_player_profile(self):
        self._clear_player_profile_status()
        selected_profile = self.profile_selection.get()
        if selected_profile == CREATE_NEW_PROFILE:
            self._clear_player_profile_form()
            return

        self.profile_name.set(selected_profile)
        self.profile_total_wins.set(self.player_profile_wins.get(selected_profile, 0))
        self.profile_commander_name.set("")
        self.profile_loaded_name = selected_profile
        self.profile_commander_draft = list(self.player_profiles.get(selected_profile, []))
        self._refresh_profile_commander_list()

    def _clear_player_profile_form(self):
        self.profile_name.set("")
        self.profile_total_wins.set(0)
        self.profile_commander_name.set("")
        self.profile_loaded_name = ""
        self.profile_commander_draft = []
        self._refresh_profile_commander_list()

    def _refresh_profile_commander_list(self):
        if self.profile_commander_list is None:
            return

        self.profile_commander_list.delete(0, tk.END)
        for commander_name in self.profile_commander_draft:
            self.profile_commander_list.insert(tk.END, commander_name)

    def _add_profile_commander(self):
        self._clear_player_profile_status()
        commander_name = self.profile_commander_name.get().strip()
        if not commander_name:
            return

        if commander_name not in self.profile_commander_draft:
            self.profile_commander_draft.append(commander_name)
        self.profile_commander_name.set("")
        self._refresh_profile_commander_list()

    def _delete_selected_profile_commander(self):
        self._clear_player_profile_status()
        if self.profile_commander_list is None:
            return

        selected_indexes = self.profile_commander_list.curselection()
        if not selected_indexes:
            return

        selected_index = selected_indexes[0]
        if 0 <= selected_index < len(self.profile_commander_draft):
            del self.profile_commander_draft[selected_index]
            self._refresh_profile_commander_list()

    def _save_player_profile(self):
        player_name = self.profile_name.get().strip()
        if not player_name:
            return

        self.player_profiles[player_name] = list(self.profile_commander_draft)
        self.player_profile_wins[player_name] = self._clamp_input(
            self.profile_total_wins,
            minimum=0,
            maximum=999999,
        )
        self.last_profile_name = player_name
        self.profile_loaded_name = player_name
        self.profile_selection.set(player_name)
        self._backfill_commander_profiles_from_player_profiles()
        self._save_app_data()
        if self.profile_selector_menu is not None:
            self.profile_selector_menu.config(values=self._profile_options())
        self.player_profile_status.set("Player updates saved.")

    def _clear_player_profile_status(self, event=None):
        self.player_profile_status.set("")

    def _show_commander_profile_screen(self, reload_profile=True):
        self._clear_window()
        self.commander_preview_canvas = None
        self.commander_preview_label = None
        self.mana_icon_labels = {}
        self.second_commander_preview_canvas = None
        self.second_mana_icon_labels = {}
        self.commander_text_widget = None
        self.second_commander_text_widget = None

        self.commander_profile_screen = tk.Canvas(self, highlightthickness=0, bg="#0b1026")
        self.commander_profile_screen.pack(fill="both", expand=True)
        self._add_view_exit_button(self.commander_profile_screen)
        self.commander_profile_screen.bind(
            "<Configure>",
            self._draw_commander_profile_background,
        )

        if reload_profile:
            if self.last_commander_profile_name in self.commander_profiles:
                self.commander_profile_selection.set(self.last_commander_profile_name)
            else:
                self.commander_profile_selection.set(CREATE_NEW_COMMANDER_PROFILE)
            self._load_selected_commander_profile()

        panel = tk.Frame(self.commander_profile_screen, bg="#111827", padx=28, pady=22)
        self.commander_profile_panel_window = self.commander_profile_screen.create_window(
            260,
            230,
            window=panel,
            anchor="center",
            tags="commander_profile_panel",
        )

        title = tk.Label(
            panel,
            text="Commander Profile",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 26, "bold"),
        )
        title.grid(
            row=0,
            column=0,
            columnspan=6 if self.second_commander_enabled.get() else 3,
            pady=(0, 18),
        )

        selector_label = tk.Label(
            panel,
            text="Commander Profile",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
        )
        selector_label.grid(row=1, column=0, sticky="w", padx=(0, 14), pady=8)

        self.commander_profile_selector_menu = ttk.Combobox(
            panel,
            textvariable=self.commander_profile_selection,
            values=self._commander_profile_options(),
            state="readonly",
            font=("Arial", 12, "bold"),
            width=34,
        )
        self.commander_profile_selector_menu.bind(
            "<<ComboboxSelected>>",
            lambda event: self._load_selected_commander_profile(
                rebuild_on_second_change=True
            ),
        )
        self.commander_profile_selector_menu.grid(row=1, column=1, columnspan=2, sticky="ew", pady=8)

        name_label = tk.Label(
            panel,
            text="Commander Name",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
        )
        name_label.grid(row=2, column=0, sticky="w", padx=(0, 14), pady=8)

        name_input = tk.Entry(
            panel,
            textvariable=self.commander_profile_name,
            width=30,
            font=("Arial", 13, "bold"),
            state="readonly" if self.second_commander_enabled.get() else "normal",
        )
        name_input.grid(row=2, column=1, columnspan=2, sticky="ew", pady=8)
        name_input.bind("<KeyPress>", self._clear_commander_profile_status)

        image_label = tk.Label(
            panel,
            text="Commander Image",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
        )
        image_label.grid(row=3, column=0, sticky="w", padx=(0, 14), pady=8)

        image_input = tk.Entry(
            panel,
            textvariable=self.commander_image_filename,
            width=30,
            font=("Arial", 11, "bold"),
            state="readonly",
        )
        image_input.grid(row=3, column=1, sticky="ew", pady=8)

        image_button = tk.Button(
            panel,
            text="Browse",
            command=self._browse_commander_image,
            bg="#f7d046",
            fg="#141414",
            activebackground="#ffe176",
            activeforeground="#141414",
            font=("Arial", 11, "bold"),
            padx=12,
            pady=5,
            relief="raised",
            bd=2,
            cursor="hand2",
        )
        image_button.grid(row=3, column=2, sticky="ew", padx=(10, 0), pady=8)

        preview_label = tk.Label(
            panel,
            text="Image Preview",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
        )
        preview_label.grid(row=4, column=0, sticky="w", padx=(0, 14), pady=8)

        self.commander_preview_canvas = tk.Canvas(
            panel,
            width=200,
            height=100,
            bg="#020617",
            highlightthickness=0,
            relief="sunken",
            bd=2,
        )
        self.commander_preview_canvas.grid(row=4, column=1, sticky="w", pady=8)
        self.commander_preview_label = self.commander_preview_canvas
        self._update_commander_image_preview()

        wins_area = tk.Frame(panel, bg="#111827")
        wins_area.grid(row=4, column=2, sticky="w", padx=(10, 0), pady=8)

        wins_label = tk.Label(
            wins_area,
            text="Total Wins",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
        )
        wins_label.pack(anchor="w", pady=(0, 6))

        wins_input = tk.Entry(
            wins_area,
            textvariable=self.commander_total_wins,
            width=10,
            font=("Arial", 11, "bold"),
        )
        wins_input.pack(anchor="w")
        wins_input.bind("<KeyPress>", self._clear_commander_profile_status)

        power_label = tk.Label(
            panel,
            text="Power / Toughness",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
        )
        power_label.grid(row=5, column=0, sticky="w", padx=(0, 14), pady=8)

        power_area = tk.Frame(panel, bg="#111827")
        power_area.grid(row=5, column=1, columnspan=2, sticky="w", pady=8)
        self._create_number_field(
            power_area,
            "Attack",
            self.commander_attack_power,
            column=0,
        )
        self._create_number_field(
            power_area,
            "Defense",
            self.commander_defense_power,
            column=1,
        )

        color_label = tk.Label(
            panel,
            text="Colors",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
        )
        color_label.grid(row=6, column=0, sticky="w", padx=(0, 14), pady=12)

        color_area = tk.Frame(panel, bg="#111827")
        color_area.grid(row=6, column=1, columnspan=2, sticky="w", pady=12)

        for column, color_name in enumerate(MANA_COLORS):
            self._create_mana_icon_selector(
                color_area,
                color_name,
                column,
                self.commander_color_vars,
                self.mana_icon_labels,
                self.commander_color_cost_vars,
            )

        text_label = tk.Label(
            panel,
            text="Commander Text",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
        )
        text_label.grid(row=7, column=0, sticky="w", padx=(0, 14), pady=8)

        commander_text_input = scrolledtext.ScrolledText(
            panel,
            width=46,
            height=6,
            wrap="word",
            font=("Arial", 11, "bold"),
        )
        commander_text_input.insert("1.0", self.commander_text.get())
        commander_text_input.grid(
            row=7,
            column=1,
            columnspan=2,
            sticky="ew",
            pady=8,
        )
        commander_text_input.bind("<KeyRelease>", self._sync_commander_text_input)
        self.commander_text_widget = commander_text_input

        second_toggle = tk.Checkbutton(
            panel,
            text="Enable 2nd Commander",
            variable=self.second_commander_enabled,
            command=self._toggle_second_commander_section,
            bg="#111827",
            fg="#ffffff",
            selectcolor="#111827",
            activebackground="#111827",
            activeforeground="#f7d046",
            font=("Arial", 13, "bold"),
        )
        second_toggle.grid(
            row=8,
            column=0,
            columnspan=6 if self.second_commander_enabled.get() else 3,
            sticky="w",
            pady=(12, 0),
        )

        next_row = 9
        if self.second_commander_enabled.get():
            self._build_second_commander_section(panel, start_row=1, start_column=3)

        button_area = tk.Frame(panel, bg="#111827")
        button_area.grid(
            row=next_row,
            column=0,
            columnspan=6 if self.second_commander_enabled.get() else 3,
            pady=(18, 0),
        )

        back_button = tk.Button(
            button_area,
            text="Back",
            command=self._show_start_screen,
            bg="#f1f5f9",
            fg="#141414",
            activebackground="#ffffff",
            activeforeground="#141414",
            font=("Arial", 13, "bold"),
            padx=22,
            pady=7,
            relief="raised",
            bd=2,
            cursor="hand2",
        )
        back_button.pack(side="left", padx=(0, 12))

        delete_button = tk.Button(
            button_area,
            text="Delete Commander",
            command=self._delete_commander_profile,
            bg="#dc2626",
            fg="#ffffff",
            activebackground="#ef4444",
            activeforeground="#ffffff",
            font=("Arial", 13, "bold"),
            padx=22,
            pady=7,
            relief="raised",
            bd=2,
            cursor="hand2",
        )
        delete_button.pack(side="left", padx=(0, 12))

        save_button = tk.Button(
            button_area,
            text="Save Commander",
            command=self._save_commander_profile,
            bg="#f7d046",
            fg="#141414",
            activebackground="#ffe176",
            activeforeground="#141414",
            font=("Arial", 13, "bold"),
            padx=22,
            pady=7,
            relief="raised",
            bd=2,
            cursor="hand2",
        )
        save_button.pack(side="left")

        status_label = tk.Label(
            panel,
            textvariable=self.commander_profile_status,
            bg="#111827",
            fg="#f7d046",
            font=("Arial", 12, "bold"),
        )
        status_label.grid(
            row=next_row + 1,
            column=0,
            columnspan=6 if self.second_commander_enabled.get() else 3,
            pady=(12, 0),
        )

    def _draw_commander_profile_background(self, event=None):
        width = self.commander_profile_screen.winfo_width()
        height = self.commander_profile_screen.winfo_height()

        self.commander_profile_screen.delete("background")
        self.commander_profile_screen.create_image(
            width // 2,
            height // 2,
            image=self.space_background,
            anchor="center",
            tags="background",
        )
        self.commander_profile_screen.tag_lower("background")

        if self.commander_profile_panel_window is not None:
            self.commander_profile_screen.coords(
                self.commander_profile_panel_window,
                width // 2,
                height // 2,
            )

    def _build_second_commander_section(self, panel, start_row, start_column):
        section_title = tk.Label(
            panel,
            text="2nd Commander",
            bg="#111827",
            fg="#f7d046",
            font=("Arial", 16, "bold"),
        )
        section_title.grid(
            row=start_row,
            column=start_column,
            columnspan=3,
            sticky="w",
            padx=(28, 0),
            pady=(0, 8),
        )

        commander_label = tk.Label(
            panel,
            text="2nd Commander",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
        )
        commander_label.grid(
            row=start_row + 1,
            column=start_column,
            sticky="w",
            padx=(28, 14),
            pady=8,
        )

        commander_input = ttk.Combobox(
            panel,
            textvariable=self.second_commander_name,
            values=self._single_commander_profile_options(),
            state="readonly",
            font=("Arial", 12, "bold"),
            width=34,
        )
        commander_input.bind(
            "<<ComboboxSelected>>",
            self._select_second_commander_profile,
        )
        commander_input.grid(
            row=start_row + 1,
            column=start_column + 1,
            columnspan=2,
            sticky="ew",
            pady=8,
        )

        image_label = tk.Label(
            panel,
            text="2nd Commander Image",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
        )
        image_label.grid(
            row=start_row + 2,
            column=start_column,
            sticky="w",
            padx=(28, 14),
            pady=8,
        )

        image_input = tk.Entry(
            panel,
            textvariable=self.second_commander_image_filename,
            width=30,
            font=("Arial", 11, "bold"),
            state="readonly",
        )
        image_input.grid(row=start_row + 2, column=start_column + 1, sticky="ew", pady=8)

        image_button = tk.Button(
            panel,
            text="Browse",
            command=self._browse_second_commander_image,
            bg="#f7d046",
            fg="#141414",
            activebackground="#ffe176",
            activeforeground="#141414",
            font=("Arial", 11, "bold"),
            padx=12,
            pady=5,
            relief="raised",
            bd=2,
            cursor="hand2",
        )
        image_button.grid(
            row=start_row + 2,
            column=start_column + 2,
            sticky="ew",
            padx=(10, 0),
            pady=8,
        )

        preview_label = tk.Label(
            panel,
            text="2nd Image Preview",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
        )
        preview_label.grid(
            row=start_row + 3,
            column=start_column,
            sticky="w",
            padx=(28, 14),
            pady=8,
        )

        self.second_commander_preview_canvas = tk.Canvas(
            panel,
            width=200,
            height=100,
            bg="#020617",
            highlightthickness=0,
            relief="sunken",
            bd=2,
        )
        self.second_commander_preview_canvas.grid(
            row=start_row + 3,
            column=start_column + 1,
            columnspan=2,
            sticky="w",
            pady=8,
        )
        self._update_second_commander_image_preview()

        power_label = tk.Label(
            panel,
            text="2nd Power / Toughness",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
        )
        power_label.grid(
            row=start_row + 4,
            column=start_column,
            sticky="w",
            padx=(28, 14),
            pady=8,
        )

        power_area = tk.Frame(panel, bg="#111827")
        power_area.grid(
            row=start_row + 4,
            column=start_column + 1,
            columnspan=2,
            sticky="w",
            pady=8,
        )
        self._create_number_field(
            power_area,
            "Attack",
            self.second_commander_attack_power,
            column=0,
        )
        self._create_number_field(
            power_area,
            "Defense",
            self.second_commander_defense_power,
            column=1,
        )

        color_label = tk.Label(
            panel,
            text="2nd Colors",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
        )
        color_label.grid(
            row=start_row + 5,
            column=start_column,
            sticky="w",
            padx=(28, 14),
            pady=12,
        )

        color_area = tk.Frame(panel, bg="#111827")
        color_area.grid(
            row=start_row + 5,
            column=start_column + 1,
            columnspan=2,
            sticky="w",
            pady=12,
        )
        for column, color_name in enumerate(MANA_COLORS):
            self._create_mana_icon_selector(
                color_area,
                color_name,
                column,
                self.second_commander_color_vars,
                self.second_mana_icon_labels,
                self.second_commander_color_cost_vars,
            )

        text_label = tk.Label(
            panel,
            text="2nd Commander Text",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
        )
        text_label.grid(
            row=start_row + 6,
            column=start_column,
            sticky="w",
            padx=(28, 14),
            pady=8,
        )

        second_commander_text_input = scrolledtext.ScrolledText(
            panel,
            width=46,
            height=6,
            wrap="word",
            font=("Arial", 11, "bold"),
        )
        second_commander_text_input.insert("1.0", self.second_commander_text.get())
        second_commander_text_input.grid(
            row=start_row + 6,
            column=start_column + 1,
            columnspan=2,
            sticky="ew",
            pady=8,
        )
        second_commander_text_input.bind("<KeyRelease>", self._sync_second_commander_text_input)
        self.second_commander_text_widget = second_commander_text_input

        return start_row + 7

    def _commander_profile_options(self):
        return [CREATE_NEW_COMMANDER_PROFILE, *sorted(self.commander_profiles)]

    def _single_commander_profile_options(self):
        return [
            commander_name
            for commander_name, profile in sorted(self.commander_profiles.items())
            if commander_name != self.primary_commander_name
            and not self._clean_second_commander_profile(
                profile.get("second_commander", {})
            )["enabled"]
        ]

    def _select_second_commander_profile(self, event=None):
        self._clear_commander_profile_status()
        self._load_commander_texts()
        commander_name = self.second_commander_name.get().strip()
        profile = self.commander_profiles.get(commander_name, {})

        self._set_second_commander_image_path(profile.get("image_path", ""))
        self._set_second_commander_text_value(
            self.commander_texts.get(commander_name, "")
        )
        self.second_commander_attack_power.set(
            self._clamp_plain_number(profile.get("attack_power", 0), 0, 99)
        )
        self.second_commander_defense_power.set(
            self._clamp_plain_number(profile.get("defense_power", 0), 0, 99)
        )
        self._set_second_commander_colors(profile.get("colors", []))
        self._set_color_cost_vars(
            profile.get("color_cost", {}),
            self.second_commander_color_cost_vars,
        )
        self._update_second_commander_image_preview()
        self._update_combined_commander_profile_name()
        self._update_combined_commander_text()

    def _sync_commander_text_input(self, event=None):
        if self.commander_text_widget is not None:
            self.commander_text.set(
                self.commander_text_widget.get("1.0", "end-1c")
            )
        self._clear_commander_profile_status()

    def _sync_second_commander_text_input(self, event=None):
        if self.second_commander_text_widget is not None:
            self.second_commander_text.set(
                self.second_commander_text_widget.get("1.0", "end-1c")
            )
        self._clear_commander_profile_status()

    def _set_commander_text_value(self, value):
        self.commander_text.set(value)
        if self.commander_text_widget is not None:
            self.commander_text_widget.delete("1.0", tk.END)
            self.commander_text_widget.insert("1.0", value)

    def _set_second_commander_text_value(self, value):
        self.second_commander_text.set(value)
        if self.second_commander_text_widget is not None:
            self.second_commander_text_widget.delete("1.0", tk.END)
            self.second_commander_text_widget.insert("1.0", value)

    def _combined_commander_text(self, primary_name, second_name):
        primary_text = self.commander_texts.get(primary_name, "").strip()
        second_text = self.commander_texts.get(second_name, "").strip()
        sections = []
        if primary_text:
            sections.append(f"{primary_name}\n{primary_text}")
        if second_text:
            sections.append(f"{second_name}\n{second_text}")
        return "\n\n".join(sections)

    def _update_combined_commander_text(self):
        if not self.second_commander_enabled.get():
            return
        combined_text = self._combined_commander_text(
            self.primary_commander_name.strip(),
            self.second_commander_name.get().strip(),
        )
        self._set_commander_text_value(combined_text)

    def _load_selected_commander_profile(self, rebuild_on_second_change=False):
        self._clear_commander_profile_status()
        self._load_commander_texts()
        self._set_commander_colors([])
        second_was_enabled = self.second_commander_enabled.get()
        selected_profile = self.commander_profile_selection.get()
        if selected_profile == CREATE_NEW_COMMANDER_PROFILE:
            self._clear_commander_profile_form()
            if rebuild_on_second_change and second_was_enabled != self.second_commander_enabled.get():
                self._show_commander_profile_screen(reload_profile=False)
            return

        profile = self.commander_profiles.get(selected_profile, {})
        self.primary_commander_name = str(
            profile.get("primary_name", selected_profile.split(" / ", 1)[0])
        ).strip()
        self.commander_profile_name.set(selected_profile)
        self.commander_total_wins.set(
            self._clamp_plain_number(profile.get("total_wins", 0), 0, 999999)
        )
        self.commander_attack_power.set(
            self._clamp_plain_number(profile.get("attack_power", 0), 0, 99)
        )
        self.commander_defense_power.set(
            self._clamp_plain_number(profile.get("defense_power", 0), 0, 99)
        )
        self._set_commander_image_path(profile.get("image_path", ""))
        self._set_commander_text_value(self.commander_texts.get(selected_profile, ""))
        self._set_commander_colors(profile.get("colors", []))
        self._set_color_cost_vars(profile.get("color_cost", {}), self.commander_color_cost_vars)
        self._load_second_commander_data(profile.get("second_commander", {}))
        if self.second_commander_enabled.get():
            self._update_combined_commander_profile_name()
        self._update_commander_image_preview()
        if rebuild_on_second_change and second_was_enabled != self.second_commander_enabled.get():
            self._show_commander_profile_screen(reload_profile=False)

    def _clear_commander_profile_form(self):
        self.primary_commander_name = ""
        self.commander_profile_name.set("")
        self.commander_total_wins.set(0)
        self.commander_attack_power.set(0)
        self.commander_defense_power.set(0)
        self._set_commander_image_path("")
        self._set_commander_text_value("")
        self._set_commander_colors([])
        self._set_color_cost_vars({}, self.commander_color_cost_vars)
        self._load_second_commander_data({})
        self._update_commander_image_preview()

    def _load_second_commander_data(self, profile):
        profile = self._clean_second_commander_profile(profile)
        self.second_commander_enabled.set(profile["enabled"])
        if not profile["enabled"]:
            self._clear_second_commander_data()
            return

        self.second_commander_name.set(profile["name"])
        self._set_second_commander_image_path(profile["image_path"])
        self._set_second_commander_text_value(
            self.commander_texts.get(profile["name"], "")
        )
        self.second_commander_attack_power.set(profile["attack_power"])
        self.second_commander_defense_power.set(profile["defense_power"])
        self._set_second_commander_colors(profile["colors"])
        self._set_color_cost_vars(profile["color_cost"], self.second_commander_color_cost_vars)
        self._update_second_commander_image_preview()

    def _clear_second_commander_data(self):
        self.second_commander_name.set("")
        self._set_second_commander_image_path("")
        self._set_second_commander_text_value("")
        self.second_commander_attack_power.set(0)
        self.second_commander_defense_power.set(0)
        self._set_second_commander_colors([])
        self._set_color_cost_vars({}, self.second_commander_color_cost_vars)
        self._update_second_commander_image_preview()

    def _set_commander_colors(self, selected_colors):
        self._set_color_vars(selected_colors, self.commander_color_vars, self.mana_icon_labels)

    def _set_second_commander_colors(self, selected_colors):
        self._set_color_vars(
            selected_colors,
            self.second_commander_color_vars,
            self.second_mana_icon_labels,
        )

    def _set_color_vars(self, selected_colors, color_vars, icon_labels):
        selected_color_set = set(selected_colors)
        for color_name, color_var in color_vars.items():
            color_var.set(color_name in selected_color_set)
            if color_name in icon_labels:
                icon_labels[color_name].config(
                    image=self._mana_icon_image(color_name, color_var.get())
                )

    def _set_color_cost_vars(self, color_cost, color_cost_vars):
        clean_color_cost = self._clean_color_cost(color_cost)
        for color_name, color_var in color_cost_vars.items():
            color_var.set(clean_color_cost[color_name])

    def _selected_commander_colors(self):
        return self._selected_colors(self.commander_color_vars)

    def _selected_second_commander_colors(self):
        return self._selected_colors(self.second_commander_color_vars)

    def _selected_commander_color_cost(self):
        return self._selected_color_cost(self.commander_color_cost_vars)

    def _selected_second_commander_color_cost(self):
        return self._selected_color_cost(self.second_commander_color_cost_vars)

    def _selected_colors(self, color_vars):
        return [
            color_name
            for color_name, color_var in color_vars.items()
            if color_var.get()
        ]

    def _selected_color_cost(self, color_cost_vars):
        return {
            color_name: self._clamp_input(
                color_var,
                minimum=0,
                maximum=99,
            )
            for color_name, color_var in color_cost_vars.items()
        }

    def _create_number_field(self, parent, label_text, variable, column):
        field_area = tk.Frame(parent, bg="#111827")
        field_area.grid(row=0, column=column, padx=(0, 14), sticky="w")

        label = tk.Label(
            field_area,
            text=label_text,
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
        )
        label.pack(anchor="w")

        number_input = tk.Spinbox(
            field_area,
            from_=0,
            to=99,
            textvariable=variable,
            width=4,
            font=("Arial", 11, "bold"),
            bg="#f8fafc",
            fg="#111827",
            justify="center",
        )
        number_input.pack(anchor="w", pady=(3, 0))
        number_input.bind("<KeyPress>", self._clear_commander_profile_status)
        number_input.bind("<ButtonRelease-1>", self._clear_commander_profile_status)

    def _create_mana_icon_selector(
        self,
        parent,
        color_name,
        column,
        color_vars,
        icon_labels,
        color_cost_vars=None,
    ):
        selected = color_vars[color_name].get()
        icon = self._mana_icon_image(color_name, selected)
        icon_label = tk.Label(parent, image=icon, bg="#111827")
        icon_labels[color_name] = icon_label
        icon_label.grid(row=0, column=column, padx=6)
        icon_label.bind(
            "<Button-1>",
            lambda event, name=color_name, label=icon_label, vars_map=color_vars: self._toggle_commander_color(
                name,
                label,
                vars_map,
            ),
        )
        icon_label.bind("<Enter>", lambda event: icon_label.config(cursor="hand2"))
        icon_label.bind("<Leave>", lambda event: icon_label.config(cursor=""))

        if color_cost_vars is not None:
            cost_input = tk.Spinbox(
                parent,
                from_=0,
                to=99,
                textvariable=color_cost_vars[color_name],
                width=3,
                font=("Arial", 10, "bold"),
                bg="#f8fafc",
                fg="#111827",
                justify="center",
            )
            cost_input.grid(row=1, column=column, padx=6, pady=(4, 0))
            cost_input.bind("<KeyPress>", self._clear_commander_profile_status)
            cost_input.bind("<ButtonRelease-1>", self._clear_commander_profile_status)

    def _toggle_commander_color(self, color_name, icon_label, color_vars):
        self._clear_commander_profile_status()
        selected = not color_vars[color_name].get()
        color_vars[color_name].set(selected)
        icon_label.config(image=self._mana_icon_image(color_name, selected))

    def _mana_icon_image(self, color_name, selected):
        cache_key = (color_name, selected)
        if cache_key not in self.mana_icon_images:
            source_path = MANA_DIR / f"{color_name}.png"
            state_name = "full" if selected else "faded"
            icon_path = MANA_DIR / f"{color_name}_{state_name}_42.png"
            if not icon_path.exists():
                if color_name == "colorless":
                    image = self._colorless_mana_icon()
                else:
                    image = Image.open(source_path).convert("RGBA")
                    image.thumbnail((42, 42), Image.LANCZOS)
                alpha = image.getchannel("A")
                if not selected:
                    alpha = ImageEnhance.Brightness(alpha).enhance(0.5)
                    image.putalpha(alpha)
                image.save(icon_path)
            self.mana_icon_images[cache_key] = tk.PhotoImage(file=icon_path)

        return self.mana_icon_images[cache_key]

    def _colorless_mana_icon(self):
        image = Image.new("RGBA", (42, 42), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((3, 3, 39, 39), fill="#a3a3a3", outline="#e5e7eb", width=2)
        return image

    def _update_commander_image_preview(self):
        if self.commander_preview_canvas is None:
            return

        image_path = self.commander_image_path.get().strip()
        self.commander_preview_image = None
        self.commander_preview_canvas.delete("all")

        if not image_path:
            self.commander_preview_canvas.create_text(
                100,
                50,
                text="No Image Selected",
                fill="#ffffff",
                font=("Arial", 11, "bold"),
            )
            return

        try:
            image = tk.PhotoImage(file=resolve_app_path(image_path))
        except tk.TclError:
            self.commander_preview_canvas.create_text(
                100,
                50,
                text="Preview unavailable",
                fill="#ffffff",
                font=("Arial", 11, "bold"),
            )
            return

        max_width = 200
        max_height = 100
        scale = max(
            1,
            (image.width() + max_width - 1) // max_width,
            (image.height() + max_height - 1) // max_height,
        )
        self.commander_preview_image = image.subsample(scale, scale)
        self.commander_preview_canvas.create_image(
            100,
            50,
            image=self.commander_preview_image,
            anchor="center",
        )

    def _update_second_commander_image_preview(self):
        if self.second_commander_preview_canvas is None:
            return

        image_path = self.second_commander_image_path.get().strip()
        self.second_commander_preview_image = None
        self.second_commander_preview_canvas.delete("all")

        if not image_path:
            self.second_commander_preview_canvas.create_text(
                100,
                50,
                text="No Image Selected",
                fill="#ffffff",
                font=("Arial", 11, "bold"),
            )
            return

        try:
            image = tk.PhotoImage(file=resolve_app_path(image_path))
        except tk.TclError:
            self.second_commander_preview_canvas.create_text(
                100,
                50,
                text="Preview unavailable",
                fill="#ffffff",
                font=("Arial", 11, "bold"),
            )
            return

        scale = max(
            1,
            (image.width() + 199) // 200,
            (image.height() + 99) // 100,
        )
        self.second_commander_preview_image = image.subsample(scale, scale)
        self.second_commander_preview_canvas.create_image(
            100,
            50,
            image=self.second_commander_preview_image,
            anchor="center",
        )

    def _set_commander_image_path(self, image_path):
        self.commander_image_path.set(app_relative_path(image_path))
        self.commander_image_filename.set(Path(image_path).name if image_path else "")

    def _set_second_commander_image_path(self, image_path):
        self.second_commander_image_path.set(app_relative_path(image_path))
        self.second_commander_image_filename.set(Path(image_path).name if image_path else "")

    def _browse_commander_image(self):
        self._clear_commander_profile_status()
        COMMANDERS_DIR.mkdir(parents=True, exist_ok=True)
        image_path = filedialog.askopenfilename(
            title="Select Commander Image",
            initialdir=COMMANDERS_DIR,
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All Files", "*.*"),
            ],
        )
        if image_path:
            self._set_commander_image_path(image_path)
            self._update_commander_image_preview()

    def _browse_second_commander_image(self):
        self._clear_commander_profile_status()
        COMMANDERS_DIR.mkdir(parents=True, exist_ok=True)
        image_path = filedialog.askopenfilename(
            title="Select 2nd Commander Image",
            initialdir=COMMANDERS_DIR,
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All Files", "*.*"),
            ],
        )
        if image_path:
            self._set_second_commander_image_path(image_path)
            self._update_second_commander_image_preview()

    def _toggle_second_commander_section(self):
        self._clear_commander_profile_status()
        if self.second_commander_enabled.get():
            current_name = self.commander_profile_name.get().strip()
            self.primary_commander_name = (
                current_name.split(" / ", 1)[0]
                if " / " in current_name
                else current_name
            )
            self._update_combined_commander_profile_name()
            self._update_combined_commander_text()
        else:
            self._clear_second_commander_data()
            self.commander_profile_name.set(self.primary_commander_name)
        self._show_commander_profile_screen(reload_profile=False)

    def _update_combined_commander_profile_name(self, event=None):
        if not self.second_commander_enabled.get():
            return

        primary_name = self.primary_commander_name.strip()
        second_name = self.second_commander_name.get().strip()
        if primary_name and second_name:
            self.commander_profile_name.set(f"{primary_name} / {second_name}")
        else:
            self.commander_profile_name.set(primary_name)

    def _save_commander_profile(self):
        self._sync_commander_text_input()
        self._sync_second_commander_text_input()
        if self.second_commander_enabled.get():
            self._update_combined_commander_profile_name()
        commander_name = self.commander_profile_name.get().strip()
        if not commander_name:
            return
        if self.second_commander_enabled.get() and not self.second_commander_name.get().strip():
            return

        primary_name = (
            self.primary_commander_name.strip()
            if self.second_commander_enabled.get()
            else commander_name
        )
        self.commander_profiles[commander_name] = {
            "primary_name": primary_name,
            "image_path": self.commander_image_path.get().strip(),
            "text_path": app_relative_path(COMMANDER_TEXT_FILE),
            "total_wins": self._clamp_input(
                self.commander_total_wins,
                minimum=0,
                maximum=999999,
            ),
            "attack_power": self._clamp_input(
                self.commander_attack_power,
                minimum=0,
                maximum=99,
            ),
            "defense_power": self._clamp_input(
                self.commander_defense_power,
                minimum=0,
                maximum=99,
            ),
            "colors": self._selected_commander_colors(),
            "color_cost": self._selected_commander_color_cost(),
            "second_commander": {
                "enabled": self.second_commander_enabled.get(),
                "name": self.second_commander_name.get().strip()
                if self.second_commander_enabled.get()
                else "",
                "image_path": self.second_commander_image_path.get().strip()
                if self.second_commander_enabled.get()
                else "",
                "text_path": app_relative_path(COMMANDER_TEXT_FILE)
                if self.second_commander_enabled.get()
                else "",
                "attack_power": self._clamp_input(
                    self.second_commander_attack_power,
                    minimum=0,
                    maximum=99,
                )
                if self.second_commander_enabled.get()
                else 0,
                "defense_power": self._clamp_input(
                    self.second_commander_defense_power,
                    minimum=0,
                    maximum=99,
                )
                if self.second_commander_enabled.get()
                else 0,
                "colors": self._selected_second_commander_colors()
                if self.second_commander_enabled.get()
                else [],
                "color_cost": self._selected_second_commander_color_cost()
                if self.second_commander_enabled.get()
                else self._empty_color_cost(),
            },
        }
        self._load_commander_texts()
        self.commander_texts[commander_name] = self.commander_text.get().strip()
        if self.second_commander_enabled.get():
            second_commander_name = self.second_commander_name.get().strip()
            if second_commander_name:
                self.commander_texts[second_commander_name] = (
                    self.second_commander_text.get().strip()
                )
        self._save_commander_texts()
        self.last_commander_profile_name = commander_name
        self.commander_profile_selection.set(commander_name)
        self._save_app_data()
        if self.commander_profile_selector_menu is not None:
            self.commander_profile_selector_menu.config(values=self._commander_profile_options())
        self.commander_profile_status.set("Commander updates saved.")

    def _delete_commander_profile(self):
        selected_profile = self.commander_profile_selection.get()
        if (
            selected_profile == CREATE_NEW_COMMANDER_PROFILE
            or selected_profile not in self.commander_profiles
        ):
            return

        del self.commander_profiles[selected_profile]
        if self.last_commander_profile_name == selected_profile:
            self.last_commander_profile_name = ""
        self.commander_profile_selection.set(CREATE_NEW_COMMANDER_PROFILE)
        self._clear_commander_profile_form()
        self._save_app_data()
        self._show_commander_profile_screen(reload_profile=False)
        self.commander_profile_status.set("Commander profile deleted.")

    def _clear_commander_profile_status(self, event=None):
        self.commander_profile_status.set("")

    def _show_settings_screen(self):
        self._clear_window()

        self.settings_screen = tk.Canvas(self, highlightthickness=0, bg="#0b1026")
        self.settings_screen.pack(fill="both", expand=True)
        self._add_view_exit_button(
            self.settings_screen,
            command=self._save_settings_and_show_start_screen,
        )
        self.settings_screen.bind("<Configure>", self._draw_settings_background)

        self.back_button = tk.Button(
            self.settings_screen,
            text="Back",
            command=self._save_settings_and_show_start_screen,
            bg="#f1f5f9",
            fg="#141414",
            activebackground="#ffffff",
            activeforeground="#141414",
            font=("Arial", 11, "bold"),
            padx=12,
            pady=5,
            relief="raised",
            bd=2,
            cursor="hand2",
        )
        self.back_button_window = self.settings_screen.create_window(
            20,
            18,
            window=self.back_button,
            anchor="nw",
            tags="back_button",
        )

        panel = tk.Frame(self.settings_screen, bg="#111827", padx=30, pady=24)
        self.settings_panel_window = self.settings_screen.create_window(
            260,
            230,
            window=panel,
            anchor="center",
            tags="settings_panel",
        )

        title = tk.Label(
            panel,
            text="Settings",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 26, "bold"),
        )
        title.grid(row=0, column=0, columnspan=2, pady=(0, 18))

        self._add_settings_row(
            panel,
            "Number of Players",
            1,
            self.number_of_players,
            minimum=2,
            maximum=6,
        )
        self._add_settings_row(
            panel,
            "Starting Life Total",
            2,
            self.starting_life_total,
            minimum=1,
            maximum=999,
        )

        game_type_label = tk.Label(
            panel,
            text="Game Type",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
        )
        game_type_label.grid(row=3, column=0, sticky="w", padx=(0, 16), pady=9)

        game_type_menu = tk.OptionMenu(panel, self.game_type, "Commander", "Standard")
        game_type_menu.config(
            bg="#f8fafc",
            fg="#141414",
            activebackground="#e2e8f0",
            font=("Arial", 12, "bold"),
            width=14,
        )
        game_type_menu["menu"].config(font=("Arial", 12, "bold"))
        game_type_menu.grid(row=3, column=1, sticky="ew", pady=9)

        start_button = tk.Button(
            panel,
            text="New Game",
            command=self._save_settings_and_show_player_setup_screen,
            bg="#f7d046",
            fg="#141414",
            activebackground="#ffe176",
            activeforeground="#141414",
            font=("Arial", 15, "bold"),
            padx=24,
            pady=9,
            relief="raised",
            bd=3,
            cursor="hand2",
        )
        start_button.grid(row=4, column=0, columnspan=2, pady=(24, 0))

    def _draw_settings_background(self, event=None):
        width = self.settings_screen.winfo_width()
        height = self.settings_screen.winfo_height()

        self.settings_screen.delete("background")
        self.settings_screen.create_image(
            width // 2,
            height // 2,
            image=self.space_background,
            anchor="center",
            tags="background",
        )
        self.settings_screen.tag_lower("background")

        if self.settings_panel_window is not None:
            self.settings_screen.coords(self.settings_panel_window, width // 2, height // 2)
        if self.back_button_window is not None:
            self.settings_screen.coords(self.back_button_window, 20, 18)
            self.settings_screen.tag_raise("back_button")

    def _add_settings_row(self, parent, label_text, row, value, minimum, maximum):
        label = tk.Label(
            parent,
            text=label_text,
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 13, "bold"),
        )
        label.grid(row=row, column=0, sticky="w", padx=(0, 16), pady=9)

        input_area = tk.Frame(parent, bg="#111827")
        input_area.grid(row=row, column=1, sticky="ew", pady=9)
        input_area.grid_columnconfigure(0, weight=1)

        input_box = tk.Entry(
            input_area,
            textvariable=value,
            width=9,
            font=("Arial", 18, "bold"),
            justify="center",
        )
        validate_command = (self.register(lambda text: self._is_valid_number(text, minimum, maximum)), "%P")
        input_box.config(validate="key", validatecommand=validate_command)
        input_box.grid(row=0, column=0, rowspan=2, sticky="nsew")

        up_button = tk.Button(
            input_area,
            text="▲",
            command=lambda: self._change_number(value, 1, minimum, maximum),
            bg="#f7d046",
            fg="#141414",
            activebackground="#ffe176",
            activeforeground="#141414",
            font=("Arial", 11, "bold"),
            width=3,
            height=1,
            relief="raised",
            bd=2,
            cursor="hand2",
        )
        up_button.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        down_button = tk.Button(
            input_area,
            text="▼",
            command=lambda: self._change_number(value, -1, minimum, maximum),
            bg="#f7d046",
            fg="#141414",
            activebackground="#ffe176",
            activeforeground="#141414",
            font=("Arial", 11, "bold"),
            width=3,
            height=1,
            relief="raised",
            bd=2,
            cursor="hand2",
        )
        down_button.grid(row=1, column=1, sticky="nsew", padx=(6, 0))

    def _change_number(self, value, amount, minimum, maximum):
        try:
            current_value = value.get()
        except tk.TclError:
            current_value = minimum

        value.set(max(minimum, min(maximum, current_value + amount)))

    def _is_valid_number(self, text, minimum, maximum):
        if text == "":
            return True
        if not text.isdigit():
            return False

        return minimum <= int(text) <= maximum

    def _save_settings(self):
        self.number_of_players.set(
            self._clamp_input(self.number_of_players, minimum=2, maximum=6)
        )
        if self.planechase_enabled.get() and self.number_of_players.get() > 5:
            self.number_of_players.set(5)
        self.starting_life_total.set(
            self._clamp_input(self.starting_life_total, minimum=1, maximum=999)
        )
        self._save_app_data()

    def _clamp_input(self, value, minimum, maximum):
        try:
            current_value = value.get()
        except tk.TclError:
            current_value = minimum

        return max(minimum, min(maximum, current_value))

    def _save_settings_and_show_start_screen(self):
        self._save_settings()
        self._show_start_screen()

    def _save_settings_and_show_player_setup_screen(self):
        self._save_settings()
        self._show_player_setup_screen()

    def _show_player_setup_screen(self):
        self._save_settings()
        self._ensure_player_fields()
        self._clear_window()

        self.player_setup_screen = tk.Canvas(self, highlightthickness=0, bg="#0b1026")
        self.player_setup_screen.pack(fill="both", expand=True)
        self._add_view_exit_button(self.player_setup_screen)
        self.player_setup_screen.bind("<Configure>", self._draw_player_setup_background)

        panel = tk.Frame(self.player_setup_screen, bg="#111827", padx=24, pady=18)
        self.player_setup_panel_window = self.player_setup_screen.create_window(
            260,
            230,
            window=panel,
            anchor="center",
            tags="player_setup_panel",
        )

        title = tk.Label(
            panel,
            text="Players",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 24, "bold"),
        )
        title.grid(row=0, column=0, columnspan=3, pady=(0, 12))

        name_header = tk.Label(
            panel,
            text="Player Name",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 12, "bold"),
        )
        name_header.grid(row=1, column=1, sticky="w", padx=6, pady=(0, 6))

        commander_header = tk.Label(
            panel,
            text="Commander Name",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 12, "bold"),
        )
        commander_header.grid(row=1, column=2, sticky="w", padx=6, pady=(0, 6))

        player_count = self._clamp_input(self.number_of_players, minimum=2, maximum=6)
        for index in range(player_count):
            player_label = tk.Label(
                panel,
                text=f"Player {index + 1}",
                bg="#111827",
                fg="#ffffff",
                font=("Arial", 11, "bold"),
            )
            player_label.grid(row=index + 2, column=0, sticky="w", padx=(0, 10), pady=5)

            player_options = self._saved_player_profile_names()
            player_menu = ttk.Combobox(
                panel,
                textvariable=self.player_names[index],
                values=player_options,
                state="readonly",
                font=("Arial", 11, "bold"),
                width=18,
            )
            player_menu.bind(
                "<<ComboboxSelected>>",
                lambda event, player=index: self._select_player_profile_for_game(
                    player,
                    self.player_names[player].get(),
                ),
            )
            player_menu.grid(row=index + 2, column=1, sticky="ew", padx=6, pady=5)

            commander_options = self._commander_options_for_player(index)
            commander_menu = ttk.Combobox(
                panel,
                textvariable=self.commander_names[index],
                values=commander_options,
                state="readonly",
                font=("Arial", 11, "bold"),
                width=28,
            )
            commander_menu.bind(
                "<<ComboboxSelected>>",
                lambda event, player=index: self._select_commander_for_game(
                    player,
                    self.commander_names[player].get(),
                ),
            )
            commander_menu.grid(row=index + 2, column=2, sticky="ew", padx=6, pady=5)

        settings_row = player_count + 2
        player_count_area = tk.Frame(panel, bg="#111827")
        player_count_area.grid(
            row=settings_row,
            column=0,
            columnspan=3,
            pady=(16, 4),
        )
        tk.Label(
            player_count_area,
            text="Number of Players",
            bg="#111827",
            fg="#ffffff",
            font=("Arial", 12, "bold"),
        ).pack(side="left", padx=(0, 12))
        tk.Button(
            player_count_area,
            text="-",
            command=lambda: self._change_setup_player_count(-1),
            bg="#f7d046",
            fg="#141414",
            activebackground="#ffe176",
            font=("Arial", 12, "bold"),
            width=3,
            cursor="hand2",
        ).pack(side="left")
        tk.Label(
            player_count_area,
            textvariable=self.number_of_players,
            bg="#f8fafc",
            fg="#141414",
            font=("Arial", 13, "bold"),
            width=4,
            relief="sunken",
            bd=2,
        ).pack(side="left", padx=6)
        tk.Button(
            player_count_area,
            text="+",
            command=lambda: self._change_setup_player_count(1),
            bg="#f7d046",
            fg="#141414",
            activebackground="#ffe176",
            font=("Arial", 12, "bold"),
            width=3,
            cursor="hand2",
        ).pack(side="left")

        planechase_toggle = tk.Checkbutton(
            panel,
            text="PlaneChase",
            variable=self.planechase_enabled,
            command=self._toggle_planechase,
            bg="#111827",
            fg="#ffffff",
            selectcolor="#111827",
            activebackground="#111827",
            activeforeground="#f7d046",
            font=("Arial", 12, "bold"),
        )
        planechase_toggle.grid(
            row=settings_row + 1,
            column=0,
            columnspan=3,
            pady=6,
        )

        action_area = tk.Frame(panel, bg="#111827")
        action_area.grid(
            row=settings_row + 2,
            column=0,
            columnspan=3,
            pady=(12, 0),
        )

        start_button = tk.Button(
            action_area,
            text="Start Game",
            command=self._save_player_setup_and_show_game_screen,
            bg="#f7d046",
            fg="#141414",
            activebackground="#ffe176",
            activeforeground="#141414",
            font=("Arial", 14, "bold"),
            width=14,
            pady=9,
            relief="raised",
            bd=3,
            cursor="hand2",
        )
        start_button.pack(side="left", padx=(0, 8))

        randomize_button = tk.Button(
            action_area,
            text="Randomize",
            command=self._randomize_player_commanders,
            bg="#dc2626",
            fg="#ffffff",
            activebackground="#ef4444",
            activeforeground="#ffffff",
            font=("Arial", 14, "bold"),
            width=14,
            pady=9,
            relief="raised",
            bd=3,
            cursor="hand2",
        )
        randomize_button.pack(side="left", padx=(8, 0))

    def _draw_player_setup_background(self, event=None):
        width = self.player_setup_screen.winfo_width()
        height = self.player_setup_screen.winfo_height()

        self.player_setup_screen.delete("background")
        self.player_setup_screen.create_image(
            width // 2,
            height // 2,
            image=self.space_background,
            anchor="center",
            tags="background",
        )
        self.player_setup_screen.tag_lower("background")

        if self.player_setup_panel_window is not None:
            self.player_setup_screen.coords(
                self.player_setup_panel_window,
                width // 2,
                height // 2,
            )

    def _ensure_player_fields(self):
        player_count = self._clamp_input(self.number_of_players, minimum=2, maximum=6)

        while len(self.player_names) < player_count:
            number = len(self.player_names) + 1
            self.player_names.append(tk.StringVar(value=f"Player {number}"))
        while len(self.commander_names) < player_count:
            self.commander_names.append(tk.StringVar(value=""))

        self.player_names = self.player_names[:player_count]
        self.commander_names = self.commander_names[:player_count]

    def _saved_player_profile_names(self):
        profile_names = sorted(self.player_profiles)
        return profile_names if profile_names else ["No Saved Profiles"]

    def _commander_options_for_player(self, player_index):
        player_name = self.player_names[player_index].get()
        commanders = self.player_profiles.get(player_name, [])
        return commanders if commanders else ["No Commanders Saved"]

    def _select_player_profile_for_game(self, player_index, selected_profile):
        if selected_profile == "No Saved Profiles":
            return

        self.player_names[player_index].set(selected_profile)
        commanders = self.player_profiles.get(selected_profile, [])
        self.commander_names[player_index].set(commanders[0] if commanders else "")
        self._show_player_setup_screen()

    def _select_commander_for_game(self, player_index, selected_commander):
        if selected_commander == "No Commanders Saved":
            self.commander_names[player_index].set("")
            return

        self.commander_names[player_index].set(selected_commander)

    def _randomize_player_commanders(self):
        player_count = self._clamp_input(self.number_of_players, minimum=2, maximum=6)
        for player_index in range(player_count):
            player_name = self.player_names[player_index].get()
            commanders = self.player_profiles.get(player_name, [])
            if commanders:
                self.commander_names[player_index].set(random.choice(commanders))

        self._save_app_data()
        self._show_game_screen()

    def _toggle_planechase(self):
        if self.planechase_enabled.get() and self.number_of_players.get() > 5:
            self.number_of_players.set(5)
            self._ensure_player_fields()
        self._save_app_data()
        self._show_player_setup_screen()

    def _change_setup_player_count(self, amount):
        maximum = 5 if self.planechase_enabled.get() else 6
        current_count = self._clamp_input(
            self.number_of_players,
            minimum=2,
            maximum=maximum,
        )
        self.number_of_players.set(max(2, min(maximum, current_count + amount)))
        self._ensure_player_fields()
        self._save_app_data()
        self._show_player_setup_screen()

    def _save_player_setup_and_show_game_screen(self):
        self._ensure_player_fields()
        self._save_app_data()
        self._show_game_screen()

    def _clear_window(self):
        self._unbind_game_keys()
        self._cancel_pending_counter_changes()
        for widget in self.winfo_children():
            widget.destroy()

    def _show_game_screen(self):
        self._clear_window()
        self._maximize_window()
        self._load_commander_texts()
        self.plane_canvas = None

        game_screen = tk.Frame(self, bg="#000000")
        game_screen.pack(fill="both", expand=True)

        controls = tk.Frame(game_screen, bg="#000000", padx=14, pady=10)
        controls.pack(fill="x")

        exit_button = self._create_game_control_button(
            controls,
            "Exit",
            self._exit_game,
        )
        exit_button.pack(side="right", padx=(8, 0))

        edit_button = self._create_game_control_button(
            controls,
            "Change Commander/Player",
            self._leave_game_for_player_setup,
        )
        edit_button.pack(side="right", padx=(8, 0))

        restart_button = self._create_game_control_button(
            controls,
            "Restart",
            self._show_game_screen,
        )
        restart_button.pack(side="right", padx=(8, 0))

        container = tk.Frame(game_screen, bg="#000000", padx=24, pady=24)
        container.pack(fill="both", expand=True)

        player_count = self._clamp_input(self.number_of_players, minimum=2, maximum=6)
        life_total = self._clamp_input(self.starting_life_total, minimum=1, maximum=999)
        self._ensure_player_fields()
        self.life_totals = [tk.IntVar(value=life_total) for _ in range(player_count)]
        self.game_life_text_items = []
        self.game_pending_change_items = []
        self.game_commander_damage_flash_items = []
        self.pending_counter_changes = {}
        self.pending_counter_timers = {}
        self.commander_damage_flash_timers = {}
        self.commander_damage_totals = [
            [0 for _ in range(player_count)]
            for _ in range(player_count)
        ]
        self.commander_damage_mode_player = None
        self.commander_damage_summary_items = []
        self.poison_counters = [0 for _ in range(player_count)]
        self.poison_mode_player = None
        self.game_winner_index = None
        self.game_win_recorded = False
        self.hidden_commander_players = set()
        if self.planechase_enabled.get() and self.planes:
            self.plane_history = [random.choice(self.planes)]
            self.current_plane_history_index = 0
            column_count = 2 if player_count <= 3 else 3
            item_count = player_count + 1
        else:
            self.plane_history = []
            self.current_plane_history_index = -1
            column_count = 2 if player_count <= 4 else 3
            item_count = player_count
        row_count = (item_count + column_count - 1) // column_count

        for row in range(row_count):
            container.grid_rowconfigure(row, weight=1, uniform="box")
        for column in range(column_count):
            container.grid_columnconfigure(column, weight=1, uniform="box")

        for index in range(player_count):
            row = index // column_count
            column = index % column_count

            box = tk.Canvas(
                container,
                bg="#000000",
                highlightthickness=2,
                highlightbackground="#2f2f2f",
            )
            box.grid(row=row, column=column, sticky="nsew", padx=10, pady=10)

            player_name = self.player_names[index].get().strip() or f"Player {index + 1}"
            commander_name = self.commander_names[index].get().strip() or "Commander"

            player_text = box.create_text(
                0,
                0,
                text=f"{index + 1}: {player_name}",
                fill="white",
                font=("Arial", 14, "bold"),
            )

            life_text = box.create_text(
                0,
                0,
                text=str(self.life_totals[index].get()),
                fill="white",
                font=("Arial", 30, "bold"),
            )
            self.game_life_text_items.append((box, life_text))
            commander_damage_flash_text = box.create_text(
                0,
                0,
                text="",
                fill="#ef4444",
                font=("Arial", 18, "bold"),
            )
            self.game_commander_damage_flash_items.append(
                (box, commander_damage_flash_text)
            )

            pending_increase_box = box.create_rectangle(
                0,
                0,
                0,
                0,
                fill="#111827",
                outline="#86efac",
                width=2,
                state="hidden",
            )
            pending_increase_text = box.create_text(
                0,
                0,
                text="",
                fill="#86efac",
                font=("Arial", 11, "bold"),
            )
            pending_decrease_box = box.create_rectangle(
                0,
                0,
                0,
                0,
                fill="#111827",
                outline="#fca5a5",
                width=2,
                state="hidden",
            )
            pending_decrease_text = box.create_text(
                0,
                0,
                text="",
                fill="#fca5a5",
                font=("Arial", 11, "bold"),
            )
            self.game_pending_change_items.append(
                (
                    box,
                    pending_increase_box,
                    pending_increase_text,
                    pending_decrease_box,
                    pending_decrease_text,
                )
            )
            self.life_totals[index].trace_add(
                "write",
                lambda *args: self._update_game_life_states(),
            )

            commander_profile_text = box.create_text(
                0,
                0,
                text=commander_name,
                fill="white",
                font=("Arial", 12, "bold"),
            )
            player_wins = self.player_profile_wins.get(player_name, 0)
            commander_wins = self._commander_total_wins_for_game(commander_name)
            wins_text = box.create_text(
                0,
                0,
                text=f"Wins: {player_wins}:{commander_wins}",
                fill="#f7d046",
                font=("Arial", 11, "bold"),
                anchor="nw",
            )
            commander_damage_text = box.create_text(
                0,
                0,
                text="",
                fill="#f7d046",
                font=("Arial", 10, "bold"),
                anchor="ne",
                justify="right",
            )
            self.commander_damage_summary_items.append(
                (box, commander_damage_text)
            )
            box.bind(
                "<Configure>",
                lambda event,
                canvas=box,
                player_index=index,
                commander_name=commander_name,
                text_items=(
                    player_text,
                    commander_profile_text,
                    life_text,
                    commander_damage_flash_text,
                    pending_increase_box,
                    pending_increase_text,
                    pending_decrease_box,
                    pending_decrease_text,
                    wins_text,
                    commander_damage_text,
                ): self._draw_game_box(
                    event,
                    canvas,
                    player_index,
                    commander_name,
                    text_items,
                ),
            )
            box.bind(
                "<Button-1>",
                lambda event,
                canvas=box,
                player_index=index,
                commander_name=commander_name,
                text_items=(
                    player_text,
                    commander_profile_text,
                    life_text,
                    commander_damage_flash_text,
                    pending_increase_box,
                    pending_increase_text,
                    pending_decrease_box,
                    pending_decrease_text,
                    wins_text,
                    commander_damage_text,
                ): self._toggle_commander_visibility(
                    canvas,
                    player_index,
                    commander_name,
                    text_items,
                ),
            )

        if self.planechase_enabled.get() and self.plane_history:
            plane_index = player_count
            plane_row = plane_index // column_count
            plane_column = plane_index % column_count
            plane_span = column_count - plane_column
            plane_box = tk.Canvas(
                container,
                bg="#000000",
                highlightthickness=2,
                highlightbackground="#f7d046",
            )
            plane_box.grid(
                row=plane_row,
                column=plane_column,
                columnspan=plane_span,
                sticky="nsew",
                padx=10,
                pady=10,
            )
            self.plane_canvas = plane_box
            plane_box.bind(
                "<Configure>",
                lambda event, canvas=plane_box: self._draw_plane_box(event, canvas),
            )

        self._update_game_life_states()
        self._bind_game_keys()

    def _draw_plane_box(self, event=None, canvas=None):
        canvas = canvas or self.plane_canvas
        if canvas is None or not self.plane_history:
            return

        width = max(1, event.width if event is not None else canvas.winfo_width())
        height = max(1, event.height if event is not None else canvas.winfo_height())
        plane = self.plane_history[self.current_plane_history_index]
        canvas.delete("all")

        image_path = resolve_app_path(plane.get("image_path", ""))
        if image_path.exists():
            try:
                image = Image.open(image_path).convert("RGB")
                image = ImageOps.fit(image, (width, height), method=Image.LANCZOS)
                image = ImageEnhance.Brightness(image).enhance(0.55)
                cache_dir = RES_DIR / "game_cache"
                cache_dir.mkdir(parents=True, exist_ok=True)
                cache_path = cache_dir / (
                    f"plane_{abs(hash((str(image_path), width, height)))}.png"
                )
                image.save(cache_path)
                self.plane_background_image = tk.PhotoImage(file=cache_path)
                canvas.create_image(
                    0,
                    0,
                    image=self.plane_background_image,
                    anchor="nw",
                )
            except OSError:
                canvas.config(bg="#000000")

        margin = max(12, width // 30)
        name_height = max(48, int(height * 0.18))
        canvas.create_text(
            margin,
            margin,
            text=f"Plane {self.current_plane_history_index + 1}",
            fill="#f7d046",
            font=("Arial", max(11, min(16, height // 28)), "bold"),
            anchor="nw",
        )
        canvas.create_text(
            width // 2,
            margin + (name_height // 2),
            text=str(plane.get("name", "")),
            fill="#ffffff",
            font=("Arial", max(14, min(24, name_height // 3)), "bold"),
            width=max(1, width - (margin * 3)),
            justify="center",
        )

        text_top = margin + name_height + margin
        canvas.create_text(
            margin * 2,
            text_top + margin,
            text=str(plane.get("planes_text", "")),
            fill="#ffffff",
            font=("Arial", max(10, min(16, height // 24)), "bold"),
            width=max(1, width - (margin * 4)),
            justify="left",
            anchor="nw",
        )

    def _show_random_plane(self):
        if not self.planechase_enabled.get() or not self.planes:
            return

        current_plane = (
            self.plane_history[self.current_plane_history_index]
            if self.plane_history
            else None
        )
        choices = [plane for plane in self.planes if plane != current_plane]
        next_plane = random.choice(choices or self.planes)
        if self.current_plane_history_index < len(self.plane_history) - 1:
            self.plane_history = self.plane_history[
                : self.current_plane_history_index + 1
            ]
        self.plane_history.append(next_plane)
        self.current_plane_history_index += 1
        self._draw_plane_box()

    def _show_previous_plane(self):
        if self.current_plane_history_index <= 0:
            return
        self.current_plane_history_index -= 1
        self._draw_plane_box()

    def _create_game_control_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg="#f7d046",
            fg="#141414",
            activebackground="#ffe176",
            activeforeground="#141414",
            font=("Arial", 11, "bold"),
            padx=12,
            pady=5,
            relief="raised",
            bd=2,
            cursor="hand2",
        )

    def _add_view_exit_button(self, parent, command=None):
        exit_button = self._create_game_control_button(
            parent,
            "Exit",
            command or self._show_start_screen,
        )
        exit_button.place(relx=1.0, x=-14, y=10, anchor="ne")
        exit_button.lift()
        return exit_button

    def _exit_game(self):
        self._record_game_winner()
        self._save_app_data()
        self._show_start_screen()

    def _leave_game_for_player_setup(self):
        self._record_game_winner()
        self._save_app_data()
        self._show_player_setup_screen()

    def _maximize_window(self):
        try:
            self.attributes("-fullscreen", False)
            self.state("zoomed")
        except tk.TclError:
            width = self.winfo_screenwidth()
            height = self.winfo_screenheight()
            self.geometry(f"{width}x{height}+0+0")

    def _toggle_commander_visibility(
        self,
        canvas,
        player_index,
        commander_name,
        text_items,
    ):
        if player_index in self.hidden_commander_players:
            self.hidden_commander_players.remove(player_index)
        else:
            self.hidden_commander_players.add(player_index)

        self._draw_game_box(
            None,
            canvas,
            player_index,
            commander_name,
            text_items,
        )

    def _draw_game_box(self, event, canvas, player_index, commander_name, text_items):
        width = max(1, event.width if event is not None else canvas.winfo_width())
        height = max(1, event.height if event is not None else canvas.winfo_height())
        commander_hidden = player_index in self.hidden_commander_players
        background = (
            None
            if commander_hidden
            else self._game_box_background(commander_name, width, height)
        )

        canvas.delete("background")
        if background is not None:
            canvas.create_image(0, 0, image=background, anchor="nw", tags="background")
            canvas.tag_lower("background")
        else:
            canvas.config(bg="#000000")

        canvas.delete("commander_text_box")
        if not commander_hidden:
            self._draw_commander_text_boxes(canvas, commander_name, width, height)

        canvas.delete("commander_stats")
        if not commander_hidden:
            self._draw_commander_stats(canvas, commander_name, width, height)

        (
            player_text,
            commander_profile_text,
            life_text,
            commander_damage_flash_text,
            pending_increase_box,
            pending_increase_text,
            pending_decrease_box,
            pending_decrease_text,
            wins_text,
            commander_damage_text,
        ) = text_items
        canvas.itemconfig(
            commander_profile_text,
            text="Unknown Commander" if commander_hidden else commander_name,
        )
        self._resize_game_box_text(
            width,
            height,
            canvas,
            player_text,
            commander_profile_text,
            life_text,
            commander_damage_flash_text,
            pending_increase_box,
            pending_increase_text,
            pending_decrease_box,
            pending_decrease_text,
            wins_text,
            commander_damage_text,
        )

    def _game_box_background(self, commander_name, width, height):
        commander_profile = self._commander_profile_for_game(commander_name)
        image_path = commander_profile.get("image_path", "")
        colors = commander_profile.get("colors", [])

        cache_key = (commander_name, width, height, image_path, tuple(colors))
        if cache_key in self.game_background_images:
            return self.game_background_images[cache_key]

        resolved_image_path = resolve_app_path(image_path) if image_path else None
        if resolved_image_path and resolved_image_path.exists():
            image = Image.open(resolved_image_path).convert("RGB")
            image = ImageOps.fit(image, (width, height), method=Image.LANCZOS)
            image = ImageEnhance.Brightness(image).enhance(0.45)
        elif colors:
            image = self._color_background_image(colors, width, height)
        else:
            return None

        cache_dir = RES_DIR / "game_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = cache_dir / f"game_bg_{abs(hash(cache_key))}.png"
        image.save(cache_path)
        background = tk.PhotoImage(file=cache_path)
        self.game_background_images[cache_key] = background
        return background

    def _color_background_image(self, colors, width, height):
        palette = {
            "black": "#111111",
            "blue": "#1d4ed8",
            "green": "#15803d",
            "red": "#b91c1c",
            "white": "#d1d5db",
            "colorless": "#737373",
        }
        selected_colors = [color for color in colors if color in palette]
        if not selected_colors:
            return Image.new("RGB", (width, height), "#000000")

        image = Image.new("RGB", (width, height), "#000000")
        draw = ImageDraw.Draw(image)
        stripe_width = max(1, width // len(selected_colors))
        for index, color_name in enumerate(selected_colors):
            x0 = index * stripe_width
            x1 = width if index == len(selected_colors) - 1 else (index + 1) * stripe_width
            draw.rectangle((x0, 0, x1, height), fill=palette[color_name])

        return ImageEnhance.Brightness(image).enhance(0.55)

    def _draw_commander_text_boxes(self, canvas, commander_name, width, height):
        commander_texts = self._game_commander_text_values(commander_name)
        if not commander_texts:
            return

        spacing = max(8, width // 50)
        total_width = max(1, int(width * 0.8))
        box_count = len(commander_texts)
        box_width = (
            max(1, (total_width - spacing) // 2)
            if box_count > 1
            else total_width
        )
        box_height = max(60, int(height * 0.28))
        full_width = (box_width * box_count) + (spacing * (box_count - 1))
        x_position = (width - full_width) // 2
        y_position = int(height * 0.80)
        y0 = max(0, y_position - (box_height // 2))
        y1 = min(height, y_position + (box_height // 2))
        font_size = max(8, min(14, (y1 - y0) // 7))

        for commander_text in commander_texts:
            x0 = x_position
            x1 = x0 + box_width
            self._create_fitted_commander_text(
                canvas,
                commander_text,
                x0,
                y0,
                x1,
                y1,
                font_size,
            )
            x_position += box_width + spacing

    def _create_fitted_commander_text(self, canvas, text, x0, y0, x1, y1, font_size):
        padding = 8
        text_item = canvas.create_text(
            x0 + padding,
            y0 + padding,
            text=text,
            fill="#ffffff",
            font=("Arial", font_size, "bold"),
            width=max(1, (x1 - x0) - (padding * 2)),
            justify="left",
            anchor="nw",
            tags="commander_text_box",
        )

        available_height = max(1, (y1 - y0) - (padding * 2))
        while font_size > 6:
            text_bounds = canvas.bbox(text_item)
            if text_bounds is None or text_bounds[3] - text_bounds[1] <= available_height:
                break
            font_size -= 1
            canvas.itemconfig(text_item, font=("Arial", font_size, "bold"))

    def _draw_commander_stats(self, canvas, commander_name, width, height):
        profile = self._commander_profile_for_game(commander_name)
        color_cost = self._clean_color_cost(profile.get("color_cost", {}))
        nonzero_pips = [
            (color_name, color_cost[color_name])
            for color_name in MANA_COLORS
            if color_cost[color_name] > 0
        ]

        margin = max(10, width // 45)
        icon_size = 42
        icon_spacing = 4
        bottom_y = height - margin
        power_font_size = max(11, min(18, min(width, height) // 16))
        attack = self._clamp_plain_number(profile.get("attack_power", 0), 0, 99)
        defense = self._clamp_plain_number(profile.get("defense_power", 0), 0, 99)
        power_text = f"{attack}/{defense}"

        canvas.create_text(
            width - margin,
            bottom_y,
            text=power_text,
            fill="#ffffff",
            font=("Arial", power_font_size, "bold"),
            anchor="se",
            tags="commander_stats",
        )

        if not nonzero_pips:
            return

        pip_total_width = (
            (len(nonzero_pips) * icon_size)
            + ((len(nonzero_pips) - 1) * icon_spacing)
        )
        start_x = max(margin, width - margin - pip_total_width)
        pip_y = bottom_y - power_font_size - icon_size // 2 - 6

        for index, (color_name, pip_count) in enumerate(nonzero_pips):
            center_x = start_x + (index * (icon_size + icon_spacing)) + icon_size // 2
            canvas.create_image(
                center_x,
                pip_y,
                image=self._mana_icon_image(color_name, True),
                anchor="center",
                tags="commander_stats",
            )
            if pip_count > 1:
                canvas.create_text(
                    center_x,
                    pip_y,
                    text=str(pip_count),
                    fill="#111827",
                    font=("Arial", 16, "bold"),
                    anchor="center",
                    tags="commander_stats",
                )

    def _game_commander_text_values(self, commander_name):
        profile = self._commander_profile_for_game(commander_name)
        second_commander = self._clean_second_commander_profile(
            profile.get("second_commander", {})
        )
        combined_text = self.commander_texts.get(commander_name, "").strip()
        if second_commander["enabled"] and combined_text:
            return [combined_text]

        primary_name = commander_name
        if primary_name not in self.commander_texts and " - " in primary_name:
            primary_name = primary_name.split(" - ", 1)[0]

        commander_texts = []
        primary_text = self.commander_texts.get(primary_name, "").strip()
        if primary_text:
            commander_texts.append(primary_text)

        if second_commander["enabled"]:
            second_text = self.commander_texts.get(
                second_commander["name"],
                "",
            ).strip()
            if second_text:
                commander_texts.append(second_text)

        return commander_texts

    def _commander_profile_for_game(self, commander_name):
        profile_name = self._commander_profile_name_for_game(commander_name)
        return self.commander_profiles.get(profile_name, {})

    def _commander_profile_name_for_game(self, commander_name):
        profile = self.commander_profiles.get(commander_name, {})
        if self._profile_has_game_assets(profile):
            return commander_name

        if " - " in commander_name:
            base_name = commander_name.split(" - ", 1)[0]
            base_profile = self.commander_profiles.get(base_name, {})
            if self._profile_has_game_assets(base_profile):
                return base_name

        return commander_name

    def _commander_total_wins_for_game(self, commander_name):
        profile_name = self._commander_win_profile_name(commander_name)
        profile = self.commander_profiles.get(profile_name, {})
        return self._clamp_plain_number(profile.get("total_wins", 0), 0, 999999)

    def _commander_win_profile_name(self, commander_name):
        if commander_name in self.commander_profiles:
            return commander_name
        return self._commander_profile_name_for_game(commander_name)

    def _profile_has_game_assets(self, profile):
        if not profile:
            return False

        second_commander = self._clean_second_commander_profile(
            profile.get("second_commander", {})
        )
        color_cost = self._clean_color_cost(profile.get("color_cost", {}))
        return any(
            [
                profile.get("image_path"),
                profile.get("text_path"),
                profile.get("colors"),
                self._clamp_plain_number(profile.get("attack_power", 0), 0, 99),
                self._clamp_plain_number(profile.get("defense_power", 0), 0, 99),
                any(color_cost.values()),
                second_commander["enabled"],
            ]
        )

    def _resize_game_box_text(
        self,
        width,
        height,
        canvas,
        player_text,
        commander_profile_text,
        life_text,
        commander_damage_flash_text,
        pending_increase_box,
        pending_increase_text,
        pending_decrease_box,
        pending_decrease_text,
        wins_text,
        commander_damage_text,
    ):
        shortest_side = max(1, min(width, height))
        player_size = max(14, shortest_side // 12)
        life_size = max(34, shortest_side // 4)
        commander_size = max(10, shortest_side // 20)

        canvas.coords(player_text, width // 2, height * 0.13)
        canvas.coords(commander_profile_text, width // 2, height * 0.22)
        canvas.coords(life_text, width // 2, height * 0.47)
        canvas.coords(commander_damage_flash_text, width // 2, height * 0.37)
        canvas.coords(pending_increase_text, width // 2, height * 0.315)
        canvas.coords(pending_decrease_text, width // 2, height * 0.625)
        canvas.coords(wins_text, 12, 12)
        canvas.coords(commander_damage_text, width - 12, 12)
        canvas.itemconfig(player_text, font=("Arial", player_size, "bold"))
        canvas.itemconfig(commander_profile_text, font=("Arial", commander_size, "bold"))
        canvas.itemconfig(life_text, font=("Arial", life_size, "bold"))
        canvas.itemconfig(
            commander_damage_flash_text,
            font=("Arial", max(16, life_size // 3), "bold"),
        )
        pending_size = max(9, min(14, shortest_side // 22))
        canvas.itemconfig(
            pending_increase_text,
            font=("Arial", pending_size, "bold"),
        )
        canvas.itemconfig(
            pending_decrease_text,
            font=("Arial", pending_size, "bold"),
        )
        self._resize_pending_change_box(
            canvas,
            pending_increase_box,
            pending_increase_text,
        )
        self._resize_pending_change_box(
            canvas,
            pending_decrease_box,
            pending_decrease_text,
        )
        canvas.itemconfig(wins_text, font=("Arial", commander_size, "bold"))
        canvas.itemconfig(
            commander_damage_text,
            font=("Arial", max(9, commander_size - 1), "bold"),
        )
        canvas.tag_raise(player_text)
        canvas.tag_raise(commander_profile_text)
        canvas.tag_raise(life_text)
        canvas.tag_raise(commander_damage_flash_text)
        canvas.tag_raise(pending_increase_box)
        canvas.tag_raise(pending_increase_text)
        canvas.tag_raise(pending_decrease_box)
        canvas.tag_raise(pending_decrease_text)
        canvas.tag_raise(wins_text)
        canvas.tag_raise(commander_damage_text)

    def _adjust_life_total(self, player_index, amount):
        if 0 <= player_index < len(self.life_totals):
            self._queue_counter_change(("life", player_index), amount)

    def _counter_value(self, counter_key):
        counter_type = counter_key[0]
        if counter_type == "life":
            return self.life_totals[counter_key[1]].get()
        if counter_type == "poison":
            return self.poison_counters[counter_key[1]]
        if counter_type == "commander":
            return self.commander_damage_totals[counter_key[1]][counter_key[2]]
        return 0

    def _queue_counter_change(self, counter_key, amount):
        current_value = self._counter_value(counter_key)
        pending_amount = self.pending_counter_changes.get(counter_key, 0)
        new_pending_amount = max(-current_value, pending_amount + amount)

        if counter_key[0] == "commander":
            self._cancel_commander_damage_commit_timer(counter_key[1])
        else:
            timer = self.pending_counter_timers.pop(counter_key, None)
            if timer is not None:
                self.after_cancel(timer)

        if new_pending_amount == 0:
            self.pending_counter_changes.pop(counter_key, None)
        else:
            self.pending_counter_changes[counter_key] = new_pending_amount
            if counter_key[0] == "commander":
                self.pending_counter_timers[
                    self._commander_damage_commit_key(counter_key[1])
                ] = self.after(
                    2000,
                    lambda target=counter_key[1]: self._commit_commander_damage_mode(
                        target
                    ),
                )
            else:
                self.pending_counter_timers[counter_key] = self.after(
                    2000,
                    lambda key=counter_key: self._commit_counter_change(key),
                )
        if (
            counter_key[0] == "commander"
            and self._commander_damage_commit_key(counter_key[1])
            not in self.pending_counter_timers
        ):
            self.pending_counter_timers[
                self._commander_damage_commit_key(counter_key[1])
            ] = self.after(
                2000,
                lambda target=counter_key[1]: self._commit_commander_damage_mode(
                    target
                ),
            )
        self._update_game_life_states()

    def _commit_counter_change(self, counter_key):
        self.pending_counter_timers.pop(counter_key, None)
        amount = self.pending_counter_changes.pop(counter_key, 0)
        if not amount:
            self._update_game_life_states()
            return

        counter_type = counter_key[0]
        if counter_type == "life":
            player_index = counter_key[1]
            self.life_totals[player_index].set(
                max(0, self.life_totals[player_index].get() + amount)
            )
        elif counter_type == "poison":
            player_index = counter_key[1]
            self.poison_counters[player_index] = max(
                0,
                self.poison_counters[player_index] + amount,
            )
        elif counter_type == "commander":
            target_player_index, source_player_index = counter_key[1:]
            self.commander_damage_totals[target_player_index][
                source_player_index
            ] = max(
                0,
                self.commander_damage_totals[target_player_index][
                    source_player_index
                ] + amount,
            )
            self.life_totals[target_player_index].set(
                max(0, self.life_totals[target_player_index].get() - amount)
            )
            if self.commander_damage_mode_player == target_player_index:
                self.commander_damage_mode_player = None
        self._update_game_life_states()
        if counter_type == "commander":
            self._show_commander_damage_flash(
                target_player_index,
                [(source_player_index, amount)],
            )

    def _commander_damage_commit_key(self, target_player_index):
        return ("commander_commit", target_player_index)

    def _cancel_commander_damage_commit_timer(self, target_player_index):
        timer_key = self._commander_damage_commit_key(target_player_index)
        timer = self.pending_counter_timers.pop(timer_key, None)
        if timer is not None:
            self.after_cancel(timer)

    def _pending_commander_damage_keys(self, target_player_index):
        return [
            counter_key
            for counter_key in self.pending_counter_changes
            if (
                counter_key[0] == "commander"
                and counter_key[1] == target_player_index
            )
        ]

    def _commit_commander_damage_mode(self, target_player_index):
        timer = self.pending_counter_timers.pop(
            self._commander_damage_commit_key(target_player_index),
            None,
        )
        if timer is not None:
            try:
                self.after_cancel(timer)
            except tk.TclError:
                pass
        pending_keys = self._pending_commander_damage_keys(target_player_index)
        total_life_delta = 0
        damage_entries = []

        for counter_key in pending_keys:
            amount = self.pending_counter_changes.pop(counter_key, 0)
            if not amount:
                continue

            source_player_index = counter_key[2]
            self.commander_damage_totals[target_player_index][
                source_player_index
            ] = max(
                0,
                self.commander_damage_totals[target_player_index][
                    source_player_index
                ] + amount,
            )
            total_life_delta += amount
            damage_entries.append((source_player_index, amount))

        if total_life_delta:
            self.life_totals[target_player_index].set(
                max(0, self.life_totals[target_player_index].get() - total_life_delta)
            )

        if self.commander_damage_mode_player == target_player_index:
            self.commander_damage_mode_player = None
        self._update_game_life_states()
        if damage_entries:
            self._show_commander_damage_flash(target_player_index, damage_entries)

    def _show_commander_damage_flash(self, player_index, damage_entries):
        if not 0 <= player_index < len(self.game_commander_damage_flash_items):
            return

        canvas, flash_text = self.game_commander_damage_flash_items[player_index]
        timer = self.commander_damage_flash_timers.pop(player_index, None)
        if timer is not None:
            self.after_cancel(timer)

        display_parts = []
        for source_player_index, damage_delta in damage_entries:
            if damage_delta > 0:
                display_parts.append(f"-{damage_delta} P{source_player_index + 1}")
            elif damage_delta < 0:
                display_parts.append(f"+{-damage_delta} P{source_player_index + 1}")

        if not display_parts:
            self._clear_commander_damage_flash(player_index)
            return

        display_text = "\n".join(display_parts)
        display_color = (
            "#ef4444"
            if any(damage_delta > 0 for _, damage_delta in damage_entries)
            else "#86efac"
        )
        canvas.itemconfig(flash_text, text=display_text, fill=display_color)
        canvas.tag_raise(flash_text)
        self.commander_damage_flash_timers[player_index] = self.after(
            2000,
            lambda index=player_index: self._clear_commander_damage_flash(index),
        )

    def _clear_commander_damage_flash(self, player_index):
        self.commander_damage_flash_timers.pop(player_index, None)
        if 0 <= player_index < len(self.game_commander_damage_flash_items):
            canvas, flash_text = self.game_commander_damage_flash_items[player_index]
            canvas.itemconfig(flash_text, text="")

    def _cancel_pending_counter_changes(self):
        for timer in self.pending_counter_timers.values():
            try:
                self.after_cancel(timer)
            except tk.TclError:
                pass
        self.pending_counter_timers = {}
        self.pending_counter_changes = {}
        for timer in self.commander_damage_flash_timers.values():
            try:
                self.after_cancel(timer)
            except tk.TclError:
                pass
        self.commander_damage_flash_timers = {}

    def _displayed_counter_key(self, player_index):
        if self.commander_damage_mode_player is not None:
            if player_index == self.commander_damage_mode_player:
                return None
            return (
                "commander",
                self.commander_damage_mode_player,
                player_index,
            )
        if self.poison_mode_player == player_index:
            return ("poison", player_index)
        return ("life", player_index)

    def _resize_pending_change_box(self, canvas, box_item, text_item):
        text = canvas.itemcget(text_item, "text")
        if not text:
            canvas.itemconfig(box_item, state="hidden")
            return

        bounds = canvas.bbox(text_item)
        if bounds is None:
            canvas.itemconfig(box_item, state="hidden")
            return

        padding_x = 5
        padding_y = 2
        canvas.coords(
            box_item,
            bounds[0] - padding_x,
            bounds[1] - padding_y,
            bounds[2] + padding_x,
            bounds[3] + padding_y,
        )
        canvas.itemconfig(box_item, state="normal")
        canvas.tag_lower(box_item, text_item)

    def _update_pending_change_displays(self):
        for player_index, (
            canvas,
            increase_box,
            increase_text,
            decrease_box,
            decrease_text,
        ) in enumerate(self.game_pending_change_items):
            counter_key = self._displayed_counter_key(player_index)
            amount = self.pending_counter_changes.get(counter_key, 0)
            canvas.itemconfig(
                increase_text,
                text=f"+{amount}" if amount > 0 else "",
            )
            canvas.itemconfig(
                decrease_text,
                text=str(amount) if amount < 0 else "",
            )
            self._resize_pending_change_box(canvas, increase_box, increase_text)
            self._resize_pending_change_box(canvas, decrease_box, decrease_text)

    def _update_game_life_states(self):
        if not self.life_totals or not self.game_life_text_items:
            return

        alive_players = [
            index
            for index, life_total in enumerate(self.life_totals)
            if life_total.get() > 0
            and not self._has_lethal_commander_damage(index)
            and not self._has_lethal_poison(index)
        ]
        self.game_winner_index = alive_players[0] if len(alive_players) == 1 else None

        for index, (canvas, life_text) in enumerate(self.game_life_text_items):
            if self.commander_damage_mode_player is not None:
                if index == self.commander_damage_mode_player:
                    display_text = "C"
                else:
                    display_text = str(
                        self.commander_damage_totals[
                            self.commander_damage_mode_player
                        ][index]
                    )
                display_color = "#ef4444"
            elif self.poison_mode_player == index:
                display_text = str(self.poison_counters[index])
                display_color = "#22c55e"
            else:
                life_total = self.life_totals[index].get()
                if index == self.game_winner_index:
                    display_text = "WINNER"
                    display_color = "#f7d046"
                elif (
                    life_total <= 0
                    or self._has_lethal_commander_damage(index)
                    or self._has_lethal_poison(index)
                ):
                    display_text = "DEAD"
                    display_color = "#7f1d1d"
                else:
                    display_text = str(life_total)
                    display_color = "#ffffff"
            canvas.itemconfig(life_text, text=display_text, fill=display_color)

        self._update_pending_change_displays()
        self._update_commander_damage_summaries()

    def _has_lethal_commander_damage(self, player_index):
        if not 0 <= player_index < len(self.commander_damage_totals):
            return False
        return any(
            damage > 20
            for source_index, damage in enumerate(
                self.commander_damage_totals[player_index]
            )
            if source_index != player_index
        )

    def _has_lethal_poison(self, player_index):
        return (
            0 <= player_index < len(self.poison_counters)
            and self.poison_counters[player_index] >= 10
        )

    def _update_commander_damage_summaries(self):
        for player_index, (canvas, text_item) in enumerate(
            self.commander_damage_summary_items
        ):
            if self.commander_damage_mode_player is not None:
                summary = ""
            else:
                summary = "\n".join(
                    f"C{source_index + 1}: {damage}"
                    for source_index, damage in enumerate(
                        self.commander_damage_totals[player_index]
                    )
                    if source_index != player_index
                )
            canvas.itemconfig(text_item, text=summary)

    def _toggle_commander_damage_mode(self, player_index):
        if not 0 <= player_index < len(self.life_totals):
            return

        if self.commander_damage_mode_player == player_index:
            self._commit_commander_damage_mode(player_index)
            return
        else:
            if self.commander_damage_mode_player is not None:
                self._commit_commander_damage_mode(
                    self.commander_damage_mode_player
                )
            self.commander_damage_mode_player = player_index
            self.poison_mode_player = None
        self._update_game_life_states()

    def _adjust_commander_damage(self, source_player_index, amount):
        target_player_index = self.commander_damage_mode_player
        if target_player_index is None:
            return
        if not 0 <= source_player_index < len(self.commander_damage_totals):
            return
        if source_player_index == target_player_index:
            return

        self._queue_counter_change(
            ("commander", target_player_index, source_player_index),
            amount,
        )

    def _toggle_poison_mode(self, player_index):
        if not 0 <= player_index < len(self.life_totals):
            return

        if self.poison_mode_player == player_index:
            self.poison_mode_player = None
        else:
            self.poison_mode_player = player_index
            if self.commander_damage_mode_player is not None:
                self._commit_commander_damage_mode(
                    self.commander_damage_mode_player
                )
            else:
                self.commander_damage_mode_player = None
        self._update_game_life_states()

    def _adjust_poison_counter(self, player_index, amount):
        if player_index != self.poison_mode_player:
            return
        self._queue_counter_change(("poison", player_index), amount)

    def _record_game_winner(self):
        if self.game_win_recorded or self.game_winner_index is None:
            return
        if not 0 <= self.game_winner_index < len(self.commander_names):
            return

        player_name = self.player_names[self.game_winner_index].get().strip()
        if player_name in self.player_profiles:
            self.player_profile_wins[player_name] = self._clamp_plain_number(
                self.player_profile_wins.get(player_name, 0),
                0,
                999999,
            ) + 1

        commander_name = self.commander_names[self.game_winner_index].get().strip()
        profile_name = self._commander_win_profile_name(commander_name)
        profile = self.commander_profiles.get(profile_name)
        if profile is not None:
            profile["total_wins"] = self._clamp_plain_number(
                profile.get("total_wins", 0),
                0,
                999999,
            ) + 1
        self.game_win_recorded = True
        self._save_app_data()

    def _bind_game_keys(self):
        self.bind_all("<KeyPress>", self._handle_game_key)

    def _unbind_game_keys(self):
        self.unbind_all("<KeyPress>")

    def _handle_game_key(self, event):
        key = event.keysym.lower()
        if key == "space":
            self._show_random_plane()
            return
        if key == "backspace":
            self._show_previous_plane()
            return

        number_keys = {
            "1": 0,
            "2": 1,
            "3": 2,
            "4": 3,
            "5": 4,
            "6": 5,
            "kp_1": 0,
            "kp_2": 1,
            "kp_3": 2,
            "kp_4": 3,
            "kp_5": 4,
            "kp_6": 5,
        }
        if key in number_keys:
            self._toggle_commander_damage_mode(number_keys[key])
            return

        poison_keys = {
            "z": 0,
            "x": 1,
            "c": 2,
            "v": 3,
            "b": 4,
            "n": 5,
        }
        if key in poison_keys:
            self._toggle_poison_mode(poison_keys[key])
            return

        if key not in self.game_key_bindings:
            return

        player_index, amount = self.game_key_bindings[key]
        if self.commander_damage_mode_player is not None:
            self._adjust_commander_damage(player_index, amount)
        elif self.poison_mode_player is not None:
            self._adjust_poison_counter(player_index, amount)
        else:
            self._adjust_life_total(player_index, amount)


if __name__ == "__main__":
    app = MagicApp()
    app.mainloop()
