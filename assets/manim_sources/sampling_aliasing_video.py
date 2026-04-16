"""Sampling & Aliasing Animation for Module 2.

Demonstrates:
  0. Intro: physiology is continuous, computers are digital, how often to sample?
  1. Continuous 10 Hz sine wave
  2. Sampling at 50 Hz (good) — dots match, reconstruction accurate
  3. Sampling at 12 Hz (barely above Nyquist) — wobbly but correct frequency
  4. Sampling at 8 Hz (below Nyquist) — aliased signal in red

Target duration: ~35-40 seconds.
"""

from manim import *
import numpy as np


class SamplingAliasing(Scene):
    def construct(self):
        # ══════════════════════════════════════════════════════════════
        # INTRO SECTION (~14 seconds)
        # ══════════════════════════════════════════════════════════════

        # ── Intro Phase 1: "Physiology is continuous" ──
        intro_title = Text(
            "Physiology is continuous", font_size=40, color=BLUE
        ).to_edge(UP, buff=0.6)

        # A smooth EEG-like waveform
        intro_axes = Axes(
            x_range=[0, 2, 0.5],
            y_range=[-1.5, 1.5, 0.5],
            x_length=10,
            y_length=3.5,
            axis_config={"include_numbers": False, "stroke_width": 1.5},
        ).shift(DOWN * 0.2)

        eeg_label = Text(
            "Brain signal (EEG)", font_size=22, color=BLUE_C
        ).next_to(intro_axes, DOWN, buff=0.25)

        def eeg_wave(t):
            """Multi-frequency waveform mimicking EEG."""
            return (
                0.5 * np.sin(2 * np.pi * 4 * t)
                + 0.3 * np.sin(2 * np.pi * 10 * t)
                + 0.15 * np.sin(2 * np.pi * 22 * t)
            )

        eeg_curve = intro_axes.plot(
            eeg_wave, x_range=[0, 2, 0.001], color=BLUE, stroke_width=3
        )

        self.play(Write(intro_title), run_time=0.8)
        self.play(
            Create(intro_axes), FadeIn(eeg_label), run_time=0.6
        )
        self.play(Create(eeg_curve), run_time=2.0)
        self.wait(0.6)

        # ── Intro Phase 2: "Computers are digital" ──
        digital_title = Text(
            "Computers are digital", font_size=40, color=GREEN
        ).to_edge(UP, buff=0.6)

        # Sample the EEG curve into dots
        n_intro_samples = 20
        intro_ts = np.linspace(0, 2, n_intro_samples)
        intro_dots = VGroup()
        for t_i in intro_ts:
            pt = intro_axes.c2p(t_i, eeg_wave(t_i))
            intro_dots.add(Dot(pt, radius=0.06, color=GREEN, z_index=3))

        # Vertical stem lines from x-axis to each dot
        intro_stems = VGroup()
        for t_i in intro_ts:
            bottom = intro_axes.c2p(t_i, 0)
            top = intro_axes.c2p(t_i, eeg_wave(t_i))
            intro_stems.add(
                Line(bottom, top, color=GREEN, stroke_width=1.5, stroke_opacity=0.5)
            )

        # Binary text decoration
        bits_text = Text(
            "0 1 1 0 1 0 0 1 1 0 1 1 0 1 0 1",
            font_size=18, color=GREEN_A, opacity=0.6,
        ).next_to(intro_axes, DOWN, buff=0.25)

        self.play(
            ReplacementTransform(intro_title, digital_title),
            FadeOut(eeg_label),
            run_time=0.5,
        )
        self.play(
            eeg_curve.animate.set_stroke(opacity=0.3),
            LaggedStart(*[GrowFromCenter(d) for d in intro_dots], lag_ratio=0.04),
            LaggedStart(*[Create(s) for s in intro_stems], lag_ratio=0.04),
            run_time=1.8,
        )
        self.play(FadeIn(bits_text), run_time=0.5)
        self.wait(0.7)

        # ── Intro Phase 3: "How often do we sample?" ──
        question_title = Text(
            "How often do we sample?", font_size=40, color=GOLD
        ).to_edge(UP, buff=0.6)

        # Two consequence lines
        too_much = Text(
            "Too often \u2192 drowning in data",
            font_size=26, color=YELLOW,
        ).move_to(DOWN * 2.4 + LEFT * 2.8)

        too_little = Text(
            "Too rarely \u2192 lost information",
            font_size=26, color=RED,
        ).move_to(DOWN * 2.4 + RIGHT * 2.8)

        self.play(
            ReplacementTransform(digital_title, question_title),
            FadeOut(bits_text),
            run_time=0.5,
        )
        self.play(
            FadeIn(too_much, shift=LEFT * 0.3),
            FadeIn(too_little, shift=RIGHT * 0.3),
            run_time=1.0,
        )
        self.wait(1.5)

        # ── Intro Phase 4: Transition — clear intro, set up main demo ──
        transition_text = Text(
            "Let's see what happens...", font_size=36, color=WHITE
        ).move_to(ORIGIN)

        self.play(
            FadeOut(question_title),
            FadeOut(eeg_curve),
            FadeOut(intro_dots),
            FadeOut(intro_stems),
            FadeOut(intro_axes),
            FadeOut(too_much),
            FadeOut(too_little),
            run_time=0.6,
        )
        self.play(FadeIn(transition_text), run_time=0.5)
        self.wait(0.8)
        self.play(FadeOut(transition_text), run_time=0.4)

        # ══════════════════════════════════════════════════════════════
        # MAIN DEMO (original content)
        # ══════════════════════════════════════════════════════════════

        # ── Parameters ──
        f_sig = 10  # Hz
        duration = 1.0  # seconds of signal shown
        omega = 2 * np.pi * f_sig

        # ── Shared axes (reused across all panels) ──
        axes = Axes(
            x_range=[0, duration, 0.2],
            y_range=[-1.5, 1.5, 0.5],
            x_length=11,
            y_length=4.5,
            axis_config={"include_numbers": False, "stroke_width": 2},
        ).shift(DOWN * 0.3)

        x_label = axes.get_x_axis_label("t\\;(s)", direction=DOWN).scale(0.7)
        y_label = axes.get_y_axis_label("V", direction=LEFT).scale(0.7)

        # ── Continuous signal ──
        continuous = axes.plot(
            lambda t: np.sin(omega * t),
            x_range=[0, duration, 0.001],
            color=BLUE,
            stroke_width=3,
        )

        title = Text("10 Hz Continuous Signal", font_size=32, color=BLUE).to_edge(UP)

        # ── SCENE 1: Show continuous wave ──
        self.play(
            Create(axes),
            FadeIn(x_label),
            FadeIn(y_label),
            run_time=1.0,
        )
        self.play(Create(continuous), Write(title), run_time=2.0)
        self.wait(2.0)

        # ── Helper: build sample dots + reconstructed line ──
        def make_samples(fs, color):
            ts = np.arange(0, duration + 1e-9, 1.0 / fs)
            ts = ts[ts <= duration]
            dots = VGroup()
            for t_i in ts:
                pt = axes.c2p(t_i, np.sin(omega * t_i))
                dots.add(Dot(pt, radius=0.07, color=color, z_index=3))
            return ts, dots

        def make_reconstruction(ts, axes_ref, color, dashed=False):
            """Sinc interpolation (ideal reconstruction)."""
            t_fine = np.linspace(0, duration, 2000)
            y_samples = np.sin(omega * ts)
            y_recon = np.zeros_like(t_fine)
            T_s = ts[1] - ts[0] if len(ts) > 1 else 1.0
            for i, t_s in enumerate(ts):
                sinc_arg = (t_fine - t_s) / T_s
                y_recon += y_samples[i] * np.sinc(sinc_arg)
            # Clip to reasonable range
            y_recon = np.clip(y_recon, -1.5, 1.5)
            points = [axes_ref.c2p(t_fine[j], y_recon[j]) for j in range(len(t_fine))]
            if dashed:
                line = DashedVMobject(
                    VMobject().set_points_smoothly(points),
                    num_dashes=60,
                    dashed_ratio=0.5,
                )
                line.set_color(color).set_stroke(width=2.5)
            else:
                line = VMobject().set_points_smoothly(points)
                line.set_color(color).set_stroke(width=2.5)
            return line

        def make_alias_wave(fs, axes_ref):
            """Show the aliased sinusoid (the frequency the samples actually trace)."""
            f_alias = abs(f_sig - round(f_sig / fs) * fs)
            if f_alias < 0.01:
                return None, 0.0
            # Match phase: at t=0, sin(omega*0) = 0, alias sin(2pi*f_alias*0) = 0
            # Need to determine sign: check a sample point
            t_test = 1.0 / fs
            true_val = np.sin(omega * t_test)
            alias_val = np.sin(2 * np.pi * f_alias * t_test)
            sign = 1 if (true_val * alias_val > 0) else -1
            wave = axes_ref.plot(
                lambda t: sign * np.sin(2 * np.pi * f_alias * t),
                x_range=[0, duration, 0.001],
                color=RED,
                stroke_width=3,
            )
            return wave, f_alias

        # ── SCENE 2: 50 Hz sampling (good) ──
        fs_good = 50
        ts_good, dots_good = make_samples(fs_good, GREEN)
        recon_good = make_reconstruction(ts_good, axes, GREEN, dashed=True)
        label_good = Text("50 Hz sampling (good)", font_size=28, color=GREEN).to_edge(UP)

        self.play(
            ReplacementTransform(title, label_good),
            LaggedStart(*[GrowFromCenter(d) for d in dots_good], lag_ratio=0.02),
            run_time=1.5,
        )
        self.play(Create(recon_good), run_time=1.5)
        self.wait(2.0)

        # ── SCENE 3: 12 Hz sampling (barely above Nyquist) ──
        fs_close = 12
        ts_close, dots_close = make_samples(fs_close, YELLOW)
        recon_close = make_reconstruction(ts_close, axes, YELLOW, dashed=True)
        label_close = Text(
            "12 Hz sampling (just above Nyquist)", font_size=28, color=YELLOW
        ).to_edge(UP)

        self.play(
            ReplacementTransform(label_good, label_close),
            FadeOut(dots_good),
            FadeOut(recon_good),
            run_time=0.6,
        )
        self.play(
            LaggedStart(*[GrowFromCenter(d) for d in dots_close], lag_ratio=0.05),
            run_time=1.2,
        )
        self.play(Create(recon_close), run_time=1.2)
        self.wait(2.0)

        # ── SCENE 4: 8 Hz sampling (ALIASED!) ──
        fs_bad = 8
        ts_bad, dots_bad = make_samples(fs_bad, RED)
        alias_wave, f_alias = make_alias_wave(fs_bad, axes)
        label_bad = Text(
            "8 Hz sampling (aliased!)", font_size=28, color=RED
        ).to_edge(UP)

        alias_note = MathTex(
            f"f_{{alias}} = |f_{{sig}} - f_s| = |10 - 8| = {f_alias:.0f}\\;\\text{{Hz}}",
            font_size=32,
            color=RED,
        ).next_to(axes, DOWN, buff=0.3)

        self.play(
            ReplacementTransform(label_close, label_bad),
            FadeOut(dots_close),
            FadeOut(recon_close),
            run_time=0.6,
        )
        self.play(
            LaggedStart(*[GrowFromCenter(d) for d in dots_bad], lag_ratio=0.08),
            run_time=1.2,
        )
        if alias_wave is not None:
            self.play(Create(alias_wave), run_time=1.5)
        self.play(FadeIn(alias_note), run_time=0.8)
        self.wait(1.5)

        # ── SCENE 5: Flash the alias wave ──
        if alias_wave is not None:
            self.play(
                Indicate(alias_wave, color=RED, scale_factor=1.05),
                run_time=0.8,
            )

        # ── SCENE 6: Nyquist rule ──
        # Fade everything except axes frame
        to_fade = VGroup(
            continuous, dots_bad, label_bad, alias_note,
        )
        if alias_wave is not None:
            to_fade.add(alias_wave)

        nyquist_tex = MathTex(
            r"f_s \geq 2 \times f_{\max}",
            font_size=64,
            color=GOLD,
        )
        nyquist_label = Text(
            "The Nyquist Rule", font_size=36, color=GOLD
        ).next_to(nyquist_tex, UP, buff=0.4)
        nyquist_group = VGroup(nyquist_label, nyquist_tex).move_to(ORIGIN)

        self.play(
            FadeOut(to_fade),
            FadeOut(axes),
            FadeOut(x_label),
            FadeOut(y_label),
            run_time=0.8,
        )
        self.play(
            Write(nyquist_label),
            Write(nyquist_tex),
            run_time=2.0,
        )

        # Gold flash
        self.play(
            Indicate(nyquist_tex, color=YELLOW, scale_factor=1.1),
            run_time=1.0,
        )
        self.wait(2.0)
