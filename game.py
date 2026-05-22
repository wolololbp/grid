#!/usr/bin/env python3
"""GRID Final Project Game: data-driven graphical narrative simulation."""
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
LINKING_DEATHS_PER_WEEK = 3000
REVOLUTION_HORIZON_WEEKS = 40
WAR_CASUALTY_UNIT = 1000


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




@dataclass
class WarZone:
    name: str
    player_control: int
    custodian_control: int
    police_control: int
    civilian_condition: int
    infrastructure_condition: int
    strategic_value: int


@dataclass
class WarState:
    active: bool = False
    week: int = 0
    max_weeks: int = 10
    major_actions_left: int = 3
    minor_actions_left: int = 2
    revolutionary_members: int = 0
    trained_organizers: int = 0
    technical_cells: int = 0
    food_reserves: int = 0
    medical_reserves: int = 0
    safehouses: int = 0
    propaganda_reach: int = 0
    public_sympathy: int = 0
    revolutionary_morale: int = 50
    custodian_morale: int = 60
    police_cohesion: int = 60
    elite_defection: int = 0
    ai_infra_access: int = 0
    civilian_trust: int = 40
    civilian_fear: int = 20
    internal_unity: int = 50
    radical_pressure: int = 20
    moderate_pressure: int = 20
    violence_level: int = 20
    casualties: int = 0
    infrastructure_damage: int = 0
    negotiation_leverage: int = 10
    international_attention: int = 0
    rune_assistance: int = 0
    betrayal_risk: int = 20
    pressure: int = 30
    legitimacy: int = 30
    momentum: int = 30
    zones: Dict[str, WarZone] = field(default_factory=dict)
    log: List[str] = field(default_factory=list)
    memory: Dict[str, int] = field(default_factory=dict)

