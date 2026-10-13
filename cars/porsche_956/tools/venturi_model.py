"""Venturi-Unterboden-Modell für den Porsche 956 (Kurzheck, Ring 1983).

Erzeugt die CSP-Aero-Map-Kennfelder (2D-LUTs über Bodenfreiheit vorn und hinten) sowie
Diagramme, mit denen die Abstimmung vor dem Spieltest geprüft werden kann.

  python venturi_model.py            Kennfelder und Diagramme nach ../physics/data/aero und ./out
  python venturi_model.py --show     zusätzlich Kennzahlen ausgeben

Alle Parameter stehen in CONFIG und sind Schätzwerte aus research/01-technische-daten.md.
Sie werden gegen Rundenzeiten und Fahrgefühl im Spiel kalibriert.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np

RHO = 1.225
G = 9.81
HERE = Path(__file__).resolve().parent
AERO_DIR = HERE.parent / "physics" / "data" / "aero"
OUT_DIR = HERE / "out"


@dataclass
class Config:
    # Zielwerte Gesamtauto bei Referenzgeschwindigkeit (Kurzheck, Schätzung)
    v_ref_kmh: float = 322.0
    total_downforce_kg: float = 1900.0      # Langheck ~1050 kg, Kurzheck ~doppelt; 962 (1993) 2540 kg. Siehe research/03
    total_drag_kg: float = 640.0            # L/D 3.0; Motor Sport nennt 2.75 für den 956, 962 (1993) 4.0
    underbody_share: float = 0.60           # Anteil des Unterbodens am Gesamtabtrieb bei Design-Bodenfreiheit
    front_balance_total: float = 0.42       # Anteil Vorderachse am Gesamtabtrieb bei Design-Höhe

    # Design-Bodenfreiheit (statisch bei Stillstand, Fahrzeug steht auf dem Flachboden-Maß)
    h_front_design: float = 0.055           # m
    h_rear_design: float = 0.085            # m

    # Unterboden-Kennfeld
    rear_exponent: float = 0.75             # Abtrieb ~ (h_ref/h_r)^n im gesunden Bereich
    front_exponent: float = 0.35            # Einfluss der vorderen Halshöhe (Singer-Delle)
    rake_gain: float = 6.0                  # Abtriebsgewinn pro Meter zusätzlicher Rake (h_r - h_f)
    rake_design: float = 0.030              # Rake bei Design-Höhe
    h_rear_stall: float = 0.030             # darunter Strömungsabriss im Diffusor
    h_front_stall: float = 0.012            # darunter Abriss am vorderen Hals
    stall_width: float = 0.008              # Breite des Übergangs in m
    stall_floor: float = 0.35               # Restabtrieb nach Abriss (Anteil)
    rake_stall: float = 0.075               # Rake, ab dem der Diffusor ablöst
    plateau_gain: float = 2.4               # Bereich B der Literatur: weiches Maximum relativ zur Design-Höhe
    plateau_softness: float = 0.35          # Weichheit des Übergangs in das Plateau

    # Balance des Unterbodens
    ub_front_balance: float = 0.40          # Anteil vorn bei Design-Höhe
    balance_rake_gain: float = -2.5         # pro Meter Rake: mehr Rake, Balance nach hinten (Diffusor arbeitet)
    balance_front_low_gain: float = 1.2     # vorn tief: Balance nach vorn

    # Unterboden-Widerstand: Grundanteil plus induziert
    ub_drag_base: float = 0.06              # Cd·A
    ub_drag_induced: float = 0.025          # Cd·A pro (Cl·A)^2

    # Gier: Tunnel verlieren Anströmung
    yaw_cl: tuple = ((0, 1.00), (5, 0.96), (10, 0.88), (15, 0.78), (20, 0.65), (30, 0.50))
    yaw_balance: tuple = ((0, 0.0), (10, 0.02), (20, 0.05))

    # Fahrwerk für das Gleichgewicht (Schätzung, Federraten des 956 nicht dokumentiert)
    mass_kg: float = 820.0
    weight_front: float = 0.44
    wheel_rate_front_n_mm: float = 140.0    # pro Rad
    wheel_rate_rear_n_mm: float = 190.0     # pro Rad
    bump_rubber_front: float = 0.018        # Restweg bis Anschlag ab Design-Höhe
    bump_rubber_rear: float = 0.045
    bump_rubber_rate_mult: float = 6.0      # Anschlagpuffer-Verhärtung

    # Flügel (bleiben als [WING] in AC): Rest des Gesamtabtriebs
    wing_rear_share: float = 0.28
    wing_front_share: float = 0.12


def q_dyn(v_kmh: float) -> float:
    v = v_kmh / 3.6
    return 0.5 * RHO * v * v


def smoothstep(x: np.ndarray, x0: float, w: float) -> np.ndarray:
    """0 unterhalb x0-w, 1 oberhalb x0+w, weich dazwischen."""
    t = np.clip((x - (x0 - w)) / (2 * w), 0, 1)
    return t * t * (3 - 2 * t)


class Underbody:
    def __init__(self, cfg: Config):
        self.c = cfg
        q = q_dyn(cfg.v_ref_kmh)
        self.cla_total = cfg.total_downforce_kg * G / q
        self.cda_total = cfg.total_drag_kg * G / q
        self.cla_ub_design = self.cla_total * cfg.underbody_share
        self.cla_wing_rear = self.cla_total * cfg.wing_rear_share
        self.cla_wing_front = self.cla_total * cfg.wing_front_share

    def gain(self, hf: np.ndarray, hr: np.ndarray) -> np.ndarray:
        """Relativer Abtrieb des Unterbodens gegenüber Design-Höhe."""
        c = self.c
        hr_s = np.maximum(hr, 1e-3)
        hf_s = np.maximum(hf, 1e-3)
        base = (c.h_rear_design / hr_s) ** c.rear_exponent * (c.h_front_design / hf_s) ** c.front_exponent
        rake = hr - hf
        base *= 1 + c.rake_gain * (rake - c.rake_design)
        # Bereich A geht weich in das Plateau B über (softmin), statt hart zu kappen
        base = np.maximum(base, 0.05)
        k = c.plateau_softness
        base = -k * np.log(np.exp(-base / k) + np.exp(-c.plateau_gain / k))
        # Abriss: hinten zu tief, vorn zu tief, oder Diffusorwinkel zu steil
        healthy = smoothstep(hr, c.h_rear_stall, c.stall_width) \
            * smoothstep(hf, c.h_front_stall, c.stall_width) \
            * (1 - smoothstep(rake, c.rake_stall, c.stall_width * 2))
        return base * (c.stall_floor + (1 - c.stall_floor) * healthy)

    def cla(self, hf, hr):
        return self.cla_ub_design * self.gain(hf, hr)

    def cda(self, hf, hr):
        cl = self.cla(hf, hr)
        return self.c.ub_drag_base + self.c.ub_drag_induced * cl ** 2

    def balance(self, hf, hr):
        c = self.c
        rake = hr - hf
        b = c.ub_front_balance + c.balance_rake_gain * (rake - c.rake_design) \
            + c.balance_front_low_gain * (c.h_front_design - hf)
        return np.clip(b, 0.15, 0.75)


def write_2dlut(path: Path, xs: np.ndarray, ys: np.ndarray, table: np.ndarray, fmt="%.4f") -> None:
    lines = ["\t" + "\t".join(fmt % x for x in xs)]
    for y, row in zip(ys, table):
        lines.append((fmt % y) + "\t" + "\t".join(fmt % v for v in row))
    path.write_text("\n".join(lines) + "\n")


def write_lut(path: Path, pairs) -> None:
    path.write_text("".join(f"{a}|{b}\n" for a, b in pairs))


def equilibrium(ub: Underbody, cfg: Config, v_kmh: float) -> tuple[float, float, float, float]:
    """Statische Einfederung bei Geschwindigkeit v. Liefert (hf, hr, Abtrieb vorn N, Abtrieb hinten N)."""
    q = q_dyn(v_kmh)
    hf, hr = cfg.h_front_design, cfg.h_rear_design
    kf = 2 * cfg.wheel_rate_front_n_mm * 1000
    kr = 2 * cfg.wheel_rate_rear_n_mm * 1000
    for _ in range(200):
        cl = float(ub.cla(np.array(hf), np.array(hr)))
        bal = float(ub.balance(np.array(hf), np.array(hr)))
        f_ub = q * cl
        f_front = f_ub * bal + q * ub.cla_wing_front
        f_rear = f_ub * (1 - bal) + q * ub.cla_wing_rear
        def deflect(force, k, travel):
            x = force / k
            if x > travel:
                x = travel + (force - k * travel) / (k * cfg.bump_rubber_rate_mult)
            return x
        hf_new = cfg.h_front_design - deflect(f_front, kf, cfg.bump_rubber_front)
        hr_new = cfg.h_rear_design - deflect(f_rear, kr, cfg.bump_rubber_rear)
        hf_new, hr_new = max(hf_new, 0.004), max(hr_new, 0.006)
        if abs(hf_new - hf) < 1e-5 and abs(hr_new - hr) < 1e-5:
            hf, hr = hf_new, hr_new
            break
        hf, hr = 0.5 * (hf + hf_new), 0.5 * (hr + hr_new)
    return hf, hr, f_front, f_rear


def build(cfg: Config, show: bool) -> dict:
    ub = Underbody(cfg)
    AERO_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    hf_axis = np.round(np.arange(0.005, 0.1001, 0.005), 4)
    hr_axis = np.round(np.arange(0.010, 0.1501, 0.005), 4)
    HF, HR = np.meshgrid(hf_axis, hr_axis)
    CL, CD, BAL = ub.cla(HF, HR), ub.cda(HF, HR), ub.balance(HF, HR)

    write_2dlut(AERO_DIR / "underbody_cl_rh.2Dlut", hf_axis, hr_axis, CL)
    write_2dlut(AERO_DIR / "underbody_cd_rh.2Dlut", hf_axis, hr_axis, CD)
    write_2dlut(AERO_DIR / "underbody_balance_rh.2Dlut", hf_axis, hr_axis, BAL, fmt="%.3f")
    write_lut(AERO_DIR / "underbody_yaw_cl.lut", cfg.yaw_cl)
    write_lut(AERO_DIR / "underbody_yaw_balance.lut", cfg.yaw_balance)

    speeds = np.arange(50, 361, 10)
    eq = np.array([equilibrium(ub, cfg, v) for v in speeds])
    summary = {
        "cla_total_design": round(ub.cla_total, 3),
        "cda_total_design": round(ub.cda_total, 3),
        "cla_underbody_design": round(ub.cla_ub_design, 3),
        "cla_wing_rear": round(ub.cla_wing_rear, 3),
        "cla_wing_front": round(ub.cla_wing_front, 3),
        "downforce_kg_at_v_ref_design_height": round(ub.cla_total * q_dyn(cfg.v_ref_kmh) / G),
        "equilibrium": [
            {"v_kmh": int(v), "h_front_mm": round(hf * 1000, 1), "h_rear_mm": round(hr * 1000, 1),
             "downforce_kg": round((ff + fr) / G), "front_balance": round(ff / (ff + fr), 3)}
            for v, (hf, hr, ff, fr) in zip(speeds, eq)
        ],
        "config": asdict(cfg),
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(15, 11))
    im = ax[0, 0].contourf(hf_axis * 1000, hr_axis * 1000, CL * q_dyn(cfg.v_ref_kmh) / G, 24, cmap="viridis")
    ax[0, 0].set_xlabel("Bodenfreiheit vorn mm"); ax[0, 0].set_ylabel("Bodenfreiheit hinten mm")
    ax[0, 0].set_title(f"Unterboden-Abtrieb kg bei {cfg.v_ref_kmh:.0f} km/h"); fig.colorbar(im, ax=ax[0, 0])
    ax[0, 0].plot(eq[:, 0] * 1000, eq[:, 1] * 1000, "w.-", lw=1, label="Gleichgewicht 50 bis 360 km/h"); ax[0, 0].legend()
    im = ax[0, 1].contourf(hf_axis * 1000, hr_axis * 1000, BAL, 24, cmap="coolwarm")
    ax[0, 1].set_title("Unterboden-Balance Anteil vorn"); ax[0, 1].set_xlabel("vorn mm"); ax[0, 1].set_ylabel("hinten mm")
    fig.colorbar(im, ax=ax[0, 1])
    ax[1, 0].plot(speeds, eq[:, 0] * 1000, label="vorn"); ax[1, 0].plot(speeds, eq[:, 1] * 1000, label="hinten")
    ax[1, 0].axhline(cfg.h_rear_stall * 1000, ls="--", c="r", label="Abriss hinten"); ax[1, 0].axhline(cfg.h_front_stall * 1000, ls=":", c="r", label="Abriss vorn")
    ax[1, 0].set_xlabel("km/h"); ax[1, 0].set_ylabel("Bodenfreiheit mm"); ax[1, 0].set_title("Einfederung über Geschwindigkeit"); ax[1, 0].legend(); ax[1, 0].grid()
    ax[1, 1].plot(speeds, (eq[:, 2] + eq[:, 3]) / G, label="gesamt"); ax[1, 1].plot(speeds, eq[:, 2] / G, label="vorn"); ax[1, 1].plot(speeds, eq[:, 3] / G, label="hinten")
    ax[1, 1].set_xlabel("km/h"); ax[1, 1].set_ylabel("Abtrieb kg"); ax[1, 1].set_title("Abtrieb über Geschwindigkeit (mit Einfederung)"); ax[1, 1].legend(); ax[1, 1].grid()
    fig.tight_layout(); fig.savefig(OUT_DIR / "venturi_model.png", dpi=110)

    if show:
        print(f"Cl·A gesamt {ub.cla_total:.2f} m²  Cd·A {ub.cda_total:.2f} m²  L/D {ub.cla_total / ub.cda_total:.2f}")
        print(f"Unterboden Cl·A {ub.cla_ub_design:.2f}, Heckflügel {ub.cla_wing_rear:.2f}, Front {ub.cla_wing_front:.2f}")
        print(f"{'km/h':>5} {'hf mm':>6} {'hr mm':>6} {'kg':>6} {'vorn':>5}")
        for e in summary["equilibrium"]:
            print(f"{e['v_kmh']:>5} {e['h_front_mm']:>6} {e['h_rear_mm']:>6} {e['downforce_kg']:>6} {e['front_balance']:>5.2f}")
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()
    build(Config(), a.show)
    print(f"Kennfelder: {AERO_DIR}\nDiagramm:   {OUT_DIR / 'venturi_model.png'}")


if __name__ == "__main__":
    main()
