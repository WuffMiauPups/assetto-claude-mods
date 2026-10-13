# Lua-Physik-Script (optional)

Nur nötig, wenn das Aero-Map-Kennfeld allein das Fahrgefühl nicht trifft. Kandidaten:

- Hysterese beim Strömungsabriss: nach Abriss bleibt der Abtrieb reduziert, bis die Bodenfreiheit deutlich über die Abrisshöhe steigt.
- Unterbodenschaden nach hartem Aufsetzen: Abtrieb dauerhaft reduziert bis zum Boxenstopp.
- Kerb-Reaktion: kurzer Abtriebsverlust bei Überfahren mit einer Seite.

Verifizierte API siehe `research/02-csp-technik.md`. Erste Datei wird ein Minimaltest, der nur `ac.addForce` und Zugriff auf die Bodenfreiheit prüft.
