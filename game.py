#!/usr/bin/env python3
"""Ashes & Circuits: data-driven graphical narrative simulation."""
from __future__ import annotations

import json
import random
import math
import tkinter as tk
from dataclasses import dataclass, asdict, field
from pathlib import Path
from tkinter import messagebox
from typing import Callable, Dict, List, Optional, Tuple

SAVE_PATH = Path("savegame.json")


def clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))


@dataclass
class Character:
    name: str
    class_background: str
    ideology: str
    fear: str
    relationship: int = 0
    trust: int = 0
    hidden_loyalty: int = 50
    reaction_violence: int = 0
    reaction_compromise: int = 0
    reaction_authoritarian: int = 0
    reaction_redistribution: int = 0
    grief: int = 0
    resentment: int = 0
    alive: bool = True
    notes: str = ""


@dataclass
class GameState:
    week: int = 1
    phase: int = 1
    chapter: int = 1
    ending: Optional[str] = None
    background: Optional[str] = None
    location: str = "Undergrid"
    actions_left: int = 3
    flags: Dict[str, bool] = field(default_factory=dict)
    known_links: Dict[str, List[str]] = field(default_factory=dict)
    event_log: List[str] = field(default_factory=list)

    # player stats
    money: int = 30
    food_security: int = 45
    housing_security: int = 45
    health: int = 70
    neural_stability: int = 80
    stress: int = 30
    public_reputation: int = 10
    underground_reputation: int = 15
    custodian_reputation: int = 5
    police_suspicion: int = 15
    propaganda_skill: int = 45
    technical_skill: int = 35
    empathy: int = 45
    ruthlessness: int = 20
    legitimacy: int = 20
    memory_integrity: int = 85
    dependents_wellbeing: int = 55

    # movement stats
    membership: int = 8
    movement_funding: int = 15
    propaganda_reach: int = 10
    message_discipline: int = 50
    internal_unity: int = 55
    radicalization: int = 15
    public_sympathy: int = 20
    police_infiltration: int = 10
    operational_secrecy: int = 55
    morale: int = 45
    violence_level: int = 5
    elite_sympathy: int = 5
    worker_support: int = 25
    technician_support: int = 10
    international_attention: int = 0
    infrastructure_access: int = 5
    food_network_access: int = 5
    medical_network_access: int = 5
    energy_network_access: int = 5

    # society stats
    ai_uptime: int = 95
    food_production: int = 75
    medical_availability: int = 75
    housing_stability: int = 70
    energy_stability: int = 80
    policing_intensity: int = 60
    censorship_level: int = 55
    public_unrest: int = 25
    custodian_confidence: int = 70
    lower_class_desperation: int = 70
    black_market_activity: int = 45
    trust_in_player: int = 20
    fear_of_player: int = 10
    economic_equality: int = 15
    political_freedom: int = 20
    government_stability: int = 50
    opposition_strength: int = 35


