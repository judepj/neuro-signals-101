"""Filtering Demo — Module 3 animation.

Shows raw EEG (alpha + drift + 60Hz noise), its FFT spectrum,
a bandpass filter mask sweeping across, and the cleaned signal.
~20 seconds, medium quality.
"""

from manim import *
import numpy as np

# Colour constants
RAW_COLOR = GREY_B
CLEAN_COLOR = BLUE
FILTER_COLOR = GREEN
PEAK_LABEL_COLOR = YELLOW


class FilteringDemo(Scene):
    def construct(self):
        # ── Signal parameters ──────────────────────────────────
        fs = 500
        dur = 2.0
        t = np.linspace(0, dur, int(fs * dur), endpoint=False)

        drift = 0.4 * np.sin(2 * np.pi * 0.5 * t)
        alpha = 1.0 * np.sin(2 * np.pi * 10 * t)
        noise60 = 0.5 * np.sin(2 * np.pi * 60 * t)
        raw = drift + alpha + noise60
        clean = alpha.copy()

        # ── FFT ────────────────────────────────────────────────
        freqs = np.fft.rfftfreq(len(raw), d=1 / fs)
        spectrum = np.abs(np.fft.rfft(raw)) / len(raw) * 2
        # Cap display at 80 Hz for clarity
        mask_disp = freqs <= 80
        freqs_d = freqs[mask_disp]
        spec_d = spectrum[mask_disp]

        # ── PART 1: Raw signal ─────────────────────────────────
        title_raw = Text("Before: Raw EEG", font_size=32, color=RAW_COLOR)
        title_raw.to_edge(UP, buff=0.3)

        ax_time = Axes(
            x_range=[0, dur, 0.5],
            y_range=[-2.2, 2.2, 1],
            x_length=11,
            y_length=3,
            axis_config={"include_tip": False, "stroke_width": 1.5},
        ).shift(UP * 0.3)
        x_label = ax_time.get_x_axis_label("t\\;(s)")
        y_label = ax_time.get_y_axis_label("\\mu V")

        raw_graph = ax_time.plot_line_graph(
            x_values=t[::2], y_values=raw[::2],
            add_vertex_dots=False, line_color=RAW_COLOR, stroke_width=1.5,
        )

        self.play(Write(title_raw), run_time=1.2)
        self.play(Create(ax_time), FadeIn(x_label), FadeIn(y_label), run_time=1.2)
        self.play(Create(raw_graph), run_time=2.5)
        self.wait(2.0)

        # ── PART 2: Frequency spectrum ─────────────────────────
        # Shrink time plot upward
        top_group = VGroup(title_raw, ax_time, x_label, y_label, raw_graph)
        self.play(top_group.animate.scale(0.55).to_edge(UP, buff=0.15), run_time=1.0)

        ax_freq = Axes(
            x_range=[0, 80, 10],
            y_range=[0, float(spec_d.max()) * 1.15, 0.2],
            x_length=11,
            y_length=2.8,
            axis_config={"include_tip": False, "stroke_width": 1.5},
        ).to_edge(DOWN, buff=0.7)
        fx_label = ax_freq.get_x_axis_label("\\text{Frequency (Hz)}")
        fy_label = ax_freq.get_y_axis_label("\\text{Power}")

        spec_graph = ax_freq.plot_line_graph(
            x_values=freqs_d[::1], y_values=spec_d[::1],
            add_vertex_dots=False, line_color=WHITE, stroke_width=1.8,
        )

        self.play(Create(ax_freq), FadeIn(fx_label), FadeIn(fy_label), run_time=1.2)
        self.play(Create(spec_graph), run_time=2.0)

        # Peak labels
        labels_data = [
            (0.5, "0.5 Hz\ndrift"),
            (10, "10 Hz\nalpha"),
            (60, "60 Hz\nnoise"),
        ]
        peak_labels = VGroup()
        for freq_val, txt in labels_data:
            idx = np.argmin(np.abs(freqs_d - freq_val))
            pt = ax_freq.c2p(freqs_d[idx], spec_d[idx])
            lbl = Text(txt, font_size=16, color=PEAK_LABEL_COLOR).next_to(pt, UP, buff=0.15)
            dot = Dot(pt, radius=0.05, color=PEAK_LABEL_COLOR)
            peak_labels.add(VGroup(lbl, dot))

        self.play(
            *[FadeIn(pl, shift=UP * 0.2) for pl in peak_labels],
            run_time=1.0,
        )
        self.wait(2.0)

        # ── PART 3: Bandpass filter mask sweeps across ─────────
        # Draw the filter passband as a semi-transparent green rectangle
        low_cut, high_cut = 1, 40
        left_edge = ax_freq.c2p(0, 0)[0]
        right_edge = ax_freq.c2p(80, 0)[0]
        top_edge = ax_freq.c2p(0, float(spec_d.max()) * 1.15)[1]
        bottom_edge = ax_freq.c2p(0, 0)[1]
        band_height = top_edge - bottom_edge

        pass_left = ax_freq.c2p(low_cut, 0)[0]
        pass_right = ax_freq.c2p(high_cut, 0)[0]
        pass_width = pass_right - pass_left

        # Grey-out regions outside passband
        block_left = Rectangle(
            width=pass_left - left_edge,
            height=band_height,
            fill_color=GREY_D,
            fill_opacity=0.0,
            stroke_width=0,
        ).move_to(
            np.array([(left_edge + pass_left) / 2, (top_edge + bottom_edge) / 2, 0])
        )
        block_right = Rectangle(
            width=right_edge - pass_right,
            height=band_height,
            fill_color=GREY_D,
            fill_opacity=0.0,
            stroke_width=0,
        ).move_to(
            np.array([(pass_right + right_edge) / 2, (top_edge + bottom_edge) / 2, 0])
        )

        # Green passband outline
        pass_rect = Rectangle(
            width=pass_width,
            height=band_height,
            stroke_color=FILTER_COLOR,
            stroke_width=2.5,
            fill_color=FILTER_COLOR,
            fill_opacity=0.15,
        ).move_to(
            np.array([(pass_left + pass_right) / 2, (top_edge + bottom_edge) / 2, 0])
        )

        bp_label = Text("Bandpass 1–40 Hz", font_size=20, color=FILTER_COLOR)
        bp_label.next_to(pass_rect, DOWN, buff=0.12)

        self.play(
            FadeIn(pass_rect),
            FadeIn(bp_label),
            run_time=1.0,
        )
        self.wait(1.0)
        self.play(
            block_left.animate.set_fill(opacity=0.6),
            block_right.animate.set_fill(opacity=0.6),
            run_time=2.0,
        )
        self.wait(1.5)

        # ── PART 4: Transform raw → clean ─────────────────────
        title_clean = Text("After: Bandpass 1–40 Hz", font_size=32, color=CLEAN_COLOR)
        title_clean.move_to(title_raw.get_center())

        # Rebuild the time-domain axes at the scaled position to plot clean signal
        # We'll just create a new graph on the same scaled axes
        # Access the original (unscaled) axes to build the graph, then scale
        clean_vals = clean[::2]
        raw_vals = raw[::2]
        t_vals = t[::2]

        # Build clean graph on original axes coordinate system
        clean_graph = ax_time.plot_line_graph(
            x_values=t_vals, y_values=clean_vals,
            add_vertex_dots=False, line_color=CLEAN_COLOR, stroke_width=2.0,
        )

        self.play(
            Transform(title_raw, title_clean),
            Transform(raw_graph, clean_graph),
            run_time=2.5,
        )
        self.wait(2.5)

        # Final hold
        self.wait(2.5)
