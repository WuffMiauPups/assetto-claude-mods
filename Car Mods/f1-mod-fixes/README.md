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
| `topspeed.py` | Topspeed je Auto aus Luftwiderstand, `power.lut` und letztem Gang rechnen |
| `quali_abstaende.py` | echte Quali-Abstände je Team einer Saison (Median, aus api.jolpi.ca) |
| `saison_stufen.py` | Abtrieb aller Autos auf die Werte einer Saisonphase setzen, Plan in `data/stufen_*.json` |

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

**Teamstärke über das Autokonzept (2026-11-08, im Spiel noch nicht getestet):** Methode wie 2010, Grid danach 0 / 0. Ziel ist der echte Saisonabstand aus `tools/quali_abstaende.py 2008`. Der Abtrieb-Rückstand zum Ferrari ergibt sich aus dem Abstand abzüglich Motor (0,095 s pro Prozent Leistung, Schätzung) und Luftwiderstand (0,04 s pro Prozent, Schätzung), geteilt durch 0,12 s pro Prozent Abtrieb (aus den 2010er Barcelona-Tests). `power.lut` gleichmäßig skaliert, alle `CL_GAIN` mit demselben Faktor, die Balance bleibt.

| Team | Abstand real (s) | Motor (PS, Schätzung) | Faktor `power.lut` | Faktor `CL_GAIN` | Abtrieb 200 km/h |
|---|---|---|---|---|---|
| Ferrari | 0.00 | 770 | 1.0886 | 1.000 | 662 kg |
| McLaren | +0.03 | 775 | 1.0878 | 0.995 | 659 kg |
| BMW | +0.47 | 770 | 1.0808 | 0.969 | 637 kg |
| Toyota | +0.50 | 750 | 1.0681 | 0.996 | 651 kg |
| Renault | +0.60 | 740 | 1.0690 | 0.992 | 652 kg |
| Red Bull | +0.66 | 740 | 1.0690 | 0.994 | 651 kg |
| Toro Rosso | +0.71 | 770 | 1.0886 | 0.959 | 628 kg |
| Williams | +0.88 | 750 | 1.0681 | 0.972 | 632 kg |
| Honda | +1.07 | 735 | 1.0730 | 0.965 | 630 kg |
| Force India | +1.95 | 770 | 1.0886 | 0.853 (nach dem ersten Test ×0.97) | 544 kg |
| Super Aguri | +2.49 | 735 | 1.0730 | 0.871 | 555 kg |

