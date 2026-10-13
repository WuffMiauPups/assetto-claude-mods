"""Roundtrip-Test und synthetische Pipeline. Ausführen: python tests/test_roundtrip.py"""
import sys, tempfile, subprocess
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastlane import AILine, read_ai, write_ai, resample, curvature, arc_length, speed_profile, VehicleLimits
from fastlane.speed import lap_time


def synthetic_track(n=400):
    """Monza-ähnliches Oval mit Schikane: zwei lange Geraden, enge Kurven."""
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    x = 900 * np.cos(t) + 60 * np.cos(5 * t)
    z = 350 * np.sin(t) + 40 * np.sin(3 * t)
    y = 2 * np.sin(2 * t)
    return np.column_stack([x, y, z]).astype(np.float32)


def test_roundtrip(tmp):
    pos = resample(synthetic_track(), 4.0)
    n = len(pos)
    line = AILine.empty(n)
    line.position[:] = pos
    line.length[:] = arc_length(np.vstack([pos, pos[:1]]))[:-1]
    line.extra[:] = np.random.default_rng(0).random((n, 18)).astype(np.float32)
    p = tmp / "fast_lane.ai"
    write_ai(line, p)
    back = read_ai(p)
    assert len(back) == n
    assert np.allclose(back.position, line.position)
    assert np.allclose(back.length, line.length)
    assert np.allclose(back.extra, line.extra)
    assert p.stat().st_size == 16 + n * (20 + 72)
    print("roundtrip ok,", back.summary())


def test_speed_profile():
    pos = resample(synthetic_track(), 2.0)
    s = arc_length(np.vstack([pos, pos[:1]]))
    k = curvature(pos)
    v = speed_profile(k, s, VehicleLimits(margin=1.0))
    assert v.min() > 5 and v.max() * 3.6 <= 300.01
    print(f"speed profile ok: {v.min()*3.6:.0f}..{v.max()*3.6:.0f} km/h, Runde {lap_time(v, s[:-1]):.1f} s")


def test_build_pipeline(tmp):
    """Synthetische Telemetrie schreiben, build.py laufen lassen, Ergebnis lesen."""
    pos = resample(synthetic_track(), 3.0)
    n = len(pos)
    rows = []
    t = 0.0
    for lap in range(2):
        for i in range(n):
            spline = i / n
            rows.append(f"{t:.3f},{lap},{spline:.5f},{pos[i,0]:.2f},{pos[i,1]:.2f},{pos[i,2]:.2f},"
                        f"{150+lap:.1f},0.8,0.0,0.01,0.0,5.0,5.0")
            t += 0.05
    csv = tmp / "lap.csv"
    csv.write_text("t,lap,spline,x,y,z,speed,gas,brake,steer,yaw_rate,track_left,track_right\n" + "\n".join(rows))
    out = tmp / "out" / "fast_lane.ai"
    r = subprocess.run([sys.executable, "scripts/build.py", "--laps", str(csv), "--out", str(out), "--margin", "0.97"],
                       capture_output=True, text=True, cwd=Path(__file__).resolve().parents[1])
    print(r.stdout); assert r.returncode == 0, r.stderr
    line = read_ai(out)
    assert abs(line.total_length - arc_length(np.vstack([pos, pos[:1]]))[-1]) < 20
    r = subprocess.run([sys.executable, "scripts/analyse.py", str(out)], capture_output=True, text=True,
                       cwd=Path(__file__).resolve().parents[1])
    print(r.stdout); assert r.returncode == 0, r.stderr
    return out


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        test_roundtrip(tmp)
        test_speed_profile()
        out = test_build_pipeline(tmp)
        import shutil; shutil.copy(str(out) + ".png", "/tmp/claude-0/-home-user-assetto-claude-mods/c22b9a1f-5d0e-5949-8457-13658f58b47c/scratchpad/synthetic.png")
    print("ALLE TESTS OK")
