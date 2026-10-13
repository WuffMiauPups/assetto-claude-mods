# Wie realistisch ist das Venturi-Modell? (Stand 2026-10-13)

Kurzfassung: Das Modell trifft die Form des Verhaltens, nicht die exakten Zahlen des 956. Es gibt keine öffentlich zugänglichen Windkanaldaten des 956, keine Zeichnungen der Tunnel und keine Setup-Blätter. Was es gibt, sind Vergleichswerte verwandter Autos, Aussagen von Norbert Singer, und die Grundlagenforschung zu Diffusoren in Bodennähe. Daran ist das Modell ausgerichtet.

## Was die Forschung über Diffusoren in Bodennähe sagt

Arbeiten von Cooper, Senior und Zhang sowie Ruhrmann und Zhang (Universität Southampton, Übersicht bei Zhang, Toet, Zerihan 2006) beschreiben die Abtriebskurve über die Bodenfreiheit in vier Bereichen:

| Bereich | Verhalten | Im Modell |
|---|---|---|
| A, Force Enhancement | Abtrieb steigt mit sinkender Höhe, weil der Unterdruck unter dem Boden „abgepumpt“ wird | ja, Potenzgesetz mit Exponent 0,75 hinten |
| B, Force Plateau | Anstieg flacht ab, Maximum | ja, seit dieser Version als weiches Maximum statt hartem Deckel |
| C, Force Reduction | Abtrieb fällt, Ablösung im Diffusor beginnt (Wirbel brechen zusammen) | ja, Übergangszone unterhalb der Abrisshöhe |
| D, Loss of Downforce | starker Verlust bei sehr geringer Höhe | ja, Restabtrieb 35 Prozent |

Weitere gesicherte Befunde:

- Der Diffusorwinkel verschiebt den Beginn des Abfalls: größerer Winkel, Abfall bei höherer Bodenfreiheit. Unter etwa 5 Grad bleibt die Strömung anliegend, darüber bildet sich eine Ablöseblase. Im Modell abgebildet über den Rake-Abriss (`rake_stall`), weil Rake beim Auto den effektiven Diffusorwinkel vergrößert.
- Ruhrmann und Zhang fanden Hysterese: Nach dem Abriss liegt die Strömung erst bei deutlich größerer Höhe wieder an. Das kann die CSP-Aero-Map nicht, dafür ist das optionale Lua-Script vorgesehen.
- Flügel in Bodennähe verlieren unterhalb von etwa 0,3 Flügeltiefe Abstand. Beim 956 relevant für den Frontbereich mit der Singer-Delle, deshalb der eigene vordere Abriss (`h_front_stall`).

Das Modell entspricht damit der qualitativen Struktur der Literatur. Was fehlt: die tatsächliche Steigung der Kurve, die Höhe des Maximums und die genaue Abrisshöhe des 956. Die hängen von Tunnelgeometrie, Diffusorlänge und der Abdichtung an den Seiten ab, und dazu gibt es keine Daten.

## Vergleichswerte für die absolute Größe

| Auto | Quelle | Wert | Umgerechnet |
|---|---|---|---|
| 956 Langheck, Le Mans | Motor Sport (Schätzung, keine Windkanaldaten) | 1050 kg Abtrieb, 382 kg Widerstand bei 200 mph | Cl·A 2,1 m², Cd·A 0,77 m², L/D 2,75 |
| 956 Kurzheck | Porsche-Pressemappe | doppelter Abtrieb des Langhecks | Cl·A grob 4 m² |
| 956 gegenüber 917 Langheck | Singer | 3,5-facher Abtrieb, 4 Prozent mehr Widerstand | |
| 962 Joest 1993, High Downforce | Mulsanne's Corner, Porsche Weissach Windkanal | Cl 2,655 auf 1,806 m², 3141 lbf bei 150 mph, L/D 4,0 bis 4,4 | Cl·A 4,8 m², 2540 kg bei 322 km/h, Cd·A 1,1 bis 1,2 |
| Jaguar XJR-14 1991 | Mulsanne's Corner | 3307 lbf bei 150 mph, L/D 4,2 | Cl·A 5,0 m² |
| Toyota TS010 1992 | Mulsanne's Corner | 5061 lbf bei 150 mph, L/D 6,1 | Cl·A 7,7 m² |

Einordnung: Der 962 von 1993 hatte zehn Jahre Entwicklung mehr als Bellofs 956 von 1983. Ein Kurzheck-956 von 1983 sollte deutlich unter Cl·A 4,8 liegen und ineffizienter sein als L/D 4. Motor Sport nennt für den 956 L/D 2,75. Gewählte Zielwerte für das Modell:

| Größe | alt | neu | Begründung |
|---|---|---|---|
| Abtrieb bei 322 km/h, Design-Höhe | 1800 kg | 1900 kg | zwischen Langheck-Schätzung mal zwei und 962-Wert, mit Abstand nach unten |
| Widerstand bei 322 km/h | 480 kg | 640 kg | L/D 3,0 statt 3,75, näher an Motor Sport 2,75 und unter dem 962 |
| Anteil Unterboden | 60 Prozent | 60 Prozent | Singer: „der Großteil“ aus dem Unterboden, Zahl nicht belegt |

