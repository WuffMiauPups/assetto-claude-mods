# Werkzeuge

- `venturi_model.py`: Venturi-Unterboden-Modell. Erzeugt die CSP-Aero-Map-Kennfelder nach `physics/data/aero/` und Diagramme nach `out/`. Alle Parameter in `Config`, Schätzwerte aus der Recherche. `--show` druckt das Gleichgewicht über Geschwindigkeit.
- `out/summary.json`: Kennzahlen des aktuellen Modells, inklusive Zielwerte für die Flügel.

Kalibrierung: Nach dem ersten Spieltest werden `total_downforce_kg`, Federraten und die Abrisshöhen so angepasst, dass Kurvengeschwindigkeiten und das Verhalten über Kuppen plausibel sind. Referenz: Ring-Schnitt 202 km/h, Mulsanne 350 km/h (Langheck).
