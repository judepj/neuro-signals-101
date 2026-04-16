"""Filtering in Action v2 — Narrative continuation of the sampling vignette.

Picks up where `sampling_aliasing_v2_vignette.py` ended: the EEG recording
is back, but contaminated with drift and 60 Hz mains noise. The attending
physician asks the tech "can we salvage this?" — and the answer is filters.

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


# Colour constants (match filtering_voiceover_edge.py)
RAW_COLOR = GREY_B
CLEAN_COLOR = BLUE
FILTER_COLOR = GREEN
PEAK_LABEL_COLOR = YELLOW


class FilteringV2(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            EdgeTTSService(voice="en-US-AndrewMultilingualNeural")
        )

        # ── Signal parameters (match filtering_voiceover_edge.py) ──
        fs = 500
        dur = 2.0
        t = np.linspace(0, dur, int(fs * dur), endpoint=False)
        drift = 0.4 * np.sin(2 * np.pi * 0.5 * t)
        alpha = 1.0 * np.sin(2 * np.pi * 10 * t)
        noise60 = 0.5 * np.sin(2 * np.pi * 60 * t)
        raw = drift + alpha + noise60
        clean = alpha.copy()

        freqs = np.fft.rfftfreq(len(raw), d=1 / fs)
        spectrum = np.abs(np.fft.rfft(raw)) / len(raw) * 2
        mask_disp = freqs <= 80
        freqs_d = freqs[mask_disp]
        spec_d = spectrum[mask_disp]

        # ══════════════════════════════════════════════════════════════
        # PHASE 1 — Continuation vignette
        # ══════════════════════════════════════════════════════════════

        scene_title = Text(
            "The recording is back — room 4",
            font_size=30, color=BLUE_B,
        ).to_edge(UP, buff=0.5)

        doctor_label = Text("Attending Physician", font_size=22, color=GOLD)
        tech_label = Text("EEG Tech", font_size=22, color=GREEN_B)

        doctor_box = RoundedRectangle(
            corner_radius=0.15, width=5.2, height=1.8,
            stroke_color=GOLD, stroke_width=2, fill_opacity=0.05, fill_color=GOLD,
        ).move_to(LEFT * 3.3 + DOWN * 1.8)
        tech_box = RoundedRectangle(
            corner_radius=0.15, width=5.2, height=1.8,
            stroke_color=GREEN_B, stroke_width=2, fill_opacity=0.05, fill_color=GREEN_B,
        ).move_to(RIGHT * 3.3 + DOWN * 1.8)

        doctor_label.next_to(doctor_box, UP, buff=0.12).align_to(doctor_box, LEFT).shift(RIGHT * 0.15)
        tech_label.next_to(tech_box, UP, buff=0.12).align_to(tech_box, LEFT).shift(RIGHT * 0.15)

        # Mini raw trace at the top where the "recording" can be inspected
        ax_mini = Axes(
            x_range=[0, dur, 0.5],
            y_range=[-2.2, 2.2, 1],
            x_length=10, y_length=2.0,
            tips=False,
            axis_config={"include_numbers": False, "stroke_width": 1.2, "color": GREY_C},
        ).shift(UP * 0.9)

        raw_mini = ax_mini.plot_line_graph(
            x_values=t[::2], y_values=raw[::2],
            add_vertex_dots=False, line_color=RAW_COLOR, stroke_width=1.5,
        )

        doctor_line_1 = Text(
            '"The recording is back.\nLet\'s take a look."',
            font_size=20, color=WHITE, line_spacing=0.9,
        ).move_to(doctor_box.get_center())

        with self.voiceover(
            text="The recording is back. Let's take a look."
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

        # Reveal the raw trace
        with self.voiceover(
            text="But something is wrong with the signal."
        ) as tracker:
            self.play(Create(ax_mini), run_time=0.5)
            self.play(Create(raw_mini), run_time=max(1.0, tracker.duration - 0.5))

        # Physician reacts
        doctor_line_2 = Text(
            '"Ugh. Baseline\'s drifting,\nand there\'s 60-hertz line\nnoise all over it."',
            font_size=19, color=WHITE, line_spacing=0.9,
        ).move_to(doctor_box.get_center())

        with self.voiceover(
            text="Ugh. Baseline is drifting, and there's sixty hertz line noise all over it."
        ) as tracker:
            self.play(FadeOut(doctor_line_1), run_time=0.3)
            self.play(
                Indicate(doctor_box, color=GOLD, scale_factor=1.03),
                Write(doctor_line_2),
                run_time=max(1.0, tracker.duration - 0.3),
            )

        # Tech replies
        tech_line_1 = Text(
            '"The prep room was\nright next to the MRI\ncontrol panel — lots of\nelectrical interference."',
            font_size=18, color=WHITE, line_spacing=0.9,
        ).move_to(tech_box.get_center())

        with self.voiceover(
            text="The prep room was right next to the M R I control panel — lots of electrical interference."
        ) as tracker:
            self.play(
                Indicate(tech_box, color=GREEN_B, scale_factor=1.03),
                Write(tech_line_1),
                run_time=max(1.2, tracker.duration),
            )

        # Physician asks: can we salvage this?
        doctor_line_3 = Text(
            '"...can we\nsalvage this?"',
            font_size=24, color=GOLD, line_spacing=0.9,
        ).move_to(doctor_box.get_center())

        with self.voiceover(
            text="The physician pauses. Can we salvage this?"
        ) as tracker:
            self.play(FadeOut(doctor_line_2), run_time=0.3)
            self.play(
                Indicate(doctor_box, color=GOLD, scale_factor=1.05),
                Write(doctor_line_3),
                run_time=max(1.0, tracker.duration - 0.3),
            )

        # Callout: Enter filters.
        enter_callout = Text(
            "Enter: filters.",
            font_size=46, color=FILTER_COLOR,
        ).move_to(ORIGIN)

        with self.voiceover(
            text="This is where filters earn their keep — the tools that turn contaminated recordings into readable clinical signal."
        ) as tracker:
            self.play(
                FadeOut(scene_title),
                FadeOut(doctor_box), FadeOut(doctor_label), FadeOut(doctor_line_3),
                FadeOut(tech_box), FadeOut(tech_label), FadeOut(tech_line_1),
                FadeOut(ax_mini), FadeOut(raw_mini),
                run_time=0.6,
            )
            self.play(Write(enter_callout), run_time=1.2)
            self.play(
                Indicate(enter_callout, color=FILTER_COLOR, scale_factor=1.08),
                run_time=max(0.8, tracker.duration - 1.8),
            )
            self.play(FadeOut(enter_callout), run_time=0.4)

        # ══════════════════════════════════════════════════════════════
        # PHASE 2 — Full raw signal with three contaminations
        # ══════════════════════════════════════════════════════════════

        title_raw = Text("Before: raw EEG", font_size=32, color=RAW_COLOR)
        title_raw.to_edge(UP, buff=0.3)

        ax_time = Axes(
            x_range=[0, dur, 0.5],
            y_range=[-2.2, 2.2, 1],
            x_length=11, y_length=3,
            axis_config={"include_tip": False, "stroke_width": 1.5},
        ).shift(UP * 0.3)
        x_label = ax_time.get_x_axis_label("t\\;(s)")
        y_label = ax_time.get_y_axis_label("\\mu V")

        raw_graph = ax_time.plot_line_graph(
            x_values=t[::2], y_values=raw[::2],
            add_vertex_dots=False, line_color=RAW_COLOR, stroke_width=1.5,
        )

        with self.voiceover(
            text="Here's the full recording. Three things are mixed together in this trace."
        ) as tracker:
            self.play(Write(title_raw), run_time=0.8)
            self.play(Create(ax_time), FadeIn(x_label), FadeIn(y_label), run_time=0.8)
            self.play(Create(raw_graph), run_time=max(1.2, tracker.duration - 1.6))

        # Three contamination bullets
        bullets = VGroup(
            Text("• 0.5 Hz baseline drift — sweat, electrode impedance",
                 font_size=22, color=RED_B),
            Text("• 10 Hz alpha — the brain signal we want",
                 font_size=22, color=BLUE_B),
            Text("• 60 Hz power line noise — US mains interference",
                 font_size=22, color=RED_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).to_edge(DOWN, buff=0.6)

        with self.voiceover(
            text="First — a slow baseline drift at half a hertz, from sweat and electrode impedance changes. Second — a ten hertz alpha rhythm: the actual brain signal, what we want. And third — sixty hertz power line noise from the U S electrical mains."
        ) as tracker:
            self.play(
                LaggedStart(*[FadeIn(b, shift=UP * 0.15) for b in bullets],
                            lag_ratio=0.45),
                run_time=max(2.5, tracker.duration - 0.4),
            )

        # ══════════════════════════════════════════════════════════════
        # PHASE 3 — FFT spectrum reveals the three peaks
        # ══════════════════════════════════════════════════════════════

        top_group = VGroup(title_raw, ax_time, x_label, y_label, raw_graph)

        ax_freq = Axes(
            x_range=[0, 80, 10],
            y_range=[0, float(spec_d.max()) * 1.15, 0.2],
            x_length=11, y_length=2.8,
            axis_config={"include_tip": False, "stroke_width": 1.5},
        ).to_edge(DOWN, buff=0.7)
        fx_label = ax_freq.get_x_axis_label("\\text{Frequency (Hz)}")
        fy_label = ax_freq.get_y_axis_label("\\text{Power}")

        spec_graph = ax_freq.plot_line_graph(
            x_values=freqs_d[::1], y_values=spec_d[::1],
            add_vertex_dots=False, line_color=WHITE, stroke_width=1.8,
        )

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

        with self.voiceover(
            text="The frequency spectrum shows exactly what's contaminating the signal — and exactly where the brain activity lives."
        ) as tracker:
            self.play(FadeOut(bullets), run_time=0.3)
            self.play(top_group.animate.scale(0.55).to_edge(UP, buff=0.15), run_time=0.8)
            self.play(Create(ax_freq), FadeIn(fx_label), FadeIn(fy_label), run_time=0.8)
            self.play(Create(spec_graph), run_time=1.0)
            self.play(
                *[FadeIn(pl, shift=UP * 0.2) for pl in peak_labels],
                run_time=max(1.0, tracker.duration - 2.9),
            )

        # ══════════════════════════════════════════════════════════════
        # PHASE 4 — Bandpass filter (1–40 Hz)
        # ══════════════════════════════════════════════════════════════

        low_cut, high_cut = 1, 40
        left_edge = ax_freq.c2p(0, 0)[0]
        right_edge = ax_freq.c2p(80, 0)[0]
        top_edge = ax_freq.c2p(0, float(spec_d.max()) * 1.15)[1]
        bottom_edge = ax_freq.c2p(0, 0)[1]
        band_height = top_edge - bottom_edge

        pass_left = ax_freq.c2p(low_cut, 0)[0]
        pass_right = ax_freq.c2p(high_cut, 0)[0]
        pass_width = pass_right - pass_left

        block_left = Rectangle(
            width=pass_left - left_edge,
            height=band_height,
            fill_color=GREY_D, fill_opacity=0.0, stroke_width=0,
        ).move_to(
            np.array([(left_edge + pass_left) / 2, (top_edge + bottom_edge) / 2, 0])
        )
        block_right = Rectangle(
            width=right_edge - pass_right,
            height=band_height,
            fill_color=GREY_D, fill_opacity=0.0, stroke_width=0,
        ).move_to(
            np.array([(pass_right + right_edge) / 2, (top_edge + bottom_edge) / 2, 0])
        )

        pass_rect = Rectangle(
            width=pass_width, height=band_height,
            stroke_color=FILTER_COLOR, stroke_width=2.5,
            fill_color=FILTER_COLOR, fill_opacity=0.15,
        ).move_to(
            np.array([(pass_left + pass_right) / 2, (top_edge + bottom_edge) / 2, 0])
        )

        bp_label = Text("Bandpass 1–40 Hz", font_size=20, color=FILTER_COLOR)
        bp_label.next_to(pass_rect, DOWN, buff=0.12)

        with self.voiceover(
            text="A bandpass filter keeps the frequencies we care about — one to forty hertz — and blocks everything else."
        ) as tracker:
            self.play(
                FadeIn(pass_rect), FadeIn(bp_label),
                run_time=max(1.2, tracker.duration - 0.2),
            )

        with self.voiceover(
            text="Drift: gone. Line noise: gone. Alpha rhythm: preserved."
        ) as tracker:
            self.play(
                block_left.animate.set_fill(opacity=0.6),
                block_right.animate.set_fill(opacity=0.6),
                run_time=max(1.8, tracker.duration),
            )

        # ══════════════════════════════════════════════════════════════
        # PHASE 5 — Before/after transformation
        # ══════════════════════════════════════════════════════════════

        title_clean = Text("After: clean alpha rhythm", font_size=32, color=CLEAN_COLOR)
        title_clean.move_to(title_raw.get_center())

        clean_vals = clean[::2]
        t_vals = t[::2]
        clean_graph = ax_time.plot_line_graph(
            x_values=t_vals, y_values=clean_vals,
            add_vertex_dots=False, line_color=CLEAN_COLOR, stroke_width=2.0,
        )

        with self.voiceover(
            text="Same recording — now readable."
        ) as tracker:
            self.play(
                Transform(title_raw, title_clean),
                Transform(raw_graph, clean_graph),
                run_time=max(1.8, tracker.duration),
            )

        # ══════════════════════════════════════════════════════════════
        # PHASE 6 — Clinical context
        # ══════════════════════════════════════════════════════════════

        # Clear freq panel + labels to give the clinical text room
        freq_group = VGroup(ax_freq, fx_label, fy_label, spec_graph,
                            peak_labels, pass_rect, bp_label,
                            block_left, block_right)

        clinical_1 = Text(
            "In clinical EEG: bandpass 0.5–70 Hz + 60 Hz notch — automatic.",
            font_size=24, color=WHITE,
        )
        clinical_2 = Text(
            "But know what the filter is doing to your signal.",
            font_size=24, color=GOLD,
        )
        clinical_3 = Text(
            "Aggressive high-pass → flattens slow delta waves.",
            font_size=22, color=RED_B,
        )
        clinical_4 = Text(
            "Wrong notch frequency → masks a real brain rhythm.",
            font_size=22, color=RED_B,
        )

        clinical_group = VGroup(
            clinical_1, clinical_2, clinical_3, clinical_4,
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.28).move_to(DOWN * 1.2)

        with self.voiceover(
            text="In clinical E E G, this happens automatically — modern machines apply a bandpass between zero point five and seventy hertz, plus a sixty hertz notch filter for line noise."
        ) as tracker:
            self.play(FadeOut(freq_group), run_time=0.5)
            self.play(
                FadeIn(clinical_1, shift=UP * 0.15),
                run_time=max(1.0, tracker.duration - 0.5),
            )

        with self.voiceover(
            text="But know what's being done to the signal — because filters can hide real pathology. A high-pass set too aggressively can flatten slow delta waves. A notch filter set at the wrong frequency can mask an actual brain rhythm."
        ) as tracker:
            self.play(
                LaggedStart(
                    FadeIn(clinical_2, shift=UP * 0.15),
                    FadeIn(clinical_3, shift=UP * 0.15),
                    FadeIn(clinical_4, shift=UP * 0.15),
                    lag_ratio=0.4,
                ),
                run_time=max(2.5, tracker.duration - 0.4),
            )

        # ══════════════════════════════════════════════════════════════
        # PHASE 7 — Callback close
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

        doctor_close = Text(
            '"Alpha\'s clean.\nI can read this.\nGood filter choice."',
            font_size=20, color=WHITE, line_spacing=0.9,
        ).move_to(doctor_box2.get_center())

        tech_close = Text(
            '"Standard bandpass —\n1 to 40.\nNotch at 60 for the mains."',
            font_size=19, color=WHITE, line_spacing=0.9,
        ).move_to(tech_box2.get_center())

        with self.voiceover(
            text="Back in room four. Alpha's clean. I can read this. Good filter choice."
        ) as tracker:
            self.play(
                FadeOut(clinical_group),
                FadeOut(title_raw), FadeOut(ax_time), FadeOut(x_label),
                FadeOut(y_label), FadeOut(raw_graph),
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
                Write(doctor_close),
                run_time=max(1.2, tracker.duration - 1.2),
            )

        with self.voiceover(
            text="Standard bandpass — one to forty. Notch at sixty for the mains."
        ) as tracker:
            self.play(
                Indicate(tech_box2, color=GREEN_B, scale_factor=1.03),
                Write(tech_close),
                run_time=max(1.2, tracker.duration),
            )

        final_line = Text(
            "Filters: the physician's lens on a noisy world.",
            font_size=32, color=BLUE_B, slant=ITALIC,
        ).move_to(ORIGIN)

        with self.voiceover(
            text="Filters — the physician's lens on a noisy world."
        ) as tracker:
            self.play(
                FadeOut(doctor_box2), FadeOut(doctor_label2), FadeOut(doctor_close),
                FadeOut(tech_box2), FadeOut(tech_label2), FadeOut(tech_close),
                run_time=0.6,
            )
            self.play(Write(final_line), run_time=max(1.2, tracker.duration - 0.6))
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
        "FilteringV2",
    ]))
