# DRS am F2004: Herleitung der Stärke

Stand 2026-10-20. Alle Zahlen aus den entpackten `data.acd` der drei Autos, gerechnet ohne die Bodenfreiheits-Faktoren (GH-LUTs), die auf den Heckflügel nicht wirken.

## Wie AC das DRS rechnet

Ein eigener Flügel in `aero.ini` steht für die Klappe. `drs.ini` setzt für diesen Flügel `EFFECT=0`: bei offenem DRS wird der Anstellwinkel mit 0 multipliziert, Auftrieb und Widerstand fallen auf die LUT-Werte bei 0 Grad. So machen es Kunos (F138, SF70H) und Cimmerian Iter 2013: Klappe 15 Grad, Spannweite wie der Hauptflügel, EFFECT 0.

## Vorlage 2013 (Cimmerian Iter Ferrari)

| Flügel | CL·A | CD·A |
|---|---|---|
| Hauptflügel WING_3, 16 Grad, Gain 1,2 / 1,5 | 0,572 | 0,184 |
| DRS-Klappe WING_7, 15 Grad | 0,467 | 0,193 |
| Klappe bei 0 Grad | 0,042 | 0,027 |

DRS offen nimmt dem Heck 0,425 CL·A (41 % des Heckflügels) und 0,165 CD·A, rund 15 % des Gesamtwiderstands dieses Autos (etwa 1,13 m²). Das passt zur Literatur: DRS brachte 2011 bis 2013 rund 10 bis 15 km/h mehr Endgeschwindigkeit, also 10 bis 15 % weniger Widerstand.

## Übertragung auf 2004

Was am 2004er Flügel anders wäre, wenn man die 2013er Klappe sinngemäß dort einbaut:

- Spannweite 1000 mm statt 750 mm (Heckflügel 2009 von 1000 auf 750 mm verkleinert, Quelle f1technical). Die Klappe hat also ein Drittel mehr Fläche, der absolute Widerstandsgewinn wächst entsprechend.
- Zwei Elemente oben, wie 2013. Das Verhältnis Klappe zu Hauptblatt ist ähnlich, die Klappe trägt in einem hoch belasteten Zweielement-Flügel rund 40 bis 45 % des Auftriebs.
- Spaltmaß: 2011 maximal 50 mm offen, ab 2019 85 mm (formula1-dictionary). Für 2013 ist der Wert nicht belegt (50 oder 65 mm). In der AC-Rechnung ist das egal, die Klappe geht ohnehin auf 0 Grad.
- Der 2004er hat mehr Grundwiderstand (CD·A im Spiel 1,24 m² statt 1,13 m²), deshalb wird aus der größeren Klappe ein ähnlicher Prozentsatz.

Umsetzung: Der Kunos-Heckflügel (WING_2, 25 Grad, Gain 0,904 / 0,88) wird in Hauptblatt und Klappe geteilt, beide mit denselben LUTs und demselben Winkel. Im Normalzustand ist die Summe exakt der originale Flügel, der F2004 fährt also wie gewohnt. Klappenanteil 45 % (Schätzung, siehe oben).

| Größe | Wert |
|---|---|
| Heckflügel gesamt | CL·A 0,871, CD·A 0,494 |
| DRS offen, Verlust | CL·A 0,363 (42 % des Heckflügels, 11 % des Autos), CD·A 0,169 (13,6 % des Autos) |
| bei 340 km/h | 923 N weniger Widerstand, 202 kg weniger Abtrieb |
| Endgeschwindigkeit | etwa plus 17 km/h bei gleicher Leistung |

Zum Vergleich der 2013er im Spiel: 15 % Widerstand, 41 % Heckflügel. Der 2004er liegt also in der Stärke praktisch gleichauf, verliert aber absolut mehr Abtrieb, weil der Flügel größer ist. In Kurven mit offenem DRS fehlen 200 kg hinten, das Heck wird deutlich leichter, so wie es 2011 die Fahrer beschrieben.

## Setup

"Rear wing main" (WING_2) verstellt nur das Hauptblatt, 5 bis 35 Grad. Die Klappe (WING_6) steht fest auf 25 Grad: `wing_animations.ini` bildet 25 Grad auf geschlossen und 0 Grad auf offen ab, ein verstellbarer Klappenwinkel würde die Animation halb öffnen.

## Animation

Das Kunos-Modell hat die obere Klappe als eigenes, nicht verbundenes Teil in der Karosserie-Mesh (128 Dreiecke, Sehne 110 mm, Anstellung rund 55 Grad, Spalt zum Hauptblatt 4 mm). `tools/make_flap.py` verschiebt diese Dreiecke in den Knoten `WING_Rear_Flap` mit Drehpunkt an der Hinterkante (0, 0.82, -2.20) und schreibt `car_wing.ksanim` (Format 2, 20 Bilder): Drehung um die Querachse, 30 Grad, Vorderkante hebt sich, Spalt rund 55 mm. Drehrichtung und Format wurden am Cimmerian 2013 nachgerechnet (dessen Klappe dreht um -45 Grad um x bei Drehpunkt hinten).

## Warum DRS zuerst nicht lud

Mit offenem `data`-Ordner stand im Log kein `LOADING DRS`, beim Kunos F138 mit `data.acd` schon. AC prüft die `drs.ini` offenbar nur in der acd. Seit dem Bau mit gepackter data.acd ist das zu prüfen.

## Grenzen

- LOD C und D (ab 45 m) haben die Klappe nicht abgetrennt, dort bleibt sie zu.
- Die Klappe nutzt dieselbe Polare wie der Hauptflügel. Ein echtes Klappenprofil hätte bei 0 Grad etwas weniger Restwiderstand.
- DRS-Zonen kommen von der Strecke (`drs_zones.ini`), CSP setzt sie durch.

Rechenskript: `tools/build.py` teilt den Flügel, die Zahlen oben entstanden mit numpy aus den LUTs (`research/drs_rechnung.py`).
