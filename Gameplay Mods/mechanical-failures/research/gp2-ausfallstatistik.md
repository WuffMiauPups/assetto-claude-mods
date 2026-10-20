# GP2 Series 2005 und 2006: Ausfallstatistik

Ziel: Ausfallprofile pro Saison für die Reliability-App (Dallara GP2/05, Mecachrome V8 4,0 l, Bridgestone, Einheitsauto). Maschinenlesbar in `data/gp2_retirements.json`. Erstellt am 2026-10-20.

## Quellen

- teamdan.com Saisonarchiv mit Ausfallgrund je Fahrer (Hauptquelle für die Gründe, "TD"):
  - 2005: https://web.archive.org/web/20081122061331/http://www.teamdan.com/archive/2005/gp2.html
  - 2006: https://web.archive.org/web/20080226044155/http://www.teamdan.com/archive/2006/gp2.html
- Wikipedia, Saisonartikel und Rundenberichte mit Klassement, Runden, Siegerzeit ("WP"); 2006 zum Teil mit Ausfallgrund:
  - https://en.wikipedia.org/wiki/2005_GP2_Series, https://en.wikipedia.org/wiki/2006_GP2_Series
  - Rundenartikel nach dem Muster https://en.wikipedia.org/wiki/2005_Imola_GP2_Series_round (alle 23 bzw. 11 Runden)
- crash.net Ergebnislisten 2005 (archiviert, ohne Grund, nur zum Abgleich der Klassemente), z. B. https://web.archive.org/web/20120922075814/http://www.crash.net/gp2/results/66428/1/gp2_race_result_1_-_imola.html
- Einzelklärungen:
  - crash.net Monza 2005 Lauf 1 (Mondini abgewürgt, Speed Defekt): https://www.crash.net/gp2/race-report/66829/1/monza-2005-kovalainen-wins-under-pressure
  - autosport Monza 2005 Lauf 2 (Piquet Kollision): https://www.autosport.com/f2/news/46715/jani-takes-close-win-in-race-2
  - crash.net Imola 2006 Lauf 1 (López Hydraulik laut Team): https://www.crash.net/gp2/race-report/67090/1/imola-2006-bruni-on-his-own
  - crash.net Barcelona 2006 Lauf 1 (Lapierre Reifen, Zuber Reifenschaden): https://www.crash.net/gp2/news/67197/1/premat-steals-barcelona-win-from-team-mate
  - racecar.com Imola 2006 Lauf 2: https://www.racecar.com/news/13283/motorsport/gp2-imola-race-2-report
  - formulascout Imola 2005 (Lapierre Lauf 2 nur zum Teileschonen gefahren): https://formulascout.com/reliving-the-first-ever-gp2-weekend-imola-2005/61778

## Methode und Definitionen

- **Start**: jedes Auto, das zum Rennen antrat oder in der Startaufstellung stand. Technische DNS (Defekt in der Einführungsrunde oder am Grid) zählen als Start und als Ausfall, weil sie für die Simulation genau so ein Defekt sind. Nicht gezählt: DNS aus Sport- oder Verletzungsgründen, Ausschlüsse vor dem Rennen (Liste unten).
- **Ausfall**: Ret/DNF, technischer DNS und "klassiert, aber nicht mehr fahrend", wenn der Grund mechanisch ist (z. B. Monaco 2005, García Motor als 10.). Klassierte Fahrer mit Dreher oder Unfall bleiben außen vor.
- **Kategorien**: ENGINE (inkl. Benzinpumpe), GEARBOX (inkl. Kupplung, "transmission"), HYDRAULICS, ELECTRICS, BRAKES, SUSPENSION (inkl. Lenkung und verlorenes Rad, da kein eigener Code), COOLING (Kühler, Wasserverlust), POWER_LOSS (Fehlzündung, Gaspedal/Drosselklappe), PUNCTURE, STALL, ACCIDENT (Unfall, Dreher, Kollision, Folgeschaden), UNKNOWN.
- **Mechanisch** in den Summen = die acht Codes ENGINE bis POWER_LOSS. PUNCTURE und STALL getrennt ausgewiesen.
- Wo TD und WP sich widersprechen, steht beides im Grundtext. Bei Widerspruch ohne dritte Quelle: UNKNOWN.
- Renndauer = Siegerzeit. Monaco (nur ein Lauf) läuft als Feature.

## Saison 2005

23 Rennen, 550 Starts, 147 Ausfälle, davon 73 mechanisch (13.3 % der Starts), 0 Reifenschäden, 2 abgewürgt, 68 Unfälle, 4 ohne Grund.

### Rennen

| # | Runde | Strecke | Typ | Starter | Runden | Siegerzeit min | Ausfälle | davon mech. |
|---|---|---|---|---|---|---|---|---|
| 0 | 1 | Imola | feature | 24 | 37 | 62.3 | 7 | 7 |
| 1 | 1 | Imola | sprint | 24 | 17 | 28.5 | 8 | 8 |
| 2 | 2 | Catalunya | feature | 24 | 39 | 58.1 | 11 | 5 |
| 3 | 2 | Catalunya | sprint | 24 | 18 | 30.2 | 6 | 2 |
| 4 | 3 | Monaco | feature | 23 | 44 | 64.7 | 12 | 7 |
| 5 | 4 | Nürburgring | feature | 24 | 33 | 61.7 | 7 | 1 |
| 6 | 4 | Nürburgring | sprint | 23 | 24 | 42.7 | 9 | 2 |
| 7 | 5 | Magny-Cours | feature | 24 | 41 | 62.9 | 5 | 3 |
| 8 | 5 | Magny-Cours | sprint | 24 | 28 | 41.5 | 3 | 1 |
| 9 | 6 | Silverstone | feature | 24 | 36 | 58.4 | 3 | 3 |
| 10 | 6 | Silverstone | sprint | 24 | 24 | 40.2 | 8 | 6 |
| 11 | 7 | Hockenheim | feature | 24 | 40 | 59.5 | 9 | 4 |
| 12 | 7 | Hockenheim | sprint | 24 | 27 | 39.9 | 3 | 2 |
| 13 | 8 | Hungaroring | feature | 24 | 42 | 71.2 | 10 | 7 |
| 14 | 8 | Hungaroring | sprint | 24 | 25 | 45.1 | 5 | 2 |
| 15 | 9 | Istanbul | feature | 24 | 34 | 61.5 | 7 | 1 |
| 16 | 9 | Istanbul | sprint | 24 | 23 | 43.8 | 4 | 1 |
| 17 | 10 | Monza | feature | 24 | 32 | 53.9 | 9 | 2 |
| 18 | 10 | Monza | sprint | 24 | 20 | 33.9 | 6 | 1 |
| 19 | 11 | Spa-Francorchamps | feature | 24 | 26 | 68.2 | 8 | 2 |
| 20 | 11 | Spa-Francorchamps | sprint | 24 | 9 | 21.3 | 0 | 0 |
| 21 | 12 | Bahrain | feature | 24 | 34 | 63.6 | 5 | 5 |
| 22 | 12 | Bahrain | sprint | 24 | 23 | 41.8 | 2 | 1 |

Mittlere Renndauer: Feature 62.2 min (12 Rennen, ohne Monaco 61.9 min), Sprint 37.2 min (11 Rennen, ohne den abgebrochenen Spa-Sprint 38.8 min).

