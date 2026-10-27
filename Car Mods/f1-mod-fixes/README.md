# F1-Mod-Fixes (Cimmerian Iter 2007 bis 2013, The Race Project 2009)

## Ziel

Gekaufte F1-Mods so angleichen, dass alle Autos eines Jahrgangs dieselbe physikalische Grundlage haben: Gewicht, KI-Werte, verbotene Fahrhilfen, defekte Dateien. Die Reihenfolge der Teams kommt danach ausschließlich über Ballast, Restrictor und KI-Level im Content-Manager-Grid (siehe [grids.md](grids.md)).

Regel, die sich bewährt hat:

| Ebene | Wofür |
|---|---|
| Physik-Dateien | Fehler und Ausreißer korrigieren, nicht die Reihenfolge |
| KI-Werte (`ai.ini`) | sauberes, realistisches Fahren, einheitlich pro Jahrgang |
| Grid (Ballast, Restrictor, KI-Level) | Abstände und Reihenfolge |

## Installation und Wiederherstellen

Die Mods selbst (`.acd`, `.kn5`, Sounds) liegen nicht im Repo. Nach einer Neuinstallation oder einem Mod-Update die Schritte unten mit den Skripten in `tools/` erneut anwenden. Jedes Skript zeigt ohne `--apply` nur an, was es ändern würde, und legt beim ersten Schreiben eine Sicherung an (`data.acd.bak`, `<datei>.bak`, `data_vor_transplantation/`).

```
cd "Car Mods/f1-mod-fixes/tools"
py -3.11 acdini.py --ac "E:/SteamLibrary/steamapps/common/assettocorsa" --prefix cim_2010_ --file car.ini --section BASIC --key TOTALMASS --value 620 --apply
```

| Skript | Zweck |
|---|---|
| `acdini.py` | beliebigen INI-Wert in `data.acd` oder `data/` lesen und setzen, für viele Autos auf einmal |
| `transplant.py` | Physik, Fahrwerk und Kollisionskörper eines Spenders übernehmen, Modell und Geometrie bleiben |
| `sound_tausch.py` | Sound-Bank eines anderen Autos einsetzen, Pfade in `GUIDs.txt` umschreiben, `[AUDIO_VOLUME]` |
| `auswertung.py` | Quali aus `race_out.json` auswerten, nur echte Runden, optional gegen `data/real_*.json` |

`Gameplay Mods/mechanical-failures/tools/patch_ai_ini.py` setzt einzelne KI-Werte (älteres Werkzeug, gleiches Ergebnis wie `acdini.py --file ai.ini`).

## Was geändert ist

### Alle Jahrgänge

- KI-Hinweise waren bei Cimmerian sehr vorsichtig (Bremse 0.75, Aero 0.75 bzw. 0.7): Die KI bremste viel zu früh.
- Gewicht: Cimmerian staffelt das Gewicht pro Team. Das ist eine versteckte Rangfolge, ersetzt durch das echte Mindestgewicht des Jahres. Abgestuft wird über den Grid.

### Trägheit (`car.ini [BASIC] INERTIA`)

Maße des Quaders, aus dem AC die Trägheit rechnet. Ein kleinerer Quader macht das Auto um die Hochachse nervös, die KI korrigiert ständig und wird langsamer. Ausreißer auf den Jahrgangsstandard gesetzt:

| Jahrgang | Autos | vorher | jetzt |
|---|---|---|---|
| 2010 | Red Bull | 1.38,1.1,3.42 | 1.6,0.75,4.1 |
| 2013 | Caterham | 1.5,0.8,3.5 | 1.6,0.7,4.1 |
| 2009 TRP | Ferrari, McLaren, Red Bull, Toro Rosso, Renault, Force India | 1.38,1.1,3.42 | 1.6,0.7,4.1 (wie BMW, Brawn, Toyota, Williams, Kunos F138) |

2007 hat bei allen Autos 1.38,1.1,3.42 und bleibt so (einheitlich).

### Lenkung (`car.ini [CONTROLS]`)

