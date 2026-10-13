# Porsche 956 (Bellof-Spezifikation) mit echtem Ground-Effect

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
| Physik-Daten | `car.ini`, `suspensions.ini`, `tyres.ini`, `engine.ini`, `aero.ini` auf Basis realer Daten | offen |
| Venturi-Modell | CSP Extended Physics, `script.lua` im Datenordner: Abtrieb und Angriffspunkt als Funktion von Bodenfreiheit vorn und hinten, Nickwinkel und Geschwindigkeit, mit Abriss | offen |
| Abstimmung | Python-Modell des Venturi-Effekts zum Entwerfen der Kennfelder vor dem Spieltest | offen |
| 3D-Modell | bestehender 956-Mod als Basis, nur Physik und Skin werden ersetzt | offen |
| Skin | Rothmans Nr. 2 (oder Nr. 7 bei Brun) als Bellof-Variante | offen |
| Sound | aus bestehendem Mod übernehmen | offen |

## Quellen für die Daten

- Porsche 956: 2649 ccm Biturbo-Flat-Six (Typ 935/76), rund 620 PS im Renntrimm, 820 bis 850 kg, Radstand 2650 mm, Aluminium-Monocoque, Fünfganggetriebe.
- Abtrieb: etwa dreifacher Wert des 917, Unterboden mit zwei Tunneln, Motor dafür hinten angehoben.
- Bellofs 956-007 am Ring 1983 mit größeren 13-Zoll-Vorderrädern und kleineren Anpassungen.

Alles weitere wird in `research/` gesammelt.

## Ordner

```
porsche_956/
  research/    Datenblätter, Messwerte, Quellen
  physics/     INI-Dateien des Autos (unverschlüsselter data-Ordner)
  script/      script.lua für das Venturi-Modell
  tools/       Python-Modell zum Entwerfen der Aero-Kennfelder
```

## Was ich brauche

1. Welchen 956-Mod hast du installiert? Ordnername aus `content/cars/` reicht. Ich brauche den entpackten `data`-Ordner (Content Manager: Auto auswählen, "Unpack data").
2. CSP-Version aus Content Manager.
3. Welche Variante: Rothmans Werks-956 von 1983 oder 1984, oder der Brun-956 von 1985?