### Ausfälle nach Kategorie

| Kategorie | Anzahl | pro 100 Starts | Feature | Sprint |
|---|---|---|---|---|
| ENGINE | 17 | 3.09 | 10 | 7 |
| GEARBOX | 25 | 4.55 | 17 | 8 |
| HYDRAULICS | 7 | 1.27 | 6 | 1 |
| ELECTRICS | 4 | 0.73 | 3 | 1 |
| BRAKES | 13 | 2.36 | 7 | 6 |
| SUSPENSION | 5 | 0.91 | 3 | 2 |
| COOLING | 0 | 0.00 | 0 | 0 |
| POWER_LOSS | 2 | 0.36 | 1 | 1 |
| PUNCTURE | 0 | 0.00 | 0 | 0 |
| STALL | 2 | 0.36 | 2 | 0 |
| ACCIDENT | 68 | 12.36 | 42 | 26 |
| UNKNOWN | 4 | 0.73 | 2 | 2 |
| **mechanisch gesamt** | **73** | **13.27** | 47 | 26 |

Mechanische Ausfälle je Start: Feature 47/287 = 16.4 %, Sprint 26/263 = 9.9 %.

### Teams

| Team | Key | Starts | mech. | Rate mech. | PUNCTURE | STALL | ACCIDENT | UNKNOWN | häufigster Defekt |
|---|---|---|---|---|---|---|---|---|---|
| BCN Competición | BCN | 45 | 10 | 22.2 % | 0 | 0 | 3 | 0 | GEARBOX 4, ENGINE 2 |
| David Price Racing (2006: DPR Direxiv) | DPR | 46 | 10 | 21.7 % | 0 | 1 | 9 | 1 | GEARBOX 5, ENGINE 2 |
| Campos Racing | Campos | 46 | 9 | 19.6 % | 0 | 0 | 6 | 0 | ENGINE 3, HYDRAULICS 2 |
| Durango | Durango | 46 | 8 | 17.4 % | 0 | 1 | 9 | 0 | GEARBOX 3, HYDRAULICS 2 |
| iSport International | iSport | 46 | 7 | 15.2 % | 0 | 0 | 3 | 0 | GEARBOX 2, BRAKES 2 |
| Racing Engineering | RacingEngineering | 45 | 6 | 13.3 % | 0 | 0 | 6 | 1 | BRAKES 3, GEARBOX 2 |
| DAMS | DAMS | 46 | 6 | 13.0 % | 0 | 0 | 7 | 0 | ENGINE 3, GEARBOX 3 |
| Hitech Piquet Sports (2006: Piquet Sports) | Piquet | 46 | 6 | 13.0 % | 0 | 0 | 7 | 0 | HYDRAULICS 2, ENGINE 1 |
| Arden International | Arden | 46 | 4 | 8.7 % | 0 | 0 | 6 | 0 | GEARBOX 3, ENGINE 1 |
| Coloni Motorsport | Coloni | 46 | 3 | 6.5 % | 0 | 0 | 5 | 1 | GEARBOX 1, ELECTRICS 1 |
| Super Nova International / Racing | SuperNova | 46 | 3 | 6.5 % | 0 | 0 | 1 | 1 | ENGINE 2, BRAKES 1 |
| ART Grand Prix | ART | 46 | 1 | 2.2 % | 0 | 0 | 6 | 0 | BRAKES 1 |

### Alle Ausfälle