Die KI gibt bei allen Autos dieselbe Lenkeingabe. Bei kleinerer Lenkübersetzung schlagen die Räder weiter ein, die KI lenkt über den Schräglauf hinaus und schiebt (beobachtet beim Red Bull 2010 in der letzten Kurve Shanghai: voller Einschlag, rutscht über die Strecke).

| Auto | vorher (Lock / Ratio / Rod / Assist) | jetzt |
|---|---|---|
| Red Bull 2010 | 250 / **12** / 0.00083 / 1 | 250 / 15 / 0.0017 / 0.760 wie alle 2010er |
| Renault 2009 | 225 / **12** / 0.00083 / 1 | 225 / 15 / 0.0017 / 0.760 |
| Force India 2009 | **420 / 16** / 0.0008 | 250 / 15 / 0.0017 (vorher bis 26° Radeinschlag) |
| Williams 2009 | 250 / 15 / **0.0007** | 250 / 15 / 0.0017 |

Einheitlich je Jahrgang sind 2006, 2008, 2012 (230/15), 2007 (225/12), 2011 und 2013 (250/13).

### Cimmerian 2006 (11 Autos)

Gewicht 605–625 auf 605. Die Reifen bleiben: Michelin (BMW, Honda, McLaren, Red Bull, Renault, Toro Rosso) und Bridgestone (Ferrari, Midland, Super Aguri, Toyota, Williams) sind der Reifenkrieg von 2006, Michelin etwas griffiger (`DY_REF` 1.75 gegen 1.73).

### Cimmerian 2007 (11 Autos)

| Wert | vorher | jetzt |
|---|---|---|
| `TOTALMASS` | BMW 605, alle anderen 680 (Fahrer doppelt) | 605 |
| `GASGAIN` / `BRAKE_HINT` / `AERO_HINT` / `TRAIL_HINT` | 0.80 / 0.75 / 0.75 / 0–1 | 0.92 / 0.97 / 1.0 / 1 |
| `LOOKAHEAD BASE` | 18 | 17 |

`cim_2007_honda_V2`: `data.acd` ist mit `cim_2007_honda_v2` (klein) verschlüsselt, ältere Werkzeuge konnten sie deshalb nicht lesen.

### Cimmerian 2008 (11 Autos)

Wie 2007: Gewicht 606–645 auf 605, KI 0.92 / 0.97 / 1.0 / 1, Lookahead 17.

### Cimmerian 2010 (17 Autos inkl. `_cod`, `_s2`)

| Wert | vorher | jetzt |
|---|---|---|
| `TOTALMASS` | 620–647 gestaffelt | 620 |
| `GASGAIN` / `BRAKE_HINT` | 0.2 / 0.97 (0.93 Williams) | 0.4 / 0.96 |
| `UP` / `DOWN` | 17850 / 84 | 17700 / 90 (DOWN ist im Format v4 ein Prozentwert von UP) |

Red Bull und Red Bull `_cod`: Diffusor-`CL_GAIN` (`WING_4` bis `WING_6`) +15 % (0.463/0.506 → 0.532/0.582), Luftwiderstand unverändert. Schätzung für den angeblasenen Diffusor des RB6. Cimmerian gab ihm nur etwa 1 % mehr Abtrieb als McLaren bei 2,7 % weniger Leistung, die KI landete hinter Mercedes und Sauber.

**Teamstärke über das Autokonzept (2026-10-27):** Alle `CL_GAIN` je Auto mit einem Faktor gegenüber Cimmerian skaliert, sodass der Abtrieb-Rückstand zum Red Bull (geschätzt mit 0,13 s pro Prozent, Motorleistung nach Cimmerian) dem Quali-Abstand im Saisonschnitt 2010 entspricht. Grid danach ohne Ballast.

Nach dem Test in Barcelona (15 min, Grid 0 / 0) nachgestellt: ein Prozent Abtrieb kostet dort etwa 0,11 s, nicht 0,13 s.

