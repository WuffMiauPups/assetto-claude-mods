"""Baut data/teams_2019.json und data/teams_2020.json für die Team-Autos aus den Formula Hybrids von RSS.

  py -3.11 plaene_hybrid.py

Gleiche Form wie teams_2018.json (für team_autos.py und team_staerke.py, Modus "quelle"). abstand aus
data/quali_abstaende.json (F1DB), ps und cd aus research/motoren_2019_2020.json. Solange die Recherche-Datei fehlt,
entstehen die Pläne ohne ps (reicht für team_autos.py). Von Hand nachgestellte Werte in FEST eintragen.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA, RES = HERE.parent / "data", HERE.parent / "research" / "motoren_2019_2020.json"

# schlüssel: (Name, F1DB-Id, Skins)
TEAMS = {
    2019: {
        "mercedes": ("Mercedes W10", "mercedes", ["44_Hamilton_Mercedes_W10", "77_Bottas_Mercedes_W10"]),
        "ferrari": ("Ferrari SF90", "ferrari", ["05_Vettel_Ferrari_SF-90", "16_Leclerc_Ferrari_SF-90"]),
        "redbull": ("Red Bull RB15", "red-bull", ["10_Red_Bull", "33_Red_Bull"]),
        "mclaren": ("McLaren MCL34", "mclaren", ["04_Norris_McLaren_MCL34_Spa", "55_Sainz_McLaren_MCL34_Spa"]),
        "haas": ("Haas VF-19", "haas", ["08_Haas_VF19_Grosjean_FH_4K", "20_Haas_VF19_Magnussen_FH_4K"]),
        "renault": ("Renault R.S.19", "renault", ["03_Renault", "27_Renault"]),
        "tororosso": ("Toro Rosso STR14", "toro-rosso", ["23_Toro_Rosso", "26_Toro_Rosso"]),
        "alfaromeo": ("Alfa Romeo C38", "alfa-romeo", ["07_Kimi_Räikkönen", "99_Antonio_Giovinazzi"]),
        "racingpoint": ("Racing Point RP19", "racing-point", ["11_Racing_Point", "18_Racing_Point"]),
        "williams": ("Williams FW42", "williams", ["RSS_F1_2019_Rokit_Williams_Racing_63", "RSS_F1_2019_Rokit_Williams_Racing_88"]),
    },
    2020: {
        "mercedes": ("Mercedes W11", "mercedes", ["a_44_Mercedes-AMG_F1_W11_EQ_Performance", "b_77_Mercedes-AMG_F1_W11_EQ_Performance"]),
        "redbull": ("Red Bull RB16", "red-bull", ["e_33_Red_Bull_Racing_RB16", "f_23_Red_Bull_Racing_RB16"]),
        "racingpoint": ("Racing Point RP20", "racing-point", ["m_11_Racing_Point_RP20", "n_18_Racing_Point__RP20"]),
        "mclaren": ("McLaren MCL35", "mclaren", ["g_55_McLaren_MCL35", "h_4_McLaren_MCL35"]),
        "ferrari": ("Ferrari SF1000", "ferrari", ["c_5_Ferrari_SF1000", "d_16_Ferrari_SF1000"]),
        "alphatauri": ("AlphaTauri AT01", "alphatauri", ["k_26_Scuderia_AlphaTauri_AT01", "l_10_Scuderia_AlphaTauri_AT01"]),
        "renault": ("Renault R.S.20", "renault", ["i_3_Renault_R.S.20", "j_31_Renault_R.S.20"]),
        "williams": ("Williams FW43", "williams", ["s_63_Williams_FW43", "t_6_Williams_FW43"]),
        "alfaromeo": ("Alfa Romeo C39", "alfa-romeo", ["o_7_Alfa_Romeo_Racing_C39", "p_99_Alfa_Romeo_Racing_C39"]),
        "haas": ("Haas VF-20", "haas", ["q_8_Haas_VF-20", "r_20_Haas_VF-20"]),
    },
}
# Nur die gut belegten Luftwiderstands-Faktoren der Recherche gelten (Ferrari 2019 0,97 und 2020 1,05); die schwach
# belegten stehen hier auf 1,0. Williams: Abtrieb bei 0,82 gedeckelt wie 2018, 2019 der Rest über den Luftwiderstand
# (der FW42 hatte wenig Abtrieb und viel Luftwiderstand).
FEST = {2019: {"mercedes": {"cd": 1.0}, "williams": {"cl": 0.82, "cd": 1.08}},
        2020: {"redbull": {"cd": 1.0}, "renault": {"cd": 1.0}, "williams": {"cl": 0.82, "cd": 1.0}}}
CL_MIN = 0.82                    # darunter bricht die KI ein (Sauber 2017, Williams 2018); Rest über cd


def main():
    quali = json.loads((DATA / "quali_abstaende.json").read_text(encoding="utf-8"))
    res = json.loads(RES.read_text(encoding="utf-8")) if RES.is_file() else {}
    for jahr, liste in TEAMS.items():
        r = res.get(str(jahr), {})
        konzept = {k["team"]: k for k in r.get("konzept", []) if k.get("cd")}
        teams = {}
        for key, (name, fid, skins) in liste.items():
            t = {"name": name, "skins": skins, "abstand": quali[str(jahr)][fid][0]}
            if key in r.get("teams", {}):
                m = r["teams"][key]
                t["ps"] = int(round(m["ps"])); t["_motor"] = f"{m['motor']} ({m.get('sicher', '?')}, {m.get('spanne', '')})"
            if key in konzept:
                t["cd"] = min(1.08, max(0.95, konzept[key]["cd"])); t["_cd"] = konzept[key]["grund"]
            t.update(FEST[jahr].get(key, {}))
            teams[key] = t
        plan = {"_hinweis": f"Team-Autos aus der Formula Hybrid {jahr} (RSS), erzeugt von tools/plaene_hybrid.py. Ordner = <quelle>_<schluessel>.",
                "_staerke": "abstand aus data/quali_abstaende.json (F1DB, 85-s-Runde), ps = Gesamtleistung und cd aus research/motoren_2019_2020.json "
                            "(Schätzungen mit Quellen). Empfindlichkeiten wie 2018, für dieses Auto ungeprüft.",
                "quelle": f"rss_formula_hybrid_{jahr}", "jahr": jahr,
                "empfindlichkeit": {"s_pro_prozent_abtrieb": 0.09, "s_pro_prozent_leistung": 0.16, "s_pro_prozent_widerstand": 0.04, "ers_ps": 163},
                "teams": teams}
        (DATA / f"teams_{jahr}.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"teams_{jahr}.json: {len(teams)} Teams" + ("" if r else ", noch ohne ps"))


if __name__ == "__main__":
    main()