| # | Rennen | Fahrer | Team | Status | Runden | Grund (Quelle) | Kategorie |
|---|---|---|---|---|---|---|---|
| 0 | Imola F | Borja García | RacingEngineering | Ret | 31 | brakes | BRAKES |
| 0 | Imola F | Ferdinando Monfardini | Durango | Ret | 31 | brakes | BRAKES |
| 0 | Imola F | Juan Cruz Álvarez | Campos | Ret | 24 | brakes | BRAKES |
| 0 | Imola F | Ryan Sharp | DPR | Ret | 12 | brakes | BRAKES |
| 0 | Imola F | Hiroki Yoshimoto | BCN | Ret | 12 | steering | SUSPENSION |
| 0 | Imola F | Alexandre Negrão | Piquet | Ret | 5 | brakes | BRAKES |
| 0 | Imola F | Nicolas Lapierre | Arden | DNS | 0 | engine | ENGINE |
| 1 | Imola S | Giorgio Pantano | SuperNova | Ret | 14 | brakes | BRAKES |
| 1 | Imola S | Nico Rosberg | ART | Ret | 12 | brakes | BRAKES |
| 1 | Imola S | Mathias Lauda | Coloni | Ret | 3 | brakes | BRAKES |
| 1 | Imola S | Can Artam | iSport | Ret | 3 | brakes | BRAKES |
| 1 | Imola S | Scott Speed | iSport | Ret | 2 | misfire | POWER_LOSS |
| 1 | Imola S | Clivio Piccione | Durango | Ret | 1 | fuel pump | ENGINE |
| 1 | Imola S | Ernesto Viso | BCN | DNS | 0 | brakes | BRAKES |
| 1 | Imola S | Ferdinando Monfardini | Durango | DNS | 0 | clutch | GEARBOX |
| 2 | Catalunya F | Clivio Piccione | Durango | Ret | 35 | spin | ACCIDENT |
| 2 | Catalunya F | Ryan Sharp | DPR | Ret | 31 | engine | ENGINE |
| 2 | Catalunya F | Olivier Pla | DPR | Ret | 30 | spin | ACCIDENT |
| 2 | Catalunya F | Mathias Lauda | Coloni | Ret | 29 | spin | ACCIDENT |
| 2 | Catalunya F | Can Artam | iSport | Ret | 27 | gearbox | GEARBOX |
| 2 | Catalunya F | Hiroki Yoshimoto | BCN | Ret | 20 | misfire | POWER_LOSS |
| 2 | Catalunya F | Ernesto Viso | BCN | Ret | 19 | transmission | GEARBOX |
| 2 | Catalunya F | Sergio Hernández | Campos | Ret | 14 | engine | ENGINE |
| 2 | Catalunya F | Juan Cruz Álvarez | Campos | Ret | 5 | spin | ACCIDENT |
| 2 | Catalunya F | Borja García | RacingEngineering | Ret | 2 | accident | ACCIDENT |
| 2 | Catalunya F | Ferdinando Monfardini | Durango | Ret | 2 | spin | ACCIDENT |
| 3 | Catalunya S | Can Artam | iSport | Ret | 11 | contact 18 | ACCIDENT |
| 3 | Catalunya S | Gianmaria Bruni | Coloni | Ret | 8 | contact 8 | ACCIDENT |
| 3 | Catalunya S | Alexandre Prémat | ART | Ret | 4 | crash 10 | ACCIDENT |
| 3 | Catalunya S | Olivier Pla | DPR | Ret | 1 | spin 16 | ACCIDENT |
| 3 | Catalunya S | Heikki Kovalainen | Arden | Ret | 0 | transmission 6 | GEARBOX |
| 3 | Catalunya S | Ernesto Viso | BCN | Ret | 0 | engine 20 | ENGINE |
| 4 | Monaco F | Borja García | RacingEngineering | Classified-not-running | 40 | engine | ENGINE |
| 4 | Monaco F | Nelson Piquet Jr. | Piquet | Classified-not-running | 40 | gearbox | GEARBOX |
| 4 | Monaco F | Nicolas Lapierre | Arden | Ret | 33 | spin | ACCIDENT |
| 4 | Monaco F | Alexandre Prémat | ART | Ret | 23 | spin | ACCIDENT |
| 4 | Monaco F | Clivio Piccione | Durango | Ret | 11 | crash | ACCIDENT |
| 4 | Monaco F | Neel Jani | RacingEngineering | Ret | 10 | brakes | BRAKES |
| 4 | Monaco F | José María López | DAMS | Ret | 10 | gearbox | GEARBOX |
| 4 | Monaco F | Ryan Sharp | DPR | Ret | 8 | gearbox | GEARBOX |
| 4 | Monaco F | Fairuz Fauzy | DAMS | Ret | 6 | engine | ENGINE |
| 4 | Monaco F | Giorgio Pantano | SuperNova | Ret | 0 | engine | ENGINE |
| 4 | Monaco F | Juan Cruz Álvarez | Campos | Ret | 0 | accident | ACCIDENT |
| 4 | Monaco F | Ferdinando Monfardini | Durango | DNS | 0 | stalled at start (TD: 0 laps/stalled; WP: DNS) | STALL |
| 5 | Nürburgring F | Juan Cruz Álvarez | Campos | Ret | 30 | accident | ACCIDENT |
| 5 | Nürburgring F | Ernesto Viso | BCN | Ret | 8 | lost wheel | SUSPENSION |
| 5 | Nürburgring F | Olivier Pla | DPR | Ret | 0 | accident | ACCIDENT |
| 5 | Nürburgring F | Adam Carroll | SuperNova | Ret | 0 | accident | ACCIDENT |
| 5 | Nürburgring F | Borja García | RacingEngineering | Ret | 0 | accident | ACCIDENT |
| 5 | Nürburgring F | Ferdinando Monfardini | Durango | Ret | 0 | accident | ACCIDENT |
| 5 | Nürburgring F | Alexandre Negrão | Piquet | Ret | 0 | accident | ACCIDENT |
| 6 | Nürburgring S | Neel Jani | RacingEngineering | Classified-not-running | 22 | brakes | BRAKES |
| 6 | Nürburgring S | Can Artam | iSport | Ret | 17 | spin | ACCIDENT |
| 6 | Nürburgring S | Gianmaria Bruni | Coloni | Ret | 16 | spin | ACCIDENT |
| 6 | Nürburgring S | Alexandre Negrão | Piquet | Ret | 6 | spin | ACCIDENT |
| 6 | Nürburgring S | Heikki Kovalainen | Arden | Ret | 2 | accident | ACCIDENT |
| 6 | Nürburgring S | Nicolas Lapierre | Arden | Ret | 1 | accident | ACCIDENT |
| 6 | Nürburgring S | Alexandre Prémat | ART | Ret | 1 | accident | ACCIDENT |
| 6 | Nürburgring S | Mathias Lauda | Coloni | Ret | 1 | accident | ACCIDENT |
| 6 | Nürburgring S | Hiroki Yoshimoto | BCN | DNS | 0 | gearbox | GEARBOX |
| 7 | Magny-Cours F | Borja García | RacingEngineering | Ret | 30 | gearbox | GEARBOX |
| 7 | Magny-Cours F | Nelson Piquet Jr. | Piquet | Ret | 24 | engine | ENGINE |
| 7 | Magny-Cours F | Olivier Pla | DPR | Ret | 15 | spin | ACCIDENT |
| 7 | Magny-Cours F | Juan Cruz Álvarez | Campos | Ret | 9 | suspension | SUSPENSION |
| 7 | Magny-Cours F | Alexandre Negrão | Piquet | Ret | 1 | spin | ACCIDENT |
| 8 | Magny-Cours S | Alexandre Prémat | ART | Ret | 23 | accident | ACCIDENT |
| 8 | Magny-Cours S | José María López | DAMS | Ret | 22 | accident | ACCIDENT |
| 8 | Magny-Cours S | Ryan Sharp | DPR | Ret | 6 | engine | ENGINE |
| 9 | Silverstone F | Fairuz Fauzy | DAMS | Ret | 31 | gearbox | GEARBOX |
| 9 | Silverstone F | Ryan Sharp | DPR | Ret | 1 | transmission | GEARBOX |
| 9 | Silverstone F | Nelson Piquet Jr. | Piquet | DNS | 0 | electrics, did not take the start (TD 0 laps/electrics; WP DNS) | ELECTRICS |
| 10 | Silverstone S | Clivio Piccione | Durango | Ret | 19 | steering | SUSPENSION |
| 10 | Silverstone S | Ryan Sharp | DPR | Ret | 18 | WP Ret after 18 laps, TD NC; no reason found | UNKNOWN |
| 10 | Silverstone S | Nicolas Lapierre | Arden | Ret | 16 | gearbox | GEARBOX |
| 10 | Silverstone S | Nelson Piquet Jr. | Piquet | Ret | 8 | spin | ACCIDENT |
| 10 | Silverstone S | Juan Cruz Álvarez | Campos | Ret | 5 | engine | ENGINE |
| 10 | Silverstone S | José María López | DAMS | DNS | 0 | engine, did not take the start (TD 0 laps/engine; WP DNS) | ENGINE |
| 10 | Silverstone S | Hiroki Yoshimoto | BCN | DNS | 0 | engine, did not take the start (TD 0 laps/engine; WP DNS) | ENGINE |
| 10 | Silverstone S | Fairuz Fauzy | DAMS | DNS | 0 | engine, did not take the start (TD 0 laps/engine; WP DNS) | ENGINE |
| 11 | Hockenheim F | Gianmaria Bruni | Coloni | Ret | 20 | WP Ret after 20 laps, TD NC; no reason found | UNKNOWN |
| 11 | Hockenheim F | Can Artam | iSport | Ret | 17 | gearbox | GEARBOX |
| 11 | Hockenheim F | Clivio Piccione | Durango | Ret | 15 | gearbox | GEARBOX |
| 11 | Hockenheim F | Neel Jani | RacingEngineering | Ret | 10 | gearbox | GEARBOX |
| 11 | Hockenheim F | Adam Carroll | SuperNova | Ret | 7 | engine | ENGINE |
| 11 | Hockenheim F | Fairuz Fauzy | DAMS | Ret | 6 | spin | ACCIDENT |
| 11 | Hockenheim F | Sergio Hernández | Campos | Ret | 4 | spin | ACCIDENT |
| 11 | Hockenheim F | Ferdinando Monfardini | Durango | Ret | 1 | accident | ACCIDENT |
| 11 | Hockenheim F | Alexandre Negrão | Piquet | Ret | 0 | accident | ACCIDENT |
| 12 | Hockenheim S | Neel Jani | RacingEngineering | Ret | 24 | WP Ret after 24 laps, TD classified 22nd; no reason found | UNKNOWN |
| 12 | Hockenheim S | Hiroki Yoshimoto | BCN | Ret | 21 | gearbox | GEARBOX |
| 12 | Hockenheim S | Juan Cruz Álvarez | Campos | Ret | 17 | suspension | SUSPENSION |
| 13 | Hungaroring F | Nelson Piquet Jr. | Piquet | Ret | 37 | hydraulics | HYDRAULICS |
| 13 | Hungaroring F | José María López | DAMS | Ret | 29 | accident | ACCIDENT |
| 13 | Hungaroring F | Juan Cruz Álvarez | Campos | Ret | 25 | gearbox | GEARBOX |
| 13 | Hungaroring F | Sergio Hernández | Campos | Ret | 24 | spin | ACCIDENT |
| 13 | Hungaroring F | Ferdinando Monfardini | Durango | Ret | 21 | hydraulics | HYDRAULICS |
| 13 | Hungaroring F | Scott Speed | iSport | Ret | 18 | hydraulics | HYDRAULICS |
| 13 | Hungaroring F | Mathias Lauda | Coloni | Ret | 18 | gearbox | GEARBOX |
| 13 | Hungaroring F | Fairuz Fauzy | DAMS | Ret | 16 | spin | ACCIDENT |
| 13 | Hungaroring F | Giorgio Mondini | DPR | Ret | 11 | electrics | ELECTRICS |
| 13 | Hungaroring F | Clivio Piccione | Durango | Ret | 8 | hydraulics | HYDRAULICS |
| 14 | Hungaroring S | Olivier Pla | DPR | Ret | 16 | electrics | ELECTRICS |
| 14 | Hungaroring S | José María López | DAMS | Ret | 6 | spin | ACCIDENT |
| 14 | Hungaroring S | Borja García | RacingEngineering | Ret | 4 | accident | ACCIDENT |
| 14 | Hungaroring S | Ernesto Viso | BCN | Ret | 4 | gearbox | GEARBOX |
| 14 | Hungaroring S | Giorgio Mondini | DPR | Ret | 2 | accident damage | ACCIDENT |
| 15 | Istanbul F | Ferdinando Monfardini | Durango | Ret | 26 | accident | ACCIDENT |
| 15 | Istanbul F | Clivio Piccione | Durango | Ret | 23 | spin | ACCIDENT |
| 15 | Istanbul F | Nicolas Lapierre | Arden | Ret | 16 | accident | ACCIDENT |
| 15 | Istanbul F | Gianmaria Bruni | Coloni | Ret | 16 | accident | ACCIDENT |
| 15 | Istanbul F | Fairuz Fauzy | DAMS | Ret | 10 | spin | ACCIDENT |
| 15 | Istanbul F | Sergio Hernández | Campos | Ret | 2 | engine | ENGINE |
| 15 | Istanbul F | Neel Jani | RacingEngineering | Ret | 0 | accident | ACCIDENT |
| 16 | Istanbul S | Ferdinando Monfardini | Durango | Ret | 18 | spin | ACCIDENT |
| 16 | Istanbul S | Neel Jani | RacingEngineering | Ret | 14 | accident | ACCIDENT |
| 16 | Istanbul S | Juan Cruz Álvarez | Campos | Ret | 10 | hydraulics | HYDRAULICS |
| 16 | Istanbul S | Giorgio Mondini | DPR | Ret | 2 | spin | ACCIDENT |
| 17 | Monza F | Ernesto Viso | BCN | Ret | 5 | crash | ACCIDENT |
| 17 | Monza F | Sergio Hernández | Campos | Ret | 5 | accident | ACCIDENT |
| 17 | Monza F | Alexandre Negrão | Piquet | Ret | 4 | accident | ACCIDENT |
| 17 | Monza F | Borja García | RacingEngineering | Ret | 4 | accident | ACCIDENT |
| 17 | Monza F | Alexandre Prémat | ART | Ret | 2 | crash | ACCIDENT |
| 17 | Monza F | Scott Speed | iSport | Ret | 2 | engine (TD); crash.net: car problem, pitted and never re-emerged | ENGINE |
| 17 | Monza F | José María López | DAMS | Ret | 2 | clutch | GEARBOX |
| 17 | Monza F | Olivier Pla | DPR | Ret | 0 | accident | ACCIDENT |
| 17 | Monza F | Giorgio Mondini | DPR | Ret | 0 | stalled at the start, did not complete lap 1 (crash.net; TD DNS) | STALL |
| 18 | Monza S | Giorgio Mondini | DPR | Ret | 14 | gearbox | GEARBOX |
| 18 | Monza S | José María López | DAMS | Ret | 8 | accident | ACCIDENT |
| 18 | Monza S | Nicolas Lapierre | Arden | Ret | 8 | crash | ACCIDENT |
| 18 | Monza S | Ernesto Viso | BCN | Ret | 6 | spin | ACCIDENT |
| 18 | Monza S | Olivier Pla | DPR | Ret | 4 | spin | ACCIDENT |
| 18 | Monza S | Nelson Piquet Jr. | Piquet | Ret | 6 | hit Yoshimoto at second chicane, lap 6 (autosport) | ACCIDENT |
| 19 | Spa-Francorchamps F | Sergio Hernández | Campos | Ret | 22 | hydraulics | HYDRAULICS |
| 19 | Spa-Francorchamps F | Giorgio Pantano | SuperNova | Ret | 22 | WP Ret after 22 laps, TD NC; no reason found | UNKNOWN |
| 19 | Spa-Francorchamps F | Alexandre Prémat | ART | Ret | 16 | accident | ACCIDENT |
| 19 | Spa-Francorchamps F | Giorgio Mondini | DPR | Ret | 13 | accident | ACCIDENT |
| 19 | Spa-Francorchamps F | Gianmaria Bruni | Durango | Ret | 8 | accident | ACCIDENT |
| 19 | Spa-Francorchamps F | Hiroki Yoshimoto | BCN | Ret | 3 | accident | ACCIDENT |
| 19 | Spa-Francorchamps F | Can Artam | iSport | Ret | 3 | accident | ACCIDENT |
| 19 | Spa-Francorchamps F | Nicolas Lapierre | Arden | Ret | 0 | gearbox | GEARBOX |
| 21 | Bahrain F | Olivier Pla | DPR | Ret | 29 | gearbox | GEARBOX |
| 21 | Bahrain F | Ferdinando Monfardini | Coloni | Ret | 20 | electrics | ELECTRICS |
| 21 | Bahrain F | Nelson Piquet Jr. | Piquet | Ret | 13 | hydraulics | HYDRAULICS |
| 21 | Bahrain F | Scott Speed | iSport | Ret | 10 | brakes | BRAKES |
| 21 | Bahrain F | Gianmaria Bruni | Durango | Ret | 7 | gearbox | GEARBOX |
| 22 | Bahrain S | Heikki Kovalainen | Arden | Ret | 1 | spin | ACCIDENT |
| 22 | Bahrain S | Olivier Pla | DPR | DNS | 0 | gearbox | GEARBOX |

