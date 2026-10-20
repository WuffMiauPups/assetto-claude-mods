# KERS 2013 und Reifen 2018 am F2004

Stand 2026-10-20.

## KERS

Reglement 2009 bis 2013: maximal 60 kW Abgabe, 400 kJ pro Runde, daraus 6,67 s volle Leistung. Der Cimmerian Iter 2013 Ferrari setzt das in `kers.ini` so um: `DISCHARGE_TIME=6600`, `MAX_KJ_PER_LAP=400`, `CHARGE_K=0.0019`, `NEGATIVE_INPUT_CHARGE_K=3`, `ATTACH=ENGINE`, Knopfbetrieb ohne Regler. Diese Werte sind übernommen.

Die Drehmomentkurve des CIM (77 Nm bis 7000, dann fallend auf 18 Nm bei 18000) ergibt nur 34 kW bei hoher Drehzahl. Für den F2004 (Begrenzer 18800, Drehzahlen bis 19500 im Spiel) ist die Kurve neu gelegt: konstant 60 kW ab 7000 (`T = 60000 / (2π·n/60)`), darunter 82 Nm gedeckelt, oberhalb 19500 null. Schätzung: ein echter 2013er MGU hielt die 60 kW über das ganze nutzbare Band.

Gewicht: bleibt bei 605 kg. 2004 war das Mindestgewicht, und ein KERS (rund 25 bis 35 kg) wäre wie 2009 bis 2013 durch weniger Ballast ausgeglichen worden.

## Reifen

Die `tyres.ini` der RSS Formula Hybrid 2018 wird unverändert übernommen, nur die Standardmischung steht auf Hyper-Soft: fünf Trockenmischungen (Hyper-Soft, Ultra-Soft, Super-Soft, Soft, Medium) mit Grip-Lastkurven (`DY_CURVE`, `DX_CURVE`), Wärme- und Verschleiß-LUTs, Sturztabellen, Druckmodell (ideal 20 psi, kalt 14/13 psi), Falloff, Breite 305/405 mm, Radius 0,335 m (1,5 Prozent länger übersetzt als die 0,330 des Kunos-Reifens, 13 Zoll Felge wie 2004). Das 3D-Modell zeigt weiter die schmalen 2004er Räder.

Zum Grip: Der Hyper-Soft liegt bei 3000 N Radlast bei µ 1,86 und bei 5000 N bei 1,64 (`DY_CURVE`). Der Kunos-Soft des F2004 kommt über `DY_REF` 1,81, `FZ0` 3451 und `LS_EXPY` 0,80 auf 1,86 bei 3000 N und 1,68 bei 5000 N, also auf praktisch dasselbe Niveau. Der 2018er fühlt sich im Original vor allem wegen 734 kg und deutlich mehr Abtrieb anders an, nicht wegen des Gummis. Wer mehr Grip will, skaliert `DY_REF`/`DX_REF` oder die Kurven in `tools/build.py` (Funktion `build_tyres`).

Setup: Druckbereich im F2004-Setup 6 bis 28 psi deckt die neuen Werte ab, Sturzbereiche (vorn bis -4, hinten bis -3,2) bleiben.
