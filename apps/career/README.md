# Karriere-System

Ersetzt die handgeführte Excel-Karriere durch ein eigenes System. Content Manager bleibt nur Startknopf für das einzelne Rennen; die Saisons von CM werden nicht benutzt.

## Referenz

`reference/F1_2017_Sabanov_McLaren.xlsx`: die bisherige Excel-Karriere (Saison 2017, McLaren-Honda). Vier Blätter: Fahrerwertung, Anforderungen, Konstrukteurs, Quali & Notizen.

## Datenmodell (aus der Excel abgeleitet)

| Entität | Felder |
|---|---|
| Karriere | Spielerfahrer, Vorgeschichte, aktuelle Saison, Historie |
| Saison | Jahr, Serie, Team, Teamkollege, Kalender (20 Rennen mit Land, Strecke, SUB-Strecke im Spiel), Punktesystem |
| Fahrer | Name, Team, Rating (Speed, Racecraft, Adaptability, Versatility, Experience, Safety, Consistency), Profiltext |
| Team | Name, Motor, Fahrer 1 und 2 |
| Rennen | Nummer, Quali-Positionen aller Fahrer, Rennpositionen aller Fahrer, Wetter, Pole, DNF-Grund, Eigenverschulden, Notiz, Schlagzeile |
| Ziel | Stufe (Pflicht, Bonus, Krönung), Kennzahl, Vergleich, Schwelle, Text bei Erfolg und Misserfolg |
| Vertrag | Laufzeit, Klauseln als Liste mit Auslöser und Konsequenz |
| Risiko | Beschreibung, Auslöser, Konsequenz |
| Beziehung | Person, Status (grün, gelb, orange, rot), Text, Verlauf |

## Kennzahlen (berechnet)

Punkte, WM-Position, beendete Rennen, DNFs gesamt und eigen, Punkteplätze, Podien, Siege, bestes Rennergebnis, Top-10-Quali, bestes Quali, Quali-Schnitt beider Teamfahrer, Q-Duell-Bilanz, Poles, Tier-Status.

## Geplante Bausteine

1. Ergebnisimport aus den AC-Ergebnisdateien (Quali und Rennen aller Fahrer)
2. Zielberechnung und Hochrechnung
3. Beziehungs- und Klausel-Regeln mit Ereignissen
4. Schlagzeilen und Interviews, manuell oder mit Vorschlägen
5. Mehrsaison-Karriere mit Fahrermarkt
6. Rennstart über Content Manager aus dem Kalender
7. Oberfläche als lokale Webseite, Export ins Excel-Layout

## Offene Fragen

- Welcher F1-2017-Mod und welche Strecken (für die Zuordnung der Ergebnisdateien)?
- Beziehungen nach festen Regeln oder manuell mit Erinnerung?
- Liegen 2014 bis 2016 ebenfalls als Excel vor?

## Status

Analyse abgeschlossen, Umsetzung wartet auf die Antworten oben.