Nicht als Start oder nicht als Ausfall gezählt:

- 2005 race 1 Nicolas Lapierre: nach 6 Runden zurückgezogen (Teamentscheidung, kein Defekt), als Start gezählt, nicht als Ausfall
- 2005 race 4 Hiroki Yoshimoto: DNS Monaco, durfte ohne gefahrene Trainingsrunde nicht starten (TD), kein Defekt im Rennen
- 2005 race 6 Borja García: von Lauf 2 Nürburgring ausgeschlossen (WP "EX", 0 Runden), nicht als Start gezählt
- 2005 Monaco: TD führt 5 DNQ, laut Klassement starteten trotzdem 23 Autos; gezählt nach Klassement

## Saison 2006

21 Rennen, 542 Starts, 172 Ausfälle, davon 67 mechanisch (12.4 % der Starts), 5 Reifenschäden, 0 abgewürgt, 94 Unfälle, 6 ohne Grund.

### Rennen

| # | Runde | Strecke | Typ | Starter | Runden | Siegerzeit min | Ausfälle | davon mech. |
|---|---|---|---|---|---|---|---|---|
| 0 | 1 | Valencia | feature | 26 | 45 | 63.2 | 8 | 6 |
| 1 | 1 | Valencia | sprint | 26 | 28 | 38.7 | 10 | 6 |
| 2 | 2 | Imola | feature | 26 | 37 | 61.2 | 12 | 3 |
| 3 | 2 | Imola | sprint | 26 | 25 | 45.3 | 6 | 1 |
| 4 | 3 | Nürburgring | feature | 26 | 35 | 61.4 | 6 | 2 |
| 5 | 3 | Nürburgring | sprint | 26 | 24 | 41.3 | 6 | 5 |
| 6 | 4 | Catalunya | feature | 26 | 39 | 57.4 | 7 | 1 |
| 7 | 4 | Catalunya | sprint | 26 | 26 | 37.6 | 6 | 2 |
| 8 | 5 | Monaco | feature | 26 | 45 | 63.9 | 13 | 3 |
| 9 | 6 | Silverstone | feature | 26 | 36 | 60.9 | 11 | 5 |
| 10 | 6 | Silverstone | sprint | 23 | 26 | 37.5 | 5 | 1 |
| 11 | 7 | Magny-Cours | feature | 26 | 41 | 61.2 | 6 | 4 |
| 12 | 7 | Magny-Cours | sprint | 26 | 28 | 40.9 | 8 | 3 |
| 13 | 8 | Hockenheim | feature | 26 | 40 | 57.7 | 3 | 2 |
| 14 | 8 | Hockenheim | sprint | 26 | 27 | 38.6 | 8 | 3 |
| 15 | 9 | Hungaroring | feature | 26 | 42 | 65.2 | 10 | 3 |
| 16 | 9 | Hungaroring | sprint | 26 | 23 | 46.0 | 12 | 1 |
| 17 | 10 | Istanbul | feature | 26 | 34 | 56.0 | 9 | 8 |
| 18 | 10 | Istanbul | sprint | 26 | 23 | 37.9 | 7 | 3 |
| 19 | 11 | Monza | feature | 26 | 32 | 51.5 | 11 | 2 |
| 20 | 11 | Monza | sprint | 25 | 21 | 32.1 | 8 | 3 |

