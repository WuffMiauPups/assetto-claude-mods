"""Dirty-Air-Modell: Abtriebsverlust des Verfolgers als Funktion von Abstand, seitlichem Versatz und Ära.

  python dirty_air_model.py        schreibt research/data/dirty_air_<era>.lut und tools/out/dirty_air.png

Stützwerte (verbleibender Abtrieb des Verfolgers, geradeaus, zwei identische Autos, FIA-CFD laut The Race):
  2019:              55 Prozent bei 10 m, 65 Prozent bei 20 m
  2022 Baseline:     85 Prozent bei 10 m, 95 Prozent bei 20 m
  2024/2025 real:    etwa 80 Prozent bei 20 m (Entwicklung hat den Gewinn aufgezehrt)
  2026 Ziel:         80 Prozent bei 10 m, 90 Prozent bei 20 m
Ältere Ären ohne Messwerte sind relativ dazu geschätzt (siehe research/dirty-air.md).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "research" / "data"
OUT = HERE / "out"


@dataclass
class Era:
    name: str
    retained_10m: float      # verbleibender Gesamtabtrieb bei 10 m
    retained_20m: float      # bei 20 m
    front_share: float = 1.35  # Verlust vorn relativ zum Gesamtverlust
    rear_share: float = 0.75   # Verlust hinten relativ zum Gesamtverlust
    wake_half_width_10m: float = 1.1   # seitliche Halbwertsbreite des Nachlaufs in m bei 10 m
    wake_spread: float = 0.06          # Zuwachs der Halbwertsbreite pro Meter Abstand
    years: str = ""
    source: str = ""


ERAS = [
    Era("1988_turbo", 0.70, 0.80, years="1988", source="geschätzt: niedrige Flügelabhängigkeit, flacher Boden, moderate Nachläufe"),
    Era("1993_1994", 0.62, 0.74, years="1993-1994", source="geschätzt: aktive Aufhängung und Diffusoren, deutlicher Verlust"),
    Era("1996_2004", 0.55, 0.68, years="1996-2004", source="geschätzt: hohe Flügelabhängigkeit, Vorläufer der 2019-Werte"),
    Era("2005_2008", 0.52, 0.64, years="2005-2008", source="geschätzt: OWG stellte 2008 massive Verluste fest, Ziel war minus 50 Prozent Abtrieb"),
    Era("2009_2013", 0.60, 0.72, years="2009-2013", source="geschätzt: OWG-Regeln halfen, Doppeldiffusor und Auspuff-Anblasen fraßen den Gewinn teils auf"),
    Era("2014_2016", 0.58, 0.70, years="2014-2016", source="geschätzt: zwischen 2009-Regeln und 2017"),
    Era("2017_2021", 0.55, 0.65, years="2017-2021", source="FIA-CFD 2019 laut The Race: 55 Prozent bei 10 m, 65 Prozent bei 20 m"),
    Era("2022_2025", 0.72, 0.82, years="2022-2025", source="FIA-CFD 2022 Baseline 85/95, bis 2024 auf etwa 80 Prozent bei 20 m verschlechtert; Mittelwert"),
    Era("2026", 0.80, 0.90, years="2026", source="FIA-Ziel laut The Race"),
]


def loss_curve(era: Era, d: np.ndarray) -> np.ndarray:
    """Gesamtverlust (0 bis 1) über Abstand in m, exponentieller Abfall durch die beiden Stützpunkte."""
    l10, l20 = 1 - era.retained_10m, 1 - era.retained_20m
    lam = 10.0 / np.log(l10 / l20) if l20 < l10 else 50.0
    l0 = l10 * np.exp(10.0 / lam)
    loss = l0 * np.exp(-d / lam)
    return np.clip(loss, 0, 0.85)


def lateral_factor(era: Era, d: np.ndarray, offset: np.ndarray) -> np.ndarray:
    w = era.wake_half_width_10m + era.wake_spread * (d - 10.0)
    w = np.maximum(w, 0.6)
    return np.exp(-0.5 * (offset / w) ** 2)


def build():
    DATA.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)
    d = np.arange(0, 80.1, 2.0)
    offsets = np.arange(0, 4.01, 0.5)
    summary = {}
    for era in ERAS:
        loss = loss_curve(era, d)
        lines = ["; Abstand m | Gesamtverlust | Verlust vorn | Verlust hinten (Anteil 0..1), " + era.name,
                 "; " + era.source]
        for di, li in zip(d, loss):
            lines.append(f"{di:.0f}|{li:.3f}|{min(li * era.front_share, 0.9):.3f}|{li * era.rear_share:.3f}")
        (DATA / f"dirty_air_{era.name}.lut").write_text("\n".join(lines) + "\n")
        lat = ["; seitlicher Versatz m | Faktor bei 10 m | bei 20 m | bei 40 m"]
        for o in offsets:
            lat.append(f"{o:.1f}|{lateral_factor(era, np.array(10.0), o):.3f}|{lateral_factor(era, np.array(20.0), o):.3f}|{lateral_factor(era, np.array(40.0), o):.3f}")
        (DATA / f"dirty_air_{era.name}_lateral.lut").write_text("\n".join(lat) + "\n")
        summary[era.name] = {"years": era.years, "retained_10m": era.retained_10m, "retained_20m": era.retained_20m,
                             "loss_5m": round(float(loss_curve(era, np.array(5.0))), 3),
                             "loss_10m": round(1 - era.retained_10m, 3), "loss_20m": round(1 - era.retained_20m, 3),
                             "loss_40m": round(float(loss_curve(era, np.array(40.0))), 3), "source": era.source}
    (DATA / "dirty_air_summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(15, 6))
    for era in ERAS:
        ax[0].plot(d, 100 * (1 - loss_curve(era, d)), label=f"{era.name} ({era.years})")
    ax[0].axvline(10, ls=":", c="gray"); ax[0].axvline(20, ls=":", c="gray")
    ax[0].set_xlabel("Abstand zum Vordermann m"); ax[0].set_ylabel("verbleibender Abtrieb %"); ax[0].set_title("Abtrieb des Verfolgers, geradeaus hinter dem Vordermann")
    ax[0].grid(); ax[0].legend(fontsize=8); ax[0].set_ylim(30, 100)
    era = ERAS[6]
    O, D = np.meshgrid(np.arange(-4, 4.01, 0.1), np.arange(2, 60, 1.0))
    L = loss_curve(era, D) * lateral_factor(era, D, np.abs(O))
    im = ax[1].contourf(O, D, 100 * L, 20, cmap="magma_r"); fig.colorbar(im, ax=ax[1], label="Gesamtverlust %")
    ax[1].set_xlabel("seitlicher Versatz m"); ax[1].set_ylabel("Abstand m"); ax[1].set_title(f"Nachlauf-Karte {era.name}")
    fig.tight_layout(); fig.savefig(OUT / "dirty_air.png", dpi=110)
    for k, v in summary.items():
        print(f"{k:12s} {v['years']:10s} Verlust bei 5/10/20/40 m: {v['loss_5m']:.2f} {v['loss_10m']:.2f} {v['loss_20m']:.2f} {v['loss_40m']:.2f}")


if __name__ == "__main__":
    build()
