# Ker Nethalas Digital Companion - Sample Data v0.1

This folder is a small, paraphrased development sample for a Python 3.12+ prototype.
It is not a complete transcription of the rulebook.

Recommended split:
- Static definitions: skills, resistances, masteries, abilities, weapons, armor, creatures.
- Scenario content: first_domain.json.
- Runtime state: seraphine_save.json.
- Regression tests: test_cases.json.

All IDs are stable snake_case identifiers intended for code and save-file compatibility.
Add a `content_version` to every production content pack and save file.
