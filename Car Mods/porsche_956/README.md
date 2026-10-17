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
| Physik-Daten | `physics/data`, erzeugt von `tools/build_aero.py` aus dem VAC-956: Aero, Fahrwerk, Reifenmaße 1983, Motor 935/76, Übersetzung Ring | fertig, 10 Messungen in `tools/out/messungen/` |
| Venturi-Modell | CSP Aero Map in `aero.ini`: 2D-Kennfelder für Abtrieb, Widerstand und Balance über Bodenfreiheit vorn und hinten, dazu Yaw-LUTs | fertig und kalibriert: 310 km/h, 2450 kg, Heck 44 mm bei Topspeed. Lua-Hysterese nicht nötig |
| Abstimmung | `tools/venturi_model.py` (Kennfelder), `tools/build_aero.py` (data-Ordner), `tools/install.py` (ins Spiel), Mess-App `app/rideheight_monitor` | fertig |
| 3D-Modell | VAC-956 als Basis, Kopie unter `content/cars/porsche_956_venturi` | fertig |
| Skin | Rothmans Nr. 2 Bellof, Ring 1983; bis dahin VAC-Skins | offen, einziger Restpunkt |
| Sound | VAC-Sound, auf neuen Ordnernamen umgeschrieben | fertig, Fahrerentscheid |

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
  app/         CSP-Lua-App Ride Height Monitor (Bodenfreiheit, Aero, Radlasten, CSV-Export)
  skins/       Rothmans Nürburgring 1983
  dist/        fertiges Auto zum Kopieren nach content/cars/
```

## Stand

Fahrbar und kalibriert (Stand 2026-10-17). Basis `vac_groupc_956`, im Spiel als `porsche_956_venturi`. Bauen und installieren aus `tools/` mit `py -3.11 venturi_model.py`, `py -3.11 build_aero.py`, `py -3.11 install.py`. Messprotokoll und Entscheidungen in `physics/README.md`. Fahrerentscheid: Nervosität bei Topspeed bleibt (historisch), Reifenverschleiß und Sound bleiben vom VAC.

Offen: Skin Rothmans Nr. 2 Bellof Ring 1983.
