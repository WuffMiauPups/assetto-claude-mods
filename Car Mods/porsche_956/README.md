# Porsche 956-007, Bellof, Nürburgring 1983, mit echtem Ground-Effect

Ziel: Ein 956, dessen Unterboden sich wie ein Venturi-Tunnel verhält, nicht wie ein fester Flügel. Vorlage: Chassis 956-007, Rothmans, Stefan Bellof, Nürburgring 1000 km 1983 (6:11.13 im Training).

## Warum die bestehenden Mods oberflächlich wirken

Original-AC definiert in `aero.ini` Flügel mit Auftriebs- und Widerstandskurven über den Anstellwinkel. Eine Abhängigkeit von der Bodenfreiheit gibt es nicht. Beim 956 kam aber der Großteil des Abtriebs aus den Tunneln, und der hängt steil von der Bodenfreiheit hinten und vom Nickwinkel ab:

- Heck senkt sich bei hoher Geschwindigkeit: Abtrieb steigt überproportional, das Auto klebt.
- Heck hebt sich beim Bremsen, über Kerbs oder bei Bodenwellen: Abtrieb bricht schlagartig ein.
- Zu geringe Bodenfreiheit: Strömungsabriss im Tunnel, Abtrieb fällt trotz Geschwindigkeit.
- Die Aero-Balance wandert mit dem Nickwinkel, das Auto wird beim Anbremsen nervös.

Das erzeugt genau das Fahrgefühl, das Derek Bell beschrieb: Das Auto auf der Straße zu halten war mit Ground-Effect schwierig.

## Umsetzung

| Baustein | Technik | Status |
|---|---|---|
| Physik-Daten | `physics/data`, erzeugt von `tools/build_aero.py` aus dem VAC-956; `aero.ini` und `car.ini` neu, Rest noch Basis-Mod | erste Fassung, im Spiel installiert als `porsche_956_venturi` |
| Venturi-Modell | CSP Aero Map in `aero.ini`: 2D-Kennfelder für Abtrieb, Widerstand und Balance über Bodenfreiheit vorn und hinten, dazu Yaw-LUTs. Lua nur für Abriss-Hysterese, falls nötig | eingebaut als `[MAP_0]`, Spieltest offen |
| Abstimmung | `tools/venturi_model.py` (Kennfelder), `tools/build_aero.py` (data-Ordner), `tools/install.py` (ins Spiel) | läuft, unkalibriert |
| 3D-Modell | bestehender 956-Mod als Basis, nur Physik und Skin werden ersetzt | offen |
| Skin | Rothmans Nr. 2 (oder Nr. 7 bei Brun) als Bellof-Variante | offen |
| Sound | aus bestehendem Mod übernehmen | offen |

## Quellen für die Daten

- Porsche 956: 2649 ccm Biturbo-Flat-Six (Typ 935/76), rund 620 PS im Renntrimm, 820 bis 850 kg, Radstand 2650 mm, Aluminium-Monocoque, Fünfganggetriebe.
- Abtrieb: etwa dreifacher Wert des 917, Unterboden mit zwei Tunneln, Motor dafür hinten angehoben.
- Bellofs 956-007 am Ring 1983 mit größeren 13-Zoll-Vorderrädern und kleineren Anpassungen.

Details und Quellen: `research/00-quellen.md` (alle Quellen), `01-technische-daten.md` (Fahrzeug), `02-csp-technik.md` (Umsetzung in CSP), `03-modellbewertung.md` (wie realistisch das Venturi-Modell ist).

## Ordner

```
porsche_956/
  research/    Quellen (00), Fahrzeugdaten (01), CSP-Technik (02), Kopien der Wiki-Seiten
  physics/     data-Ordner des Autos, Vorlagen für aero.ini und setup.ini
  tools/       venturi_model.py und Ausgaben
  script/      optionales Lua-Script (Abriss-Hysterese, Schaden)
  skins/       Rothmans Nürburgring 1983
  dist/        fertiges Auto zum Kopieren nach content/cars/
```

## Stand und nächste Schritte

Basis ist `vac_groupc_956` (entpackte Daten in `reference/`), CSP 0.3.0-preview649. Das Auto liegt im Spiel als eigener Ordner `porsche_956_venturi`, das Original bleibt unberührt.

1. Spieltest auf der Nordschleife: lädt das Auto, wie verhält sich die Bodenfreiheit über Geschwindigkeit, wo liegt der Abriss. Ablauf in `physics/README.md`.
2. Kalibrierung von Abtrieb, Widerstand und Federraten in `tools/venturi_model.py`.
3. Masse, Motor, Getriebe, Reifen auf 1983 bringen.
4. Offen: Variante (Rothmans Werks-956 1983 oder 1984, oder Brun 1985) für den Skin.