Motorleistung: keine offiziellen Zahlen, Quellen widersprechen sich ([f1technical](https://www.f1technical.net/forum/viewtopic.php?p=81608), [team-bhp](https://www.team-bhp.com/forum/intl-motorsport/74232-f1-engine.html), [grandprix.com](https://www.grandprix.com/ns/ns21079.html), [auto123](https://www.auto123.com/en/news/amp/f1-mercedes-benzs-advantage-is-25-horsepower-report/3966/)). Am unsichersten ist Honda. Cimmerian lag bei 685 bis 712 PS.

| Wert | vorher | jetzt |
|---|---|---|
| `electronics.ini` `[TRACTION_CONTROL]` `PRESENT` / `ACTIVE` | 1 / 1 | 0 / 0 (TC war 2008 verboten) |
| `ai.ini` `UP` | 17800 | 18600 (beste Hochschaltdrehzahl gerechnet 18450 bis 18825) |
| `ai.ini` `DOWN` | 14500 | 16000 (Format v3, Drehzahl; 16000 × größte Gangstufe 1.188 ≈ Begrenzer 19000) |

Ferrari und McLaren sind bei Reifen, Bremsen, Getriebe, KI und Fahrwerk identisch, es unterscheiden sich nur 6 cm Radstand, 0,7 % Leistung und minimale Aero-Werte. Für die 1,7 s aus dem alten Silverstone-Test gibt es keine physikalische Ursache, der Ferrari bekommt deshalb keinen Extra-Malus.

Erster Test (Melbourne, 10 min, Grid 0 / 0, 1 bis 5 gezeitete Runden je Fahrer): schnellste KI 1:25.520 gegen die echte Bestzeit aus Q1/Q2 von 1:25.187, die meisten Teams bis auf 0,2 s beim echten Abstand zur Spitze. Force India lag 0,8 s zu nah an der Spitze und bekam `CL_GAIN` ×0.97 (561 → 544 kg, etwa 0,35 s). Er hat damit weniger Abtrieb als Super Aguri (555 kg), aber 35 PS mehr. Einzelne langsame Zeiten kamen laut Nutzer von Schäden, Ferrari bleibt unverändert.

### Cimmerian 2010 (17 Autos inkl. `_cod`, `_s2`)

| Wert | vorher | jetzt |
|---|---|---|
| `TOTALMASS` | 620–647 gestaffelt | 620 |
| `GASGAIN` / `BRAKE_HINT` | 0.2 / 0.97 (0.93 Williams) | 0.4 / 0.96 |
| `UP` / `DOWN` | 17850 / 84 | 17700 / 90 (DOWN ist im Format v4 ein Prozentwert von UP) |

Red Bull und Red Bull `_cod`: Diffusor-`CL_GAIN` (`WING_4` bis `WING_6`) +15 % (0.463/0.506 → 0.532/0.582), Luftwiderstand unverändert. Schätzung für den angeblasenen Diffusor des RB6. Cimmerian gab ihm nur etwa 1 % mehr Abtrieb als McLaren bei 2,7 % weniger Leistung, die KI landete hinter Mercedes und Sauber.

**Teamstärke über das Autokonzept (2026-10-27):** Alle `CL_GAIN` je Auto mit einem Faktor gegenüber Cimmerian skaliert, sodass der Abtrieb-Rückstand zum Red Bull (geschätzt mit 0,13 s pro Prozent, Motorleistung nach Cimmerian) dem Quali-Abstand im Saisonschnitt 2010 entspricht. Grid danach ohne Ballast.

Nach dem Test in Barcelona (15 min, Grid 0 / 0) nachgestellt: ein Prozent Abtrieb kostet dort etwa 0,11 s, nicht 0,13 s.

Nach dem zweiten Barcelona-Test nochmals nachgestellt: Sauber, Force India, Williams, Toro Rosso ×0.96, McLaren ×0.97 (das Mittelfeld lag in beiden Sessions etwa 0,5 s zu nah an Red Bull). Zwischen zwei 15-Minuten-Sessions schwanken unveränderte Teams um bis zu 1 s, deshalb nur auf Abweichungen reagieren, die in mehreren Sessions gleich sind.

| Team | Faktor auf CL gegenüber Cimmerian | Abtrieb zu Red Bull (200 km/h) | Sonstiges |
|---|---|---|---|
| Red Bull | Diffusor ×1.15, danach alles ×1.02 (gesamt 1.089) | 0 | Balance vorn 46,4 % (andere 47,5–48 %) |
| Renault | 0.9714 | −12 % | nach dem vierten Test ×0.97 |
| Ferrari | 0.9813 | −11 % | |
| Mercedes | 0.9470 | −14 % | nach dem dritten Test ×0.98, am 2026-11-04 nochmals ×0.98 |
| McLaren | 0.9232 | −16 % | Heckflügel-CD ×0.81 (F-Schacht), 7. Gang 1.1034 |
| Williams (`_s2`) | 0.9278 | −17 % | `cim_2010_williams` hat ein anderes Aero-Modell, gleicher Faktor |
| Sauber | 0.9218 | −18 % | |
| Force India | 0.8608 | −23 % | alle CD ×0.96, nach dem vierten Test ×0.97, am 2026-11-04 ×0.98 |
| Toro Rosso | 0.8941 | −21 % | |
| Lotus | 0.8347 | −27 % | |
| Virgin | 0.7842 | −32 % | |
| HRT | 0.7455 | −35 % | |

Ergebnis vor dem Nachstellen (Abstand zu Red Bull, Ziel Saisonschnitt): McLaren +0.19 (Ziel +0.6), Ferrari +0.27 (+0.6), Renault +0.83 (+1.0), Force India +0.94 (+1.3), Mercedes +1.03 (+0.9), Williams +1.10 (+1.3), Toro Rosso +1.30 (+1.6), Sauber +1.42 (+1.5), Lotus +2.43 (+3.0), Virgin +2.75 (+3.6), HRT +3.85 (+4.3).

Dritter Test mit dem heutigen Stand (40 min, Grid 0 / 0, Team-Schnitt der Bestzeiten zu Red Bull): McLaren +0.48 (Ziel +0.6), Ferrari +0.61 (+0.6), Force India +0.98 (+1.3), Renault +1.07 (+1.0, nur Kubica), Williams +1.12 (+1.3), Sauber +1.50 (+1.5), Toro Rosso +2.04 (+1.6, nur Alguersuari, Buemi fuhr mit Schaden 2 s langsamer), Lotus +2.50 (+3.0), Virgin +4.39 (+3.6), HRT +5.60 (+4.3, nur Senna), Mercedes +0.16 (+0.9, nur Rosberg, Schumacher nach einer Runde raus).

Alle drei Sessions auf den heutigen Stand umgerechnet (0,11 s pro Prozent), Abweichung vom Ziel im Schnitt: Ferrari 0.00, McLaren +0.04, Williams +0.02, Renault +0.02, Toro Rosso +0.18, Virgin +0.17, Sauber −0.16, Lotus −0.22, Force India −0.27, Mercedes −0.39, HRT +0.40. Alle innerhalb der Streuung. Nur Mercedes war zweimal 0,6–0,75 s zu schnell (einmal 0,1 s zu langsam) und bekam als letzte Änderung ×0.98 auf alle `CL_GAIN` (630 → 609 kg, etwa 0,2 s, Balance unverändert 47,5 %). Die übrigen Teams bleiben, weitere Korrekturen würden nur die Streuung nachzeichnen.

Vierter Test (Barcelona, vorzeitig beendet, etwa 5 Runden je Fahrer): Kubica 0,8 s vor Red Bull statt 1,0 s dahinter, auch in Shanghai fiel der Renault als zu stark auf. Über alle vier Barcelona-Sessions im Schnitt 0,44 s zu schnell, deshalb Renault ×0.97 auf alle `CL_GAIN` (630 → 611 kg, etwa 0,3 s, Balance unverändert 47,6 %). Damit hat er etwa so viel Abtrieb wie Mercedes, aber den schwächeren Motor (740 gegen 755 PS).

Force India ebenfalls ×0.97 (564 → 547 kg, etwa 0,3 s): in drei von vier Sessions zu schnell, im Schnitt 0,28 s. Er hat damit etwas weniger Abtrieb als Toro Rosso (551 kg), bleibt durch weniger Luftwiderstand und den Mercedes-Motor auf den Geraden aber schneller.

**Topspeed und Feinschliff (2026-11-04):** `tools/topspeed.py` rechnet den Topspeed aus Luftwiderstand (mit den dynamischen Flügel-Controllern bei Vollgas), `power.lut` und letztem Gang, ohne Rollwiderstand (absolute Werte zu hoch, Reihenfolge stimmt; für `cim_2010_williams` mit dem anderen Aero-Modell unbrauchbar). Vorher lag Force India mit 328 km/h vor McLaren mit 327, der F-Schacht brachte nur 3 km/h gegenüber Mercedes. Real waren es 5 bis 10 km/h ([Auto123](https://www.auto123.com/en/news/amp/f1-technical-how-works-the-infamous-f-duct/33798/), [Top Gear NL](https://topgear.nl/formule-1/hoe-de-f-duct-in-formule-1-de-topsnelheid-van-de-autos-verhoogde)). Deshalb beim McLaren und McLaren `_cod`:

- Heckflügel-`CD_GAIN` (`WING_3`, `WING_7`) auf Original ×0.81 statt ×0.94
- 7. Gang 1.1034 statt 1.1304 (`_cod` 1.1334), Wert aus `7th.rto`; sonst Begrenzer bei 330 km/h
- alle `CL_GAIN` ×0.985 als Ausgleich für den geringeren Luftwiderstand (geschätzt 0,15 s in Barcelona), Rundenzeit soll gleich bleiben

Topspeed danach: McLaren 331, Force India 328, Mercedes und Ferrari 324, Red Bull, Williams, Sauber, Toro Rosso 322, Renault, Lotus, Virgin, HRT 321 km/h.

Nach dem Eindruck des Nutzers aus Rennen (Schätzung, je etwa 0,2 s): Red Bull alle `CL_GAIN` ×1.02 (683 → 696 kg, Balance unverändert), Mercedes, Force India und Williams ×0.98. Weil Red Bull schneller wird, wächst der Abstand aller anderen Teams zu ihm um etwa 0,2 s, bei Mercedes, Force India und Williams um etwa 0,4 s.

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

**2012: Teamstärke über das Autokonzept (2026-11-12, im Spiel noch nicht getestet):** Methode wie 2008 bis 2010, Grid danach 0 / 0. Ziel ist der echte Saisonabstand aus `tools/quali_abstaende.py 2012`. Abtrieb-Rückstand zum Red Bull = Abstand abzüglich Motor (0,095 s pro Prozent), Luftwiderstand (0,04 s pro Prozent) und fehlendem KERS (0,3 s, Schätzung), geteilt durch 0,12 s pro Prozent Abtrieb. `power.lut` gleichmäßig skaliert, alle `CL_GAIN` mit demselben Faktor. Motorwerte wie 2010 (eingefrorene V8, Schätzungen).

| Team | Abstand real (s) | Motor (PS) | Faktor `power.lut` | Faktor `CL_GAIN` | Abtrieb 200 km/h |
|---|---|---|---|---|---|
| Red Bull | 0.00 | 747 (nach Test, siehe unten) | 1.0797 | 1.0300 | 666 kg |
| McLaren | +0.03 | 755 | 1.0597 | 0.9874 | 632 kg |
| Ferrari | +0.19 | 750 | 1.0603 | 0.9844 | 630 kg |
| Mercedes | +0.21 | 755 | 1.0597 | 0.9796 | 625 kg |
| Lotus | +0.22 | 740 | 1.0690 | 0.9869 | 634 kg |
| Sauber | +0.28 | 750 | 1.0603 | 0.9886 | 624 kg |
| Williams | +0.35 | 740 | 1.0690 | 0.9857 | 627 kg |
| Force India | +0.37 | 755 | 1.0597 | 1.0219 (nach Test, siehe unten) | 640 kg |
| Toro Rosso | +0.81 | 750 | 1.0603 | 0.9622 | 597 kg |
| Caterham | +2.10 | 740 | 1.0690 | 0.8710 | 534 kg |
| Marussia | +3.20 | 745 | 1.1112 | 0.8029 | 487 kg |
| HRT | +3.93 | 745 | 1.1112 | 0.7405 | 448 kg |

Marussia: `kers.ini` und `kers_torque.lut` aus der `data.acd` entfernt. Der MR01 fuhr 2012 ohne KERS ([Sky Sports](https://www.skysports.com/f1/news/17581/7459648/Marussia-not-running-KERS), [Wikipedia](https://en.wikipedia.org/wiki/Marussia_MR01)), HRT hatte in der Mod schon keins.

2012 Kollider: Ferrari, Caterham und HRT hatten einen eigenen Satz Kollisionskörper (`colliders.ini`, alle sechs Körper leicht anders, `COLLIDER_3` vorn am Unterboden mit `GROUND_ENABLE=1`). Sie haben jetzt dieselben Werte wie die anderen neun 2012er (Stand Red Bull, `COLLIDER_3` ohne Bodenkontakt, `SPARKS_AS=SKIDPAD`). Fahrhöhe, Trägheit, Lenkung, Gewicht und KI-Werte waren bei allen 2012ern schon einheitlich.

Erster Test 2012 (Montreal, 10 min, 1 bis 3 Runden je Fahrer): Reihenfolge stimmt, die meisten Teams etwa 0,3 s neben dem echten Wochenende, Force India 0,9 s zu langsam, KI absolut etwa 1 s langsamer als real. Zu kurz für Änderungen, die KI ist auf dieser Strecke schwach.

Zweiter Test 2012 (Silverstone GP, 18 min, 3 bis 8 Runden je Fahrer, Bezug McLaren): Ferrari, Mercedes, Williams innerhalb von 0,3 s ihres Ziels, Sauber 0,5 s. Red Bull 1,1 s und der KI-Lotus 2,2 s zu langsam, Force India 0,8 s (wie in Montreal). Toro Rosso, Caterham und Marussia 0,8 bis 1,7 s zu langsam, in Montreal aber zu schnell: nicht geändert.

Änderungen danach (2026-11-12, noch nicht nachgetestet):

- Force India: alle `CL_GAIN` nochmals x1,04 (615 auf 640 kg, Balance unverändert 48,4 % vorn). Das Auto liegt damit über dem rechnerischen Wert, die KI kommt mit ihm schlechter zurecht.
- Red Bull und Lotus: `electronics.ini` auf den Stand der anderen zehn 2012er gesetzt (Kopie Williams: ABS und TC `PRESENT=0`, `ACTIVE=1`, `CURVE=` leer). Vorher stand bei beiden die TC auf `ACTIVE=0` mit Kurvendatei (Red Bull verwies auf eine fehlende `t_c.lut`), beim Lotus auch ABS auf `ACTIVE=0` und ein `[EDL]`-Abschnitt. Das war der einzige Unterschied außer dem Abtrieb zu den Autos, die die KI schnell fährt. Ob es die Ursache ist, ist eine Vermutung und muss der nächste Test zeigen.

Dritter Test 2012 (Silverstone GP, 18 min, 1 bis 5 Runden je Fahrer, schnellstes Auto je Team gegen den schnellsten McLaren): Force India +0,43 s (Ziel +0,34), Räikkönen +1,02 s (vorher +2,64), Red Bull unverändert +0,95 s. Die Elektronik war beim Red Bull also nicht die Ursache; seine Physikdaten unterscheiden sich vom Williams nur im Abtrieb und um 7 mm im Radstand.

Änderung danach (2026-11-12, auf Wunsch des Nutzers, noch nicht nachgetestet): Red Bull alle `CL_GAIN` x1,03 (647 auf 666 kg, Balance 48,4 % vorn) und `power.lut` x1,01 (740 auf 747 PS). Das ist ein Ausgleich für die KI und liegt über dem historisch gerechneten Wert; wer den Red Bull selbst fährt, hat ein etwas zu starkes Auto.

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

**Teamstärke über das Autokonzept in zwei Saisonstufen (2026-11-09, im Spiel noch nicht getestet):** Methode wie 2008 und 2010, Grid danach 0 / 0. Vorher hatten alle außer Brawn identische 606 kg und 661 PS. Die Stärke kommt aus `tools/quali_abstaende.py`, getrennt für R1–R7 und R8–R17 (Median aus Q1/Q2, 85-Sekunden-Runde), umgerechnet mit 0,12 s pro Prozent Abtrieb und 0,095 s pro Prozent Leistung. Brawn und Red Bull weichen in Stufe 1 bewusst vom reinen Quali-Wert ab (Schätzung): Brawn 665 kg (Faktor 1.0349), Red Bull 650 kg (Faktor 1.0731), gerechnet etwa 0,45 s Vorsprung für Brawn. In Q1/Q2 waren beide gleichauf, aber Brawn fuhr im Rennen in R1–R7 im Median 0,19 s schneller (beste Rennrunde) und gewann 6 von 7 Rennen. Der RB5 hatte bis Monaco keinen Doppeldiffusor, der real etwa 0,3 s ([ESPN](https://www.espn.co.uk/f1/story/_/id/28167450/busting-myth-brawn-gp-legendary-double-diffuser), Aussage von Brawn) bis 0,5 s ([autoevolution](https://www.autoevolution.com/news/red-bull-to-protest-brawn-gp-rear-diffuser-design-5293.html), Protest von Red Bull) wert war, also etwa 2,5 bis 4 % Abtrieb.

Umschalten (vor Silverstone auf Stufe 2, Stand jetzt Stufe 1):

```
py -3.11 saison_stufen.py --ac "E:/SteamLibrary/steamapps/common/assettocorsa" --plan ../data/stufen_2009.json --stufe 2 --apply
```

| Team | Motor (PS, Schätzung) | Abstand real R1–R7 | Abtrieb Stufe 1 | Abstand real R8–R17 | Abtrieb Stufe 2 |
|---|---|---|---|---|---|
| Brawn | 755 | 0.00 | 665 kg | +0.10 | 636 kg |
| Red Bull | 740 | +0.01 | 650 kg | 0.00 | 653 kg |
| Toyota | 740 | +0.18 | 643 kg | +0.35 | 634 kg |
| Ferrari | 750 | +0.25 | 633 kg | +0.30 | 629 kg |
| Williams | 740 | +0.26 | 639 kg | +0.20 | 642 kg |
| BMW | 750 | +0.56 | 616 kg | +0.40 | 624 kg |
| McLaren | 755 | +0.56 | 612 kg | +0.01 | 642 kg |
| Renault | 740 | +0.59 | 621 kg | +0.39 | 631 kg |
| Toro Rosso | 750 | +1.05 | 589 kg | +0.69 | 608 kg |
| Force India | 755 | +1.38 | 567 kg | +0.66 | 606 kg |

Motoren: Mercedes, Ferrari und Renault wie 2010, die Motoren waren eingefroren. BMW und Toyota sind Schätzungen aus den 2008er Werten minus Drehzahlsenkung auf 18000 U/min. `power.lut` gleichmäßig skaliert (661 PS auf Zielwert, Faktor 1.119 bis 1.142).

Alle zehn Autos: 7. Gang 1.200 → 1.133 (Wert aus `7th.rto`), sonst läge der Begrenzer mit der höheren Leistung bei 317 km/h, jetzt 336 km/h.

McLaren, Ferrari und BMW haben in AC KERS und wiegen deshalb 620 statt 605 kg (`TOTALMASS`, Schätzung). Das System wog real etwa 25 bis 40 kg, ging bei leichten Fahrern aber zulasten des Ballasts, sodass die Autos oft trotzdem bei 605 kg blieben ([Theissen, BMW](https://f1technical.net/news/11809)). 15 kg kosten nach den Barcelona-Tests (50 kg = 1,2 s) etwa 0,35 s und gleichen damit ungefähr den Gewinn durch 400 kJ pro Runde aus (Schätzung). Die echten Abstände enthalten KERS schon. Im Test prüfen, ob die KI das KERS überhaupt nutzt: Falls nicht, sind diese drei Teams jetzt etwas zu langsam.

## Erkenntnisse zum Testen

- **AC rechnet beim vorzeitigen Verlassen hoch** und kopiert Runden an Fahrer ohne eigene Zeit. `auswertung.py` filtert beides.
- **RARE** (`apps/lua/RARE`) setzt die KI in der Quali auf 100 % (Fahrerstärken wirken nur im Rennen), tankt 3,5 Runden aus `fuel_cons.ini` und staffelt die Out-Laps. Ohne RARE fahren alle gleichzeitig los, das gab Massencrashs.
- **Strecke:** Nur Kunos-Strecken zum Abstimmen. Die Melbourne-Mod hat eine schwache KI-Linie (KI rund 1 bis 3 s langsamer als der Spieler), Spa hat ein Problem in Kurve 14.
- **Kosten einer Stufe** (10 kg + 1 %): grob 0,35 bis 0,7 s je nach Auto und Strecke, für Barcelona etwa 0,45 bis 0,5 s.

## Status

Angewendet und im Spiel getestet (Stand 2026-10-27). Grids für 2009 und 2010 abgestimmt in Barcelona, 2007 in Silverstone, 2013 in Melbourne. Nächster Schritt: Grids für 2011 und 2012, Gewichte 2011 bis 2013 prüfen.

## Formula Hybrid (RSS): ein Auto je Team

Bei den Formula Hybrids von RSS sind die Teams nur Skins eines einzigen Autos, Motor und Abtrieb je Team lassen sich so nicht einstellen. `tools/team_autos.py` legt deshalb je Team einen eigenen Auto-Ordner an (`<quelle>_<team>`, Plan in `data/teams_<jahr>.json`):

```
python team_autos.py --ac <AC> --plan ../data/teams_2017.json            (Trockenlauf)
python team_autos.py --ac <AC> --plan ../data/teams_2017.json --apply
```

- Modell, Texturen, Skins, Animationen und Sound-Bank sind Hardlinks auf die Quelle. Zehn Team-Autos 2017 belegen zusammen rund 5 MB. Wer eine verlinkte Datei im Team-Ordner bearbeitet (zum Beispiel einen Skin), ändert auch das Original.
- `data.acd` wird mit dem neuen Ordnernamen neu verschlüsselt, geändert ist nur `SCREEN_NAME`. `sfx/GUIDs.txt` und `ui/ui_car.json` tragen den neuen Namen, die CSP-Konfiguration `extension/config/cars/loaded/<quelle>.ini` wird je Team kopiert.
- Die Quelle bleibt unverändert, ein vorhandener Team-Ordner wird nie überschrieben.

Stand 2026-11-12: 2017 gebaut (`rss_formula_hybrid_2017_mercedes`, `_ferrari`, `_redbull`, `_williams`, `_forceindia`, `_tororosso`, `_renault`, `_haas`, `_mclaren`, `_sauber`, im Spiel als "F1 2017 <Auto>"), Physik noch bei allen gleich der Quelle. Im Spiel noch nicht geladen. Toro Rosso hat die Skins Hartley und Kwjat, Renault Sainz und Hülkenberg (so liefert RSS sie). Nächster Schritt: laden, Sound und Skins prüfen, dann Teamstärke über Motor und Abtrieb (Hybrid-Antrieb braucht eine eigene Rechnung).
