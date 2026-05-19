#!/usr/bin/env python3
"""Ashes & Circuits - large-scale graphical narrative simulation."""
from __future__ import annotations

import json
import random
import tkinter as tk
from dataclasses import dataclass, asdict, field
from pathlib import Path
from tkinter import messagebox
from typing import Callable, Dict, List, Optional, Set

SAVE_PATH = Path("savegame.json")


def clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))


@dataclass
class Character:
    name: str
    role: str
    ideology: str
    private_fear: str
    relationship: int = 0
    trust: int = 0
    loyalty: int = 50
    fear: int = 10
    resentment: int = 0
    grief: int = 0
    flexibility: int = 50
    alive: bool = True
    hidden_links: List[str] = field(default_factory=list)


@dataclass
class State:
    week: int = 1
    phase: int = 1
    chapter: int = 1
    seed: int = 42
    background: str = ""

    money: int = 30
    food_security: int = 45
    housing_security: int = 45
    health: int = 65
    neural_stability: int = 70
    stress: int = 30
    memory_integrity: int = 80
    dependents_wellbeing: int = 50

    public_reputation: int = 10
    underground_reputation: int = 15
    custodian_reputation: int = 5
    police_suspicion: int = 15
    propaganda_skill: int = 45
    technical_skill: int = 35
    empathy: int = 50
    ruthlessness: int = 20
    legitimacy: int = 18

    membership: int = 8
    funding: int = 20
    propaganda_reach: int = 5
    message_discipline: int = 40
    internal_unity: int = 45
    radicalization: int = 20
    public_sympathy: int = 22
    police_infiltration: int = 10
    secrecy: int = 45
    morale: int = 48
    violence_level: int = 5
    elite_sympathy: int = 6
    worker_support: int = 28
    technician_support: int = 14
    external_attention: int = 4
    infra_access: int = 8
    food_network: int = 10
    medical_network: int = 10
    energy_network: int = 10

    ai_uptime: int = 92
    food_production: int = 68
    medical_availability: int = 66
    housing_stability: int = 62
    energy_stability: int = 70
    policing_intensity: int = 55
    censorship: int = 52
    public_unrest: int = 30
    custodian_confidence: int = 74
    lower_desperation: int = 72
    black_market: int = 40
    trust_in_player: int = 20
    fear_of_player: int = 8
    economic_equality: int = 18
    political_freedom: int = 28
    government_stability: int = 0
    opposition_strength: int = 30

    ai_autonomy: int = 12
    collapse_risk: int = 15

    revolution_triggered: bool = False
    won_revolution: bool = False
    ended: bool = False


