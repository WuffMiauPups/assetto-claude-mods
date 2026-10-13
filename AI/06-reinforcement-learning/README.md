# 06 Reinforcement Learning

Ein Agent lernt Fahren und Gegner-Interaktion in einem schnellen Python-Simulator und wird danach nach Assetto Corsa übertragen.

## Warum zweistufig

Assetto Corsa läuft nur in Echtzeit. RL braucht Millionen Schritte. Daher lernt der Agent zuerst in einem 2D-Zwilling der Strecke mit tausenden Schritten pro Sekunde, und erst danach folgt ein kurzes Feintuning im Spiel.

## Stufe 1: Simulator

- Einspur-Fahrzeugmodell mit Reifenkennlinie
- Streckengeometrie aus `fast_lane.ai` und Rändern (Projekt 01)
- Skriptgesteuerte Gegner mit Blockierverhalten, damit Überholen und Antäuschen überhaupt belohnt werden können
- Gymnasium-Umgebung, vektorisiert, Training mit PPO oder SAC in PyTorch

## Stufe 2: Transfer

- Policy als Gewichtsmatrizen exportiert, Vorwärtsdurchlauf in reinem Lua
- Beobachtungen identisch zu Stufe 1: Abstände zu Rändern voraus, Krümmung, Geschwindigkeit, Gierrate, relative Gegnerpositionen
- Steuerung der KI-Autos über die CSP-API aus Projekt 04

## Erwartung

Schnellere Linie als Kunos: gut erreichbar. Überhol- und Verteidigungsverhalten: entsteht mit passender Belohnung. Reward-Hacking-Phasen (Abkürzen, Gegner als Bremshilfe) sind normal und kosten Iterationen.

## Geplante Struktur

```
06-reinforcement-learning/
  sim/                 Fahrzeugmodell, Strecke, Gegner, Gym-Umgebung
  train/               Trainingsskripte und Konfigurationen
  export/              Policy nach Lua
  notebooks/           Auswertung
```

## Status

Noch nicht begonnen. Baut auf Projekt 01 und 04 auf.
