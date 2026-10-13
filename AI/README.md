# AI

Teilprojekte zur Verbesserung der Gegner-KI in Assetto Corsa.

## Das Problem

Die Kunos-KI folgt stur einer einzigen Linie (`fast_lane.ai`). Blockiert man sie, bremst sie hart, weil sie keine alternativen Spuren kennt. Sie hat kein Gedächtnis und keine Absicht über den nächsten Zielpunkt hinaus. Ihre Geschwindigkeit ist durch die aufgenommene Linie begrenzt, die oft konservativ ist.

## Drei Hebel, sechs Projekte

| Hebel | Projekte |
|---|---|
| Die Linie selbst schneller machen | 01, 05, 06 |
| Das Bremsverhalten entschärfen | 02, 03 |
| Echtes Renn-Verhalten ergänzen | 04, 06 |

## Gemeinsame Bausteine

- `01-fast-lane-recorder/fastlane/` wird das Python-Paket zum Lesen und Schreiben von `fast_lane.ai`. Projekte 05 und 06 importieren es.
- Telemetrie-Logs aus der Aufnahme-App (Projekt 01) sind das Trainings- und Vergleichsmaterial für 04, 05 und 06.
- Streckendaten (Mittellinie, Ränder) liegen pro Strecke unter `AI/data/<track>/` und werden nicht ins Repo eingecheckt, wenn sie aus Kunos-Content stammen. Siehe `.gitignore`.
