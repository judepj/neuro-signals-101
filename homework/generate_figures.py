"""Generate the two figures embedded in homework.pdf.

Uses the SAME parametric models as the website's Plotly.js widgets so the
visuals match what the student sees in the modules. Outputs at 300 dpi PNG.

Run from the homework/ directory or via absolute path; figures land in figures/.
"""

from pathlib import Path
import math
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────
# Shared seeded RNG matching the JS Lehmer generator used in the modules
# ──────────────────────────────────────────────────────────────────────────
def seeded_rand(seed):
    s = [seed]
    def f():
        s[0] = (s[0] * 16807) % 2147483647
        return (s[0] - 1) / 2147483646
    return f


# ──────────────────────────────────────────────────────────────────────────
# Figure 1 — phase-reversal bipolar trace (M5b)
# ──────────────────────────────────────────────────────────────────────────
def build_phase_reversal():
    sr = 500
    dur = 2.0
    t = np.arange(0, dur, 1 / sr)
    spike_t = 1.0
    spike_width = 0.03

    # Channel layout: each (name, falloff_relative_to_C3)
    # C3 sits at the source; F3 and P3 are neighbors with reduced amplitude;
    # Fp1 and O1 see almost nothing.
    site_falloff = {"Fp1": 0.10, "F3": 0.40, "C3": 1.00, "P3": 0.40, "O1": 0.10}

    rand = seeded_rand(42)
    background_phase = {k: rand() * 2 * math.pi for k in site_falloff}

    # Per-electrode raw voltage: alpha-rhythm background + spike at C3 with falloff
    def electrode(name):
        bg = 7 * np.sin(2 * math.pi * 10 * t + background_phase[name])
        # biphasic-ish negative spike (cortical surface-negative)
        spike = np.zeros_like(t)
        dt = t - spike_t
        amp = 90 * site_falloff[name]
        # sharp negative
        mask = (dt > -0.018) & (dt < 0.018)
        spike[mask] = -amp * np.exp(-(dt[mask] ** 2) / 4e-5)
        # slow positive recovery
        mask2 = (dt >= 0.018) & (dt < 0.20)
        spike[mask2] = 0.45 * amp * np.exp(-((dt[mask2] - 0.08) ** 2) / 0.003)
        return bg + spike

    V = {n: electrode(n) for n in site_falloff}

    chains = [("Fp1-F3", "Fp1", "F3"),
              ("F3-C3",  "F3",  "C3"),
              ("C3-P3",  "C3",  "P3"),
              ("P3-O1",  "P3",  "O1")]

    spacing = 90
    fig = go.Figure()
    yticks, ytext = [], []
    for i, (label, a, b) in enumerate(chains):
        ch = V[a] - V[b]
        offset = -i * spacing
        # negative-up: plot −ch + offset (clinical convention)
        fig.add_trace(go.Scatter(
            x=t, y=-ch + offset,
            mode="lines",
            line=dict(color="#2c3e50", width=1.4),
            hoverinfo="skip", showlegend=False,
        ))
        yticks.append(offset)
        ytext.append(label)

    # Vertical guide at the spike for visual orientation
    fig.add_vline(x=spike_t, line=dict(color="#bbbbbb", width=1, dash="dot"))

    fig.update_layout(
        xaxis=dict(title="Time (s)", range=[0, dur], showgrid=False, zeroline=False),
        yaxis=dict(
            tickvals=yticks, ticktext=ytext,
            range=[-spacing * len(chains) + 30, spacing * 0.6],
            tickfont=dict(size=11), showgrid=False, zeroline=False,
        ),
        margin=dict(l=70, r=20, t=30, b=50),
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        title=dict(text="4-channel bipolar EEG (negative-up clinical convention)",
                   font=dict(size=12, color="#555")),
    )
    out = OUT / "prob6_phase_reversal.png"
    fig.write_image(str(out), width=1950, height=1500, scale=1)
    print(f"  wrote {out.name}")


# ──────────────────────────────────────────────────────────────────────────
# Figure 2 — 4-artifact grid (M6)
# A=blink  B=muscle  C=60 Hz  D=ECG
# ──────────────────────────────────────────────────────────────────────────
def clean_eeg(seed=42, sr=500, dur=3.0):
    rand = seeded_rand(seed)
    t = np.arange(0, dur, 1 / sr)
    return t, np.array([
        25 * math.sin(2 * math.pi * 10 * ti + 0.3)
        + 10 * math.sin(2 * math.pi * 6 * ti + 1.2)
        + 5 * math.sin(2 * math.pi * 18 * ti + 0.7)
        + 8 * (rand() - 0.5)
        for ti in t
    ])


