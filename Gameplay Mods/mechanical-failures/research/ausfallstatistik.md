# Ausfallstatistik F1 1988 bis 2025

Berechnet aus F1DB (https://github.com/f1db/f1db, CC BY 4.0) mit `tools/failure_stats.py`. Jeder Rennstart wird nach dem eingetragenen Ausfallgrund einer Kategorie zugeordnet; Unfälle, Kollisionen, Dreher, Disqualifikationen zählen nicht als mechanisch. Ergebnis: Prozent pro Auto und Rennen, Tabelle in `data/failure_rates.md`, Profile pro Jahr in `profiles/failures_<jahr>.ini`.

## Kernzahlen (mechanische Ausfälle in Prozent der Starts)

| Jahr | gesamt | Motor | Getriebe | Hydraulik | Elektrik |
|---|---|---|---|---|---|
| 1996 | 27,1 | 11,0 | 5,8 | 1,2 | 2,1 |
| 1999 | 33,8 | 6,8 | 13,4 | 2,0 | 2,6 |
| 2002 | 31,5 | 12,8 | 6,4 | 3,6 | 1,7 |
| 2004 | 19,2 | 6,1 | 5,3 | 1,9 | 1,1 |
| 2006 | 18,2 | 6,3 | 3,5 | 3,5 | 0,8 |
| 2008 | 9,0 | 2,7 | 2,2 | 1,1 | 0,5 |
| 2010 | 14,9 | 2,9 | 2,9 | 4,6 | 0,0 |
| 2013 | 9,3 | 1,9 | 1,2 | 1,2 | 0,5 |
| 2014 | 15,0 | 5,7 | 2,2 | 0,3 | 1,5 |
| 2017 | 15,0 | 5,5 | 1,5 | 1,5 | 1,3 |
| 2021 | 7,1 | 1,1 | 0,9 | 0,2 | 0,7 |
| 2024 | 4,6 | 1,0 | 0,8 | 0,4 | 0,0 |
| 2025 | 4,2 | 1,3 | 0,2 | 0,2 | 0,0 |

## Beispiele für Fahrer-Multiplikatoren

Aus `data/failure_rates.json`, Abschnitt `engine_manufacturers` und `constructors`:

| Jahr | Einheit | mech. Ausfälle | Faktor gegenüber Saison |
|---|---|---|---|
| 2017 | Honda (McLaren) | 30 Prozent der Starts | Motor 2,3 |
| 2017 | Renault | 30 Prozent | Motor 1,5 |
| 2017 | Mercedes | 5 Prozent | Motor 0,4 |
| 1997 | Ford | 51 Prozent | Motor 1,9 |
| 1995 | Peugeot | 44 Prozent | Motor 2,2 |

Das Karriere-System setzt daraus `ENGINE_MULT` pro Fahrer. Faustregel für die Skalierung auf kürzere Rennen: `RACE_LENGTH_MIN` in `failures.ini` auf die tatsächliche Renndauer setzen, die Raten gelten für die volle Distanz.

## Grenzen

- Ausfallgründe in den Ergebnislisten sind grob (oft nur „Engine“), Doppelursachen fehlen.
- Nicht erfasst: Ausfälle, die als Unfall gewertet wurden, aber mechanisch verursacht waren (Reifenschaden, Bremsen).
- Ab 2014 verstecken sich viele Probleme in Gridstrafen und Leistungsreduktion statt in Ausfällen; dafür sind die Degradationsraten in Version 2 vorgesehen.