Mittlere Renndauer: Feature 60.0 min (11 Rennen, ohne Monaco 59.6 min), Sprint 39.6 min (10 Rennen).

### Ausfälle nach Kategorie

| Kategorie | Anzahl | pro 100 Starts | Feature | Sprint |
|---|---|---|---|---|
| ENGINE | 22 | 4.06 | 13 | 9 |
| GEARBOX | 27 | 4.98 | 17 | 10 |
| HYDRAULICS | 0 | 0.00 | 0 | 0 |
| ELECTRICS | 1 | 0.18 | 0 | 1 |
| BRAKES | 4 | 0.74 | 3 | 1 |
| SUSPENSION | 8 | 1.48 | 4 | 4 |
| COOLING | 2 | 0.37 | 2 | 0 |
| POWER_LOSS | 3 | 0.55 | 0 | 3 |
| PUNCTURE | 5 | 0.92 | 5 | 0 |
| STALL | 0 | 0.00 | 0 | 0 |
| ACCIDENT | 94 | 17.34 | 50 | 44 |
| UNKNOWN | 6 | 1.11 | 2 | 4 |
| **mechanisch gesamt** | **67** | **12.36** | 39 | 28 |

Mechanische Ausfälle je Start: Feature 39/286 = 13.6 %, Sprint 28/256 = 10.9 %.

### Teams

| Team | Key | Starts | mech. | Rate mech. | PUNCTURE | STALL | ACCIDENT | UNKNOWN | häufigster Defekt |
|---|---|---|---|---|---|---|---|---|---|
| FMS International | FMS | 42 | 9 | 21.4 % | 0 | 0 | 4 | 1 | GEARBOX 8, ENGINE 1 |
| BCN Competición | BCN | 42 | 8 | 19.0 % | 0 | 0 | 9 | 0 | GEARBOX 5, ENGINE 2 |
| Campos Racing | Campos | 42 | 8 | 19.0 % | 0 | 0 | 8 | 1 | GEARBOX 4, ENGINE 3 |
| Durango | Durango | 40 | 7 | 17.5 % | 1 | 0 | 5 | 2 | ENGINE 4, GEARBOX 3 |
| Trident Racing | Trident | 42 | 7 | 16.7 % | 2 | 0 | 10 | 0 | GEARBOX 3, SUSPENSION 3 |
| David Price Racing (2006: DPR Direxiv) | DPR | 42 | 6 | 14.3 % | 0 | 0 | 8 | 0 | ENGINE 2, SUSPENSION 2 |
| Super Nova International / Racing | SuperNova | 42 | 6 | 14.3 % | 0 | 0 | 8 | 1 | ENGINE 2, GEARBOX 2 |
| DAMS | DAMS | 41 | 4 | 9.8 % | 0 | 0 | 10 | 0 | ENGINE 4 |
| Arden International | Arden | 42 | 3 | 7.1 % | 1 | 0 | 9 | 0 | ENGINE 2, COOLING 1 |
| Racing Engineering | RacingEngineering | 42 | 3 | 7.1 % | 0 | 0 | 7 | 0 | ENGINE 1, SUSPENSION 1 |
| iSport International | iSport | 41 | 2 | 4.9 % | 0 | 0 | 7 | 0 | ENGINE 1, GEARBOX 1 |
| ART Grand Prix | ART | 42 | 2 | 4.8 % | 0 | 0 | 2 | 1 | GEARBOX 1, SUSPENSION 1 |
| Hitech Piquet Sports (2006: Piquet Sports) | Piquet | 42 | 2 | 4.8 % | 1 | 0 | 7 | 0 | SUSPENSION 1, POWER_LOSS 1 |

### Alle Ausfälle