def gen_blink(t):
    """Asymmetric gamma-ish blink: fast rise ~80 ms, slow fall ~320 ms."""
    out = np.zeros_like(t)
    blinks = [0.7, 2.0]
    riseT, fallT = 0.08, 0.32
    for b in blinks:
        dt = t - b
        in_window = (dt >= 0) & (dt < riseT + fallT)
        rising = in_window & (dt < riseT)
        falling = in_window & ~rising
        out[rising] += 160 * np.sin(0.5 * math.pi * dt[rising] / riseT)
        fp = (dt[falling] - riseT) / fallT
        out[falling] += 160 * np.where(fp >= 1, 0, np.cos(0.5 * math.pi * fp))
    return out


def gen_muscle(t, sr=500):
    """Filtered white noise, burst envelope sin^2 over 0.75–1.85 s."""
    rand = seeded_rand(77)
    raw = np.array([rand() - 0.5 for _ in t])
    # AR(1) smoothing → high-frequency rough noise via first difference
    smoothed = np.zeros_like(raw)
    smoothed[0] = raw[0]
    a = 0.55
    for i in range(1, len(raw)):
        smoothed[i] = a * smoothed[i - 1] + (1 - a) * raw[i]
    rough = np.diff(smoothed, prepend=smoothed[0])
    env = np.where(
        (t >= 0.75) & (t <= 1.85),
        np.sin(math.pi * (t - 0.75) / 1.10) ** 2,
        0.02,
    )
    return rough * env * 600


def gen_line_noise(t):
    """60 Hz fundamental + tiny harmonics for realism."""
    return (14 * np.sin(2 * math.pi * 60 * t)
            + 1.5 * np.sin(2 * math.pi * 120 * t)
            + 0.8 * np.sin(2 * math.pi * 180 * t))


def gen_ecg(t):
    """Biphasic Q-R-S + T-wave, ~72 bpm (1.2 Hz)."""
    hr = 1.2
    out = np.zeros_like(t)
    ph = (t * hr) % 1.0
    # Q (small negative, 15 ms)
    m = (ph > 0.255) & (ph < 0.27)
    out[m] += -6 * np.sin(math.pi * (ph[m] - 0.255) / 0.015)
    # R (big positive, 30 ms)
    m = (ph > 0.27) & (ph < 0.30)
    out[m] += 38 * np.sin(math.pi * (ph[m] - 0.27) / 0.03)
    # S (small negative, 20 ms)
    m = (ph > 0.30) & (ph < 0.32)
    out[m] += -10 * np.sin(math.pi * (ph[m] - 0.30) / 0.02)
    # T (small positive, 140 ms)
    m = (ph > 0.42) & (ph < 0.56)
    out[m] += 9 * np.sin(math.pi * (ph[m] - 0.42) / 0.14)
    return out


def build_artifact_grid():
    t, eeg = clean_eeg()
    panels = [
        ("(A)", eeg + gen_blink(t),       "#e74c3c"),
        ("(B)", eeg + gen_muscle(t),       "#e67e22"),
        ("(C)", eeg + gen_line_noise(t),   "#8e44ad"),
        ("(D)", eeg + gen_ecg(t),          "#27ae60"),
    ]
    fig = make_subplots(rows=2, cols=2, subplot_titles=[p[0] for p in panels],
                        horizontal_spacing=0.08, vertical_spacing=0.18)
    positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
    for (label, sig, color), (r, c) in zip(panels, positions):
        fig.add_trace(go.Scatter(
            x=t, y=sig, mode="lines",
            line=dict(color=color, width=1.2),
            hoverinfo="skip", showlegend=False,
        ), row=r, col=c)

    for r in (1, 2):
        for c in (1, 2):
            fig.update_xaxes(range=[0, 3], showgrid=False, zeroline=False,
                             title_text="Time (s)" if r == 2 else "",
                             row=r, col=c)
            # negative-up axis (clinical convention)
            fig.update_yaxes(autorange="reversed", showgrid=False, zeroline=False,
                             title_text="μV" if c == 1 else "",
                             row=r, col=c)

    fig.update_layout(
        margin=dict(l=60, r=20, t=40, b=50),
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
    )
    out = OUT / "prob7_artifact_grid.png"
    fig.write_image(str(out), width=1950, height=1500, scale=1)
    print(f"  wrote {out.name}")


if __name__ == "__main__":
    print("Generating homework figures...")
    build_phase_reversal()
    build_artifact_grid()
    print("Done.")
