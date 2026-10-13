# 01 Fast Lane Recorder

Eigene Runden aufnehmen und daraus eine neue `fast_lane.ai` erzeugen, damit die KI deine Linie und dein Tempo fährt.

## Ziel

- Aufnahme-App (Lua für CSP) loggt Position, Geschwindigkeit, Gierrate, Pedale und Lenkung mit hoher Rate in eine CSV.
- Python-Paket `fastlane` liest und schreibt das Binärformat von `fast_lane.ai`.
- Pipeline: beste Runde wählen, glätten, gegen Streckenränder prüfen, Geschwindigkeitsprofil mit einstellbarer Reserve aufbauen, Datei schreiben.
- Vergleichsdiagramme: alte gegen neue Linie, Geschwindigkeit über Streckenmeter, Krümmung, Bremspunkte.

## Geplante Struktur

```
01-fast-lane-recorder/
  app/                 Lua-App für CSP (Aufnahme im Spiel)
  fastlane/            Python-Paket: Parser, Writer, Geometrie
  scripts/             Kommandozeilen-Werkzeuge (analyse, build, compare)
  tests/
  dist/                Fertige Dateien zum Kopieren ins Spiel
```

## Installation

1. Ordner `app/` nach `assettocorsa/apps/lua/` kopieren.
2. Im Spiel die App öffnen, Aufnahme starten, einige saubere Runden fahren.
3. CSV aus `assettocorsa/apps/lua/<app>/logs/` nach `AI/data/<track>/laps/` legen.
4. `python scripts/build.py --track <track> --margin 0.97` ausführen.
5. Erzeugte `fast_lane.ai` nach `content/tracks/<track>/ai/` kopieren. Original vorher sichern.

## Status

Noch nicht begonnen. Benötigt: Streckenname, Original-`fast_lane.ai`, CSP-Version.
