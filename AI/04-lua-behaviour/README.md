# 04 Lua-Verhaltensschicht

Ein Lua-Script pro KI-Auto, das über die CSP-API eine Verhaltensebene über die Kunos-KI legt.

## Ziel

Zustandsmaschine mit den Zuständen Folgen, Druck aufbauen, Antäuschen, Angriff, Rückzug. Eingaben: Abstand und Delta-Speed zum Vordermann, Spurposition, Kurventyp voraus, eigene Reifen- und Spritlage. Ausgaben: Überlagerung von Lenkung, Gas und Bremse sowie Zielspur.

Geplante Verhalten:

- Fake-Move: kurz nach innen ziehen, Reaktion abwarten, bei Blockade außen durchgehen oder Angriff auf die nächste Bremszone verschieben
- Verteidigen der Innenlinie bei Angriff von hinten
- Menschliche Streuung bei Bremspunkten, Verbremser unter Druck
- Persönlichkeiten pro Fahrer: Geduld, Risiko, Konsistenz
- Blue-Flag-Verhalten und Boxenstopp-Entscheidung

## Grenzen

Die Kunos-Pfadfindung bleibt die Basis. Wie weit die CSP-API Eingriffe in Lenkung und Pedale der KI stabil erlaubt, hängt von der CSP-Version ab und wird mit einem Minimaltest zuerst geprüft.

## Geplante Struktur

```
04-lua-behaviour/
  minimal-test/        Prüft, welche KI-Eingriffe die API erlaubt
  behaviour/           Zustandsmaschine, Persönlichkeiten, Telemetrie
  personalities/       Fahrerprofile als Konfigurationsdateien
```

## Status

Noch nicht begonnen. Erster Schritt ist der Minimaltest.
