# assetto-claude-mods

Sammlung aller eigenen Assetto-Corsa-Mods. Oberste Ebene: Mod-Kategorien. Darunter: die einzelnen Mods, jede mit eigenem README (Ziel, Installation, Status).

## Kategorien

| Ordner | Inhalt |
|---|---|
| `AI Mods/` | Gegner-KI: sechs Teilprojekte, siehe unten |
| `Car Mods/` | Fahrzeuge und Fahrzeugphysik, ein Unterordner pro Auto |
| `Layout Mods/` | Strecken, Layouts und Strecken-Konfigurationen |
| `App Mods/` | In-Game-Apps (Lua für CSP, Python für das klassische SDK) |
| `Career Mods/` | Karriere-System als Ersatz für Excel und Content-Manager-Saisons |
| `Gameplay Mods/` | Spielregeln und Rennverlauf: mechanische Ausfälle und mehr |
| `Tools/` | Externe Werkzeuge: Telemetrie, Konverter, Prüfskripte |

## Aktuelle Mods

| Kategorie | Mod | Status |
|---|---|---|
| AI Mods | `01-fast-lane-recorder` Eigene Runden als `fast_lane.ai` | Paket, App und Skripte fertig, Test mit Monza offen |
| AI Mods | `02-ai-hints` `ai_hints.ini` gegen Panikbremsen | geplant |
| AI Mods | `03-csp-ai-profile` Profile für CSP New AI Behaviour | geplant |
| AI Mods | `04-lua-behaviour` Fake-Moves, Druck, Verteidigung | geplant |
| AI Mods | `05-line-optimizer` Ideallinie berechnen | geplant |
| AI Mods | `06-reinforcement-learning` RL-Agent im Simulator | geplant |
| Car Mods | `porsche_956` Bellof Ring-Rekord 1983 mit Ground-Effect | Recherche und Venturi-Modell fertig, Physikdaten offen |
| Career Mods | `career-system` Import der Excel-Karrieren, Ziele, Beziehungen, Rennstart | Importer für 2017er Datei fertig |
| Gameplay Mods | `mechanical-failures` Defekte, Verschleiß, Dirty Air pro Ära, Bauteil und Fahrer | Konzept, Liste und Script-Entwurf |

Reihenfolge bei den AI Mods: 1, dann 2 und 3 parallel, danach 4 oder 6. Projekt 1 liefert Parser und Telemetrie, auf denen 5 und 6 aufbauen.

## Voraussetzungen

- Assetto Corsa mit Content Manager
- Custom Shaders Patch (CSP), Version im jeweiligen Mod-README vermerkt
- Python 3.11 oder neuer für die Werkzeuge

## Installation einer Mod

Jede Mod hat ein eigenes README mit Installationsschritten. Faustregel: Dateien aus `dist/` der Mod in den passenden Ordner unter `assettocorsa/content/` oder `assettocorsa/apps/` kopieren. Originaldateien vorher sichern.
