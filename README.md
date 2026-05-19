# Ashes & Circuits

Graphical narrative-simulation game (Python + Tkinter) with long-form weekly progression.

## Features
- 3-phase campaign loop: survival, organization, governance.
- 8+ chapter beats over 40-60 weeks.
- 18 major characters with hidden links.
- 12-map location system with class barriers.
- Weekly action economy, propaganda system, surveillance pressure, relationship scenes.
- Revolution readiness and multiple transition paths.
- Post-revolution government + economic model choices.
- 12+ distinct ending outcomes based on systemic stats.
- Save/Load/Reset with JSON persistence (`savegame.json`).

## Run
```bash
python3 game.py
```

## Notes for extending content
`game.py` is data-driven around:
- `make_characters()` for cast and hidden links.
- `LOCATIONS` + `visit()` for location mechanics.
- `random_weekly_event()` for weekly content/event volume.
- `determine_ending()` for ending logic.

Add more events/scenes by expanding those structured lists and handlers.
