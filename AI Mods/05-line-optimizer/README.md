# 05 Line Optimizer

Ideallinie algorithmisch berechnen statt sie zu fahren.

## Ziel

Aus Mittellinie und Streckenrändern wird eine Rennlinie berechnet, die schneller sein kann als jede aufgenommene Runde:

- Minimum-Curvature-Optimierung als schneller erster Schritt
- Zeitoptimale Linie mit einfachem Fahrzeugmodell (Reibkreis, Leistungsgrenze) als zweiter Schritt
- Geschwindigkeitsprofil aus Krümmung und Fahrzeugparametern
- Ausgabe als `fast_lane.ai` über das Paket aus Projekt 01

## Geplante Struktur

```
05-line-optimizer/
  optimizer/           Algorithmen
  vehicles/            Fahrzeugparameter (Masse, Grip, Leistung) pro Auto
  scripts/             optimize.py, compare.py
```

## Status

Noch nicht begonnen. Baut auf Projekt 01 auf.