| # | Rennen | Fahrer | Team | Status | Runden | Grund (Quelle) | Kategorie |
|---|---|---|---|---|---|---|---|
| 0 | Valencia F | Hiroki Yoshimoto | BCN | Ret | 27 | engine | ENGINE |
| 0 | Valencia F | Andreas Zuber | Trident | Ret | 23 | accident | ACCIDENT |
| 0 | Valencia F | Luca Filippi | FMS | Ret | 15 | gearbox | GEARBOX |
| 0 | Valencia F | Félix Porteiro | Campos | Ret | 7 | engine | ENGINE |
| 0 | Valencia F | Sergio Hernández | Durango | Ret | 4 | gearbox | GEARBOX |
| 0 | Valencia F | Tristan Gommendy | iSport | Ret | 2 | engine | ENGINE |
| 0 | Valencia F | Clivio Piccione | DPR | Ret | 1 | accident | ACCIDENT |
| 0 | Valencia F | Jason Tahincioğlu | FMS | DNS | 0 | gearbox, did not start (TD DNS; WP Ret 0 laps) | GEARBOX |
| 1 | Valencia S | Clivio Piccione | DPR | Ret | 24 | spin | ACCIDENT |
| 1 | Valencia S | Adrián Vallés | Campos | Ret | 23 | accident | ACCIDENT |
| 1 | Valencia S | Adam Carroll | RacingEngineering | Ret | 22 | accident | ACCIDENT |
| 1 | Valencia S | José María López | SuperNova | Ret | 22 | accident | ACCIDENT |
| 1 | Valencia S | Ferdinando Monfardini | DAMS | Ret | 5 | engine | ENGINE |
| 1 | Valencia S | Alexandre Prémat | ART | Ret | 3 | suspension | SUSPENSION |
| 1 | Valencia S | Luca Filippi | FMS | Ret | 0 | gearbox | GEARBOX |
| 1 | Valencia S | Félix Porteiro | Campos | Ret | 0 | engine | ENGINE |
| 1 | Valencia S | Jason Tahincioğlu | FMS | Ret | 0 | gearbox | GEARBOX |
| 1 | Valencia S | Sergio Hernández | Durango | Ret | 0 | clutch | GEARBOX |
| 2 | Imola F | Andreas Zuber | Trident | Ret | 30 | puncture | PUNCTURE |
| 2 | Imola F | Tristan Gommendy | iSport | Ret | 30 | accident | ACCIDENT |
| 2 | Imola F | Fairuz Fauzy | SuperNova | Ret | 29 | accident | ACCIDENT |
| 2 | Imola F | Adam Carroll | RacingEngineering | Ret | 26 | spin | ACCIDENT |
| 2 | Imola F | Jason Tahincioğlu | FMS | Ret | 25 | engine | ENGINE |
| 2 | Imola F | Sergio Hernández | Durango | Ret | 25 | WP "Retired" after 25 laps, TD no reason | UNKNOWN |
| 2 | Imola F | Alexandre Negrão | Piquet | Ret | 13 | accident | ACCIDENT |
| 2 | Imola F | Franck Perera | DAMS | Ret | 13 | accident | ACCIDENT |
| 2 | Imola F | Lucas di Grassi | Durango | Ret | 7 | accident | ACCIDENT |
| 2 | Imola F | Olivier Pla | DPR | Ret | 7 | accident | ACCIDENT |
| 2 | Imola F | José María López | SuperNova | Ret | 1 | gearbox (WP, TD); crash.net: hydraulic problems | GEARBOX |
| 2 | Imola F | Clivio Piccione | DPR | Ret | 0 | engine | ENGINE |
| 3 | Imola S | Jason Tahincioğlu | FMS | Ret | 19 | conflict: WP engine (lap 5) vs TD spin (lap 19) | UNKNOWN |
| 3 | Imola S | Gianmaria Bruni | Trident | Ret | 12 | brakes | BRAKES |
| 3 | Imola S | Michael Ammermüller | Arden | Ret | 1 | accident damage | ACCIDENT |
| 3 | Imola S | Alexandre Prémat | ART | Ret | 0 | accident | ACCIDENT |
| 3 | Imola S | Adrián Vallés | Campos | Ret | 0 | accident | ACCIDENT |
| 3 | Imola S | Lucas di Grassi | Durango | Ret | 0 | accident | ACCIDENT |
| 4 | Nürburgring F | Nelson Piquet Jr. | Piquet | Ret | 30 | puncture | PUNCTURE |
| 4 | Nürburgring F | Ferdinando Monfardini | DAMS | Ret | 29 | spin | ACCIDENT |
| 4 | Nürburgring F | Gianmaria Bruni | Trident | Ret | 18 | accident | ACCIDENT |
| 4 | Nürburgring F | Adrián Vallés | Campos | Ret | 18 | accident | ACCIDENT |
| 4 | Nürburgring F | Luca Filippi | FMS | Ret | 11 | gearbox | GEARBOX |
| 4 | Nürburgring F | Franck Perera | DAMS | Ret | 0 | engine | ENGINE |
| 5 | Nürburgring S | Timo Glock | BCN | Ret | 13 | electrics | ELECTRICS |
| 5 | Nürburgring S | Félix Porteiro | Campos | Ret | 11 | gearbox | GEARBOX |
| 5 | Nürburgring S | Luca Filippi | FMS | Ret | 6 | gearbox | GEARBOX |
| 5 | Nürburgring S | Olivier Pla | DPR | Ret | 5 | suspension | SUSPENSION |
| 5 | Nürburgring S | Sergio Hernández | Durango | Ret | 0 | engine | ENGINE |
| 5 | Nürburgring S | Andreas Zuber | Trident | Ret | 0 | accident | ACCIDENT |
| 6 | Catalunya F | Nicolas Lapierre | Arden | Ret | 34 | TD puncture; crash.net: tyres went off, pitted and retired; WP gearbox | PUNCTURE |
| 6 | Catalunya F | José María López | SuperNova | Ret | 22 | accident | ACCIDENT |
| 6 | Catalunya F | Gianmaria Bruni | Trident | Ret | 22 | accident | ACCIDENT |
| 6 | Catalunya F | Hiroki Yoshimoto | BCN | Ret | 20 | gearbox (TD); WP "Retired" | GEARBOX |
| 6 | Catalunya F | Andreas Zuber | Trident | Ret | 16 | left rear deflated (WP puncture, TD wheel, crash.net) | PUNCTURE |
| 6 | Catalunya F | Sergio Hernández | Durango | Ret | 16 | puncture (TD); WP "Retired" | PUNCTURE |
| 6 | Catalunya F | Fairuz Fauzy | SuperNova | Ret | 15 | spin (TD); WP "Retired" | ACCIDENT |
| 7 | Catalunya S | Nicolas Lapierre | Arden | Ret | 20 | engine | ENGINE |
| 7 | Catalunya S | Hiroki Yoshimoto | BCN | Ret | 16 | gearbox | GEARBOX |
| 7 | Catalunya S | Félix Porteiro | Campos | Ret | 12 | conflict: WP gearbox vs TD engine (mechanical in both) | UNKNOWN |
| 7 | Catalunya S | José María López | SuperNova | Ret | 8 | conflict: WP engine vs TD spin | UNKNOWN |
| 7 | Catalunya S | Franck Perera | DAMS | Ret | 0 | accident | ACCIDENT |
| 7 | Catalunya S | Clivio Piccione | DPR | Ret | 0 | accident | ACCIDENT |
| 8 | Monaco F | Adrián Vallés | Campos | Ret | 39 | brakes | BRAKES |
| 8 | Monaco F | Timo Glock | BCN | Ret | 36 | gearbox | GEARBOX |
| 8 | Monaco F | Hiroki Yoshimoto | BCN | Ret | 23 | accident | ACCIDENT |
| 8 | Monaco F | Ernesto Viso | iSport | Ret | 23 | accident damage | ACCIDENT |
| 8 | Monaco F | Jason Tahincioğlu | FMS | Ret | 12 | accident | ACCIDENT |
| 8 | Monaco F | Giorgio Pantano | FMS | Ret | 11 | accident | ACCIDENT |
| 8 | Monaco F | Olivier Pla | DPR | Ret | 2 | accident | ACCIDENT |
| 8 | Monaco F | Gianmaria Bruni | Trident | Ret | 0 | accident | ACCIDENT |
| 8 | Monaco F | Adam Carroll | RacingEngineering | Ret | 0 | engine | ENGINE |
| 8 | Monaco F | Javier Villa | RacingEngineering | Ret | 0 | accident | ACCIDENT |
| 8 | Monaco F | Nicolas Lapierre | Arden | Ret | 0 | accident | ACCIDENT |
| 8 | Monaco F | Tristan Gommendy | iSport | Ret | 0 | accident | ACCIDENT |
| 8 | Monaco F | Alexandre Negrão | Piquet | Ret | 0 | accident | ACCIDENT |
| 9 | Silverstone F | Andreas Zuber | Trident | Ret | 30 | spin | ACCIDENT |
| 9 | Silverstone F | Luca Filippi | BCN | Ret | 29 | gearbox | GEARBOX |
| 9 | Silverstone F | Gianmaria Bruni | Trident | Ret | 26 | gearbox | GEARBOX |
| 9 | Silverstone F | Hiroki Yoshimoto | BCN | Ret | 24 | gearbox | GEARBOX |
| 9 | Silverstone F | Ferdinando Monfardini | DAMS | Ret | 20 | accident | ACCIDENT |
| 9 | Silverstone F | Ernesto Viso | iSport | Ret | 18 | gearbox | GEARBOX |
| 9 | Silverstone F | Lucas di Grassi | Durango | Ret | 16 | "wing" (TD), unclear whether failure or contact damage | UNKNOWN |
| 9 | Silverstone F | Michael Ammermüller | Arden | Ret | 7 | radiator | COOLING |
| 9 | Silverstone F | Alexandre Negrão | Piquet | Ret | 1 | accident damage | ACCIDENT |
| 9 | Silverstone F | Franck Perera | DAMS | Ret | 0 | spin | ACCIDENT |
| 9 | Silverstone F | José María López | SuperNova | Ret | 0 | accident | ACCIDENT |
| 10 | Silverstone S | Adrián Vallés | Campos | Ret | 13 | gearbox | GEARBOX |
| 10 | Silverstone S | Neel Jani | Arden | Ret | 5 | accident | ACCIDENT |
| 10 | Silverstone S | Michael Ammermüller | Arden | Ret | 5 | accident | ACCIDENT |
| 10 | Silverstone S | Alexandre Prémat | ART | Ret | 2 | "driver gave up" (TD), no further detail | UNKNOWN |
| 10 | Silverstone S | Andreas Zuber | Trident | Ret | 0 | accident | ACCIDENT |
| 11 | Magny-Cours F | Franck Perera | DAMS | Ret | 34 | engine | ENGINE |
| 11 | Magny-Cours F | Jason Tahincioğlu | FMS | Ret | 16 | gearbox | GEARBOX |
| 11 | Magny-Cours F | Fairuz Fauzy | SuperNova | Ret | 4 | gearbox | GEARBOX |
| 11 | Magny-Cours F | Gianmaria Bruni | Trident | Ret | 1 | clutch | GEARBOX |
| 11 | Magny-Cours F | Luca Filippi | BCN | Ret | 1 | accident | ACCIDENT |
| 11 | Magny-Cours F | Andreas Zuber | Trident | Ret | 1 | accident | ACCIDENT |
| 12 | Magny-Cours S | Gianmaria Bruni | Trident | Ret | 23 | gearbox | GEARBOX |
| 12 | Magny-Cours S | Luca Filippi | BCN | Ret | 18 | spin | ACCIDENT |
| 12 | Magny-Cours S | Clivio Piccione | DPR | Ret | 16 | suspension | SUSPENSION |
| 12 | Magny-Cours S | José María López | SuperNova | Ret | 3 | engine | ENGINE |
| 12 | Magny-Cours S | Alexandre Negrão | Piquet | Ret | 2 | accident damage | ACCIDENT |
| 12 | Magny-Cours S | Ferdinando Monfardini | DAMS | Ret | 0 | accident | ACCIDENT |
| 12 | Magny-Cours S | Hiroki Yoshimoto | BCN | Ret | 0 | accident | ACCIDENT |
| 12 | Magny-Cours S | Ernesto Viso | iSport | Ret | 0 | accident | ACCIDENT |
| 13 | Hockenheim F | Andreas Zuber | Trident | Ret | 1 | steering | SUSPENSION |
| 13 | Hockenheim F | Ferdinando Monfardini | DAMS | Ret | 0 | spin | ACCIDENT |
| 13 | Hockenheim F | Lucas di Grassi | Durango | DNS | 0 | engine, did not start (TD DNS; WP Ret 0 laps) | ENGINE |
| 14 | Hockenheim S | Sergio Hernández | Durango | Ret | 22 | engine | ENGINE |
| 14 | Hockenheim S | Michael Ammermüller | Arden | Ret | 20 | accident | ACCIDENT |
| 14 | Hockenheim S | Adrián Vallés | Campos | Ret | 20 | accident | ACCIDENT |
| 14 | Hockenheim S | Lucas di Grassi | Durango | Ret | 14 | engine | ENGINE |
| 14 | Hockenheim S | Hiroki Yoshimoto | BCN | Ret | 9 | accident | ACCIDENT |
| 14 | Hockenheim S | Alexandre Prémat | ART | Ret | 9 | accident | ACCIDENT |
| 14 | Hockenheim S | Clivio Piccione | DPR | Ret | 0 | accident | ACCIDENT |
| 14 | Hockenheim S | Nelson Piquet Jr. | Piquet | DNS | 0 | throttle, did not start (TD) | POWER_LOSS |
| 15 | Hungaroring F | Adrián Vallés | Campos | Ret | 26 | accident | ACCIDENT |
| 15 | Hungaroring F | Gianmaria Bruni | Trident | Ret | 25 | suspension | SUSPENSION |
| 15 | Hungaroring F | Sergio Hernández | Durango | Ret | 25 | spin | ACCIDENT |
| 15 | Hungaroring F | Jason Tahincioğlu | FMS | Ret | 22 | accident | ACCIDENT |
| 15 | Hungaroring F | Hiroki Yoshimoto | BCN | Ret | 17 | accident | ACCIDENT |
| 15 | Hungaroring F | Nicolas Lapierre | Arden | Ret | 17 | accident | ACCIDENT |
| 15 | Hungaroring F | Javier Villa | RacingEngineering | Ret | 16 | accident | ACCIDENT |
| 15 | Hungaroring F | Félix Porteiro | Campos | Ret | 16 | accident | ACCIDENT |
| 15 | Hungaroring F | Clivio Piccione | DPR | Ret | 7 | engine | ENGINE |
| 15 | Hungaroring F | Michael Ammermüller | Arden | Ret | 0 | engine | ENGINE |
| 16 | Hungaroring S | Javier Villa | RacingEngineering | Ret | 21 | accident | ACCIDENT |
| 16 | Hungaroring S | Hiroki Yoshimoto | BCN | Ret | 18 | accident | ACCIDENT |
| 16 | Hungaroring S | Sergio Hernández | Durango | Ret | 17 | accident | ACCIDENT |
| 16 | Hungaroring S | Nicolas Lapierre | Arden | Ret | 12 | spin | ACCIDENT |
| 16 | Hungaroring S | Adam Carroll | RacingEngineering | Ret | 12 | accident damage | ACCIDENT |
| 16 | Hungaroring S | Lucas di Grassi | Durango | Ret | 10 | accident | ACCIDENT |
| 16 | Hungaroring S | Franck Perera | DAMS | Ret | 8 | accident | ACCIDENT |
| 16 | Hungaroring S | Fairuz Fauzy | SuperNova | Ret | 7 | accident | ACCIDENT |
| 16 | Hungaroring S | Clivio Piccione | DPR | Ret | 5 | accident | ACCIDENT |
| 16 | Hungaroring S | Alexandre Negrão | Piquet | Ret | 4 | accident | ACCIDENT |
| 16 | Hungaroring S | José María López | SuperNova | Ret | 4 | throttle | POWER_LOSS |
| 16 | Hungaroring S | Luca Filippi | BCN | Ret | 4 | accident | ACCIDENT |
| 17 | Istanbul F | Ferdinando Monfardini | DAMS | Ret | 32 | engine | ENGINE |
| 17 | Istanbul F | Félix Porteiro | Campos | Ret | 30 | gearbox | GEARBOX |
| 17 | Istanbul F | Hiroki Yoshimoto | BCN | Ret | 27 | engine | ENGINE |
| 17 | Istanbul F | Giorgio Pantano | FMS | Ret | 13 | gearbox | GEARBOX |
| 17 | Istanbul F | Clivio Piccione | DPR | Ret | 11 | brakes | BRAKES |
| 17 | Istanbul F | Adrián Vallés | Campos | Ret | 9 | gearbox | GEARBOX |
| 17 | Istanbul F | Ernesto Viso | iSport | Ret | 9 | spin | ACCIDENT |
| 17 | Istanbul F | Fairuz Fauzy | SuperNova | Ret | 8 | brakes | BRAKES |
| 17 | Istanbul F | Gianmaria Bruni | Trident | Ret | 6 | wheel fell off | SUSPENSION |
| 18 | Istanbul S | Félix Porteiro | Campos | Ret | 3 | engine | ENGINE |
| 18 | Istanbul S | Alexandre Negrão | Piquet | Ret | 2 | steering | SUSPENSION |
| 18 | Istanbul S | Fairuz Fauzy | SuperNova | Ret | 2 | engine | ENGINE |
| 18 | Istanbul S | Luca Filippi | BCN | Ret | 0 | accident | ACCIDENT |
| 18 | Istanbul S | Clivio Piccione | DPR | Ret | 0 | accident | ACCIDENT |
| 18 | Istanbul S | Giorgio Pantano | FMS | Ret | 0 | accident | ACCIDENT |
| 18 | Istanbul S | Michael Ammermüller | Arden | Ret | 0 | accident | ACCIDENT |
| 19 | Monza F | José María López | SuperNova | Ret | 19 | accident damage | ACCIDENT |
| 19 | Monza F | Vitaly Petrov | DPR | Ret | 18 | lost water | COOLING |
| 19 | Monza F | Timo Glock | iSport | Ret | 17 | accident | ACCIDENT |
| 19 | Monza F | Adrián Vallés | Campos | Ret | 17 | accident | ACCIDENT |
| 19 | Monza F | Gianmaria Bruni | Trident | Ret | 15 | accident | ACCIDENT |
| 19 | Monza F | Ferdinando Monfardini | DAMS | Ret | 15 | accident | ACCIDENT |
| 19 | Monza F | Adam Carroll | RacingEngineering | Ret | 10 | lost wheel | SUSPENSION |
| 19 | Monza F | Félix Porteiro | Campos | Ret | 8 | accident | ACCIDENT |
| 19 | Monza F | Ernesto Viso | iSport | Ret | 0 | accident | ACCIDENT |
| 19 | Monza F | Alexandre Negrão | Piquet | Ret | 0 | accident | ACCIDENT |
| 19 | Monza F | Andreas Zuber | Trident | Ret | 0 | accident | ACCIDENT |
| 20 | Monza S | José María López | SuperNova | Ret | 17 | accident | ACCIDENT |
| 20 | Monza S | Alexandre Prémat | ART | Ret | 15 | gearbox | GEARBOX |
| 20 | Monza S | Sergio Hernández | Durango | Ret | 12 | gearbox | GEARBOX |
| 20 | Monza S | Adam Carroll | RacingEngineering | Ret | 5 | accident | ACCIDENT |
| 20 | Monza S | Alexandre Negrão | Piquet | Ret | 4 | accident | ACCIDENT |
| 20 | Monza S | Ferdinando Monfardini | DAMS | Ret | 4 | accident | ACCIDENT |
| 20 | Monza S | Michael Ammermüller | Arden | Ret | 2 | accident | ACCIDENT |
| 20 | Monza S | Javier Villa | RacingEngineering | Ret | 1 | throttle | POWER_LOSS |