| Team | Faktor auf CL gegenüber Cimmerian | Abtrieb zu Red Bull (200 km/h) | Sonstiges |
|---|---|---|---|
| Red Bull | Diffusor ×1.15 | 0 | Balance vorn 46,4 % (andere 47,5–48 %) |
| Renault | 1.0014 | −8 % | |
| Ferrari | 0.9813 | −9 % | |
| Mercedes | 0.9860 | −9 % | |
| Williams (`_s2`) | 0.9862 | −10 % | `cim_2010_williams` hat ein anderes Aero-Modell, gleicher Faktor |
| McLaren | 0.9663 | −10 % | Heckflügel-CD ×0.94 (F-Schacht) |
| Sauber | 0.9603 | −13 % | |
| Force India | 0.9434 | −14 % | alle CD ×0.96 |
| Toro Rosso | 0.9314 | −16 % | |
| Lotus | 0.8347 | −25 % | |
| Virgin | 0.7842 | −31 % | |
| HRT | 0.7455 | −34 % | |

Ergebnis vor dem Nachstellen (Abstand zu Red Bull, Ziel Saisonschnitt): McLaren +0.19 (Ziel +0.6), Ferrari +0.27 (+0.6), Renault +0.83 (+1.0), Force India +0.94 (+1.3), Mercedes +1.03 (+0.9), Williams +1.10 (+1.3), Toro Rosso +1.30 (+1.6), Sauber +1.42 (+1.5), Lotus +2.43 (+3.0), Virgin +2.75 (+3.6), HRT +3.85 (+4.3).