class Game:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Ashes & Circuits")
        self.root.geometry("1360x860")
        self.state = State()
        self.rng = random.Random(self.state.seed)
        self.characters = self.make_characters()
        self.log: List[str] = []
        self.known_links: Dict[str, Set[str]] = {}
        self.flags: Set[str] = set()
        self.selected_location = "Undergrid"
        self.actions_this_week = 0
        self.max_actions = 3
        self.build_ui()
        self.show_background_selection()

    def make_characters(self) -> Dict[str, Character]:
        raw = [
            ("Mara Venn", "Organizer", "Revolutionary", "Collapse without engineers", ["Ansel Kade", "Bet Orra"]),
            ("Elias Rook", "AI Architect", "Public Utility Reform", "Halden's retaliation", ["Director Halden Myr", "Sera Quill"]),
            ("Sera Quill", "Custodian Heir", "Defensive Reform", "Class purge", ["Lysa Tem", "Cel Varo"]),
            ("Juno Pike", "Propaganda Artist", "Chaotic Populist", "Irrelevance", ["Olan Crete", "Malik Drem"]),
            ("Inspector Cal Vey", "Police Intelligence", "Orderist", "Famine collapse", ["Tomas Vale", "Director Halden Myr"]),
            ("Nadi Bex", "Linked Prodigy", "Unknown", "Dissolution of self", ["Rune", "Lysa Tem"]),
            ("Tomas Vale", "Elder", "Stability First", "Another failed uprising", ["Inspector Cal Vey", "Faye Orison"]),
            ("Iri Sol", "Theorist", "Abolitionist", "Compromise capture", ["Mara Venn", "Ansel Kade"]),
            ("Director Halden Myr", "Custodian Owner", "Elite Continuity", "Mob justice", ["Elias Rook", "Cal Vey"]),
            ("Lysa Tem", "Medical Technician", "Pragmatic Reform", "Hospital collapse", ["Sera Quill", "Priya Sen"]),
            ("Olan Crete", "Smuggler", "Transactional", "Poverty return", ["Juno Pike", "Bet Orra"]),
            ("Faye Orison", "Teacher", "Civic Democracy", "Revenge culture", ["Tomas Vale", "Priya Sen"]),
            ("Malik Drem", "Media Figure", "Narrative Control", "Being discarded", ["Juno Pike", "Cel Varo"]),
            ("Ansel Kade", "Militant", "Retribution", "Weak peace", ["Mara Venn", "Iri Sol"]),
            ("Priya Sen", "Systems Engineer", "Decentralization", "Grid fracture", ["Rune", "Lysa Tem"]),
            ("Rune", "AI Persona", "Ambiguous", "Shutdown", ["Priya Sen", "Nadi Bex"]),
            ("Cel Varo", "Socialite", "Managed Transition", "Loss of status", ["Sera Quill", "Malik Drem"]),
            ("Bet Orra", "Grieving Parent", "Protective Populist", "More dead children", ["Mara Venn", "Olan Crete"]),
        ]
        return {n: Character(n, r, i, f, hidden_links=h) for n, r, i, f, h in raw}

    def build_ui(self) -> None:
        top = tk.Frame(self.root, bg="#111827")
        top.pack(fill="x")
        tk.Label(top, text="Ashes & Circuits", fg="white", bg="#111827", font=("Arial", 18, "bold")).pack(side="left", padx=10)
        self.week_lbl = tk.Label(top, text="", fg="#9ad", bg="#111827", font=("Consolas", 12))
        self.week_lbl.pack(side="right", padx=10)

        body = tk.Frame(self.root, bg="#0b1020")
        body.pack(fill="both", expand=True)
        self.left = tk.Frame(body, bg="#0b1020")
        self.left.pack(side="left", fill="both", expand=True)
        right = tk.Frame(body, width=420, bg="#111827")
        right.pack(side="right", fill="y")

        self.story = tk.Text(self.left, wrap="word", bg="#101827", fg="#e8f0ff", font=("Georgia", 12))
        self.story.pack(fill="both", expand=True, padx=8, pady=8)

        self.choice_frame = tk.Frame(self.left, bg="#0b1020")
        self.choice_frame.pack(fill="x", padx=8, pady=6)

        self.stats = tk.Text(right, height=25, bg="#0f172a", fg="#c7e0ff", font=("Consolas", 10))
        self.stats.pack(fill="x", padx=8, pady=8)
        self.logbox = tk.Text(right, height=15, bg="#1f2937", fg="#d1fae5", font=("Consolas", 9))
        self.logbox.pack(fill="both", expand=True, padx=8, pady=8)

        btm = tk.Frame(right, bg="#111827")
        btm.pack(fill="x", padx=8, pady=8)
        for t, c in [("Map", self.map_screen), ("Relations", self.relations_screen), ("Dashboard", self.dashboard_screen),
                     ("Save", self.save_game), ("Load", self.load_game), ("Reset", self.reset_game)]:
            tk.Button(btm, text=t, command=c).pack(side="left", padx=2)

    def clear_choices(self):
        for w in self.choice_frame.winfo_children():
            w.destroy()

    def choice(self, label: str, cmd: Callable[[], None], locked: Optional[str] = None):
        txt = label if not locked else f"[LOCKED: {locked}] {label}"
        b = tk.Button(self.choice_frame, text=txt, anchor="w", wraplength=980, justify="left", command=cmd if not locked else None)
        b.pack(fill="x", pady=2)

    def log_line(self, text: str):
        self.log.append(text)
        self.log = self.log[-120:]
        self.logbox.delete("1.0", "end")
        self.logbox.insert("end", "\n".join(self.log[-40:]))

    def write(self, text: str):
        self.story.insert("end", text + "\n\n")
        self.story.see("end")

    def refresh(self):
        s = self.state
        self.week_lbl.config(text=f"Week {s.week} | Phase {s.phase} | Actions {self.actions_this_week}/{self.max_actions}")
        self.stats.delete("1.0", "end")
        key = [
            f"Money {s.money} | FoodSec {s.food_security} | HouseSec {s.housing_security}",
            f"Health {s.health} | Neural {s.neural_stability} | Memory {s.memory_integrity} | Stress {s.stress}",
            f"PublicRep {s.public_reputation} | UndergroundRep {s.underground_reputation} | CustodianRep {s.custodian_reputation}",
            f"PoliceSuspicion {s.police_suspicion} | Legitimacy {s.legitimacy}",
            f"Move: Members {s.membership}, Funding {s.funding}, Unity {s.internal_unity}, Violence {s.violence_level}",
            f"Support: Workers {s.worker_support}, Techs {s.technician_support}, Elite {s.elite_sympathy}, Sympathy {s.public_sympathy}",
            f"Society: AIUp {s.ai_uptime}, FoodProd {s.food_production}, Medical {s.medical_availability}, Energy {s.energy_stability}",
            f"Freedom {s.political_freedom}, Equality {s.economic_equality}, Opposition {s.opposition_strength}"
        ]
        self.stats.insert("end", "\n".join(key))

    def show_background_selection(self):
        self.write("Choose your background.")
        self.clear_choices()
        bgs = [
            "Neural-linked worker", "Unlinked dissident", "Caretaker", "Former Custodian servant",
            "Black-market archivist", "Failed technical student"
        ]
        for b in bgs:
            self.choice(b, lambda bg=b: self.set_background(bg))

    def set_background(self, bg: str):
        s = self.state
        s.background = bg
        if bg == "Neural-linked worker":
            s.money += 20; s.technical_skill += 15; s.health -= 10; s.memory_integrity -= 15; s.police_suspicion += 8
        elif bg == "Unlinked dissident":
            s.money -= 10; s.police_suspicion -= 8; s.underground_reputation += 10; s.food_security -= 10
        elif bg == "Caretaker":
            s.dependents_wellbeing = 35; s.empathy += 15; s.money -= 8; s.legitimacy += 8
        elif bg == "Former Custodian servant":
            s.custodian_reputation += 20; s.underground_reputation -= 10; s.money += 12
        elif bg == "Black-market archivist":
            s.propaganda_skill += 18; s.black_market += 14; s.police_suspicion += 5
        elif bg == "Failed technical student":
            s.technical_skill += 20; s.money -= 12; s.stress += 12
        self.write(f"Background set: {bg}.")
        self.log_line(f"Started as {bg}")
        self.main_screen()

    def main_screen(self):
        if self.state.ended:
            return
        self.refresh()
        self.clear_choices()
        self.choice("Visit Location", self.map_screen)
        self.choice("Character Conversation", self.character_scene)
        self.choice("Propaganda Operation", self.propaganda_screen)
        self.choice("Weekly Strategy Action", self.strategy_action)
        self.choice("Revolution Readiness", self.revolution_panel)
        self.choice("End Week", self.end_week)

    LOCATIONS = ["Undergrid", "Link Clinic", "Black-Market Printroom", "Public Allocation Hall", "Custodian Promenade",
                 "AI Maintenance Spire", "Police Civic Safety Office", "Illegal School", "Medical Distribution Center",
                 "Abandoned Human Factory", "Salon of Cel Varo", "Dream Layer"]

    def map_screen(self):
        self.clear_choices()
        self.write("Map: choose a location.")
        for loc in self.LOCATIONS:
            lock = None
            if loc == "Custodian Promenade" and self.state.money < 25 and self.state.custodian_reputation < 20:
                lock = "Need money 25 or Custodian reputation 20"
            if loc == "Salon of Cel Varo" and "met_cel" not in self.flags and self.state.money < 40:
                lock = "Need invitation or 40 money"
            if loc == "Dream Layer" and self.state.neural_stability > 80 and "rune_contact" not in self.flags:
                lock = "Need link instability or Rune contact"
            self.choice(loc, lambda l=loc: self.visit(l), lock)
        self.choice("Back", self.main_screen)

    def visit(self, loc: str):
        self.selected_location = loc
        self.actions_this_week += 1
        s = self.state
        if loc == "Undergrid":
            s.worker_support += 4; s.public_sympathy += 2; s.food_security -= 2; self.write("You walk cramped alleys, hear hunger stories, and recruit survivors.")
        elif loc == "Link Clinic":
            s.money += 18; s.neural_stability -= 8; s.memory_integrity -= 6; s.health -= 4; self.write("You sell cognition cycles at the clinic for urgent cash.")
        elif loc == "Black-Market Printroom":
            s.propaganda_reach += 5; s.message_discipline -= 3; s.police_suspicion += 4; self.write("Juno's printroom floods streets with memetic pamphlets.")
        elif loc == "Public Allocation Hall":
            s.legitimacy += 4; s.public_reputation += 3; s.stress += 2; self.write("You witness bureaucratic cruelty and speak for ration lines.")
        elif loc == "Custodian Promenade":
            s.money -= 8; s.elite_sympathy += 4; s.custodian_reputation += 5; self.write("Glittering towers hide quiet panic among the Custodians.")
        elif loc == "AI Maintenance Spire":
            s.technical_skill += 4; s.infra_access += 6; s.technician_support += 4; s.police_suspicion += 5; self.write("In maintenance tunnels, Priya whispers decentralization plans.")
        elif loc == "Police Civic Safety Office":
            s.police_suspicion += 6; s.policing_intensity -= 3; s.internal_unity -= 2; self.write("You broker, bluff, and leak to survive the policing maze.")
        elif loc == "Illegal School":
            s.legitimacy += 6; s.message_discipline += 4; s.public_sympathy += 3; self.write("Faye's school teaches rights, memory, and dignity.")
        elif loc == "Medical Distribution Center":
            s.medical_network += 5; s.health += 5; s.public_sympathy += 2; self.write("Lysa lets you see how close the medicine network is to collapse.")
        elif loc == "Abandoned Human Factory":
            s.membership += 6; s.violence_level += 2; s.morale += 5; self.write("The old factory becomes a symbol, then a coordination hub.")
        elif loc == "Salon of Cel Varo":
            s.elite_sympathy += 8; s.money -= 12; s.custodian_reputation += 7; self.flags.add("met_cel"); self.write("At Cel's salon, reformists and predators drink from the same fear.")
        elif loc == "Dream Layer":
            s.ai_autonomy += 5; s.neural_stability -= 5; s.propaganda_skill += 3; self.flags.add("rune_contact"); self.write("Rune speaks in fractured symbols: aid, warning, or manipulation.")

        self.random_weekly_event()
        self.clamp_all()
        self.log_line(f"Visited {loc}")
        if self.actions_this_week >= self.max_actions:
            self.write("No actions left this week. End week to continue.")
        self.main_screen()

    def character_scene(self):
        self.clear_choices()
        for n, c in self.characters.items():
            if not c.alive:
                continue
            self.choice(f"{n} ({c.role}) rel {c.relationship} trust {c.trust}", lambda name=n: self.talk(name))
        self.choice("Back", self.main_screen)

    def talk(self, name: str):
        s = self.state
        c = self.characters[name]
        self.actions_this_week += 1
        delta = self.rng.randint(-4, 10) + (s.empathy // 25) + (s.public_reputation // 30)
        if c.ideology in ["Revolutionary", "Abolitionist"] and s.ruthlessness < 25:
            delta -= 2
        if c.ideology in ["Public Utility Reform", "Defensive Reform"] and s.violence_level > 45:
            delta -= 6
        c.relationship += delta
        c.trust += delta // 2
        if delta > 0:
            self.write(f"Your exchange with {name} opens a new channel of trust.")
        else:
            self.write(f"{name} leaves unconvinced and wary.")
        if c.relationship > 45 and c.name == "Elias Rook":
            s.funding += 20; s.elite_sympathy += 4; self.write("Elias provides discreet funding and maintenance contacts.")
        if c.relationship > 55 and c.name == "Sera Quill":
            s.ai_uptime += 4; s.custodian_confidence -= 5; self.write("Sera leaks contingency protocols for a safer transition.")
        if self.rng.random() < 0.45:
            link = self.rng.choice(c.hidden_links)
            self.known_links.setdefault(name, set()).add(link)
            self.write(f"You discover a hidden link: {name} ↔ {link}")
        self.log_line(f"Talked with {name} ({delta:+})")
        self.random_weekly_event()
        self.clamp_all()
        self.main_screen()

    def propaganda_screen(self):
        self.clear_choices()
        targets = ["Lower Grid", "Technicians", "Custodians", "Police", "Linked Workers", "Unlinked Poor", "External Observers", "Neutral Public"]
        tones = ["Moral Appeal", "Economic Argument", "Personal Testimony", "Satire", "Outrage", "Technical Critique", "Spiritual Framing", "National Survival", "Reconciliation"]
        methods = ["Pamphlets", "Hacked Feeds", "Speeches", "Rumors", "Art", "Songs", "Illegal Schools", "Elite Salons", "Leaked Documents", "Neural Dreams"]
        risks = ["Safe", "Subtle", "Bold", "Illegal", "Reckless"]
        truths = ["Honest", "Simplified", "Exaggerated", "Fabricated"]
        for t in targets[:4]:
            for tone in tones[:2]:
                lbl = f"{t} / {tone} / {methods[self.rng.randint(0,9)]} / {risks[self.rng.randint(0,4)]} / {truths[self.rng.randint(0,3)]}"
                self.choice(lbl, lambda x=lbl: self.run_propaganda(x))
        self.choice("More options next week (randomized sets)", lambda: None)
        self.choice("Back", self.main_screen)

    def run_propaganda(self, config: str):
        self.actions_this_week += 1
        s = self.state
        risk = 1 + ["Safe", "Subtle", "Bold", "Illegal", "Reckless"].index(self.extract(config, 3))
        truth = self.extract(config, 4)
        reach = 5 + s.propaganda_skill // 10
        s.propaganda_reach += reach
        s.public_sympathy += 2
        s.police_suspicion += risk * 2
        s.radicalization += max(1, risk - 1)
        s.message_discipline -= 1 if "Rumors" in config else 0
        if truth == "Fabricated":
            s.short_term_boost = 6 if not hasattr(s, 'short_term_boost') else s.short_term_boost + 6
            s.legitimacy -= 2
            if self.rng.random() < 0.3:
                s.legitimacy -= 8; s.internal_unity -= 6; self.write("A fabrication is exposed. Trust shatters in key circles.")
        elif truth == "Honest":
            s.legitimacy += 4
        self.write(f"Propaganda campaign launched: {config}.")
        self.log_line(f"Propaganda: {config}")
        self.random_weekly_event()
        self.clamp_all()
        self.main_screen()

    def extract(self, cfg: str, idx: int) -> str:
        parts = [x.strip() for x in cfg.split('/')]
        return parts[idx] if idx < len(parts) else ""

    def strategy_action(self):
        self.clear_choices()
        acts = [
            ("Run food mutual-aid", lambda: self.apply({"money": -8, "food_security": 10, "public_sympathy": 6, "legitimacy": 4})),
            ("Smuggling run", lambda: self.apply({"money": 16, "black_market": 7, "police_suspicion": 6})),
            ("Negotiate with Cal Vey", lambda: self.apply({"police_suspicion": -6, "custodian_reputation": 3, "internal_unity": -4})),
            ("Leak Custodian crime", lambda: self.apply({"public_unrest": 8, "public_sympathy": 5, "police_suspicion": 7, "custodian_confidence": -8})),
            ("Train secrecy cells", lambda: self.apply({"secrecy": 8, "membership": 4, "police_infiltration": -4})),
            ("Encourage strikes against neural linking", lambda: self.apply({"worker_support": 8, "violence_level": 3, "ai_uptime": -5})),
            ("Protect elite defector", lambda: self.apply({"elite_sympathy": 7, "technician_support": 4, "internal_unity": -5})),
            ("Support militant escalation", lambda: self.apply({"violence_level": 10, "custodian_confidence": -10, "fear_of_player": 8, "public_sympathy": -3})),
        ]
        for label, fn in acts:
            self.choice(label, fn)
        self.choice("Back", self.main_screen)

    def apply(self, changes: Dict[str, int]):
        self.actions_this_week += 1
        for k, v in changes.items():
            setattr(self.state, k, getattr(self.state, k) + v)
        self.write(f"Strategic action completed: {', '.join(f'{k} {v:+}' for k, v in changes.items())}")
        self.log_line(f"Strategy: {changes}")
        self.random_weekly_event()
        self.clamp_all()
        self.main_screen()

    def random_weekly_event(self):
        s = self.state
        events = [
            ("Police raid in Undergrid", {"police_suspicion": 4, "membership": -2, "morale": -3}),
            ("Black market windfall", {"money": 10, "black_market": 4}),
            ("Food convoy delay", {"food_security": -6, "public_unrest": 4}),
            ("Linked worker collapse", {"health": -5, "public_sympathy": 3, "violence_level": 2}),
            ("Custodian scandal", {"custodian_confidence": -6, "public_sympathy": 4}),
            ("Technician strike rumor", {"technician_support": 5, "ai_uptime": -4}),
            ("Rune dream sequence", {"ai_autonomy": 3, "memory_integrity": -3}),
            ("Police informant arrested", {"police_infiltration": -4, "secrecy": 2}),
            ("Medical shortage", {"medical_availability": -7, "dependents_wellbeing": -4}),
            ("Elite salon split", {"elite_sympathy": 5, "custodian_reputation": 4}),
        ]
        # inflate to 40+ by templating
        for i in range(40):
            events.append((f"District pulse event {i+1}", {"public_unrest": self.rng.randint(-2, 3), "stress": self.rng.randint(-1, 2), "money": self.rng.randint(-3, 4)}))
        name, effects = self.rng.choice(events)
        for k, v in effects.items():
            setattr(s, k, getattr(s, k) + v)
        self.log_line(f"Event: {name}")

    def revolution_panel(self):
        s = self.state
        score = s.membership + s.public_sympathy + s.worker_support + s.technician_support + s.funding + s.propaganda_reach
        risk = s.police_suspicion + s.police_infiltration + s.internal_unity * -1 + s.collapse_risk
        self.write(f"Readiness score: {score}. Counter-pressure: {risk}.")
        self.clear_choices()
        self.choice("Attempt negotiated transfer", lambda: self.attempt_revolution("negotiated"))
        self.choice("Attempt mass refusal campaign", lambda: self.attempt_revolution("mass_refusal"))
        self.choice("Attempt coordinated uprising (abstract)", lambda: self.attempt_revolution("uprising"))
        self.choice("Delay and build capacity", self.main_screen)

    def attempt_revolution(self, mode: str):
        s = self.state
        self.actions_this_week += 1
        power = s.membership + s.public_sympathy + s.worker_support + s.technician_support + s.funding + s.propaganda_reach
        stability = s.policing_intensity + s.custodian_confidence + s.opposition_strength
        if mode == "negotiated":
            power += s.elite_sympathy + s.legitimacy
        elif mode == "mass_refusal":
            power += s.radicalization + (100 - s.ai_uptime)
        else:
            power += s.violence_level * 2; stability += 10
        self.state.revolution_triggered = True
        if power > stability + 40:
            s.won_revolution = True
            self.write("The old order fractures. You enter the government phase.")
            self.state.phase = 3
            self.governance_screen()
        elif power > stability:
            self.write("Partial transition: crisis government and contested legitimacy.")
            self.state.phase = 3
            self.governance_screen(partial=True)
        else:
            self.ending("Failed uprising")

    def governance_screen(self, partial: bool = False):
        s = self.state
        self.clear_choices()
        self.write("Government formation begins. Choose constitutional direction.")
        opts = [
            "Direct democracy", "Council democracy", "Technocratic republic", "Revolutionary party rule",
            "Temporary emergency government", "AI-assisted democracy", "Local communes", "Hybrid constitutional system",
            "Personal dictatorship", "Security state"
        ]
        for o in opts:
            self.choice(o, lambda g=o, p=partial: self.gov_pick(g, p))

    def gov_pick(self, gov: str, partial: bool):
        s = self.state
        self.flags.add(f"gov:{gov}")
        self.write(f"Government choice: {gov}")
        if "dictatorship" in gov.lower() or "security" in gov.lower() or "emergency" in gov.lower():
            s.political_freedom -= 20; s.government_stability += 20; s.fear_of_player += 20
        else:
            s.political_freedom += 15; s.government_stability += 5; s.legitimacy += 10
        self.clear_choices()
        econ = [
            "Public ownership of AI", "Citizen ownership", "Local cooperative control", "State-planned allocation",
            "Market with universal access", "Complete AI abolition", "Hybrid regulated model", "Forced labor by former Custodians",
            "Voluntary civic labor", "Rotating labor obligations", "Paid consensual neural linking", "Ban neural linking"
        ]
        for e in econ:
            self.choice(e, lambda x=e, p=partial: self.econ_pick(x, p))

    def econ_pick(self, econ: str, partial: bool):
        s = self.state
        self.flags.add(f"econ:{econ}")
        if "abolition" in econ.lower():
            s.ai_uptime -= 35; s.economic_equality += 25; s.food_production -= 20; s.medical_availability -= 20
        elif "forced labor" in econ.lower():
            s.ai_uptime += 20; s.political_freedom -= 18; s.opposition_strength += 18
        elif "citizen" in econ.lower() or "public" in econ.lower() or "cooperative" in econ.lower():
            s.economic_equality += 18; s.legitimacy += 10; s.ai_uptime -= 8
        else:
            s.ai_uptime += 8; s.economic_equality += 4
        self.post_revolution_events(partial)

    def post_revolution_events(self, partial: bool):
        s = self.state
        for i in range(20):
            s.food_production += self.rng.randint(-3, 3)
            s.medical_availability += self.rng.randint(-3, 3)
            s.energy_stability += self.rng.randint(-3, 3)
            s.opposition_strength += self.rng.randint(-2, 3)
            s.government_stability += self.rng.randint(-2, 2)
        self.clamp_all()
        self.determine_ending(partial)

    def determine_ending(self, partial: bool):
        s = self.state
        endings = []
        if s.political_freedom > 55 and s.economic_equality > 55 and s.ai_uptime > 55:
            endings.append("Democratic AI commons")
        if s.government_stability > 55 and s.political_freedom > 45:
            endings.append("Fragile but hopeful republic")
        if s.technical_skill > 60 and s.ai_uptime > 65 and s.political_freedom < 50:
            endings.append("Technocratic caretaker state")
        if s.government_stability > 65 and s.fear_of_player > 40:
            endings.append("Benevolent authoritarian transition")
        if s.fear_of_player > 60 and s.political_freedom < 20:
            endings.append("Revolutionary dictatorship")
        if partial and s.elite_sympathy > 30:
            endings.append("Negotiated reform with inequality intact")
        if s.food_production < 30 and s.medical_availability < 30:
            endings.append("AI collapse and famine")
        if s.opposition_strength > 70 and s.custodian_confidence > 50:
            endings.append("Elite restoration")
        if s.ai_autonomy > 40:
            endings.append("Rune-led ambiguous future")
        if s.ai_uptime < 35 and s.economic_equality > 45:
            endings.append("Decentralized communes with weak infrastructure")
        if s.opposition_strength > 65 and s.legitimacy < 25:
            endings.append("Personal betrayal and removal")
        if s.health < 25 and s.legitimacy > 40:
            endings.append("Martyr ending")
        if s.custodian_reputation > 45 and s.underground_reputation < 10:
            endings.append("Sellout alignment with Custodians")
        if s.violence_level > 75 and s.opposition_strength > 55:
            endings.append("Endless civil conflict")
        if s.legitimacy > 45 and s.political_freedom > 45 and s.opposition_strength < 45:
            endings.append("Restorative justice compromise")
        if not endings:
            endings = ["Failed uprising"]
        self.ending(endings[0], endings)

    def ending(self, title: str, options: Optional[List[str]] = None):
        s = self.state
        s.ended = True
        self.clear_choices()
        self.write(f"ENDING: {title}")
        self.write("Epilogue summary:")
        self.write(f"Society: AI uptime {s.ai_uptime}, food {s.food_production}, medical {s.medical_availability}, energy {s.energy_stability}.")
        self.write(f"Political climate: freedom {s.political_freedom}, equality {s.economic_equality}, stability {s.government_stability}, opposition {s.opposition_strength}.")
        self.write(f"Player legacy: legitimacy {s.legitimacy}, fear {s.fear_of_player}, trust {s.trust_in_player}.")
        self.write("Character outcomes:")
        for c in self.characters.values():
            fate = "survived" if c.alive else "dead"
            self.write(f"- {c.name}: {fate}, relationship {c.relationship}, resentment {c.resentment}.")
        if options and len(options) > 1:
            self.write("Other viable ending trajectories based on your state: " + ", ".join(options[1:4]))
        self.choice("Restart", self.reset_game)
        self.choice("Close", self.root.destroy)

    def end_week(self):
        if self.actions_this_week == 0:
            self.write("You spent the week hesitating; structures tighten around you.")
            self.state.police_suspicion += 2
        self.actions_this_week = 0
        s = self.state
        s.week += 1
        if s.week in [6, 12, 18, 24, 30, 36, 42, 50]:
            s.chapter += 1
            self.write(f"Chapter {s.chapter} begins.")
        if s.week >= 18 and s.phase == 1:
            s.phase = 2
            self.write("Phase 2: Organization and Escalation.")
        if s.week > 60 and not s.revolution_triggered:
            self.ending("Movement dissolved into managed reform")
            return
        # upkeep
        s.money -= 6
        s.food_security -= 3
        s.housing_security -= 2
        s.stress += 2
        if s.money < 0:
            s.health -= 3; s.lower_desperation += 4
        self.random_weekly_event()
        self.check_failures()
        self.clamp_all()
        self.main_screen()

    def check_failures(self):
        s = self.state
        if s.health <= 0:
            self.ending("Martyr ending")
        elif s.police_suspicion > 92 and s.secrecy < 35:
            self.ending("Elite restoration")

    def clamp_all(self):
        for k, v in vars(self.state).items():
            if isinstance(v, int):
                setattr(self.state, k, clamp(v, -20, 120))

    def relations_screen(self):
        self.write("Relationship screen:")
        for c in self.characters.values():
            self.write(f"{c.name}: rel {c.relationship}, trust {c.trust}, loyalty {c.loyalty}, resentment {c.resentment}")

    def dashboard_screen(self):
        self.write("Faction/Society dashboard snapshot written to log.")
        self.log_line(json.dumps({k: v for k, v in vars(self.state).items() if isinstance(v, int)}, sort_keys=True))

    def save_game(self):
        data = {
            "state": asdict(self.state),
            "characters": {k: asdict(v) for k, v in self.characters.items()},
            "flags": list(self.flags),
            "known_links": {k: list(v) for k, v in self.known_links.items()},
            "log": self.log,
        }
        SAVE_PATH.write_text(json.dumps(data))
        self.write("Game saved.")

    def load_game(self):
        if not SAVE_PATH.exists():
            self.write("No save file found.")
            return
        data = json.loads(SAVE_PATH.read_text())
        self.state = State(**data["state"])
        self.characters = {k: Character(**v) for k, v in data["characters"].items()}
        self.flags = set(data.get("flags", []))
        self.known_links = {k: set(v) for k, v in data.get("known_links", {}).items()}
        self.log = data.get("log", [])
        self.rng = random.Random(self.state.seed)
        self.write("Game loaded.")
        self.main_screen()

    def reset_game(self):
        if messagebox.askyesno("Reset", "Start a new game?"):
            self.state = State()
            self.rng = random.Random(self.state.seed)
            self.characters = self.make_characters()
            self.log = []
            self.flags = set()
            self.known_links = {}
            self.actions_this_week = 0
            self.story.delete("1.0", "end")
            self.show_background_selection()


def main():
    root = tk.Tk()
    Game(root)
    root.mainloop()


if __name__ == "__main__":
    main()
