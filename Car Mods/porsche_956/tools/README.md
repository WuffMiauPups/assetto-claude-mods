# Werkzeuge

Reihenfolge: `venturi_model.py` → `build_aero.py` → `install.py`, alle aus diesem Ordner heraus aufrufen.

- `venturi_model.py`: Venturi-Unterboden-Modell. Erzeugt die CSP-Aero-Map-Kennfelder nach `physics/data/aero/` und Diagramme nach `out/`. Alle Parameter in `Config`, Schätzwerte aus der Recherche. `--show` druckt das Gleichgewicht über Geschwindigkeit.
- `build_aero.py`: baut `physics/data` komplett: kopiert den Basis-`data`-Ordner aus `reference/`, setzt `car.ini` auf `VERSION=extended-2`, erzeugt `aero.ini` mit skalierten Flügeln und dem `[MAP_0]`-Block. Flügel-Gains werden aus den Zielwerten in `out/summary.json` berechnet. `--check` rechnet nur. Kennzahlen landen in `out/build_aero.json`.
- `install.py`: legt im Spiel `content/cars/porsche_956_venturi` an (Kopie des VAC-956 ohne `data.acd`, Sound umbenannt) und spiegelt `physics/data` hinein. Der alte `data`-Ordner im Spiel wird als `data.bak` behalten. Das Original `vac_groupc_956` wird nicht angefasst.
- `out/summary.json`: Kennzahlen des Modells, inklusive Zielwerte für die Flügel.

Kalibrierung: Nach dem ersten Spieltest werden `total_downforce_kg`, `total_drag_kg`, Federraten und die Abrisshöhen so angepasst, dass Kurvengeschwindigkeiten, Topspeed und das Verhalten über Kuppen plausibel sind. Referenz: Ring-Schnitt 202 km/h, Mulsanne 350 km/h (Langheck).