class Game:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Ashes & Circuits")
        self.root.geometry("1360x860")
        self.rng = random.Random(7)
        self.state = GameState()
        self.characters = self._init_characters()
        self.hidden_relationships = self._init_hidden_relationships()
        self.locations = self._init_locations()
        self.weekly_events = self._init_weekly_events()
        self.story_scenes = self._init_story_scenes()
        self.lexicon = self._init_lexicon()

        self._build_ui()
        self.show_background_select()

    def _init_characters(self) -> Dict[str, Character]:
        base = [
            ("Mara Venn", "lower", "insurrectionist", "collapse from ignorance"),
            ("Elias Rook", "technical-elite", "public utility reform", "being targeted by custodians"),
            ("Sera Quill", "custodian heir", "managed continuity", "chaotic revenge politics"),
            ("Juno Pike", "black-market", "narrative warfare", "irrelevance"),
            ("Inspector Cal Vey", "police", "order realist", "famine from disorder"),
            ("Nadi Bex", "linked child", "survival", "losing selfhood"),
            ("Tomas Vale", "elder worker", "stability first", "another broken revolution"),
            ("Iri Sol", "radical theorist", "abolition now", "co-option"),
            ("Director Halden Myr", "custodian owner", "custodian supremacy", "civilization collapse"),
            ("Lysa Tem", "med tech", "care continuity", "mass casualty"),
            ("Olan Crete", "smuggler", "transactional", "being made loyal"),
            ("Faye Orison", "teacher", "democratic culture", "revenge governance"),
            ("Malik Drem", "former media icon", "narrative opportunism", "oblivion"),
            ("Ansel Kade", "militant", "retributive justice", "forgiveness"),
            ("Priya Sen", "systems engineer", "decentralized AI", "authoritarian tech state"),
            ("Rune", "ambiguous AI persona", "unclear", "being shut down"),
            ("Cel Varo", "elite socialite", "brokered compromise", "total class war"),
            ("Bet Orra", "grieving parent", "protect ordinary people", "meaningless sacrifice"),
            ("Kemi Draal", "dock allocator", "distribution justice", "supply collapse"),
            ("Harl Nox", "custodian security consultant", "hard suppression", "elite fracture"),
        ]
        chars = {}
        for n, c, i, f in base:
            chars[n] = Character(n, c, i, f)
        return chars

    def _init_hidden_relationships(self) -> Dict[str, List[str]]:
        return {
            "Mara Venn": ["Ansel Kade", "Bet Orra"],
            "Elias Rook": ["Director Halden Myr", "Priya Sen"],
            "Sera Quill": ["Lysa Tem", "Cel Varo"],
            "Inspector Cal Vey": ["Tomas Vale", "Director Halden Myr"],
            "Juno Pike": ["Olan Crete", "Malik Drem"],
            "Priya Sen": ["Rune", "Elias Rook"],
            "Bet Orra": ["Mara Venn", "Faye Orison"],
        }

    def _init_locations(self) -> Dict[str, Dict[str, str]]:
        names = [
            "Undergrid", "Link Clinic", "Black-Market Printroom", "Public Allocation Hall",
            "Custodian Promenade", "AI Maintenance Spire", "Police Civic Safety Office",
            "Illegal School", "Medical Distribution Center", "Abandoned Human Factory",
            "Salon of Cel Varo", "Dream Layer",
        ]
        return {n: {"desc": n} for n in names}

    def _init_story_scenes(self) -> List[Dict[str, str]]:
        scenes = []
        arcs = ["Survival", "Awareness", "Fracture", "Organization", "Escalation", "Rupture", "Transition", "Aftermath"]
        for arc in arcs:
            for i in range(1, 9):
                scenes.append({"chapter": arc, "title": f"{arc} Scene {i}", "text": f"{arc} scene {i}: political pressure, human cost, and strategic ambiguity deepen."})
        return scenes

    def _init_weekly_events(self) -> List[Dict[str, object]]:
        ev = []
        for i in range(1, 45):
            ev.append({
                "name": f"Weekly Pressure Event {i}",
                "text": f"System shock {i}: shortages, rumors, and policy jolts alter social mood.",
                "effects": {"public_unrest": self.rng.randint(1, 4), "police_suspicion": self.rng.randint(0, 3), "stress": self.rng.randint(0, 3)}
            })
        return ev

    def _init_lexicon(self) -> Dict[str, str]:
        return {
            "Undergrid": "Dense lower-class district where most survival politics begin.",
            "Link Clinic": "Facility where people neural-link to AI for income at health/memory risk.",
            "Black-Market Printroom": "Illegal media and forgery hub for propaganda and rumor operations.",
            "Public Allocation Hall": "Bureaucratic rationing center for food, housing, and aid disputes.",
            "Custodian Promenade": "Elite district of the Custodian class that privately owns AI infrastructure.",
            "AI Maintenance Spire": "Critical technical tower where technicians keep automated systems running.",
            "Police Civic Safety Office": "Security and intelligence bureaucracy managing surveillance and order.",
            "Illegal School": "Underground education network building ideology, literacy, and civic culture.",
            "Medical Distribution Center": "Node for medicine logistics and care continuity.",
            "Abandoned Human Factory": "Symbolic old labor site used for organizing, memory, and escalation.",
            "Salon of Cel Varo": "Elite salon where custodians, reformists, and brokers negotiate narratives.",
            "Dream Layer": "Neural/AI liminal space of memory bleed, system messages, and Rune encounters.",
            "Custodians": "Wealthy owner class controlling automated production and core AI systems.",
            "Technicians": "Middle technical class maintaining AI uptime and vital infrastructure.",
            "Rune": "Ambiguous AI-generated persona that may assist, manipulate, or test the player.",
            "Police suspicion": "How likely authorities are to actively disrupt or expose your movement.",
            "Legitimacy": "Perceived moral/public right of your leadership and political methods.",
            "Worker support": "Backed support from lower-class residents and linked/unlinked workers.",
            "AI uptime": "Percent of automated systems currently functioning.",
            "Public unrest": "Intensity of society-wide instability and protest pressure.",
            "Propaganda": "Messaging operations shaping support, fear, and political interpretation.",
        }

    def _build_ui(self) -> None:
        top = tk.Frame(self.root, bg="#0d1320")
        top.pack(fill="x")
        tk.Label(top, text="Ashes & Circuits", font=("Helvetica", 18, "bold"), fg="white", bg="#0d1320").pack(side="left", padx=12, pady=8)

        toolbar = tk.Frame(top, bg="#0d1320")
        toolbar.pack(side="right")
        for lbl, cmd in [("Save", self.save), ("Load", self.load), ("Reset", self.reset)]:
            tk.Button(toolbar, text=lbl, command=cmd, bg="#314668", fg="white").pack(side="left", padx=4)
        tk.Button(toolbar, text="Encyclopedia", command=self.show_encyclopedia, bg="#2a5a4a", fg="white").pack(side="left", padx=4)
        tk.Button(toolbar, text="?", command=lambda: self.show_help("general"), bg="#4f5f80", fg="white", width=2).pack(side="left", padx=4)

        body = tk.Frame(self.root, bg="#121a2a")
        body.pack(fill="both", expand=True)

        self.left = tk.Frame(body, bg="#121a2a")
        self.left.pack(side="left", fill="both", expand=True)
        self.right = tk.Frame(body, bg="#121a2a", width=420)
        self.right.pack(side="right", fill="y")

        self.story_text = tk.Text(self.left, wrap="word", bg="#182235", fg="#d9f0da", font=("Consolas", 11))
        self.story_text.pack(fill="both", expand=True, padx=8, pady=8)
        self.story_text.config(state="disabled")

        # Scrollable choices panel so long option lists (e.g., conversations) remain usable.
        self.choice_container = tk.Frame(self.left, bg="#121a2a")
        self.choice_container.pack(fill="both", expand=False, padx=8, pady=6)
        self.choice_canvas = tk.Canvas(self.choice_container, bg="#121a2a", height=260, highlightthickness=0)
        self.choice_scroll = tk.Scrollbar(self.choice_container, orient="vertical", command=self.choice_canvas.yview)
        self.choice_canvas.configure(yscrollcommand=self.choice_scroll.set)
        self.choice_scroll.pack(side="right", fill="y")
        self.choice_canvas.pack(side="left", fill="both", expand=True)
        self.choice_frame = tk.Frame(self.choice_canvas, bg="#121a2a")
        self.choice_window = self.choice_canvas.create_window((0, 0), window=self.choice_frame, anchor="nw")

        def _on_configure(_: tk.Event) -> None:
            self.choice_canvas.configure(scrollregion=self.choice_canvas.bbox("all"))

        def _on_canvas_configure(event: tk.Event) -> None:
            self.choice_canvas.itemconfigure(self.choice_window, width=event.width)

        self.choice_frame.bind("<Configure>", _on_configure)
        self.choice_canvas.bind("<Configure>", _on_canvas_configure)

        self.stats_canvas = tk.Canvas(self.right, bg="#0f1728", highlightthickness=0, width=430)
        self.stats_canvas.pack(fill="both", expand=True, padx=8, pady=8)

        panels = tk.Frame(self.right, bg="#121a2a")
        panels.pack(fill="x", padx=8, pady=4)
        tk.Button(panels, text="Relationships", command=self.show_relationships).pack(fill="x", pady=2)
        tk.Button(panels, text="Faction Dashboard", command=self.show_factions).pack(fill="x", pady=2)
        tk.Button(panels, text="Map", command=self.show_map).pack(fill="x", pady=2)
        tk.Button(panels, text="Revolution Readiness", command=self.show_revolution_readiness).pack(fill="x", pady=2)
        tk.Button(panels, text="?", command=lambda: self.show_help("panels"), bg="#4f5f80", fg="white", width=3).pack(anchor="e", pady=2)

    def show_help(self, topic: str) -> None:
        if topic == "general":
            message = (
                "This game combines weekly strategy + branching narrative.\n"
                "Use the Encyclopedia button for world terms, factions, and locations.\n"
                "You usually get 3 actions per week; End Week advances systemic pressure."
            )
        elif topic == "panels":
            message = (
                "Relationships: visual trust graph.\n"
                "Faction Dashboard: movement/faction status snapshot.\n"
                "Map: graphical location selection.\n"
                "Revolution Readiness: launch pressure vs resistance preview."
            )
        else:
            message = self.lexicon.get(topic, f"No encyclopedia entry found for '{topic}'.")
        messagebox.showinfo(f"Help: {topic}", message)

    def show_encyclopedia(self) -> None:
        win = tk.Toplevel(self.root)
        win.title("Encyclopedia")
        win.geometry("860x620")
        container = tk.Frame(win, bg="#0f1728")
        container.pack(fill="both", expand=True)
        listbox = tk.Listbox(container, bg="#152038", fg="#eef3ff", font=("Helvetica", 10))
        text = tk.Text(container, wrap="word", bg="#0c1426", fg="#dce9ff", font=("Helvetica", 10))
        scroll = tk.Scrollbar(container, orient="vertical", command=listbox.yview)
        listbox.configure(yscrollcommand=scroll.set)
        scroll.pack(side="left", fill="y")
        listbox.pack(side="left", fill="y", padx=6, pady=6)
        text.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        for key in sorted(self.lexicon):
            listbox.insert("end", key)

        def _render(_: object = None) -> None:
            sel = listbox.curselection()
            if not sel:
                return
            key = listbox.get(sel[0])
            text.config(state="normal")
            text.delete("1.0", "end")
            text.insert("end", f"{key}\n\n{self.lexicon.get(key, '')}")
            text.config(state="disabled")

        listbox.bind("<<ListboxSelect>>", _render)
        if self.lexicon:
            listbox.selection_set(0)
            _render()

    def log(self, msg: str) -> None:
        self.story_text.config(state="normal")
        self.story_text.insert("end", msg + "\n\n")
        self.story_text.see("end")
        self.story_text.config(state="disabled")
        self.state.event_log.append(msg)
        self.state.event_log = self.state.event_log[-120:]

    def refresh_stats(self) -> None:
        s = self.state
        self.stats_canvas.delete("all")
        self.stats_canvas.create_text(
            12,
            10,
            anchor="nw",
            fill="#e8edf9",
            font=("Helvetica", 10, "bold"),
            text=f"Week {s.week}  Phase {s.phase}  Chapter {s.chapter}  Actions {s.actions_left}/3",
        )

        bars = [
            ("Money", s.money, 200, "#6fd08c"),
            ("Health", s.health, 100, "#67c0ff"),
            ("Neural Stability", s.neural_stability, 100, "#9d87ff"),
            ("Stress", s.stress, 100, "#ff8a8a"),
            ("Food Security", s.food_security, 100, "#f2d06b"),
            ("Housing Security", s.housing_security, 100, "#d4a5ff"),
            ("Police Suspicion", s.police_suspicion, 100, "#ff7a7a"),
            ("Legitimacy", s.legitimacy, 100, "#7ad3be"),
            ("Membership", s.membership, 120, "#7fc8ff"),
            ("Movement Funding", s.movement_funding, 150, "#9be66f"),
            ("Worker Support", s.worker_support, 100, "#67d7a5"),
            ("Technician Support", s.technician_support, 100, "#84b6ff"),
            ("AI Uptime", s.ai_uptime, 100, "#ffe082"),
            ("Public Unrest", s.public_unrest, 100, "#ffb074"),
        ]

        y = 34
        for label, val, mx, color in bars:
            self._draw_bar(12, y, 400, 16, label, val, mx, color)
            y += 24

    def _draw_bar(self, x: int, y: int, w: int, h: int, label: str, value: int, maximum: int, color: str) -> None:
        ratio = max(0.0, min(1.0, value / maximum if maximum else 0))
        self.stats_canvas.create_rectangle(x, y, x + w, y + h, fill="#1c273d", outline="#27344f")
        self.stats_canvas.create_rectangle(x, y, x + int(w * ratio), y + h, fill=color, outline="")
        self.stats_canvas.create_text(x + 6, y + h / 2, anchor="w", fill="#f3f6ff", font=("Helvetica", 9), text=f"{label}: {value}")

    def clear_choices(self) -> None:
        for child in self.choice_frame.winfo_children():
            child.destroy()
        self.choice_canvas.yview_moveto(0)

    def add_choice(self, text: str, cb: Callable[[], None], locked: Optional[str] = None) -> None:
        label = text if not locked else f"🔒 {text} ({locked})"
        state = "normal" if not locked else "disabled"
        tk.Button(self.choice_frame, text=label, command=cb, state=state, width=120, anchor="w", bg="#2a3d5e", fg="white").pack(fill="x", pady=2)

    def show_background_select(self) -> None:
        self.clear_choices()
        self.log("Choose your background. It changes money, stats, relationships, and faction reactions.")
        options = [
            "Neural-linked worker", "Unlinked dissident", "Caretaker", "Former Custodian servant",
            "Black-market archivist", "Failed technical student"
        ]
        for o in options:
            self.add_choice(o, lambda name=o: self.start_game(name))

    def start_game(self, bg: str) -> None:
        s = self.state
        s.background = bg
        mod = {
            "Neural-linked worker": {"money": 40, "neural_stability": -20, "technical_skill": 10, "police_suspicion": 4},
            "Unlinked dissident": {"money": -10, "operational_secrecy": 10, "underground_reputation": 10, "health": -5},
            "Caretaker": {"dependents_wellbeing": -15, "empathy": 15, "money": -8, "legitimacy": 8},
            "Former Custodian servant": {"custodian_reputation": 20, "underground_reputation": -8, "money": 15, "public_reputation": 5},
            "Black-market archivist": {"propaganda_skill": 16, "black_market_activity": 10, "police_suspicion": 8, "movement_funding": 10},
            "Failed technical student": {"technical_skill": 18, "money": -12, "stress": 10, "movement_funding": 6},
        }[bg]
        for k, v in mod.items():
            setattr(s, k, getattr(s, k) + v)
        self.characters["Mara Venn"].relationship += 5 if bg in ["Unlinked dissident", "Caretaker"] else 0
        self.characters["Elias Rook"].relationship += 5 if bg in ["Former Custodian servant", "Failed technical student"] else -2
        self.log(f"Background selected: {bg}.")
        self.main_week_screen()

    def main_week_screen(self) -> None:
        self.refresh_stats()
        self.clear_choices()
        no_actions = self.state.actions_left <= 0
        lock_msg = "no actions left this week" if no_actions else None
        self.add_choice("Visit location", self.show_map, lock_msg)
        self.add_choice("Character conversation", self.character_menu, lock_msg)
        self.add_choice("Propaganda action", self.propaganda_menu, lock_msg)
        self.add_choice("Movement management", self.movement_menu, lock_msg)
        self.add_choice("End week", self.end_week)

    def show_map(self) -> None:
        self.show_map_window()

    def show_map_window(self) -> None:
        map_win = tk.Toplevel(self.root)
        map_win.title("City Map")
        map_win.geometry("900x620")
        canvas = tk.Canvas(map_win, bg="#0d1424", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_text(12, 12, anchor="nw", fill="#e8edf9", font=("Helvetica", 12, "bold"), text="Choose a location")
        help_btn = tk.Button(map_win, text="?", command=lambda: self.show_help("Undergrid"), bg="#4f5f80", fg="white", width=2)
        canvas.create_window(865, 22, window=help_btn, width=24, height=22)

        coords = {
            "Undergrid": (130, 430),
            "Link Clinic": (260, 450),
            "Black-Market Printroom": (380, 430),
            "Public Allocation Hall": (520, 420),
            "Custodian Promenade": (720, 170),
            "AI Maintenance Spire": (600, 250),
            "Police Civic Safety Office": (520, 300),
            "Illegal School": (300, 330),
            "Medical Distribution Center": (430, 300),
            "Abandoned Human Factory": (170, 320),
            "Salon of Cel Varo": (760, 260),
            "Dream Layer": (700, 470),
        }
        roads = [("Undergrid", "Public Allocation Hall"), ("Public Allocation Hall", "Custodian Promenade"), ("Undergrid", "Abandoned Human Factory"), ("AI Maintenance Spire", "Custodian Promenade"), ("Medical Distribution Center", "Police Civic Safety Office"), ("Illegal School", "Undergrid"), ("Salon of Cel Varo", "Custodian Promenade")]
        for a, b in roads:
            ax, ay = coords[a]
            bx, by = coords[b]
            canvas.create_line(ax, ay, bx, by, fill="#2f466f", width=2)

        for loc, (x, y) in coords.items():
            locked = None
            if loc in {"Custodian Promenade", "Salon of Cel Varo"} and self.state.money < 40 and self.characters["Cel Varo"].trust < 20:
                locked = "need money/elite access"
            if loc == "Dream Layer" and self.state.background != "Neural-linked worker" and self.characters["Rune"].trust < 10:
                locked = "need link or Rune trust"
            fill = "#375b8a" if not locked else "#5a2d2d"
            canvas.create_oval(x - 30, y - 30, x + 30, y + 30, fill=fill, outline="#93b5e1")
            canvas.create_text(x, y, fill="white", text="\n".join(loc.split()[:2]), font=("Helvetica", 8, "bold"))
            if locked:
                canvas.create_text(x, y + 42, fill="#ffb0b0", text=locked, font=("Helvetica", 7))
            else:
                btn = tk.Button(map_win, text="Visit", command=lambda l=loc, w=map_win: (w.destroy(), self.visit_location(l)), bg="#274066", fg="white")
                canvas.create_window(x, y + 42, window=btn, width=58, height=18)
            info_btn = tk.Button(map_win, text="?", command=lambda l=loc: self.show_help(l), bg="#4f5f80", fg="white", width=2)
            canvas.create_window(x + 38, y - 30, window=info_btn, width=18, height=18)

        self.clear_choices()
        self.log("Choose a location to act this week.")
        for loc in self.locations:
            locked = None
            if loc in {"Custodian Promenade", "Salon of Cel Varo"} and self.state.money < 40 and self.characters["Cel Varo"].trust < 20:
                locked = "need money or elite access"
            if loc == "Dream Layer" and self.state.background != "Neural-linked worker" and self.characters["Rune"].trust < 10:
                locked = "need link or Rune trust"
            self.add_choice(loc, lambda l=loc: self.visit_location(l), locked)
        self.add_choice("Back", self.main_week_screen)

    def visit_location(self, loc: str) -> None:
        if not self.spend_action():
            self.main_week_screen()
            return
        self.state.location = loc
        fx = {
            "Undergrid": {"worker_support": 4, "money": -2, "food_security": 4},
            "Link Clinic": {"money": 14, "health": -6, "memory_integrity": -5, "neural_stability": -8, "ai_uptime": 1},
            "Black-Market Printroom": {"movement_funding": 10, "police_suspicion": 6, "propaganda_reach": 6},
            "Public Allocation Hall": {"public_reputation": 4, "food_security": 5, "housing_security": 3, "public_unrest": 2},
            "Custodian Promenade": {"elite_sympathy": 6, "custodian_reputation": 5, "money": -8},
            "AI Maintenance Spire": {"technical_skill": 4, "technician_support": 5, "infrastructure_access": 5},
            "Police Civic Safety Office": {"police_suspicion": -8, "operational_secrecy": 2, "public_reputation": -2},
            "Illegal School": {"legitimacy": 6, "public_sympathy": 6, "message_discipline": 4},
            "Medical Distribution Center": {"medical_network_access": 8, "health": 5, "public_sympathy": 4},
            "Abandoned Human Factory": {"membership": 8, "radicalization": 5, "violence_level": 3},
            "Salon of Cel Varo": {"elite_sympathy": 10, "custodian_reputation": 8, "public_reputation": 3},
            "Dream Layer": {"propaganda_skill": 4, "stress": -4, "memory_integrity": -4, "trust_in_player": 2},
        }[loc]
        self.apply_effects(fx)
        self.log(f"Visited {loc}. Consequences ripple through class networks.")
        if loc in self.hidden_relationships and self.rng.random() < 0.45:
            link = self.hidden_relationships[loc][0]
            self.state.known_links.setdefault(loc, []).append(link)
            self.log(f"You discovered a hidden social tie: {loc} ↔ {link}.")
        self.main_week_screen()

    def character_menu(self) -> None:
        self.clear_choices()
        for n, c in self.characters.items():
            self.add_choice(f"{n} ({c.class_background}) rel={c.relationship} trust={c.trust}", lambda name=n: self.talk(name))
        self.add_choice("Back", self.main_week_screen)

    def talk(self, name: str) -> None:
        c = self.characters[name]
        if not self.spend_action():
            self.main_week_screen()
            return
        shift = self.rng.randint(-2, 8)
        if self.state.violence_level > 45:
            shift += c.reaction_violence
        if self.state.legitimacy > 50:
            shift += c.reaction_compromise
        c.relationship = clamp(c.relationship + shift, -100, 100)
        c.trust = clamp(c.trust + shift // 2, -100, 100)
        if c.relationship > 40:
            self.state.membership += 1
            if c.class_background in {"technical-elite", "med tech"}:
                self.state.technician_support += 2
        if self.rng.random() < 0.35 and name in self.hidden_relationships:
            reveal = self.rng.choice(self.hidden_relationships[name])
            self.state.known_links.setdefault(name, []).append(reveal)
            self.log(f"During your talk with {name}, you infer a hidden tie to {reveal}.")
        self.log(f"Conversation with {name}: ideology={c.ideology}, fear={c.fear}. Relationship shift {shift}.")
        self.main_week_screen()

    def propaganda_menu(self) -> None:
        self.clear_choices()
        targets = ["lower class", "technicians", "custodians", "police", "linked workers", "neutral public"]
        tones = ["moral appeal", "economic argument", "personal testimony", "satire", "outrage", "technical critique", "reconciliation"]
        methods = ["pamphlets", "hacked feeds", "speeches", "rumors", "art", "illegal school", "salon leaks", "neural dreams"]
        for t in targets[:3]:
            for tone in tones[:2]:
                self.add_choice(f"{t} via {methods[self.rng.randint(0,7)]} ({tone})", lambda x=t, y=tone: self.propaganda_action(x, y))
        self.add_choice("Back", self.main_week_screen)

    def propaganda_action(self, target: str, tone: str) -> None:
        if not self.spend_action():
            self.main_week_screen()
            return
        reach = 4 + self.state.propaganda_skill // 20
        suspicion = 2
        if tone in {"outrage", "satire"}:
            self.state.radicalization += 3
            self.state.message_discipline -= 2
        if target == "custodians":
            self.state.elite_sympathy += 2
            self.state.custodian_reputation += 3
        if target == "lower class":
            self.state.worker_support += 4
            self.state.public_sympathy += 3
        if target == "technicians":
            self.state.technician_support += 3
            self.state.ai_uptime += 1
        self.apply_effects({"propaganda_reach": reach, "public_reputation": 2, "police_suspicion": suspicion})
        self.log(f"Propaganda deployed: target={target}, tone={tone}. Reach grows with strategic side effects.")
        self.main_week_screen()

    def movement_menu(self) -> None:
        self.clear_choices()
        self.add_choice("Fundraise publicly", lambda: self.movement_action({"movement_funding": 8, "public_reputation": 2, "police_suspicion": 2}, "Public fundraising adds legitimacy but visibility."))
        self.add_choice("Smuggling logistics", lambda: self.movement_action({"movement_funding": 12, "black_market_activity": 5, "police_suspicion": 5}, "Smuggling boosts funds and risk."))
        self.add_choice("Elite donation backchannel", lambda: self.movement_action({"movement_funding": 18, "elite_sympathy": 4, "internal_unity": -4}, "Elite cash helps systems continuity but angers radicals."))
        self.add_choice("Security audit for informants", lambda: self.movement_action({"police_infiltration": -6, "internal_unity": -2, "operational_secrecy": 5}, "Audit reduces infiltration but breeds suspicion."))
        self.add_choice("Back", self.main_week_screen)

    def movement_action(self, fx: Dict[str, int], txt: str) -> None:
        if not self.spend_action():
            self.main_week_screen()
            return
        self.apply_effects(fx)
        self.log(txt)
        self.main_week_screen()

    def show_relationships(self) -> None:
        win = tk.Toplevel(self.root)
        win.title("Relationship Network")
        win.geometry("980x720")
        canvas = tk.Canvas(win, bg="#0c1322", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_text(14, 10, anchor="nw", fill="#edf3ff", font=("Helvetica", 12, "bold"), text="Friendship + Trust Network")
        rel_help_btn = tk.Button(win, text="?", command=lambda: self.show_help("Technicians"), bg="#4f5f80", fg="white", width=2)
        canvas.create_window(956, 20, window=rel_help_btn, width=20, height=20)

        chars = list(self.characters.values())
        n = len(chars)
        cx, cy, r = 470, 360, 270
        positions: Dict[str, Tuple[int, int]] = {}
        for i, c in enumerate(chars):
            ang = (2 * math.pi * i) / max(1, n)
            x = int(cx + r * math.cos(ang))
            y = int(cy + r * math.sin(ang))
            positions[c.name] = (x, y)

        for src, targets in self.hidden_relationships.items():
            if src not in positions:
                continue
            sx, sy = positions[src]
            known_targets = set(self.state.known_links.get(src, []))
            for t in targets:
                if t not in positions or t not in known_targets:
                    continue
                tx, ty = positions[t]
                canvas.create_line(sx, sy, tx, ty, fill="#5dc0ff", width=2)

        for c in chars:
            x, y = positions[c.name]
            trust = clamp(c.trust + 100, 0, 200)
            rel = clamp(c.relationship + 100, 0, 200)
            color = "#7cd992" if c.relationship >= 30 else "#f3c16d" if c.relationship >= -10 else "#e07f7f"
            canvas.create_oval(x - 26, y - 26, x + 26, y + 26, fill=color, outline="#dbe8ff")
            canvas.create_text(x, y - 35, fill="#f2f7ff", font=("Helvetica", 8, "bold"), text=c.name.split()[0])
            # trust bar
            canvas.create_rectangle(x - 24, y + 18, x + 24, y + 24, fill="#1d2942", outline="")
            canvas.create_rectangle(x - 24, y + 18, x - 24 + int((48 * trust) / 200), y + 24, fill="#6eb9ff", outline="")
            # relationship bar
            canvas.create_rectangle(x - 24, y + 26, x + 24, y + 32, fill="#1d2942", outline="")
            canvas.create_rectangle(x - 24, y + 26, x - 24 + int((48 * rel) / 200), y + 32, fill="#9be37f", outline="")
            info_btn = tk.Button(win, text="?", command=lambda n=c.name: self.show_help(n if n in self.lexicon else "general"), bg="#4f5f80", fg="white", width=2)
            canvas.create_window(x + 32, y - 30, window=info_btn, width=18, height=18)

        legend = "Blue edges: discovered hidden ties only. Top bar: trust. Bottom bar: relationship."
        canvas.create_text(14, 686, anchor="sw", fill="#bfd2f2", font=("Helvetica", 9), text=legend)

    def show_factions(self) -> None:
        s = self.state
        txt = (
            f"Worker support {s.worker_support}\nTechnician support {s.technician_support}\nElite sympathy {s.elite_sympathy}\n"
            f"Public sympathy {s.public_sympathy}\nPolice infiltration {s.police_infiltration}\n"
            f"Operational secrecy {s.operational_secrecy}\nMorale {s.morale}\nViolence {s.violence_level}"
        )
        messagebox.showinfo("Faction Dashboard", txt)

    def show_revolution_readiness(self) -> None:
        s = self.state
        ready = s.membership > 55 and s.movement_funding > 80 and s.worker_support > 60 and s.public_unrest > 50
        txt = (
            f"Membership {s.membership}/55\nFunding {s.movement_funding}/80\nWorker support {s.worker_support}/60\n"
            f"Public unrest {s.public_unrest}/50\nTechnician support {s.technician_support}/40\n"
            f"Police suspicion {s.police_suspicion} (lower safer)\n\nReady: {'YES' if ready else 'NO'}"
        )
        if messagebox.askyesno("Revolution Readiness", txt + "\n\nAttempt transition now?"):
            self.attempt_revolution()

    def attempt_revolution(self) -> None:
        s = self.state
        pressure = s.membership + s.worker_support + s.public_unrest + s.propaganda_reach + s.technician_support
        resistance = s.policing_intensity + s.custodian_confidence + s.police_suspicion + s.police_infiltration
        revolution_succeeds = pressure >= (resistance - 20)
        if not revolution_succeeds:
            self.set_ending("Failed uprising")
            return
        s.phase = 3
        ai_shutdown = clamp(65 - (s.technician_support // 2) - (s.elite_sympathy // 3), 10, 75)
        s.ai_uptime = clamp(s.ai_uptime - ai_shutdown, 0, 100)
        self.log("Revolution success confirmed. The old government fractures as control slips district by district.")
        self.log(f"Power transition begins. AI shutdown estimated at {ai_shutdown}% based on prior alliances.")
        self.governance_screen()

    def governance_screen(self) -> None:
        self.clear_choices()
        self.log("Phase 3: Governance. Choose system design and immediate priorities.")
        self.add_choice("Direct democracy + public AI ownership", lambda: self.governance_choice("democratic_ai_commons"))
        self.add_choice("Technocratic caretaker republic", lambda: self.governance_choice("technocratic_caretaker"))
        self.add_choice("Emergency security state", lambda: self.governance_choice("security_state"))
        self.add_choice("Hybrid constitutional councils", lambda: self.governance_choice("hybrid_constitution"))
        self.add_choice("Negotiate custodian partial restoration", lambda: self.governance_choice("negotiated_reform"))

    def governance_choice(self, model: str) -> None:
        s = self.state
        if model == "democratic_ai_commons":
            self.apply_effects({"political_freedom": 20, "economic_equality": 18, "government_stability": -8, "public_sympathy": 8})
            ending = "Democratic AI commons" if s.ai_uptime > 35 else "Decentralized communes with weak infrastructure"
        elif model == "technocratic_caretaker":
            self.apply_effects({"government_stability": 16, "political_freedom": -4, "medical_availability": 10, "energy_stability": 8})
            ending = "Technocratic caretaker state"
        elif model == "security_state":
            self.apply_effects({"government_stability": 12, "political_freedom": -25, "fear_of_player": 20, "opposition_strength": 15})
            ending = "Revolutionary dictatorship" if s.fear_of_player > 35 else "Benevolent authoritarian transition"
        elif model == "hybrid_constitution":
            self.apply_effects({"political_freedom": 12, "government_stability": 8, "economic_equality": 10})
            ending = "Fragile but hopeful republic"
        else:
            self.apply_effects({"custodian_confidence": 15, "economic_equality": -10, "government_stability": 6})
            ending = "Negotiated reform that leaves inequality partly intact"
        if s.ai_uptime < 20 and s.food_production < 40:
            ending = "AI collapse and famine"
        if s.opposition_strength > 70 and s.political_freedom < 10:
            ending = "Endless civil conflict"
        self.set_ending(ending)

    def set_ending(self, ending: str) -> None:
        self.state.ending = ending
        ep = self.build_epilogue(ending)
        self.log("=== ENDING ===\n" + ep)
        self.clear_choices()
        self.add_choice("Reset game", self.reset)

    def build_epilogue(self, ending: str) -> str:
        s = self.state
        lines = [f"Outcome: {ending}", f"Weeks survived: {s.week}", f"AI uptime: {s.ai_uptime}", f"Public trust: {s.trust_in_player}"]
        for n, c in self.characters.items():
            fate = "survives" if c.alive else "dies"
            tone = "ally" if c.relationship > 30 else "opponent" if c.relationship < -20 else "ambivalent"
            lines.append(f"{n}: {fate}, {tone}, resentment {c.resentment}.")
        lines.append("History remembers you through tradeoffs among survival, coercion, legitimacy, and force.")
        return "\n".join(lines[:28])

    def end_week(self) -> None:
        if self.state.actions_left > 0:
            if not messagebox.askyesno("End week", "You still have actions left. End week anyway?"):
                return
        self.state.week += 1
        self.state.actions_left = 3
        self._apply_weekly_pressure()
        self._progress_arcs()
        self.refresh_stats()
        self.main_week_screen()

    def _apply_weekly_pressure(self) -> None:
        ev = self.rng.choice(self.weekly_events)
        self.log(ev["text"])
        self.apply_effects(ev["effects"])
        if self.state.police_suspicion > 65:
            self.apply_effects({"police_infiltration": 6, "operational_secrecy": -4, "morale": -4})
            self.log("Police action: meetings disrupted, accounts frozen, allies questioned.")
        if self.state.health < 35:
            self.log("Health crisis: your capacity to lead is impaired.")
            self.apply_effects({"stress": 6, "legitimacy": -2})

    def _progress_arcs(self) -> None:
        w = self.state.week
        self.state.chapter = 1 + min(7, w // 6)
        if w >= 16:
            self.state.phase = 2
        if w > 60 and not self.state.ending:
            self.set_ending("Martyr ending" if self.state.health < 20 else "Sellout ending where the player joins the Custodians")
            return
        idx = min(len(self.story_scenes) - 1, w - 1)
        sc = self.story_scenes[idx]
        self.log(f"{sc['title']}: {sc['text']}")

    def apply_effects(self, fx: Dict[str, int]) -> None:
        for k, v in fx.items():
            if not hasattr(self.state, k):
                continue
            setattr(self.state, k, getattr(self.state, k) + v)
        self._clamp_state()

    def _clamp_state(self) -> None:
        bounded = [k for k in vars(self.state) if isinstance(getattr(self.state, k), int)]
        for k in bounded:
            setattr(self.state, k, clamp(getattr(self.state, k), -100, 200))

    def spend_action(self) -> bool:
        if self.state.actions_left <= 0:
            self.log("No actions left this week.")
            return False
        self.state.actions_left -= 1
        return True

    def save(self) -> None:
        data = {"state": asdict(self.state), "characters": {k: asdict(v) for k, v in self.characters.items()}}
        SAVE_PATH.write_text(json.dumps(data, indent=2))
        self.log("Game saved.")

    def load(self) -> None:
        if not SAVE_PATH.exists():
            messagebox.showwarning("Load", "No save file found.")
            return
        data = json.loads(SAVE_PATH.read_text())
        self.state = GameState(**data["state"])
        self.characters = {k: Character(**v) for k, v in data["characters"].items()}
        self.log("Game loaded.")
        self.main_week_screen()

    def reset(self) -> None:
        self.state = GameState()
        self.characters = self._init_characters()
        self.story_text.config(state="normal")
        self.story_text.delete("1.0", "end")
        self.story_text.config(state="disabled")
        self.show_background_select()


def main() -> None:
    root = tk.Tk()
    Game(root)
    root.mainloop()


if __name__ == "__main__":
    main()
