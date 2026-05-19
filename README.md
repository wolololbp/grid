# Ashes & Circuits

A data-driven graphical political/social simulation + branching visual novel game built with Python/Tkinter.

## Features
- 3-phase campaign loop (survival, organization, governance) spanning 40-60 weeks.
- 8 major arcs with event-driven story progression and systemic simulation.
- 20 major characters with relationship/trust/resentment dynamics and hidden links.
- 12+ endings via governance and revolution outcomes.
- 12 locations with class barriers and different action risks/rewards.
- Weekly action economy + random pressure events.
- Save/load/reset + autosafe state model (JSON-serializable game state).

## Run
```bash
python3 game.py
```

## Notes for extending content
- Add scenes in `_init_story_scenes`.
- Add weekly systemic events in `_init_weekly_events`.
- Add new characters in `_init_characters`.
- Add location effects in `visit_location`.
- Add more propaganda combinations in `propaganda_menu`.
