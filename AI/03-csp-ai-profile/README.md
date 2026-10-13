# 03 CSP AI Profile

Abgestimmte Einstellungen für das New AI Behaviour des Custom Shaders Patch.

## Ziel

CSP kann die KI zwischen mehreren Splines überblenden und seitlich ausweichen lassen. Die Parameter (Aggressivität, Sicherheitsabstand, Überholbereitschaft, Rückkehr nach Dreher) werden hier als Profile gepflegt:

- `touring-aggressiv`: enges Racing, viele Angriffe
- `gt-ausgewogen`: Standard für Sprintrennen
- `endurance-vorsichtig`: lange Rennen, wenig Kontakt

Dazu ein Vergleichsprotokoll, um Profile im Rennen gegen die Standardwerte zu bewerten.

## Geplante Struktur

```
03-csp-ai-profile/
  profiles/            Eine Datei pro Profil
  docs/                Parameterbeschreibung und Testprotokoll
```

## Status

Noch nicht begonnen. Benötigt: CSP-Version, um die verfügbaren Parameter zu bestimmen.
