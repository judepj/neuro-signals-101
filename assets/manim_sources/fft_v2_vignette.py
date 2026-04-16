"""FFT Decomposition v2 — Narrative continuation of sampling + filtering vignettes.

Picks up where `filtering_v2_vignette.py` ended: the EEG is clean. Now the
physician sees only wiggles and asks what's inside. The EEG tech runs the
spectral analysis, the FFT decomposes the trace into theta/alpha/beta, and
the video walks through the five clinical bands — the diagnostic payoff.

Audience: future physicians (medical students).
Voice: Andrew (edge-tts), via EdgeTTSService + VoiceoverScene.
"""

import sys
from pathlib import Path

# Ensure local import of edge_tts_service works when manim loads this file
sys.path.insert(0, str(Path(__file__).parent))

from manim import *
from manim_voiceover import VoiceoverScene
from edge_tts_service import EdgeTTSService
import numpy as np


# Clinical band colours
DELTA_COLOR = "#3498db"   # blue
THETA_COLOR = "#2ecc71"   # green
ALPHA_COLOR = "#8e44ad"   # purple
BETA_COLOR  = "#e67e22"   # orange
GAMMA_COLOR = "#e74c3c"   # red
COMPOSITE_COLOR = "#2c3e50"
REASSEMBLE_COLOR = "#f1c40f"