class Game:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("GRID Final Project Game")
        self.root.geometry("1360x860")
        self.rng = random.Random(7)
        self.state = GameState()
        self.characters = self._init_characters()
        self.hidden_relationships = self._init_hidden_relationships()
        self.locations = self._init_locations()
        self.weekly_events = self._init_weekly_events()
        self.story_scenes = self._init_story_scenes()
        self.lexicon = self._init_lexicon()
        self.war_state: Optional[WarState] = None
        self.war_events = self._init_war_events()

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
            "Undergrid", "Link Clinic", "Public Print Station", "Public Allocation Hall",
            "Custodian Promenade", "AI Maintenance Spire", "Police Civic Safety Office",
            "Civic School", "Medical Distribution Center", "Abandoned Human Factory",
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
        # Varied systemic shocks across infrastructure, class politics, information war, and governance stress.
        return [
            {"name": "Protein-Vat Contamination", "text": "A food biovats cluster fails contamination checks. Ration lines lengthen and rumors of elite stockpiles spread.", "effects": {"food_production": -8, "food_security": -6, "public_unrest": 4, "worker_support": 2}},
            {"name": "Transit Grid Brownout", "text": "Rolling transit failures isolate districts for two days, disrupting medicine routing and organizer mobility.", "effects": {"energy_stability": -5, "medical_availability": -4, "stress": 3, "public_unrest": 3}},
            {"name": "Custodian Dividend Gala", "text": "A leaked elite celebration during shortages spikes class anger and boosts recruitment conversations.", "effects": {"public_unrest": 5, "worker_support": 4, "custodian_reputation": -3, "public_reputation": 2}},
            {"name": "Algorithmic Welfare Reclassification", "text": "Allocation systems reclassify thousands as low-priority claimants, triggering paperwork chaos.", "effects": {"housing_security": -5, "food_security": -4, "public_unrest": 4, "legitimacy": 1}},
            {"name": "Police Metadata Sweep", "text": "Security authorities run a citywide metadata dragnet and freeze several shell wallets.", "effects": {"police_suspicion": 7, "police_infiltration": 4, "movement_funding": -6, "operational_secrecy": -4}},
            {"name": "Medical Queue Surge", "text": "Critical care queues spike after a respiratory wave; triage rules ignite moral outrage.", "effects": {"medical_availability": -7, "health": -4, "public_unrest": 3, "empathy": 1}},
            {"name": "Technician Walkout Threat", "text": "Maintenance crews threaten slowdown unless safety demands are met.", "effects": {"technician_support": 5, "ai_uptime": -5, "public_unrest": 2, "elite_sympathy": -1}},
            {"name": "Deepfake Scandal", "text": "Competing factions weaponize deepfakes; trust in public messages drops across the city.", "effects": {"message_discipline": -6, "public_reputation": -3, "police_suspicion": 2, "propaganda_reach": -2}},
            {"name": "Black-Market Credit Squeeze", "text": "Loan sharks tighten terms and collateral violence rises in peripheral blocks.", "effects": {"money": -8, "black_market_activity": 6, "stress": 4, "public_unrest": 2}},
            {"name": "Dock Strike at Allocation Port", "text": "Dock allocators halt distribution software handoffs, exposing logistics fragility.", "effects": {"food_network_access": -4, "energy_network_access": -3, "membership": 2, "public_unrest": 4}},
            {"name": "Elite Defection Rumor", "text": "Whispers that a mid-tier custodian wants immunity in exchange for records.", "effects": {"elite_sympathy": 4, "internal_unity": -3, "police_suspicion": 1, "movement_funding": 3}},
            {"name": "Neighborhood Mutual Aid Boom", "text": "Local kitchens and clinics self-organize faster than official channels.", "effects": {"food_security": 5, "health": 3, "public_sympathy": 4, "legitimacy": 3}},
            {"name": "Censorship Patch Rollout", "text": "Platform moderation firmware flags political speech as instability content.", "effects": {"censorship_level": 8, "propaganda_reach": -4, "police_suspicion": 2, "public_unrest": 2}},
            {"name": "Heatwave Load Emergency", "text": "Extreme heat drives grid demand beyond forecasts and triggers emergency rationing.", "effects": {"energy_stability": -7, "health": -3, "stress": 4, "public_unrest": 3}},
            {"name": "Memory Drift Cases Rise", "text": "Clinicians report increasing cognitive drift among linked workers, renewing ethical panic.", "effects": {"memory_integrity": -6, "neural_stability": -5, "public_unrest": 3, "legitimacy": 2}},
            {"name": "Counter-Propaganda Offensive", "text": "State media launches a coordinated narrative framing organizers as famine profiteers.", "effects": {"public_reputation": -5, "trust_in_player": -4, "worker_support": -2, "police_suspicion": 3}},
            {"name": "Spire Maintenance Breakthrough", "text": "Engineers deploy a robust patch that stabilizes routing efficiency for several cycles.", "effects": {"ai_uptime": 6, "energy_stability": 4, "technician_support": 3, "custodian_confidence": 2}},
            {"name": "Audit Leak from Civic Safety", "text": "Internal audit files expose manipulated arrest quotas and fabricated risk tags.", "effects": {"policing_intensity": -4, "public_unrest": 5, "worker_support": 3, "police_suspicion": -1}},
            {"name": "Undergrid Fire Cascade", "text": "A tenement fire reveals deferred infrastructure maintenance and poor emergency access.", "effects": {"housing_stability": -8, "health": -4, "public_unrest": 4, "legitimacy": 2}},
            {"name": "Emergency Grain Import", "text": "External emergency shipments temporarily ease pressure in ration districts.", "effects": {"food_production": 4, "food_security": 6, "public_unrest": -2, "international_attention": 3}},
        ]

    def _init_lexicon(self) -> Dict[str, str]:
        return {
            "general": "Core help for navigating weekly actions, systems pressure, and branching outcomes.",
            "panels": "Overview of utility panels: Relationships, Faction Dashboard, Map, and Revolution Readiness.",
            "relationships_tab": "Visual social graph of characters. Links appear only when hidden ties are discovered.",
            "map_tab": "Graphical city map of districts and institutions. Locked areas require social or material access.",
            "factions_tab": "Snapshot of faction/class momentum shaping transition outcomes.",
            "revolution_readiness_tab": "Compares movement pressure to state resistance before launch.",
            "Undergrid": "Dense lower-class district where most survival politics begin.",
            "Link Clinic": "Facility where people neural-link to AI for income at health/memory risk.",
            "Public Print Station": "Open-access print/media cooperative for propaganda, messaging, and rumor contests.",
            "Public Allocation Hall": "Bureaucratic rationing center for food, housing, and aid disputes.",
            "Custodian Promenade": "Elite district of the Custodian class that privately owns AI infrastructure.",
            "AI Maintenance Spire": "Critical technical tower where technicians keep automated systems running.",
            "Police Civic Safety Office": "Security and intelligence bureaucracy managing surveillance and order.",
            "Civic School": "Community education network building ideology, literacy, and civic culture in the open democratic sphere.",
            "Medical Distribution Center": "Node for medicine logistics and care continuity.",
            "Abandoned Human Factory": "Symbolic old labor site used for organizing, memory, and escalation.",
            "Salon of Cel Varo": "Elite salon where custodians, reformists, and brokers negotiate narratives.",
            "Dream Layer": "Neural/AI liminal space of memory bleed, system messages, and Rune encounters.",
            "Custodians": "Wealthy owner class controlling automated production and core AI systems.",
            "Technicians": "Middle technical class maintaining AI uptime and vital infrastructure.",
            "Mara Venn": "Lower-grid organizer favoring rupture; fears collapse if technical continuity is ignored.",
            "Elias Rook": "Affluent AI maintenance architect who can fund transition and reduce shutdown risk.",
            "Sera Quill": "Custodian heir balancing class continuity, legitimacy, and private doubt.",
            "Juno Pike": "Black-market narrative operator who boosts reach but can destabilize message discipline.",
            "Inspector Cal Vey": "Security strategist who equates unmanaged unrest with famine risk.",
            "Nadi Bex": "Linked child whose condition embodies coercion through survival dependency.",
            "Tomas Vale": "Older resident prioritizing stability after prior social breakdowns.",
            "Iri Sol": "Radical theorist pressing immediate abolition of AI ownership structures.",
            "Director Halden Myr": "Custodian power broker arguing elite control is necessary for continuity.",
            "Lysa Tem": "Medical technician focused on care continuity under political transition.",
            "Olan Crete": "Logistics smuggler; useful but transactional in loyalty.",
            "Faye Orison": "Underground educator emphasizing democratic culture and anti-revenge politics.",
            "Malik Drem": "Former regime media figure skilled in persuasion and narrative manipulation.",
            "Ansel Kade": "Militant leader whose grief can sharpen mobilization and escalation.",
            "Priya Sen": "Systems engineer advocating decentralized, auditable AI governance.",
            "Rune": "Ambiguous AI-generated persona that may assist, manipulate, or test the player.",
            "Cel Varo": "Elite salon broker connecting custodians, reformists, and opportunists.",
            "Bet Orra": "Grieving lower-grid parent measuring politics by civilian protection outcomes.",
            "Kemi Draal": "Allocator managing distribution chokepoints in stressed supply systems.",
            "Harl Nox": "Custodian security consultant favoring hard containment over compromise.",
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
        tk.Label(top, text="GRID Final Project Game", font=("Helvetica", 18, "bold"), fg="white", bg="#0d1320").pack(side="left", padx=12, pady=8)

        toolbar = tk.Frame(top, bg="#0d1320")
        toolbar.pack(side="right")
        for lbl, cmd in [("Save", self.save), ("Load", self.load), ("Reset", self.reset)]:
            tk.Button(toolbar, text=lbl, command=cmd, bg="#314668", fg="white").pack(side="left", padx=4)
        tk.Button(toolbar, text="Cheats", command=self.open_cheat_console, bg="#6a4a2f", fg="white").pack(side="left", padx=4)
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
        self.content_canvas = tk.Canvas(self.left, bg="#0d1424", highlightthickness=0)

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
        row1 = tk.Frame(panels, bg="#121a2a")
        row1.pack(fill="x", pady=2)
        tk.Button(row1, text="Relationships", command=self.show_relationships).pack(side="left", fill="x", expand=True)
        tk.Button(row1, text="?", command=lambda: self.show_help("relationships_tab"), bg="#4f5f80", fg="white", width=3).pack(side="left", padx=3)

        row2 = tk.Frame(panels, bg="#121a2a")
        row2.pack(fill="x", pady=2)
        tk.Button(row2, text="Faction Dashboard", command=self.show_factions).pack(side="left", fill="x", expand=True)
        tk.Button(row2, text="?", command=lambda: self.show_help("factions_tab"), bg="#4f5f80", fg="white", width=3).pack(side="left", padx=3)

        row3 = tk.Frame(panels, bg="#121a2a")
        row3.pack(fill="x", pady=2)
        tk.Button(row3, text="Map", command=self.show_map).pack(side="left", fill="x", expand=True)
        tk.Button(row3, text="?", command=lambda: self.show_help("map_tab"), bg="#4f5f80", fg="white", width=3).pack(side="left", padx=3)

        row4 = tk.Frame(panels, bg="#121a2a")
        row4.pack(fill="x", pady=2)
        self.revolution_button = tk.Button(row4, text="Revolution Readiness", command=self.show_revolution_readiness)
        self.revolution_button.pack(side="left", fill="x", expand=True)
        tk.Button(row4, text="?", command=lambda: self.show_help("revolution_readiness_tab"), bg="#4f5f80", fg="white", width=3).pack(side="left", padx=3)
        tk.Button(panels, text="?", command=lambda: self.show_help("panels"), bg="#4f5f80", fg="white", width=3).pack(anchor="e", pady=2)

    def _init_war_events(self) -> List[Dict[str, object]]:
        return [
            {"name":"Police unit refusal","text":"A police unit refuses an eviction order after family-targeted messaging.","effects":{"police_cohesion":-6,"public_sympathy":3,"pressure":2}},
            {"name":"Unauthorized hardline strike","text":"A radical wing acts without approval; disruption rises but legitimacy drops.","effects":{"pressure":4,"legitimacy":-5,"internal_unity":-4,"casualties":2}},
            {"name":"Hospital emergency","text":"Lysa demands immediate grid support for clinics.","effects":{"medical_reserves":-4,"casualties":3,"legitimacy":2}},
            {"name":"Elite amnesty offer","text":"Sera offers defections if amnesty terms are discussed.","effects":{"elite_defection":5,"internal_unity":-3,"negotiation_leverage":3}},
            {"name":"Mara challenge","text":"Mara warns compromise is draining momentum.","effects":{"radical_pressure":3,"pressure":2,"moderate_pressure":-1}},
            {"name":"Elias systems warning","text":"Elias warns the Spire will crash without protected technicians.","effects":{"ai_infra_access":-3,"infrastructure_damage":2,"technical_cells":-1}},
            {"name":"Ansel ultimatum","text":"Ansel demands harsher reprisals.","effects":{"radical_pressure":4,"civilian_fear":3,"legitimacy":-2}},
            {"name":"Bet Orra confrontation","text":"Bet demands civilian protections after neighborhood losses.","effects":{"civilian_trust":2,"pressure":-1,"legitimacy":2}},
            {"name":"Juno viral exaggeration","text":"Juno's message explodes but overpromises outcomes.","effects":{"propaganda_reach":4,"legitimacy":-3}},
            {"name":"Vey ceasefire corridor","text":"Inspector Vey offers a food corridor ceasefire.","effects":{"food_reserves":4,"pressure":-2,"police_cohesion":-2,"negotiation_leverage":3}},
            {"name":"Rune proposal","text":"Rune offers substrate assistance for influence over linked minds.","effects":{"rune_assistance":4,"civilian_fear":2,"pressure":2}},
            {"name":"Safehouse exposure","text":"A safehouse network is compromised.","effects":{"safehouses":-2,"betrayal_risk":4,"casualties":2}},
            {"name":"Allocation hall panic","text":"Crowds at Allocation Hall turn on both factions.","effects":{"public_sympathy":-3,"civilian_trust":-2,"pressure":-1}},
            {"name":"Custodian lie dossier","text":"Custodian media releases damaging half-truth dossiers.","effects":{"legitimacy":-4,"public_sympathy":-2}},
            {"name":"Linked refusal wave","text":"Linked workers coordinate mass refusal beyond expectations.","effects":{"pressure":5,"ai_infra_access":-2,"food_reserves":-2}},
            {"name":"Technician strike threat","text":"Technicians demand protection guarantees.","effects":{"technical_cells":2,"internal_unity":-2,"ai_infra_access":2}},
            {"name":"Maintenance route leak","text":"Former servants reveal hidden maintenance tunnels.","effects":{"ai_infra_access":4,"pressure":2}},
            {"name":"School assembly surge","text":"Civic School assemblies strengthen civic legitimacy.","effects":{"legitimacy":4,"civilian_trust":3,"moderate_pressure":2}},
            {"name":"Factory becomes symbol","text":"The old factory becomes a mass coordination hub.","effects":{"pressure":3,"revolutionary_morale":3}},
            {"name":"Energy yard instability","text":"Switching yard failsafe alarms trigger citywide panic.","effects":{"infrastructure_damage":4,"civilian_fear":4,"pressure":1}},
            {"name":"Captured ally broadcast","text":"A captured ally appears in coercive broadcast propaganda.","effects":{"revolutionary_morale":-4,"betrayal_risk":3}},
            {"name":"Hated enemy requests asylum","text":"A former regime figure requests protection from revenge.","effects":{"legitimacy":3,"radical_pressure":3,"internal_unity":-2}},
            {"name":"Moderate pre-election demand","text":"Moderates ask for vote commitments before victory.","effects":{"moderate_pressure":4,"pressure":-1,"legitimacy":2}},
            {"name":"Militant split threat","text":"Militants threaten a split without escalation.","effects":{"radical_pressure":4,"internal_unity":-4,"pressure":2}},
            {"name":"Fear inversion","text":"Civilians begin fearing the revolution more than custodians.","effects":{"civilian_fear":5,"civilian_trust":-4,"legitimacy":-3}},
        ]

    def _init_war_from_preparation(self) -> WarState:
        s=self.state
        ws=WarState(active=True)
        ws.max_weeks=clamp(8 + (s.police_suspicion//20) + (s.internal_unity<45),6,14)
        ws.revolutionary_members=clamp(s.membership,10,150)
        ws.trained_organizers=clamp(s.membership//3 + s.legitimacy//10,5,80)
        ws.technical_cells=clamp(s.technician_support//2 + s.technical_skill//15,2,60)
        ws.food_reserves=clamp(s.food_network_access + s.food_security//3,5,90)
        ws.medical_reserves=clamp(s.medical_network_access + s.health//4,5,90)
        ws.safehouses=clamp(s.operational_secrecy//8,2,30)
        ws.propaganda_reach=clamp(s.propaganda_reach + s.propaganda_skill//8,5,120)
        ws.public_sympathy=clamp(s.public_sympathy + s.worker_support//3,10,100)
        ws.revolutionary_morale=clamp(45 + s.membership//4 + s.legitimacy//5,20,100)
        ws.custodian_morale=clamp(65 + s.custodian_confidence//5 - s.public_unrest//6,10,100)
        ws.police_cohesion=clamp(60 + s.policing_intensity//8 + s.police_suspicion//7 - s.public_sympathy//10,5,100)
        ws.elite_defection=clamp(s.elite_sympathy//2,0,80)
        ws.ai_infra_access=clamp(s.infrastructure_access + s.technician_support//4,0,100)
        ws.internal_unity=clamp(s.internal_unity,5,100)
        ws.radical_pressure=clamp(s.radicalization + s.violence_level//2,0,100)
        ws.moderate_pressure=clamp(s.legitimacy + s.public_sympathy//3,0,100)
        ws.violence_level=clamp(s.violence_level,0,100)
        ws.negotiation_leverage=clamp(s.elite_sympathy + s.legitimacy//2,0,100)
        ws.international_attention=clamp(s.international_attention,0,100)
        ws.rune_assistance=10 if (s.background=="Neural-linked worker" or self.characters.get("Rune",Character("","","","")).trust>20) else 0
        ws.betrayal_risk=clamp(30 + s.police_infiltration - s.operational_secrecy//5,0,100)
        ws.pressure=clamp(ws.revolutionary_members//3 + ws.radical_pressure//2 + ws.propaganda_reach//6 + ws.ai_infra_access//5,0,100)
        ws.legitimacy=clamp(s.legitimacy + ws.public_sympathy//4 - ws.violence_level//6,0,100)
        ws.momentum=clamp(ws.pressure + ws.revolutionary_morale//4 - ws.custodian_morale//5,0,100)
        zone_names=["Undergrid","Link Clinic Network","Public Allocation Hall","AI Maintenance Spire","Medical Distribution Center","Custodian Promenade","Police Civic Safety Office","Public Print Station","Civic School","Abandoned Human Factory","Energy Switching Yard","Dream Layer / AI Substrate"]
        for zn in zone_names:
            p=clamp(20 + ws.pressure//4 + (8 if zn in ["Undergrid","Public Print Station","Civic School"] else 0),0,90)
            c=clamp(70 - p + (8 if zn in ["Custodian Promenade","Police Civic Safety Office"] else 0),5,95)
            pol=clamp(ws.police_cohesion//2 + (10 if zn=="Police Civic Safety Office" else 0),0,95)
            civ=clamp(45 + ws.public_sympathy//5 - ws.violence_level//8,5,95)
            infra=clamp(50 + ws.ai_infra_access//6 - ws.violence_level//10,5,95)
            sv=80 if zn in ["AI Maintenance Spire","Medical Distribution Center","Public Allocation Hall","Energy Switching Yard"] else 55
            ws.zones[zn]=WarZone(zn,p,c,pol,civ,infra,sv)
        if ws.rune_assistance<=0:
            ws.zones.pop("Dream Layer / AI Substrate",None)
        return ws

    def start_war_phase(self) -> None:
        if self.war_state and self.war_state.active:
            self.log("War phase is already active. Returning to the current war instance.")
            self.war_week_screen()
            return
        self.war_state=self._init_war_from_preparation()
        self.state.phase=3
        self.state.flags["war_start_week"] = self.state.week
        self.update_phase_ui()
        self.log("War Phase begins: allies commit, hesitators stall, and rivals test your command.")
        self.war_week_screen()

    def update_phase_ui(self) -> None:
        if hasattr(self, "revolution_button"):
            active_war = bool(self.war_state and self.war_state.active)
            self.revolution_button.configure(state="disabled" if active_war else "normal")

    def war_week_screen(self) -> None:
        ws=self.war_state
        if not ws or not ws.active:
            return
        self.show_canvas_view()
        c=self.content_canvas
        c.create_text(12,12,anchor='nw',fill='#edf3ff',font=('Helvetica',12,'bold'),text=f"War Week {ws.week+1}/{ws.max_weeks}  Pressure {ws.pressure} vs Legitimacy {ws.legitimacy}  Momentum {ws.momentum}")
        c.create_text(12,38,anchor='nw',fill='#c9d9ff',font=('Helvetica',9),text=f"Rev morale {ws.revolutionary_morale} | Custodian morale {ws.custodian_morale} | Police cohesion {ws.police_cohesion} | Casualties {ws.casualties} | Infra damage {ws.infrastructure_damage}")
        # zone map
        cols=4
        for i,z in enumerate(ws.zones.values()):
            x=40+(i%cols)*220; y=90+(i//cols)*115
            c.create_rectangle(x,y,x+190,y+95,fill='#1a2740',outline='#3d5b85')
            c.create_text(x+6,y+6,anchor='nw',fill='white',font=('Helvetica',9,'bold'),text=z.name[:24])
            c.create_text(x+6,y+26,anchor='nw',fill='#9fd3ff',font=('Helvetica',8),text=f"Ctrl R/C/P: {z.player_control}/{z.custodian_control}/{z.police_control}")
            c.create_text(x+6,y+42,anchor='nw',fill='#bde7be',font=('Helvetica',8),text=f"Civil {z.civilian_condition}  Infra {z.infrastructure_condition}")
            c.create_text(x+6,y+58,anchor='nw',fill='#ffd59a',font=('Helvetica',8),text=f"Strategic value {z.strategic_value}")
        self.clear_choices()
        # major actions (3)
        if ws.major_actions_left>0:
            self.add_choice("Major: Defend communities", lambda: self.war_action('defend'))
            self.add_choice("Major: Occupy infrastructure", lambda: self.war_action('occupy'))
            self.add_choice("Major: Mass refusal campaign", lambda: self.war_action('refusal'))
            self.add_choice("Major: Encourage elite defections", lambda: self.war_action('defect'))
            self.add_choice("Major: Protect medical centers", lambda: self.war_action('medical'))
            self.add_choice("Major: Centralize command", lambda: self.war_action('centralize'))
            self.add_choice("Major: Ruthless purge operation", lambda: self.war_action('purge'))
        if ws.minor_actions_left>0:
            self.add_choice("Minor: Emergency propaganda", lambda: self.war_action('propaganda',minor=True))
            self.add_choice("Minor: Counter police raids", lambda: self.war_action('counter_raid',minor=True))
            self.add_choice("Minor: Public assemblies", lambda: self.war_action('assemblies',minor=True))
            self.add_choice("Minor: Restrain radicals", lambda: self.war_action('restrain',minor=True))
            self.add_choice("Minor: Negotiate ceasefire corridor", lambda: self.war_action('ceasefire',minor=True))
            self.add_choice("Minor: Brutal reprisals", lambda: self.war_action('reprisal',minor=True))
        self.add_choice("Resolve War Week", self.resolve_war_week)
        self.add_choice("Back to Console", self.main_week_screen)

    def war_action(self, action: str, minor: bool=False) -> None:
        ws=self.war_state
        if not ws: return
        if minor and ws.minor_actions_left<=0: return
        if not minor and ws.major_actions_left<=0: return
        if minor: ws.minor_actions_left-=1
        else: ws.major_actions_left-=1
        effects={
            'defend': {'civilian_trust':4,'casualties':-1,'pressure':1,'food_reserves':-2},
            'occupy': {'pressure':5,'ai_infra_access':3,'infrastructure_damage':2,'legitimacy':-1},
            'refusal': {'pressure':4,'custodian_morale':-4,'food_reserves':-3,'medical_reserves':-2},
            'defect': {'elite_defection':5,'custodian_morale':-5,'internal_unity':-2,'negotiation_leverage':3},
            'medical': {'medical_reserves':3,'casualties':-3,'legitimacy':3,'pressure':-1},
            'centralize': {'pressure':3,'internal_unity':2,'legitimacy':-3,'civilian_fear':3},
            'purge': {'pressure':7,'police_cohesion':-4,'civilian_fear':6,'casualties':4,'legitimacy':-6,'violence_level':8},
            'propaganda': {'propaganda_reach':3,'public_sympathy':2,'pressure':1},
            'counter_raid': {'police_cohesion':-2,'safehouses':1,'betrayal_risk':-2},
            'assemblies': {'legitimacy':4,'civilian_trust':3,'pressure':-1},
            'restrain': {'radical_pressure':-3,'legitimacy':2,'pressure':-1},
            'ceasefire': {'food_reserves':2,'medical_reserves':2,'pressure':-2,'negotiation_leverage':2},
            'reprisal': {'pressure':3,'police_cohesion':-2,'civilian_fear':3,'legitimacy':-3,'violence_level':4},
        }[action]
        for k,v in effects.items():
            setattr(ws,k,clamp(getattr(ws,k)+v,-100,200))
        ws.log.append(f"Action: {action}")
        self.war_week_screen()

    def resolve_war_week(self) -> None:
        ws=self.war_state
        if not ws: return
        # enemy response + event
        event=self.rng.choice(self.war_events)
        ws.log.append(event['name']+": "+event['text'])
        for k,v in event['effects'].items():
            setattr(ws,k,clamp(getattr(ws,k)+v,-100,200))
        if self.rng.random() < ws.betrayal_risk / 100:
            betrayal_loss = self.rng.randint(2, 6)
            ws.internal_unity = clamp(ws.internal_unity - betrayal_loss, 0, 100)
            ws.revolutionary_morale = clamp(ws.revolutionary_morale - betrayal_loss, 0, 100)
            ws.safehouses = clamp(ws.safehouses - 1, 0, 200)
            ws.casualties = clamp(ws.casualties + self.rng.randint(1, 3), 0, 200)
            ws.log.append("Betrayal during the war: an exposed channel costs lives and fractures trust.")
        # zone shifts from pressure/legitimacy vs enemy morale/cohesion
        for z in ws.zones.values():
            swing=(ws.pressure//15 + ws.public_sympathy//20 + ws.ai_infra_access//25) - (ws.police_cohesion//20 + ws.custodian_morale//20)
            z.player_control=clamp(z.player_control+swing,0,100)
            z.custodian_control=clamp(z.custodian_control-swing,0,100)
            z.police_control=clamp(z.police_control + (1 if ws.police_cohesion>55 else -1),0,100)
            z.civilian_condition=clamp(z.civilian_condition + ws.food_reserves//30 + ws.medical_reserves//35 - ws.casualties//12,0,100)
            z.infrastructure_condition=clamp(z.infrastructure_condition - ws.infrastructure_damage//15 + ws.technical_cells//25,0,100)
        ws.week+=1
        ws.major_actions_left=3
        ws.minor_actions_left=2
        ws.pressure=clamp(ws.pressure + ws.radical_pressure//20 + ws.revolutionary_morale//25 - ws.casualties//20,0,100)
        ws.legitimacy=clamp(ws.legitimacy + ws.civilian_trust//25 - ws.civilian_fear//20 - ws.violence_level//30,0,100)
        ws.momentum=clamp((ws.pressure+ws.legitimacy+ws.revolutionary_morale)//3 - ws.police_cohesion//8,0,100)
        required_ruthlessness = 20 + ws.week * 2
        if ws.week >= 4 and ws.violence_level < required_ruthlessness:
            ws.active = False
            self.state.flags['war_outcome'] = 'Failed uprising'
            self.log(
                f"War failed: command judged insufficiently ruthless "
                f"(violence {ws.violence_level} < required {required_ruthlessness})."
            )
            self.set_ending('Failed uprising')
            return
        # outcome checks
        avg_ctrl=sum(z.player_control for z in ws.zones.values())/max(1,len(ws.zones))
        if ws.week>=6 and avg_ctrl>58 and ws.custodian_morale<35 and ws.police_cohesion<40:
            self.state.flags['war_outcome']='Clear revolutionary victory' if ws.legitimacy>45 else 'Damaged victory'
            self.state.flags['war_weeks'] = ws.week
            self.state.flags['war_casualties_points'] = ws.casualties
            ws.active=False
            self.log(f"War outcome: {self.state.flags['war_outcome']}.")
            self.set_ending(self.state.flags['war_outcome'])
            return
        if ws.week>=6 and ws.negotiation_leverage>55 and ws.pressure>35 and ws.legitimacy>35 and ws.custodian_morale<55:
            self.state.flags['war_outcome']='Negotiated transition'
            self.state.flags['war_weeks'] = ws.week
            self.state.flags['war_casualties_points'] = ws.casualties
            ws.active=False
            self.log("War outcome: Negotiated transition.")
            self.set_ending("Negotiated transition")
            return
        if ws.week>=ws.max_weeks:
            if ws.momentum<35:
                self.set_ending('Failed uprising')
            elif avg_ctrl<45:
                self.set_ending('Stalled conflict')
            else:
                self.state.flags['war_outcome']='Split government'
                self.state.flags['war_weeks'] = ws.week
                self.state.flags['war_casualties_points'] = ws.casualties
                ws.active=False
                self.log('War outcome: Split government.')
                self.set_ending('Split government')
            return
        self.war_week_screen()

    def show_help(self, topic: str) -> None:
        if topic == "general":
            message = (
                "This game combines weekly strategy + branching narrative in a formal representative democracy shaped by capitalist inequality.\n"
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

    def open_cheat_console(self) -> None:
        win = tk.Toplevel(self.root)
        win.title("Presentation Cheat Console")
        win.geometry("520x260")
        tk.Label(win, text="Enter cheat code:", font=("Helvetica", 10, "bold")).pack(pady=8)
        entry = tk.Entry(win, width=48)
        entry.pack(pady=6)
        tk.Label(
            win,
            text=(
                "Codes: FAST_PREP, FORCE_WAR, WIN_WAR, FORCE_GOV, MAX_ALL,\n"
                "CALM_CITY, CHAOS_CITY, MONEY_DROP, SPEEDRUN"
            ),
            justify="left",
            fg="#cfe2ff",
            bg="#1c2538",
            padx=8,
            pady=8,
        ).pack(pady=6)

        def run_code() -> None:
            code = entry.get().strip().upper()
            ok, msg = self.apply_cheat(code)
            messagebox.showinfo("Cheat", msg)
            if ok:
                self.refresh_stats()
                self.main_week_screen()

        tk.Button(win, text="Apply", command=run_code, bg="#35557e", fg="white").pack(pady=8)

    def apply_cheat(self, code: str) -> Tuple[bool, str]:
        s = self.state
        if code == "FAST_PREP":
            self.apply_effects({
                "membership": 60, "movement_funding": 120, "worker_support": 65, "public_unrest": 55,
                "technician_support": 45, "elite_sympathy": 35, "infrastructure_access": 30,
                "food_network_access": 30, "medical_network_access": 30, "operational_secrecy": 70,
                "legitimacy": 55, "public_sympathy": 55, "money": 120,
            })
            return True, "FAST_PREP applied: revolution readiness dramatically increased."
        if code == "FORCE_WAR":
            self.start_war_phase()
            return True, "FORCE_WAR applied: war phase started immediately."
        if code == "WIN_WAR":
            if not self.war_state or not self.war_state.active:
                return False, "WIN_WAR failed: war phase is not active."
            ws = self.war_state
            ws.pressure = 90
            ws.legitimacy = 72
            ws.momentum = 88
            ws.custodian_morale = 18
            ws.police_cohesion = 22
            for z in ws.zones.values():
                z.player_control = 75
                z.custodian_control = 15
            self.resolve_war_week()
            return True, "WIN_WAR applied: conflict pushed toward immediate victory path."
        if code == "FORCE_GOV":
            self.state.flags["war_outcome"] = "Clear revolutionary victory"
            self.set_ending("Clear revolutionary victory")
            return True, "FORCE_GOV applied: ended the game immediately."
        if code == "MAX_ALL":
            for k in vars(s):
                if isinstance(getattr(s, k), int):
                    setattr(s, k, 95)
            s.actions_left = 3
            return True, "MAX_ALL applied: most numeric stats set to high values."
        if code == "CALM_CITY":
            self.apply_effects({"public_unrest": -40, "police_suspicion": -35, "stress": -25, "health": 20})
            return True, "CALM_CITY applied: unrest and pressure sharply reduced."
        if code == "CHAOS_CITY":
            self.apply_effects({"public_unrest": 40, "police_suspicion": 25, "radicalization": 30, "violence_level": 25})
            return True, "CHAOS_CITY applied: escalation pressure and instability increased."
        if code == "MONEY_DROP":
            self.apply_effects({"money": 150, "movement_funding": 90})
            return True, "MONEY_DROP applied: large funding injection granted."
        if code == "SPEEDRUN":
            self.apply_effects({"membership": 50, "movement_funding": 100, "worker_support": 55, "public_unrest": 50, "technician_support": 40, "legitimacy": 50})
            self.state.week = max(self.state.week, 18)
            return True, "SPEEDRUN applied: advanced campaign to late-organization conditions."
        return False, f"Unknown code: {code}"

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
        if self.content_canvas.winfo_ismapped():
            self.content_canvas.pack_forget()
            self.story_text.pack(fill="both", expand=True, padx=8, pady=8, before=self.choice_container)
        self.story_text.config(state="normal")
        self.story_text.insert("end", msg + "\n\n")
        self.story_text.see("end")
        self.story_text.config(state="disabled")
        self.state.event_log.append(msg)
        self.state.event_log = self.state.event_log[-120:]

    def refresh_stats(self) -> None:
        s = self.state
        ws = self.war_state
        war_outcome = s.flags.get("war_outcome", "")
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

    def show_console_view(self) -> None:
        if self.content_canvas.winfo_ismapped():
            self.content_canvas.pack_forget()
        if not self.story_text.winfo_ismapped():
            self.story_text.pack(fill="both", expand=True, padx=8, pady=8, before=self.choice_container)

    def show_canvas_view(self) -> None:
        if self.story_text.winfo_ismapped():
            self.story_text.pack_forget()
        if not self.content_canvas.winfo_ismapped():
            self.content_canvas.pack(fill="both", expand=True, padx=8, pady=8, before=self.choice_container)
        self.content_canvas.delete("all")

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
        self.show_console_view()
        self.update_phase_ui()
        self.refresh_stats()
        self.clear_choices()
        no_actions = self.state.actions_left <= 0
        lock_msg = "no actions left this week" if no_actions else None
        if self.war_state and self.war_state.active:
            lock_msg = "war phase active"
        self.add_choice("Visit location", self.show_map, lock_msg)
        self.add_choice("Character conversation", self.character_menu, lock_msg)
        self.add_choice("Propaganda action", self.propaganda_menu, lock_msg)
        self.add_choice("Movement management", self.movement_menu, lock_msg)
        self.add_choice("End week", self.end_week)

    def show_map(self) -> None:
        self.show_canvas_view()
        canvas = self.content_canvas
        canvas.create_text(12, 12, anchor="nw", fill="#e8edf9", font=("Helvetica", 12, "bold"), text="Choose a location")
        help_btn = tk.Button(self.left, text="?", command=lambda: self.show_help("map_tab"), bg="#4f5f80", fg="white", width=2)
        canvas.create_window(865, 22, window=help_btn, width=24, height=22)

        coords = {
            "Undergrid": (130, 430),
            "Link Clinic": (260, 450),
            "Public Print Station": (380, 430),
            "Public Allocation Hall": (520, 420),
            "Custodian Promenade": (720, 170),
            "AI Maintenance Spire": (600, 250),
            "Police Civic Safety Office": (520, 300),
            "Civic School": (300, 330),
            "Medical Distribution Center": (430, 300),
            "Abandoned Human Factory": (170, 320),
            "Salon of Cel Varo": (760, 260),
            "Dream Layer": (700, 470),
        }
        roads = [("Undergrid", "Public Allocation Hall"), ("Public Allocation Hall", "Custodian Promenade"), ("Undergrid", "Abandoned Human Factory"), ("AI Maintenance Spire", "Custodian Promenade"), ("Medical Distribution Center", "Police Civic Safety Office"), ("Civic School", "Undergrid"), ("Salon of Cel Varo", "Custodian Promenade")]
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
                btn = tk.Button(self.left, text="Visit", command=lambda l=loc: self.visit_location(l), bg="#274066", fg="white")
                canvas.create_window(x, y + 42, window=btn, width=58, height=18)
            info_btn = tk.Button(self.left, text="?", command=lambda l=loc: self.show_help(l), bg="#4f5f80", fg="white", width=2)
            canvas.create_window(x + 38, y - 30, window=info_btn, width=18, height=18)

        self.clear_choices()
        self.add_choice("Back to Console", self.main_week_screen)

    def visit_location(self, loc: str) -> None:
        if not self.spend_action():
            self.main_week_screen()
            return
        self.state.location = loc
        fx = {
            "Undergrid": {"worker_support": 4, "money": -2, "food_security": 4},
            "Link Clinic": {"money": 14, "health": -6, "memory_integrity": -5, "neural_stability": -8, "ai_uptime": 1},
            "Public Print Station": {"movement_funding": 10, "police_suspicion": 6, "propaganda_reach": 6},
            "Public Allocation Hall": {"public_reputation": 4, "food_security": 5, "housing_security": 3, "public_unrest": 2},
            "Custodian Promenade": {"elite_sympathy": 6, "custodian_reputation": 5, "money": -8},
            "AI Maintenance Spire": {"technical_skill": 4, "technician_support": 5, "infrastructure_access": 5},
            "Police Civic Safety Office": {"police_suspicion": -8, "operational_secrecy": 2, "public_reputation": -2},
            "Civic School": {"legitimacy": 6, "public_sympathy": 6, "message_discipline": 4},
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
            side = self.character_side(c)
            locked = None
            if self.war_state and self.war_state.active and side == "custodian_loyalist":
                locked = "hostile during war"
            self.add_choice(
                f"{n} [{side}] ({c.class_background}) rel={c.relationship} trust={c.trust}",
                lambda name=n: self.talk(name),
                locked,
            )
        self.add_choice("Back", self.main_week_screen)

    def character_side(self, c: Character) -> str:
        if self.war_state and self.war_state.active:
            if c.class_background in {"custodian heir", "custodian owner", "custodian security consultant"} and c.relationship < 20:
                return "custodian_loyalist"
            if c.class_background in {"police"} and c.trust < 10:
                return "state_aligned"
            if c.relationship > 35 or c.trust > 20:
                return "revolutionary_aligned"
            return "fence_sitter"
        return "civilian"

    def talk(self, name: str) -> None:
        c = self.characters[name]
        if self.war_state and self.war_state.active:
            side = self.character_side(c)
            if side == "custodian_loyalist":
                self.log(f"{name} refuses a direct conversation during open conflict.")
                self.main_week_screen()
                return
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
        if self.war_state and self.war_state.active:
            violence_profiles = [("low-risk messaging", -1), ("hardline messaging", 2), ("incitement messaging", 5)]
        else:
            violence_profiles = [("calming messaging", -2), ("aggressive messaging", 1), ("threat messaging", 3)]
        for t in targets[:3]:
            for tone in tones[:2]:
                method = methods[self.rng.randint(0,7)]
                for profile_name, profile_shift in violence_profiles:
                    self.add_choice(
                        f"{t} via {method} ({tone}, {profile_name})",
                        lambda x=t, y=tone, z=profile_shift, p=profile_name: self.propaganda_action(x, y, z, p),
                    )
        self.add_choice("Back", self.main_week_screen)

    def propaganda_action(self, target: str, tone: str, violence_shift: int, profile_name: str) -> None:
        if not self.spend_action():
            self.main_week_screen()
            return
        reach = 4 + self.state.propaganda_skill // 20
        suspicion = 2
        applied_violence_shift = violence_shift
        if self.war_state and self.war_state.active:
            applied_violence_shift = clamp(violence_shift, -1, 2)
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
        self.apply_effects({
            "propaganda_reach": reach,
            "public_reputation": 2,
            "police_suspicion": suspicion,
            "violence_level": applied_violence_shift,
            "ruthlessness": max(0, applied_violence_shift),
        })
        if self.war_state and self.war_state.active:
            self.war_state.violence_level = clamp(self.war_state.violence_level + applied_violence_shift, 0, 100)
            self.war_state.radical_pressure = clamp(self.war_state.radical_pressure + max(0, applied_violence_shift), 0, 100)
        self.log(
            f"Propaganda deployed: target={target}, tone={tone}, profile={profile_name}. "
            f"Violence shift {applied_violence_shift}."
        )
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
        self.show_canvas_view()
        canvas = self.content_canvas
        canvas.update_idletasks()
        width = max(760, canvas.winfo_width())
        height = max(520, canvas.winfo_height())
        canvas.create_text(14, 10, anchor="nw", fill="#edf3ff", font=("Helvetica", 12, "bold"), text="Friendship + Trust Network")
        rel_help_btn = tk.Button(self.left, text="?", command=lambda: self.show_help("relationships_tab"), bg="#4f5f80", fg="white", width=2)
        canvas.create_window(width - 24, 20, window=rel_help_btn, width=20, height=20)

        chars = list(self.characters.values())
        n = len(chars)
        cx, cy = width // 2, max(220, height // 2)
        r = max(170, min(width, height) // 2 - 90)
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
            info_btn = tk.Button(self.left, text="?", command=lambda n=c.name: self.show_help(n if n in self.lexicon else "general"), bg="#4f5f80", fg="white", width=2)
            canvas.create_window(x + 32, y - 30, window=info_btn, width=18, height=18)

        legend = "Blue edges: discovered hidden ties only. Top bar: trust. Bottom bar: relationship."
        canvas.create_text(14, height - 14, anchor="sw", fill="#bfd2f2", font=("Helvetica", 9), text=legend)
        self.clear_choices()
        self.add_choice("Back to Console", self.main_week_screen)

    def show_factions(self) -> None:
        s = self.state
        txt = (
            f"Worker support {s.worker_support}\nTechnician support {s.technician_support}\nElite sympathy {s.elite_sympathy}\n"
            f"Public sympathy {s.public_sympathy}\nPolice infiltration {s.police_infiltration}\n"
            f"Operational secrecy {s.operational_secrecy}\nMorale {s.morale}\nViolence {s.violence_level}"
        )
        messagebox.showinfo("Faction Dashboard", txt)

    def show_revolution_readiness(self) -> None:
        if self.war_state and self.war_state.active:
            messagebox.showinfo("Revolution Readiness", "War phase is already active. Revolution escalation cannot be triggered again.")
            return
        s = self.state
        ready = s.membership > 55 and s.movement_funding > 80 and s.worker_support > 60 and s.public_unrest > 50
        stat_hints = {
            "Membership": "Recruit in abandoned human factory.",
            "Funding": "Run operations and secure resource caches.",
            "Worker support": "Complete worker-focused actions and protections.",
            "Public unrest": "Expose custodian abuses and spread agitation.",
            "Technician support": "Win over specialists through tech and safety choices.",
            "Police suspicion": "Use low-profile tactics and avoid noisy crackdowns.",
        }
        txt = (
            f"Membership: {s.membership}/55 (?) {stat_hints['Membership']}\n"
            f"Funding: {s.movement_funding}/80 (?) {stat_hints['Funding']}\n"
            f"Worker support: {s.worker_support}/60 (?) {stat_hints['Worker support']}\n"
            f"Public unrest: {s.public_unrest}/50 (?) {stat_hints['Public unrest']}\n"
            f"Technician support: {s.technician_support}/40 (?) {stat_hints['Technician support']}\n"
            f"Police suspicion: {s.police_suspicion} (lower safer) (?) {stat_hints['Police suspicion']}\n\n"
            f"Ready: {'YES' if ready else 'NO'}"
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
        self.log("Escalation chosen: open conflict begins across contested zones.")
        self.start_war_phase()

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
        war_outcome = s.flags.get("war_outcome", "")
        if war_outcome == "Damaged victory":
            self.apply_effects({"medical_availability": -8, "food_production": -8, "trust_in_player": -6})
        elif war_outcome == "Negotiated transition":
            self.apply_effects({"economic_equality": -6, "government_stability": 4, "political_freedom": 4})
        elif war_outcome == "Split government":
            self.apply_effects({"government_stability": -8, "opposition_strength": 10})

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

        war_start_week = int(s.flags.get("war_start_week", s.week))
        war_weeks = int(s.flags.get("war_weeks", 0))
        prep_weeks = max(0, war_start_week - 1)
        war_deaths = int(s.flags.get("war_casualties_points", 0)) * WAR_CASUALTY_UNIT

        baseline_linking_deaths = REVOLUTION_HORIZON_WEEKS * LINKING_DEATHS_PER_WEEK
        prep_linking_deaths = prep_weeks * LINKING_DEATHS_PER_WEEK
        revolution_deaths_total = prep_linking_deaths + war_deaths
        estimated_saved = baseline_linking_deaths - revolution_deaths_total

        lines.append(f"War length: {war_weeks} weeks after {prep_weeks} prep weeks.")
        lines.append(f"Deaths from brain-linking (baseline 40 weeks): {baseline_linking_deaths:,}.")
        lines.append(f"Deaths during revolution path: {revolution_deaths_total:,} (linking before war: {prep_linking_deaths:,}; war: {war_deaths:,}).")
        lines.append(
            "People saved = (40 weeks × 3,000) - ((prep weeks × 3,000) + war deaths)"
            f" = {estimated_saved:,}."
        )

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
        peaceful = bool(self.state.flags.get("peaceful_propaganda_used_this_week"))
        non_peaceful = bool(self.state.flags.get("non_peaceful_propaganda_used_this_week"))
        if peaceful and not non_peaceful:
            self.state.flags["peaceful_propaganda_streak_weeks"] = int(
                self.state.flags.get("peaceful_propaganda_streak_weeks", 0)
            ) + 1
        else:
            self.state.flags["peaceful_propaganda_streak_weeks"] = 0
        self.state.flags["peaceful_propaganda_used_this_week"] = False
        self.state.flags["non_peaceful_propaganda_used_this_week"] = False
        if int(self.state.flags.get("peaceful_propaganda_streak_weeks", 0)) >= 40:
            self.set_ending("Peaceful electoral transition: anti-linking candidate elected")
            return
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
