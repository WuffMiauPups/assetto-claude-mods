# KERS 2013 und Reifen 2018 am F2004

Stand 2026-10-20.

## KERS

Reglement 2009 bis 2013: maximal 60 kW Abgabe, 400 kJ pro Runde, daraus 6,67 s volle Leistung. Der Cimmerian Iter 2013 Ferrari setzt das in `kers.ini` so um: `DISCHARGE_TIME=6600`, `MAX_KJ_PER_LAP=400`, `CHARGE_K=0.0019`, `NEGATIVE_INPUT_CHARGE_K=3`, `ATTACH=ENGINE`, Knopfbetrieb ohne Regler. Diese Werte sind übernommen.

Die Drehmomentkurve des CIM (77 Nm bis 7000, dann fallend auf 18 Nm bei 18000) ergibt nur 34 kW bei hoher Drehzahl. Für den F2004 (Begrenzer 18800, Drehzahlen bis 19500 im Spiel) ist die Kurve neu gelegt: konstant 60 kW ab 7000 (`T = 60000 / (2π·n/60)`), darunter 82 Nm gedeckelt, oberhalb 19500 null. Schätzung: ein echter 2013er MGU hielt die 60 kW über das ganze nutzbare Band.

Gewicht: bleibt bei 605 kg. 2004 war das Mindestgewicht, und ein KERS (rund 25 bis 35 kg) wäre wie 2009 bis 2013 durch weniger Ballast ausgeglichen worden.

## Reifen

Die fünf Trockenmischungen der RSS Formula Hybrid 2018 (Hyper-Soft, Ultra-Soft, Super-Soft, Soft, Medium) werden mit allen Parametern übernommen: Grip-Lastkurven (`DY_CURVE`, `DX_CURVE`), Wärme- und Verschleiß-LUTs, Sturztabellen, Druckmodell (ideal 20 psi, kalt 14/13 psi), Falloff. Standard ist Hyper-Soft (meister Grip, `DY_REF` 1,65 gegen 1,81 beim Kunos-Soft, der Vergleich ist aber nicht direkt möglich, weil die RSS-Lastkurven anders skaliert sind).

Nur die Geometrie bleibt 2004: Breite 245/325 mm statt 305/405, Radius 0,330 m (Übersetzung und Modell passen), Felge 13 Zoll, Trägheit der Kunos-Räder. Die Federrate der Karkasse bleibt die der 2018er, weil sie mit deren Druckmodell gekoppelt ist. Einschätzung: Die schmaleren Räder tragen in AC dieselbe Gummimischung, der Grip pro Last ist also der von 2018, die Lastempfindlichkeit auch. Realistisch wäre bei 20 bis 25 % weniger Aufstandsfläche etwas weniger Grip, das ist bewusst nicht modelliert, weil die Mischungen gewünscht waren.

Setup: Druckbereich im F2004-Setup 6 bis 28 psi deckt die neuen Werte ab, Sturzbereiche (vorn bis -4, hinten bis -3,2) bleiben.
