# 02 AI Hints und Side-Lines

Streckenspezifische Konfiguration, die der Kunos-KI Bremspunkte, Überholzonen und Gefahrenstellen vorgibt.

## Ziel

- `ai_hints.ini` pro Strecke: Bremsmodifikatoren pro Abschnitt, Überholverbote in engen Passagen, Freigaben auf Geraden.
- Side-Lines prüfen und bei Bedarf korrigieren, damit die KI seitlich mehr Raum nutzt.
- Werkzeug, das aus dem Telemetrie-Log von Projekt 01 Vorschläge für Hint-Abschnitte ableitet.

## Wirkung

Nimmt dem Panikbremsen bei Blockaden etwas die Schärfe und lässt die KI an sinnvollen Stellen angreifen. Löst das Grundproblem nicht, ist aber mit wenig Aufwand ein spürbarer Gewinn.

## Geplante Struktur

```
02-ai-hints/
  templates/           Kommentierte Vorlagen für ai_hints.ini
  scripts/             Generator aus Telemetrie
  tracks/<track>/      Fertige Hints pro Strecke
```

## Status

Noch nicht begonnen.