Nicht als Start oder nicht als Ausfall gezählt:

- 2006 race 20 Timo Glock: DNS injured - sprained wrist
- 2006 race 10 Ferdinando Monfardini: DNS Silverstone Sprint (WP DNS, Grund nicht belegt, vermutlich Folge seines schweren Unfalls im Feature), nicht gezählt
- 2006 race 10 Lucas di Grassi, Sergio Hernández: vom Silverstone-Sprint ausgeschlossen (WP "Excluded", Hernández war im Feature wegen eines illegal veränderten Flügels disqualifiziert worden, Zusammenhang nicht belegt), nicht gezählt

## Abdeckung und Qualität

- Klassemente (Starter, Runden, Siegerzeit) sind vollständig: Wikipedia und teamdan stimmen bis auf Einzelfälle überein, die Abweichungen sind oben in den Gründen vermerkt.
- Gründe: 2005 sind von 147 Ausfällen 143 belegt, 4 UNKNOWN (alle Fälle, in denen WP "Ret" und TD "nicht klassiert" ohne Grund führt). 2006 sind von 172 Ausfällen 166 belegt, 6 UNKNOWN (davon 3 Widersprüche zwischen den Quellen, 1 davon sicher mechanisch).
- Fast alle Gründe stammen aus einer Quelle (teamdan, zeitgenössische Fan-Datenbank nach den offiziellen GP2-Ergebnislisten). Wo Wikipedia 2006 eigene Gründe nennt, stimmen sie in 53 von 57 Fällen mit teamdan überein (die 4 Abweichungen sind oben als UNKNOWN oder mit Begründung vermerkt).
- Bekannte Unschärfe: teamdan nennt "spin" auch bei Drehern nach Defekt; "accident damage" kann aus einer frühen Berührung stammen. Die Unfallzahl ist deshalb eher eine Obergrenze, die Mechanik-Zahl eher eine Untergrenze.
- Sonderfall Imola 2005: die Carbonbremsen des Einheitsautos versagten reihenweise (9 Bremsausfälle plus Viso DNS wegen Bremse in einem Wochenende). Das ist ein Debüt-Effekt und sollte für ein Saisonprofil eher gedämpft werden. Ohne Imola: 2005 3 statt 13 Bremsausfälle.
- Silverstone 2005 Sprint: drei Motorschäden vor dem Start (López, Fauzy, Yoshimoto). WP führt sie als DNS, TD als "0 laps/engine". Gezählt als Start mit ENGINE-Ausfall.
- Teams 2006: Coloni fehlt (sein Startplatz lief als FMS International), Petrol Ofisi war Sponsor von FMS, kein eigenes Team. DPR fuhr 2006 als DPR Direxiv, Hitech Piquet Sports als Piquet Sports.