class FFTV2(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            EdgeTTSService(voice="en-US-AndrewMultilingualNeural")
        )

        # ── Shared signal parameters ──
        dur = 1.0
        fs = 500
        t = np.linspace(0, dur, fs)
        components = [
            {"freq": 4,  "amp": 1.0,  "label": "4 Hz — Theta",  "color": THETA_COLOR},
            {"freq": 10, "amp": 0.6,  "label": "10 Hz — Alpha", "color": ALPHA_COLOR},
            {"freq": 30, "amp": 0.35, "label": "30 Hz — Beta",  "color": BETA_COLOR},
        ]

        def wave(freq, amp):
            return amp * np.sin(2 * np.pi * freq * t)

        composite = sum(wave(c["freq"], c["amp"]) for c in components)

        # ══════════════════════════════════════════════════════════════
        # PHASE 1 — Continuation vignette
        # ══════════════════════════════════════════════════════════════

        scene_title = Text(
            "Clean recording — now what's inside?",
            font_size=30, color=BLUE_B,
        ).to_edge(UP, buff=0.5)

        doctor_label = Text("Attending Physician", font_size=22, color=GOLD)
        tech_label = Text("EEG Tech", font_size=22, color=GREEN_B)

        doctor_box = RoundedRectangle(
            corner_radius=0.15, width=5.2, height=1.8,
            stroke_color=GOLD, stroke_width=2, fill_opacity=0.05, fill_color=GOLD,
        ).move_to(LEFT * 3.3 + DOWN * 0.2)
        tech_box = RoundedRectangle(
            corner_radius=0.15, width=5.2, height=1.8,
            stroke_color=GREEN_B, stroke_width=2, fill_opacity=0.05, fill_color=GREEN_B,
        ).move_to(RIGHT * 3.3 + DOWN * 0.2)

        doctor_label.next_to(doctor_box, UP, buff=0.12).align_to(doctor_box, LEFT).shift(RIGHT * 0.15)
        tech_label.next_to(tech_box, UP, buff=0.12).align_to(tech_box, LEFT).shift(RIGHT * 0.15)

        doctor_line_1 = Text(
            '"Okay, we\'ve got a\nclean signal now.\nBut all I see is...\nwiggles."',
            font_size=20, color=WHITE, line_spacing=0.9,
        ).move_to(doctor_box.get_center())

        with self.voiceover(
            text="Okay, we've got a clean signal now. But all I see is... wiggles."
        ) as tracker:
            self.play(Write(scene_title), run_time=0.7)
            self.play(
                FadeIn(doctor_box, shift=RIGHT * 0.2),
                FadeIn(tech_box, shift=LEFT * 0.2),
                FadeIn(doctor_label), FadeIn(tech_label),
                run_time=0.6,
            )
            self.play(
                Indicate(doctor_box, color=GOLD, scale_factor=1.03),
                Write(doctor_line_1),
                run_time=max(1.0, tracker.duration - 1.3),
            )

        tech_line_1 = Text(
            '"Let me run the\nspectral analysis.\nEvery EEG is a sum\nof underlying rhythms —\nthe FFT pulls them apart."',
            font_size=17, color=WHITE, line_spacing=0.9,
        ).move_to(tech_box.get_center())

        with self.voiceover(
            text="Let me run the spectral analysis. Every E E G is a sum of underlying rhythms — the F F T pulls them apart for you."
        ) as tracker:
            self.play(
                Indicate(tech_box, color=GREEN_B, scale_factor=1.03),
                Write(tech_line_1),
                run_time=max(1.2, tracker.duration),
            )

        # Callout
        enter_callout = Text(
            "Enter: the Fast Fourier Transform.",
            font_size=40, color=REASSEMBLE_COLOR,
        ).move_to(ORIGIN)

        with self.voiceover(
            text="To read an E E G clinically, you don't just look at it — you look inside it. You ask: which brain rhythms are present, and in what proportion? The F F T answers that question."
        ) as tracker:
            self.play(
                FadeOut(scene_title),
                FadeOut(doctor_box), FadeOut(doctor_label), FadeOut(doctor_line_1),
                FadeOut(tech_box), FadeOut(tech_label), FadeOut(tech_line_1),
                run_time=0.6,
            )
            self.play(Write(enter_callout), run_time=1.2)
            self.play(
                Indicate(enter_callout, color=REASSEMBLE_COLOR, scale_factor=1.08),
                run_time=max(1.2, tracker.duration - 1.8),
            )
            self.play(FadeOut(enter_callout), run_time=0.4)

        # ══════════════════════════════════════════════════════════════
        # PHASE 2 — Mystery composite signal
        # ══════════════════════════════════════════════════════════════

        title = Text(
            "FFT: Decomposing a Complex Signal",
            font_size=32, color=WHITE
        ).to_edge(UP, buff=0.3)
        subtitle = Text(
            "What frequencies are hiding inside?",
            font_size=20, color=GREY_B, slant=ITALIC
        ).next_to(title, DOWN, buff=0.15)

        ax_top = Axes(
            x_range=[0, dur, 0.2],
            y_range=[-2.2, 2.2, 1],
            x_length=10, y_length=2.8,
            tips=False,
            axis_config={"stroke_width": 1.5, "color": GREY_C},
        ).shift(UP * 0.3)
        ax_top_labels = ax_top.get_axis_labels(
            Tex(r"Time (s)", font_size=22),
            Tex(r"", font_size=22),
        )

        composite_graph = ax_top.plot_line_graph(
            x_values=t, y_values=composite,
            add_vertex_dots=False,
            line_color=COMPOSITE_COLOR,
            stroke_width=2.5,
        )
        mystery_label = Text(
            "Clean EEG trace", font_size=18, color=COMPOSITE_COLOR
        ).next_to(ax_top, LEFT, buff=0.15).shift(UP * 0.2)

        with self.voiceover(
            text="Here's what the clean trace looks like. A complex wave. To the untrained eye — chaos."
        ) as tracker:
            self.play(Write(title), run_time=0.8)
            self.play(FadeIn(subtitle), run_time=0.5)
            self.play(
                Create(ax_top), FadeIn(ax_top_labels),
                run_time=0.8,
            )
            self.play(
                Create(composite_graph), FadeIn(mystery_label),
                run_time=max(0.8, tracker.duration - 2.1),
            )

        # ══════════════════════════════════════════════════════════════
        # PHASE 3 — FFT decomposes with clinical narration
        # ══════════════════════════════════════════════════════════════

        decompose_text = Text(
            "The FFT reveals the hidden components...",
            font_size=20, color=GREY_B, slant=ITALIC
        ).next_to(title, DOWN, buff=0.15)

        ax_top_small = Axes(
            x_range=[0, dur, 0.2],
            y_range=[-2.2, 2.2, 1],
            x_length=10, y_length=1.6,
            tips=False,
            axis_config={"stroke_width": 1.5, "color": GREY_C},
        ).shift(UP * 1.8)

        composite_graph_small = ax_top_small.plot_line_graph(
            x_values=t, y_values=composite,
            add_vertex_dots=False,
            line_color=COMPOSITE_COLOR,
            stroke_width=2,
        )
        mystery_label_small = Text(
            "Composite", font_size=16, color=COMPOSITE_COLOR
        ).next_to(ax_top_small, LEFT, buff=0.15)

        with self.voiceover(
            text="The F F T — Fast Fourier Transform — pulls it apart."
        ) as tracker:
            self.play(FadeOut(subtitle), run_time=0.4)
            self.play(FadeIn(decompose_text), run_time=0.6)
            self.play(
                ReplacementTransform(ax_top, ax_top_small),
                ReplacementTransform(composite_graph, composite_graph_small),
                ReplacementTransform(mystery_label, mystery_label_small),
                FadeOut(ax_top_labels),
                run_time=max(0.5, tracker.duration - 1.0),
            )

        comp_axes = []
        comp_graphs = []
        comp_labels = []

        component_narrations = [
            # Theta — clinical
            "Theta — four to eight hertz. Normal in drowsy adults and children. Pathologic when it dominates in wakefulness — think encephalopathy, or focal slowing over a lesion.",
            # Alpha — clinical
            "Alpha — eight to twelve hertz. The posterior dominant rhythm. Present when the patient closes their eyes. Its absence, or asymmetry between sides, is clinically meaningful.",
            # Beta — clinical
            "Beta — thirteen to thirty hertz. Fast activity. Increased by benzodiazepines and barbiturates. Spike-wave discharges here can signal epileptiform activity.",
        ]

        for i, c in enumerate(components):
            y_vals = wave(c["freq"], c["amp"])
            ax = Axes(
                x_range=[0, dur, 0.2],
                y_range=[-1.2, 1.2, 0.5],
                x_length=10, y_length=1.2,
                tips=False,
                axis_config={"stroke_width": 1, "color": GREY_D},
            )
            ax.move_to(ORIGIN).shift(DOWN * (0.1 + i * 1.4))
            ax.shift(DOWN * 0.2)

            graph = ax.plot_line_graph(
                x_values=t, y_values=y_vals,
                add_vertex_dots=False,
                line_color=c["color"],
                stroke_width=2.5,
            )

            label = Text(
                c["label"], font_size=18, color=c["color"]
            ).next_to(ax, LEFT, buff=0.15)

            comp_axes.append(ax)
            comp_graphs.append(graph)
            comp_labels.append(label)

            with self.voiceover(text=component_narrations[i]) as tracker:
                self.play(
                    Create(ax),
                    Create(graph),
                    FadeIn(label),
                    run_time=max(0.8, tracker.duration),
                )

        # ══════════════════════════════════════════════════════════════
        # PHASE 4 — Clinical bands overview (rainbow bar)
        # ══════════════════════════════════════════════════════════════

        to_fade_decomp = VGroup(
            ax_top_small, composite_graph_small, mystery_label_small,
            decompose_text, title,
            *comp_axes, *comp_graphs, *comp_labels,
        )

        bands_title = Text(
            "The Five Clinical Bands",
            font_size=34, color=GOLD,
        ).to_edge(UP, buff=0.5)

        # Frequency axis for the band chart
        band_ax = NumberLine(
            x_range=[0, 80, 10],
            length=11,
            include_numbers=True,
            label_direction=DOWN,
            font_size=22,
            stroke_width=2,
            color=GREY_B,
        ).shift(DOWN * 1.2)
        band_ax_label = Text(
            "Frequency (Hz)", font_size=22, color=GREY_B,
        ).next_to(band_ax, DOWN, buff=0.4)

        # Band segments: (low, high, color, name)
        bands = [
            (0.5, 4,  DELTA_COLOR, "Delta",  "0.5–4 Hz",
             "Deep sleep; pathologic slowing when awake"),
            (4, 8,    THETA_COLOR, "Theta",  "4–8 Hz",
             "Drowsy; encephalopathy if dominant"),
            (8, 12,   ALPHA_COLOR, "Alpha",  "8–12 Hz",
             "Eyes-closed posterior rhythm"),
            (13, 30,  BETA_COLOR,  "Beta",   "13–30 Hz",
             "Alert; benzodiazepine effect"),
            (30, 80,  GAMMA_COLOR, "Gamma",  "30–80+ Hz",
             "Cognitive binding; HFOs = epileptogenic"),
        ]

        band_rects = VGroup()
        band_name_labels = VGroup()
        for (lo, hi, col, name, rng, meaning) in bands:
            left = band_ax.number_to_point(lo)[0]
            right = band_ax.number_to_point(hi)[0]
            width = right - left
            rect = Rectangle(
                width=width, height=0.55,
                stroke_color=col, stroke_width=2,
                fill_color=col, fill_opacity=0.55,
            ).move_to(np.array([(left + right) / 2, band_ax.get_center()[1] + 0.35, 0]))
            name_lbl = Text(name, font_size=18, color=WHITE, weight=BOLD).move_to(rect.get_center())
            band_rects.add(rect)
            band_name_labels.add(name_lbl)

        # Meaning lines — shown on top, one per voiceover beat
        meaning_lines = VGroup(*[
            Text(f"{name} ({rng}) — {meaning}",
                 font_size=19, color=col)
            for (_, _, col, name, rng, meaning) in bands
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(UP * 1.7)

        with self.voiceover(
            text="These five bands are how every E E G is read. Not as wiggles — as proportions across a diagnostic spectrum."
        ) as tracker:
            self.play(FadeOut(to_fade_decomp), run_time=0.6)
            self.play(Write(bands_title), run_time=0.8)
            self.play(
                Create(band_ax), FadeIn(band_ax_label),
                run_time=0.8,
            )
            self.play(
                LaggedStart(*[
                    AnimationGroup(FadeIn(r), FadeIn(n))
                    for r, n in zip(band_rects, band_name_labels)
                ], lag_ratio=0.15),
                run_time=max(1.2, tracker.duration - 2.2),
            )

        with self.voiceover(
            text="Delta — zero point five to four hertz — deep sleep, or pathologic slowing when the patient is awake. "
                 "Theta — four to eight — drowsy, or encephalopathy if dominant. "
                 "Alpha — eight to twelve — the eyes-closed posterior rhythm. "
                 "Beta — thirteen to thirty — alert, or benzodiazepine effect. "
                 "And gamma — thirty to eighty and beyond — cognitive binding, and in surgery workups, high-frequency oscillations mark epileptogenic tissue."
        ) as tracker:
            self.play(
                LaggedStart(*[
                    FadeIn(line, shift=UP * 0.1) for line in meaning_lines
                ], lag_ratio=0.5),
                run_time=max(4.0, tracker.duration),
            )

        # ══════════════════════════════════════════════════════════════
        # PHASE 5 — Reassemble + equation
        # ══════════════════════════════════════════════════════════════

        reassemble_title = Text(
            "Any EEG = weighted sum of sine waves",
            font_size=32, color=WHITE
        ).to_edge(UP, buff=0.3)

        reassemble_ax = Axes(
            x_range=[0, dur, 0.2],
            y_range=[-2.2, 2.2, 1],
            x_length=10, y_length=2.4,
            tips=False,
            axis_config={"stroke_width": 1.5, "color": GREY_C},
        ).shift(UP * 0.3)
        reassemble_graph = reassemble_ax.plot_line_graph(
            x_values=t, y_values=composite,
            add_vertex_dots=False,
            line_color=REASSEMBLE_COLOR,
            stroke_width=3,
        )

        equation = MathTex(
            r"s(t) = ",
            r"\underbrace{A_1 \sin(2\pi \cdot 4t)}_{\text{Theta}}",
            r" + ",
            r"\underbrace{A_2 \sin(2\pi \cdot 10t)}_{\text{Alpha}}",
            r" + ",
            r"\underbrace{A_3 \sin(2\pi \cdot 30t)}_{\text{Beta}}",
            font_size=24,
        ).to_edge(DOWN, buff=0.4)
        equation[1].set_color(THETA_COLOR)
        equation[3].set_color(ALPHA_COLOR)
        equation[5].set_color(BETA_COLOR)

        with self.voiceover(
            text="Any E E G, any biosignal, is a weighted sum of sine waves. The F F T just tells you the weights."
        ) as tracker:
            self.play(
                FadeOut(bands_title), FadeOut(band_ax), FadeOut(band_ax_label),
                FadeOut(band_rects), FadeOut(band_name_labels),
                FadeOut(meaning_lines),
                run_time=0.6,
            )
            self.play(Write(reassemble_title), run_time=0.8)
            self.play(
                Create(reassemble_ax), Create(reassemble_graph),
                run_time=1.2,
            )
            self.play(Write(equation), run_time=max(1.0, tracker.duration - 2.6))

        # ══════════════════════════════════════════════════════════════
        # PHASE 6 — Callback close
        # ══════════════════════════════════════════════════════════════

        doctor_label2 = Text("Attending Physician", font_size=22, color=GOLD)
        tech_label2 = Text("EEG Tech", font_size=22, color=GREEN_B)

        doctor_box2 = RoundedRectangle(
            corner_radius=0.15, width=5.6, height=2.0,
            stroke_color=GOLD, stroke_width=2, fill_opacity=0.05, fill_color=GOLD,
        ).move_to(LEFT * 3.3 + DOWN * 0.2)
        tech_box2 = RoundedRectangle(
            corner_radius=0.15, width=5.6, height=2.0,
            stroke_color=GREEN_B, stroke_width=2, fill_opacity=0.05, fill_color=GREEN_B,
        ).move_to(RIGHT * 3.3 + DOWN * 0.2)

        doctor_label2.next_to(doctor_box2, UP, buff=0.12).align_to(doctor_box2, LEFT).shift(RIGHT * 0.15)
        tech_label2.next_to(tech_box2, UP, buff=0.12).align_to(tech_box2, LEFT).shift(RIGHT * 0.15)

        doctor_close_1 = Text(
            '"Posterior alpha dominant,\nwell-formed, symmetric.\nNo abnormal slowing."',
            font_size=19, color=WHITE, line_spacing=0.9,
        ).move_to(doctor_box2.get_center())

        tech_close = Text(
            '"Consistent with a\nnormal awake EEG."',
            font_size=20, color=WHITE, line_spacing=0.9,
        ).move_to(tech_box2.get_center())

        with self.voiceover(
            text="Back in room four. Posterior alpha dominant, well-formed, symmetric. No abnormal slowing."
        ) as tracker:
            self.play(
                FadeOut(reassemble_title), FadeOut(reassemble_ax),
                FadeOut(reassemble_graph), FadeOut(equation),
                run_time=0.6,
            )
            self.play(
                FadeIn(doctor_box2, shift=RIGHT * 0.2),
                FadeIn(tech_box2, shift=LEFT * 0.2),
                FadeIn(doctor_label2), FadeIn(tech_label2),
                run_time=0.6,
            )
            self.play(
                Indicate(doctor_box2, color=GOLD, scale_factor=1.03),
                Write(doctor_close_1),
                run_time=max(1.2, tracker.duration - 1.2),
            )

        with self.voiceover(
            text="Consistent with a normal awake E E G."
        ) as tracker:
            self.play(
                Indicate(tech_box2, color=GREEN_B, scale_factor=1.03),
                Write(tech_close),
                run_time=max(1.0, tracker.duration),
            )

        doctor_close_2 = Text(
            '"So... no electrographic\nevidence of temporal\nlobe epilepsy today.\nBut we\'ll monitor."',
            font_size=18, color=WHITE, line_spacing=0.9,
        ).move_to(doctor_box2.get_center())

        with self.voiceover(
            text="So — no electrographic evidence of temporal lobe epilepsy today. But we'll monitor."
        ) as tracker:
            self.play(FadeOut(doctor_close_1), run_time=0.3)
            self.play(
                Indicate(doctor_box2, color=GOLD, scale_factor=1.03),
                Write(doctor_close_2),
                run_time=max(1.2, tracker.duration - 0.3),
            )

        final_line = Text(
            "FFT: from wiggles to diagnosis.",
            font_size=36, color=BLUE_B, slant=ITALIC,
        ).move_to(ORIGIN)

        with self.voiceover(
            text="F F T — from wiggles to diagnosis."
        ) as tracker:
            self.play(
                FadeOut(doctor_box2), FadeOut(doctor_label2), FadeOut(doctor_close_2),
                FadeOut(tech_box2), FadeOut(tech_label2), FadeOut(tech_close),
                run_time=0.6,
            )
            self.play(Write(final_line), run_time=max(1.0, tracker.duration - 0.6))
            self.play(
                Indicate(final_line, color=BLUE_B, scale_factor=1.05),
                run_time=0.6,
            )

        self.wait(0.5)


# Allow direct execution
if __name__ == "__main__":
    import subprocess
    sys.exit(subprocess.call([
        sys.executable, "-m", "manim",
        "-qm",
        "--disable_caching",
        __file__,
        "FFTV2",
    ]))
