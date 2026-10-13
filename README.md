# assetto-claude-mods

Sammlung aller eigenen Assetto-Corsa-Mods: KI-Verbesserungen, Fahrzeuge, Strecken, Apps und Werkzeuge.

## Struktur

| Ordner | Inhalt |
|---|---|
| `AI/` | Alles rund um die Gegner-KI, sechs Teilprojekte (siehe unten) |
| `cars/` | Eigene Fahrzeuge und Physik-Mods (ein Unterordner pro Auto) |
| `tracks/` | Eigene Strecken und Strecken-Konfigurationen |
| `apps/` | In-Game-Apps (Lua für CSP, Python für das klassische SDK) |
| `tools/` | Externe Werkzeuge: Telemetrie, Konverter, Prüfskripte |

## AI-Teilprojekte

| Nr. | Ordner | Ziel | Aufwand |
|---|---|---|---|
| 1 | `AI/01-fast-lane-recorder` | Eigene Runden aufnehmen und als `fast_lane.ai` schreiben | niedrig bis mittel |
| 2 | `AI/02-ai-hints` | `ai_hints.ini` und Side-Lines gegen Panikbremsen | niedrig |
| 3 | `AI/03-csp-ai-profile` | Abgestimmte Profile für CSP New AI Behaviour | niedrig |
| 4 | `AI/04-lua-behaviour` | Lua-Verhaltensschicht: Fake-Moves, Druck, Verteidigung | mittel bis hoch |
| 5 | `AI/05-line-optimizer` | Ideallinie algorithmisch berechnen | mittel |
| 6 | `AI/06-reinforcement-learning` | RL-Agent im Python-Simulator, Transfer nach AC | hoch |

Reihenfolge der Arbeit: 1, dann 2 und 3 parallel, danach 4 oder 6. Projekt 1 liefert Parser und Telemetrie, auf denen 5 und 6 aufbauen.

## Voraussetzungen

- Assetto Corsa mit Content Manager
- Custom Shaders Patch (CSP), Version im jeweiligen Projekt-README vermerkt
- Python 3.11 oder neuer für die Werkzeuge in `AI/` und `tools/`

## Installation einer Mod

Jedes Teilprojekt hat ein eigenes README mit Installationsschritten. Faustregel: Dateien aus `dist/` des Projekts in den passenden Ordner unter `assettocorsa/content/` oder `assettocorsa/apps/` kopieren. Originaldateien vorher sichern.