**Motorleistung (2026-10-27):** `power.lut` gleichmäßig skaliert (Form der Kurve bleibt), Spitzenleistung aus `power.lut` gerechnet. Cimmerian lag bei 671 bis 713 PS, real 2010 rund 750 PS. Ziel (Schätzungen, keine offiziellen Werte): Mercedes 755 PS (Analyse 2009, [motorsport.com](https://www.motorsport.com/f1/news/analysis-of-f1-engine-performance-in-2009/3217681/)), Ferrari 750 PS ([Wikipedia Ferrari F10](https://en.wikipedia.org/wiki/Ferrari_F10)), Cosworth 745 PS (Cosworth nannte rund 770, aber Verbrauch und Fahrbarkeit schwächer), Renault 740 PS (galt als schwächster Motor, Abstand bester zu schlechtestem Motor unter 2,5 %).

| Motor | Teams | vorher | jetzt |
|---|---|---|---|
| Mercedes | Mercedes, McLaren, Force India | 713 PS | 755 PS (×1.059) |
| Ferrari | Ferrari, Sauber, Toro Rosso | 708 PS | 750 PS (×1.060) |
| Cosworth | Williams, Lotus, Virgin, HRT | 671 PS | 745 PS (×1.111) |
| Renault | Red Bull, Renault | 692 PS | 740 PS (×1.069) |

Die Abtrieb-Faktoren oben wurden noch mit Cosworth −3 % und Renault −2,8 % gerechnet. Mit den neuen Werten sind die Cosworth-Teams etwa 0,15 s, Red Bull und Renault etwa 0,1 s schneller als dort angenommen (Schätzung, kleiner als die Unsicherheit der Abtrieb-Rechnung).

Bremse 0.97 gab Blockierer, 0.94 kostete die KI fast eine Sekunde, 0.96 ist der Kompromiss. Topspeed in Barcelona rund 307 km/h, nicht übersetzungsbegrenzt (330 km/h am Begrenzer).

### Cimmerian 2011 bis 2013

| Wert | vorher | jetzt |
|---|---|---|
| `GASGAIN` | 0.2 | 0.3 |
| `BRAKE_HINT` / `AERO_HINT` 2011, 2013, Williams 2010 | 0.75 / 0.7 | 0.97 / 1.0 |
| `DOWN` 2013 | 80 | 85 |
| 2013 `suspensions.ini [REAR] BASEY` | −0.03 bis 0.08 je Team | 0.02 für alle |
| 2013 `[FRONT] BASEY` | 0.10 bis 0.13 | 0.10 |
| 2011 `BASEY` vorn / hinten | 0.02–0.08 / −0.02–0.04 | 0.06 / 0.02 |
| Gewicht 2012 / 2013 | 640–745 (HRT) / 642–655 | 640 / 642 (2011 war schon 640) |
| 2013 Mercedes `colliders.ini GROUND_ENABLE` | 0 | 1 wie alle anderen 2013er |

BASEY hinten entscheidet über die Höhe des Diffusors, dessen Kennlinie unter etwa 4 cm stark einbricht: Der Red Bull 2013 war mit −0.03 über eine Sekunde zu langsam, mit 0.02 holte er Pole.

Sounds 2013: Die Banks von Mercedes, McLaren, Force India, Lotus, Williams und Caterham hatten nur 30 Samples ohne Namen und keinen Innen-Sound. Sie bekommen die 2012er Bank desselben Teams (`sound_tausch.py`, `--int 4.9 --ext 1.0`). Ferrari, Sauber und Toro Rosso behalten ihr Original.

### The Race Project 2009 (`f1_2009_*`, offene data-Ordner)

| Problem | Lösung |
|---|---|
| Renault, Williams, Force India stammen physikalisch aus einem anderen Projekt (andere Reifen, Aero, Getriebe, Renault 845 PS) | Transplantation: Renault ← Red Bull, Williams ← Toyota, Force India ← Red Bull |
| Drei Fahrwerksgruppen (Federn, Stabis, Fahrhöhe), die Pace folgte fast nur der Gruppe | alle bekommen `suspensions.ini` und `setup.ini` des BMW (Gruppe A), Geometrie bleibt |
| Force India, Williams, Brawn, Ferrari: Kollisionskörper mit Bodenkontakt, Force India blieb in der Box hängen | alle mit `colliders.ini` des BMW (ein Körper, `GROUND_ENABLE=0`) |
| Kleinere Reifen (0.311) bei Renault und Force India: Autos lagen zu tief und blieben hängen | Spender-Reifen 0.320 |
| Traktionskontrolle bei Brawn, McLaren, Red Bull, Toro Rosso, Renault (2009 verboten) | `PRESENT=0` |
| Brawn: eigene Aero (Diffusor 0.35), +10 % Leistung, ohne TC Abflüge auf der Out-Lap | Aero, Leistung, Übersetzung, Fahrwerk vom BMW, dann Diffusor-`CL_GAIN` 0.5 → 0.575 (Doppeldiffusor, Schätzung) |
| Gewicht 585 bis 610 kg | 605 |
| McLaren ohne KERS (fuhr 2009 damit) | `kers.ini` und `kers_torque.lut` vom Ferrari (60 kW, 400 kJ) |
| Force India, Renault, Williams ohne `fuel_cons.ini`: RARE tankte sie voll (Division durch 0) | Datei vom Toyota |
| KI | `GASGAIN 0.4`, `BRAKE_HINT 0.94`, `UP 17700`, `DOWN 90`, `AERO_HINT 1.0`, Lookahead 17 |

Brawn-Diffusor nachbauen: `acdini.py --cars f1_2009_BrawnGP_001 --file aero.ini --section WING_4 --key CL_GAIN --value 0.575 --apply`, ebenso `WING_5` und `WING_6`.

## Erkenntnisse zum Testen

- **AC rechnet beim vorzeitigen Verlassen hoch** und kopiert Runden an Fahrer ohne eigene Zeit. `auswertung.py` filtert beides.
- **RARE** (`apps/lua/RARE`) setzt die KI in der Quali auf 100 % (Fahrerstärken wirken nur im Rennen), tankt 3,5 Runden aus `fuel_cons.ini` und staffelt die Out-Laps. Ohne RARE fahren alle gleichzeitig los, das gab Massencrashs.
- **Strecke:** Nur Kunos-Strecken zum Abstimmen. Die Melbourne-Mod hat eine schwache KI-Linie (KI rund 1 bis 3 s langsamer als der Spieler), Spa hat ein Problem in Kurve 14.
- **Kosten einer Stufe** (10 kg + 1 %): grob 0,35 bis 0,7 s je nach Auto und Strecke, für Barcelona etwa 0,45 bis 0,5 s.

## Status

Angewendet und im Spiel getestet (Stand 2026-10-27). Grids für 2009 und 2010 abgestimmt in Barcelona, 2007 in Silverstone, 2013 in Melbourne. Nächster Schritt: Grids für 2011 und 2012, Gewichte 2011 bis 2013 prüfen.
