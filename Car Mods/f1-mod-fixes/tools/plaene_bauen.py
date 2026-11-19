"""Baut die Plan-Dateien data/teams_<satz>.json für team_staerke.py (Modus "absolut").

  py -3.11 plaene_bauen.py            (schreibt alle Pläne neu)

Quellen: data/quali_abstaende.json (echte Abstände, tools/quali_f1db.py) und research/motoren_*.json
(Motorleistung und Autokonzept je Team, mit Quellen). Hier steht nur, welcher Auto-Ordner welches Team ist
und welche Annahmen je Satz gelten. Von Hand nachgestellte Werte gehören in "fest" des Satzes, sonst gehen sie
beim nächsten Lauf verloren.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA, RES = HERE.parent / "data", HERE.parent / "research"

SAUGER = {"s_pro_prozent_abtrieb": 0.12, "s_pro_prozent_leistung": 0.095, "s_pro_prozent_widerstand": 0.04, "s_pro_kg": 0.024}
HYBRID = {"s_pro_prozent_abtrieb": 0.09, "s_pro_prozent_leistung": 0.16, "s_pro_prozent_widerstand": 0.04, "s_pro_kg": 0.024}
TURBO88 = ["mclaren", "ferrari", "lotus", "arrows", "zakspeed", "osella"]


def autos(prefix, text):
    """'key=ordnerteil[:f1db-id]' je Wort; ohne '=' ist der Ordnerteil der Schlüssel."""
    out = {}
    for w in text.split():
        key, rest = w.split("=") if "=" in w else (w, w)
        teil, fid = rest.split(":") if ":" in rest else (rest, key)
        out[key] = (prefix + teil, fid)
    return out


# name: (jahr, recherche-datei, empfindlichkeit, cl_min, plan-zusätze, autos, zusätze je team)
SAETZE = {
    "1988": (1988, "motoren_1988_1994", SAUGER, 0.65, {},
             autos("f1_1988_", "mclaren ferrari lotus arrows zakspeed osella williams benetton march tyrrell rial minardi ligier larrousse=larrousse:lola ags coloni dallara eurobrun"),
             {k: {"masse": 615 if k in TURBO88 else 575} for k in "mclaren ferrari lotus arrows zakspeed osella williams benetton march tyrrell rial minardi ligier larrousse ags coloni dallara eurobrun".split()}),
    # 1990 (Sim Dream): gleiche Mod-Familie wie 1993. Life hat sich nie vorqualifiziert und hat keinen Abstand: fester Abtrieb.
    "1990": (1990, "motoren_1990_1995_2016", SAUGER, 0.65, {"masse": 575},
             autos("f1_1990_", "mclaren ferrari williams tyrrell benetton larrousse=larrousse:lola lotus minardi dallara brabham leytonhouse=march:leyton-house ligier arrows=footwork:arrows osella onyx ags eurobrun coloni life"), {}),
    # 1995 (sagastiiim): kein Ferrari in der Mod. Ordner f1_1995_tyrell (so geschrieben) und f1_1995_arrows (Footwork).
    "1995": (1995, "motoren_1990_1995_2016", SAUGER, 0.65, {"masse": 595, "ps_anker": 732},
             autos("f1_1995_", "williams benetton mclaren jordan sauber ligier tyrrell=tyrell footwork=arrows minardi simtek pacific forti"), {}),
    # 2016 (ACFL): Die Mod staffelt den Luftwiderstand von Mercedes bis Sauber/Renault/Manor um 19 % als Rangfolge
    # (der Manor war real eines der Autos mit dem wenigsten Luftwiderstand). Deshalb alle auf den Wert des Mercedes,
    # darauf nur die gut belegten Faktoren der Recherche.
    "2016": (2016, "motoren_1990_1995_2016", HYBRID, 0.80, {"cd_angleichen": True},
             autos("acfl_2016_", "mercedes=mercedes_off ferrari=ferrari_off redbull=redbull_off:red-bull williams=williams_off forceindia=force_india_off:force-india mclaren=mclaren_off tororosso=toro_rosso_off:toro-rosso haas=haas_off renault=renault_off manor=manor_off sauber=sauber_off"), {}),
    "1993": (1993, "motoren_1988_1994", SAUGER, 0.65, {"masse": 580},
             autos("f1_1993_", "williams mclaren benetton ferrari ligier lotus sauber footwork jordan larrousse lola minardi tyrrell"), {}),
    "1994": (1994, "motoren_1988_1994", SAUGER, 0.65, {},
             autos("acfl_1994_", "benetton williams ferrari mclaren jordan tyrrell ligier sauber footwork minardi larrousse lotus simtek pacific"), {}),
    "1996": (1996, "motoren_1996_2000", SAUGER, 0.65, {},
             autos("f1_1996_", "williams ferrari benetton mclaren jordan sauber tyrrell ligier footwork minardi forti"), {}),
    "1997": (1997, "motoren_1996_2000", SAUGER, 0.65, {"masse": 600},
             autos("f1_1997_", "williams ferrari benetton mclaren jordan prost sauber arrows stewart tyrrell minardi"), {}),
    "1997_gp": (1997, "motoren_1996_2000", SAUGER, 0.65, {"masse": 600},
                autos("gp_1997_", "williams=fw19 ferrari=f310b benetton=b197 mclaren=mp412 jordan=j197 prost=js45 sauber=c16 arrows=a18 stewart=sf01 tyrrell=025 minardi=m197"), {}),
    "1998_gp": (1998, "motoren_1996_2000", SAUGER, 0.65, {"masse": 600},
                autos("gp_1998_", "mclaren=mp4_13 ferrari=f300 williams=fw20 jordan=j198 benetton=b198 sauber=c17 arrows=a19 stewart=sf2 prost=ap01 tyrrell=026 minardi=m198"), {}),
    "1999": (1999, "motoren_1996_2000", SAUGER, 0.65, {},
             autos("f1_1999_", "ferrari mclaren jordan stewart williams benetton prost sauber arrows minardi bar"), {}),
    "2000_gp": (2000, "motoren_1996_2000", SAUGER, 0.65, {"masse": 600},
                autos("gp_2000_", "ferrari=f2000 mclaren=mp4_15 williams=fw22 benetton=b200 bar=bar_02 jordan=ej10 arrows=a21 sauber=c19 jaguar=r1 minardi=m02 prost=ap03"), {}),
    "2001": (2001, "motoren_2001_2007", SAUGER, 0.65, {"masse": 600},
             autos("f1_2001_", "ferrari mclaren williams sauber jordan bar benetton jaguar prost arrows minardi"), {}),
    "2002": (2002, "motoren_2001_2007", SAUGER, 0.65, {"masse": 600},
             autos("F1_2002_", "ferrari=Ferrari_F2002 williams=Williams_FW24_S1 williams_s2=Williams_FW24_S2:williams mclaren=McLaren_Mp4-17 renault=Renault_R202 sauber=Sauber_C21 jordan=Jordan_EJ12 jaguar=Jaguar_R3 bar=BAR_004 minardi=Minardi_PS02 toyota=Toyota_TF102 arrows=Arrows_A23"), {}),
    "2003": (2003, "motoren_2001_2007", SAUGER, 0.65, {"masse": 600},
             autos("f1_2003_", "ferrari williams mclaren renault bar sauber jaguar toyota jordan minardi"), {}),
    "2004": (2004, "motoren_2001_2007", SAUGER, 0.65, {"masse": 605, "ps_anker": 873, "abtrieb_bezug": 819},
             autos("F1_2004_", "ferrari=Ferrari_F2004_Kun bar=BAR_006 renault=Renault_R24 williams=Williams_FW26 williams_b=Williams_FW26_Vers_B:williams mclaren=McLaren_MP4-19 sauber=Sauber_C23 jaguar=Jaguar_R5 toyota=Toyota_TF104 jordan=Jordan_EJ14 minardi=Minardi_PS04B"), {}),
    "2006_cim": (2006, "motoren_2001_2007", SAUGER, 0.65, {"ps_anker": 707},
                 autos("cim_2006_", "renault ferrari mclaren honda bmw_sauber=bmw_sauber:bmw-sauber toyota redbull=redbull:red-bull williams tororosso=tororosso:toro-rosso midland superaguri=superaguri:super-aguri"),
                 {k: {"s_sonst": 0.3} for k in ("ferrari", "toyota", "williams", "midland", "superaguri")}),
    "2007": (2007, "motoren_2001_2007", SAUGER, 0.65, {},
             autos("cim_2007_", "mclaren ferrari bmw_sauber=bmw_sauber:bmw-sauber renault williams redbull=redbull:red-bull toyota tororosso=tororosso:toro-rosso honda=honda_V2 superaguri=superaguri:super-aguri spyker"), {}),
    "2011": (2011, "motoren_2011_2026", SAUGER, 0.65, {"ps_anker": 694},
             autos("cim_2011_", "redbull=redbull:red-bull mclaren ferrari mercedes renault forceindia=forceindia:force-india sauber tororosso=tororosso:toro-rosso williams lotus=lotus:lotus-racing hrt virgin"), {}),
    "2013": (2013, "motoren_2011_2026", SAUGER, 0.65, {},
             autos("cim_2013_", "redbull=redbull:red-bull mercedes ferrari lotus=lotus:lotus-f1 mclaren forceindia=forceindia:force-india sauber tororosso=tororosso:toro-rosso williams marussia caterham"), {}),
    "2014": (2014, "motoren_2011_2026", HYBRID, 0.80, {"masse": 691},
             autos("f1_2014_", "mercedes=mercedes_w05 redbull=red_bull_rb10:red-bull williams=williams_fw36 ferrari=ferrari_f14_t mclaren=mclaren_mp4_29 forceindia=force_india_vjm07:force-india tororosso=toro_rosso_str9:toro-rosso lotus=lotus_e22:lotus-f1 marussia=marussia_mr03 sauber=sauber_c33 caterham=caterham_ct05"), {}),
    # 2025: acht Autos der Deploy/Senna-Familie in zwei Physik-Ständen (Aston Martin und Racing Bulls: weniger Reifengrip,
    # mehr Abtrieb, anderer Motor). Deshalb Reifen, Motorkurve und die sieben gemeinsamen Flügel (BODY bis HALO) des McLaren
    # für alle, danach die Teamfaktoren. Eigene Zusatzflügel (Index 7 und höher) bleiben, damit Setup und DRS passen.
    # Alpine und Haas (SuzQ, anderes Modell) sind nicht dabei.
    "2025": (2025, "motoren_2011_2026", HYBRID, 0.80, {"masse": 800, "angleichen": {"referenz": "mclaren", "dateien": ["tyres.ini", "power.lut"], "aero_fluegel": 7}},
             autos("", "mclaren=mclaren_mcl39 redbull=red_bull_rb21:red-bull mercedes=mercedes_w16 ferrari=ferrari_sf25 williams=williams_fw47 racingbulls=racingbulls_rb02:racing-bulls astonmartin=aston_martin_amr25:aston-martin sauber=forbys_sauber_c45:kick-sauber"), {}),
    "2026": (2026, "motoren_2011_2026", HYBRID, 0.80, {"masse": 768},
             autos("f1_2026_", "mclaren=mclaren_mcl40 mercedes=mercedes_amg_w17 redbull=redbull_rb22:red-bull ferrari=ferrari_sf26 williams=williams_fw48 racingbulls=rb_vcarb03:racing-bulls astonmartin=aston_martin_amr26:aston-martin haas=haas_vf26 audi=audi_r26 alpine=alpine_a526 cadillac=cadillac_mac26"), {}),
}

# Luftwiderstands-Vorschläge der Recherche, die nur auf Textaussagen beruhen: nicht übernommen.
SCHWACH_BELEGT = {(1993, "lola"), (1993, "larrousse"), (1994, "pacific"), (1994, "benetton"), (2025, "williams"), (2025, "mercedes")}

# Von Hand festgelegte Werte je Satz und Team (nach Tests oder auf Wunsch), überschreiben die Rechnung.
FEST = {
    "1990": {"life": {"cl": 0.65}},      # ohne Quali-Zeit: Abtrieb an der Untergrenze, dazu der schwache W12

    # Die Mod gibt dem FW36 rund 25 % mehr Luftwiderstand als dem Mercedes; real war er das Auto mit dem wenigsten
    # Luftwiderstand. 0.77 bringt ihn auf Mercedes x 0.96 (Vorschlag der Recherche).
    "2014": {"williams": {"cd": 0.77, "_cd": "Luftwiderstand der Mod korrigiert: Ziel Mercedes x 0.96 (Speed-Trap 2014)"}},
    # 2026: Das recherchierte Übergewicht einzelner Autos (Williams +26 kg) wird nicht gesetzt. Wunsch des Nutzers:
    # Fahrphysik und Gewicht bei allen gleich, Unterschiede nur über Leistung, Abtrieb und Luftwiderstand.
}


def main():
    quali = json.loads((DATA / "quali_abstaende.json").read_text(encoding="utf-8"))
    for name, (jahr, datei, e, cl_min, zusatz, cars, extra) in SAETZE.items():
        if not (RES / f"{datei}.json").is_file():
            print(f"teams_{name}.json: research/{datei}.json fehlt, übersprungen"); continue
        res = json.loads((RES / f"{datei}.json").read_text(encoding="utf-8"))[str(jahr)]
        konzept = {k["team"]: k for k in res.get("konzept", []) if k.get("cd") and k.get("beleg", "gut") == "gut"}
        ohne_kers = set(res.get("ohne_kers", []))
        teams = {}
        for key, (ordner, fid) in cars.items():
            rk = key.split("_s2")[0].replace("williams_b", "williams").replace("caterham_late", "caterham")
            m = res["teams"][rk]
            t = {"ordner": ordner, **({"abstand": quali[str(jahr)][fid][0]} if fid in quali[str(jahr)] else {}), "ps": int(round(m["ps"])),
                 "_motor": f"{m['motor']} ({m.get('sicher', '?')}" + (f", {m['spanne']}" if m.get("spanne") else "") + ")"}
            if rk in konzept and (jahr, rk) not in SCHWACH_BELEGT:
                t["cd"] = min(1.08, max(0.95, konzept[rk]["cd"])); t["_cd"] = konzept[rk]["grund"]
            if rk in ohne_kers: t["ohne_kers"] = True
            t.update(extra.get(key, {})); t.update(FEST.get(name, {}).get(key, {}))
            teams[key] = t
        plan = {"_hinweis": f"Erzeugt von tools/plaene_bauen.py. abstand aus data/quali_abstaende.json (F1DB), ps und cd aus research/{datei}.json "
                            "(Schätzungen mit Quellen). Empfindlichkeiten stammen aus den Tests der V8-Jahrgänge bzw. der Hybrid-Autos und sind "
                            "für diesen Satz ungeprüft.",
                "jahr": jahr, "absolut": True, "cl_min": cl_min, "empfindlichkeit": e, **zusatz, "teams": teams}
        (DATA / f"teams_{name}.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"teams_{name}.json: {len(teams)} Autos")


if __name__ == "__main__":
    main()
