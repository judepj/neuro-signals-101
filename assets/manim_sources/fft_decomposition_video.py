"""FFT Decomposition Animation for Module 4.

Shows a composite EEG-like signal being decomposed into
theta (4 Hz), alpha (10 Hz), and beta (30 Hz) components,
then reassembled.

~25 seconds total. 720p.
"""

from manim import *
import numpy as np

# EEG band colors — clinical palette
THETA_COLOR = "#2ecc71"   # green
ALPHA_COLOR = "#8e44ad"   # purple
BETA_COLOR  = "#e67e22"   # orange
COMPOSITE_COLOR = "#2c3e50"  # dark blue-grey
REASSEMBLE_COLOR = "#f1c40f"  # gold


class FFTDecomposition(Scene):
    def construct(self):
        # ── Parameters ──
        dur = 1.0       # seconds of signal to show
        fs = 500        # visual samples
        t = np.linspace(0, dur, fs)

        components = [
            {"freq": 4,  "amp": 1.0,  "label": "4 Hz — Theta",  "color": THETA_COLOR},
            {"freq": 10, "amp": 0.6,  "label": "10 Hz — Alpha", "color": ALPHA_COLOR},
            {"freq": 30, "amp": 0.35, "label": "30 Hz — Beta",  "color": BETA_COLOR},
        ]

        def wave(freq, amp):
            return amp * np.sin(2 * np.pi * freq * t)

        composite = sum(wave(c["freq"], c["amp"]) for c in components)

        # ── Title ──
        title = Text(
            "FFT: Decomposing a Complex Signal",
            font_size=32, color=WHITE
        ).to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.5)

        # ── Phase 1: Show mystery composite ──
        subtitle = Text(
            "What frequencies are hiding inside?",
            font_size=20, color=GREY_B, slant=ITALIC
        ).next_to(title, DOWN, buff=0.15)
        self.play(FadeIn(subtitle), run_time=0.6)

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
            "Mystery signal", font_size=18, color=COMPOSITE_COLOR
        ).next_to(ax_top, LEFT, buff=0.15).shift(UP * 0.2)

        self.play(
            Create(ax_top), FadeIn(ax_top_labels),
            run_time=1.0
        )
        self.play(
            Create(composite_graph), FadeIn(mystery_label),
            run_time=1.5
        )
        self.wait(2.0)

        # ── Phase 2: Decompose — peel off components below ──
        self.play(FadeOut(subtitle), run_time=0.4)

        decompose_text = Text(
            "The FFT reveals the hidden components...",
            font_size=20, color=GREY_B, slant=ITALIC
        ).next_to(title, DOWN, buff=0.15)
        self.play(FadeIn(decompose_text), run_time=0.6)
        self.wait(0.5)

        # Shrink composite plot upward to make room
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

        self.play(
            ReplacementTransform(ax_top, ax_top_small),
            ReplacementTransform(composite_graph, composite_graph_small),
            ReplacementTransform(mystery_label, mystery_label_small),
            FadeOut(ax_top_labels),
            run_time=1.0
        )

        # Component axes stacked below
        comp_axes = []
        comp_graphs = []
        comp_labels = []
        y_positions = [0.2, -1.3, -2.8]

        for i, c in enumerate(components):
            y_vals = wave(c["freq"], c["amp"])
            ax = Axes(
                x_range=[0, dur, 0.2],
                y_range=[-1.2, 1.2, 0.5],
                x_length=10, y_length=1.2,
                tips=False,
                axis_config={"stroke_width": 1, "color": GREY_D},
            ).shift(DOWN * (-y_positions[i]))  # negative because DOWN

            # Actually position them
            ax.move_to(ORIGIN).shift(DOWN * (0.1 + i * 1.4) + LEFT * 0)
            ax.shift(DOWN * 0.2)  # extra nudge

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

            # Animate each component peeling off
            self.play(
                Create(ax),
                Create(graph),
                FadeIn(label),
                run_time=1.5
            )
            self.wait(1.0)

        self.wait(1.5)

        # ── Phase 3: Reassemble — show them adding back together ──
        self.play(FadeOut(decompose_text), run_time=0.4)

        reassemble_text = Text(
            "Add them back together...",
            font_size=20, color=GREY_B, slant=ITALIC
        ).next_to(title, DOWN, buff=0.15)
        self.play(FadeIn(reassemble_text), run_time=0.6)
        self.wait(0.5)

        # Flash each component, then morph the composite to gold
        for i in range(len(components)):
            self.play(
                comp_graphs[i].animate.set_stroke(width=5),
                run_time=0.2
            )
            self.play(
                comp_graphs[i].animate.set_stroke(width=2.5),
                run_time=0.2
            )

        # Highlight the composite in gold
        composite_gold = ax_top_small.plot_line_graph(
            x_values=t, y_values=composite,
            add_vertex_dots=False,
            line_color=REASSEMBLE_COLOR,
            stroke_width=3,
        )
        self.play(
            ReplacementTransform(composite_graph_small, composite_gold),
            run_time=1.5
        )
        self.wait(0.5)

        # Final equation — lower, with breathing room above components
        equation = MathTex(
            r"s(t) = ",
            r"\underbrace{A_1 \sin(2\pi \cdot 4t)}_{\text{Theta}}",
            r" + ",
            r"\underbrace{A_2 \sin(2\pi \cdot 10t)}_{\text{Alpha}}",
            r" + ",
            r"\underbrace{A_3 \sin(2\pi \cdot 30t)}_{\text{Beta}}",
            font_size=22,
        ).to_edge(DOWN, buff=0.05)

        # Color the terms
        equation[1].set_color(THETA_COLOR)
        equation[3].set_color(ALPHA_COLOR)
        equation[5].set_color(BETA_COLOR)

        self.play(Write(equation), run_time=2.0)
        self.wait(3.0)

        # Fade out
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1.0
        )


# Allow direct execution
if __name__ == "__main__":
    import subprocess, sys
    sys.exit(subprocess.call([
        sys.executable, "-m", "manim",
        "-qm",  # medium quality (720p)
        "--disable_caching",
        __file__,
        "FFTDecomposition",
    ]))