## Was am Modell gesichert ist und was nicht

Gesichert, aus Literatur und Aussagen:
- Die vier Bereiche der Kurve und ihre Reihenfolge.
- Rake erhöht den Abtrieb bis zur Ablösung.
- Gierwinkel reduziert den Unterboden-Abtrieb, weil die seitliche Anströmung der Tunnel gestört wird (Singer betont die seitliche Zuströmung).
- Größenordnung: Kurzheck etwa Faktor zwei über Langheck, 956 unter dem späten 962.
- Beobachtung aus der Entwicklung: Bei hoher Geschwindigkeit sank das Auto tiefer als geplant, mit Diffusor-Ablösung und Aufschaukeln. Das Modell reproduziert, dass der Gleichgewichtspfad bei Höchstgeschwindigkeit in die Abrisszone läuft.

Geschätzt, ohne Beleg:
- Exponenten der Kurve (0,75 hinten, 0,35 vorn).
- Abrisshöhen (30 mm hinten, 12 mm vorn), Breite des Übergangs, Restabtrieb.
- Balance des Unterbodens (40 Prozent vorn) und ihre Wanderung mit Rake.
- Federraten, Anschlagpuffer, Gewichtsverteilung.
- Design-Bodenfreiheit 55 mm vorn, 85 mm hinten.

Nicht modelliert:
- Hysterese nach Abriss (nur mit Lua).
- Einfluss von Rollwinkel und Lenkwinkel auf den Unterboden (LUTs vorhanden, aber nicht gefüllt).
- Zeitliche Dynamik der Strömung; CSP bietet dafür nur die Kraftverzögerung.
- Reifenverformung und tatsächliche Unterkante des Flachbodens gegenüber der Fahrwerks-Bodenfreiheit.

## Konsequenz für die Umsetzung

Das Modell ist ein belastbarer Startpunkt, weil es die richtige Struktur hat und in der richtigen Größenordnung liegt. Die exakten Werte werden im Spiel kalibriert, mit zwei Referenzen: Rundenzeit und Charakter. Für den Ring 1983 sind das 6:11 bei 202 km/h Schnitt mit einem Auto, das über Kuppen leicht wird und in schnellen Kurven „klebt“. Mehr Genauigkeit wäre nur mit Windkanaldaten von Porsche oder einer CFD-Rechnung an einem vermessenen Unterboden möglich.

## Quellen dieser Bewertung

- Zhang, Toet, Zerihan: Ground Effect Aerodynamics of Race Cars, Applied Mechanics Reviews 59, 2006. https://eprints.soton.ac.uk/42969/1/GetPDFServlet.pdf
- Katz: Aerodynamics of Race Cars, Annual Review of Fluid Mechanics 38, 2006. https://sites.fem.unicamp.br/~phoenics/EM974/PROJETOS/Temas%20Projetos/Cars%20aerodynamics/annurev.fluid.38.050304.092016.pdf
- Review of Ground-Effect Diffuser Aerodynamics (2018). https://www.researchgate.net/publication/326525637_A_Review_of_Ground-Effect_Diffuser_Aerodynamics
- Investigation of vehicle ride height and diffuser ramp angle. https://www.researchgate.net/publication/325400439_Investigation_of_vehicle_ride_height_and_diffuser_ramp_angle_on_downforce_and_efficiency
- Influence of Diffuser Angle on a Bluff Body in Ground Effect (Ruhrmann, Zhang). https://www.researchgate.net/publication/237900355_Influence_of_Diffuser_Angle_on_a_Bluff_Body_in_Ground_Effect
- Mulsanne's Corner, 1993 Joest-Porsche 962. http://www.mulsannescorner.com/aerodatabasejoestporsche962.html
- Mulsanne's Corner, Jaguar XJR-14. http://www.mulsannescorner.com/aerodatabasejaguarxjr-14.html
- Mulsanne's Corner, Toyota TS010. https://www.mulsannescorner.com/aerodatabasetoyotaTS010.html
- Motor Sport, Under the skin of the Porsche 956. https://www.motorsportmagazine.com/archive/article/february-2018/80/may-downforce-be-you/
- Motor Sport, 956 and 962 track test 2022. https://www.motorsportmagazine.com/archive/article/july-2022/80/porsches-le-mans-conquering-group-c-cars-driven-956-and-962-track-test/
- Porsche 40 Years Group C Mediakit. https://newsroom.porsche.com/dam/jcr:a6f33b52-c47d-47b4-98c1-7e963661f587/40%20Years%20Group%20C.pdf
- Revs Institute, Dream Debut for Porsche's 956. https://automedia.revsinstitute.org/dream-debut-for-porsches-956
- Technik Museum, Norbert Singer im Interview. https://stories.technik-museum.de/de/community/museumsgeschichten/norbert-singer-im-interview/
- Motor Sport, Lunch with Norbert Singer 2015. https://www.motorsportmagazine.com/archive/article/june-2015/86/lunch-norbert-singer/
- F1technical, 956/962 nose diffuser. https://www.f1technical.net/forum/viewtopic.php?p=1027661
