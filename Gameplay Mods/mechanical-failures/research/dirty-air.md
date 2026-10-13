# Dirty Air: Datenlage und Modell

## Messwerte

| Ära | verbleibender Abtrieb 10 m | 20 m | Quelle |
|---|---|---|---|
| 2019 | 55 Prozent | 65 Prozent | FIA-CFD, geradeaus, zwei identische Autos, laut The Race |
| 2022 Baseline | 85 Prozent | 95 Prozent | FIA-CFD, laut The Race |
| 2024 bis 2025 | | etwa 80 Prozent | FIA, laut The Race: Entwicklung hat den Gewinn aufgezehrt |
| 2026 Ziel | 80 Prozent | 90 Prozent | FIA-Ziel, laut Fanseiten |
| 2008 | | | OWG stellte massive Verluste fest, Ziel war minus 50 Prozent Abtrieb bei gleichem Widerstand; keine Zahl zum Nachlauf veröffentlicht |

Weitere Befunde:
- Der axiale Geschwindigkeitsverlust im Nachlauf erklärt bis zu 90 Prozent des Abtriebsverlusts (F1technical-Forum, nicht primär belegt).
- Der Frontbereich verliert stärker als das Heck, die Balance wandert nach vorn, das Auto untersteuert. Nach Ansicht mancher ist die Bodenvorderkante wichtiger als der Frontflügel.
- Reifen: mehr Rutschen, weniger Kühlluft. Ein Blog nennt bis 8 Grad mehr hinten nach wenigen Runden, unbelegt.
- Eine Studie (arXiv 2608.03192) findet in Rundenzeiten 2021 bis 2025 keinen signifikanten Unterschied der Dirty-Air-Strafe durch die 2022er Regeln. Rundenzeit, nicht Abtrieb.

Ältere Ären (1988 bis 2016) sind nicht gemessen. Die Werte im Modell sind relativ zu 2019 geschätzt: hohe Flügelabhängigkeit 1996 bis 2008 ähnlich oder schlechter als 2019, 2009 bis 2013 nach den OWG-Regeln etwas besser, 1988 mit flachem Boden und Turbo-Ära moderat.

## Modell (`tools/dirty_air_model.py`)

- Gesamtverlust über Abstand: exponentieller Abfall durch die beiden Stützpunkte 10 m und 20 m, gedeckelt bei 85 Prozent.
- Vorn und hinten: Verlust vorn das 1,35-fache, hinten das 0,75-fache des Gesamtverlusts. Damit entsteht die Balancewanderung.
- Seitlicher Versatz: Gauß mit Halbwertsbreite 1,1 m bei 10 m, wächst um 6 cm pro Meter Abstand.
- Mehrere Vordermänner: der stärkste zählt.
- Tiefpass mit etwa 0,15 s, damit Lenkimpulse nicht zu Sprüngen führen.
- Kurvenfahrt: Der Nachlauf folgt der Fahrtrichtung des Vordermanns. In Kurven liegt der Verfolger deshalb oft seitlich versetzt und bekommt weniger ab, es sei denn er folgt exakt. Eine Krümmung des Nachlaufs ist für Version 2 vorgesehen.
- Widerstand: AC hat den Windschatten bereits, das Script lässt ihn unberührt.

Ausgaben: `research/data/dirty_air_<era>.lut` (Abstand, Gesamt, vorn, hinten), `_lateral.lut`, `dirty_air_summary.json`, `tools/out/dirty_air.png`.

## Quellen

- https://www.the-race.com/formula-1/exclusive-new-data-f1-aero-losses-ruining-close-racing/
- https://arxiv.org/abs/2608.03192
- https://scuderiafans.com/ground-effect-regulations-failed-downforce-loss-now-at-35-as-2026-f1-reset-approaches/
- https://www.f1-fansite.com/glossary/dirty-air/
- https://www.f1technical.net/forum/viewtopic.php?t=27035
- https://www.f1technical.net/forum/viewtopic.php?t=16756
- https://www.racefans.net/2009/01/16/how-the-f1-rules-changes-for-2009-are-meant-to-improve-racing-part-13/
- https://www.f1technical.net/features/11525
- https://www.motorsport.com/f1/news/retro-f1-tech-the-big-shake-ups-of-the-2000s-874524/874524/
- https://themotorsportmetrics.com/f1-dirty-air-effect/
