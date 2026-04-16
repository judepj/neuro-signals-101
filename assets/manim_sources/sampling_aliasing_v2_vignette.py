"""Sampling & Aliasing v2 — Clinical vignette framing + two-panel layout.

Opens with a physician/tech dialogue vignette — the ordering physician
doesn't know what sampling rate to request. By the end, they (and the
viewer) will. Then the video answers visually with a stacked two-panel
sampling demo:
 - Top panel: continuous 10 Hz sine (persistent)
 - Bottom panel: samples with stem lines dropping from x-axis
and closes with an expanded Nyquist reveal that circles back to the
vignette: the physician now answers the tech.

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


class SamplingAliasingV2(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            EdgeTTSService(voice="en-US-AndrewMultilingualNeural")
        )

        # ══════════════════════════════════════════════════════════════
        # PHASE 1 — Clinical vignette (physician orders, tech asks)
        # ══════════════════════════════════════════════════════════════

        scene_title = Text(
            "Ordering an EEG — temporal lobe epilepsy workup",
            font_size=30, color=BLUE_B,
        ).to_edge(UP, buff=0.5)

        # Physician dialogue block (left) and tech dialogue block (right)
        doctor_label = Text("Attending Physician", font_size=22, color=GOLD)
        tech_label = Text("EEG Tech", font_size=22, color=GREEN_B)

        doctor_box = RoundedRectangle(
            corner_radius=0.15, width=5.2, height=1.6,
            stroke_color=GOLD, stroke_width=2, fill_opacity=0.05, fill_color=GOLD,
        ).move_to(LEFT * 3.3 + DOWN * 0.2)
        tech_box = RoundedRectangle(
            corner_radius=0.15, width=5.2, height=1.6,
            stroke_color=GREEN_B, stroke_width=2, fill_opacity=0.05, fill_color=GREEN_B,
        ).move_to(RIGHT * 3.3 + DOWN * 0.2)

        doctor_label.next_to(doctor_box, UP, buff=0.12).align_to(doctor_box, LEFT).shift(RIGHT * 0.15)
        tech_label.next_to(tech_box, UP, buff=0.12).align_to(tech_box, LEFT).shift(RIGHT * 0.15)

        # Beat A — physician places the order
        doctor_order = Text(
            '"Routine EEG on room 4 —\nrule out temporal lobe epilepsy."',
            font_size=22, color=WHITE, line_spacing=0.9,
        ).move_to(doctor_box.get_center())

        with self.voiceover(
            text="The attending physician places an order. Routine E E G on room four, rule out temporal lobe epilepsy."
        ) as tracker:
            self.play(Write(scene_title), run_time=0.8)
            self.play(
                FadeIn(doctor_box, shift=RIGHT * 0.2),
                FadeIn(tech_box, shift=LEFT * 0.2),
                FadeIn(doctor_label), FadeIn(tech_label),
                run_time=0.6,
            )
            self.play(
                Indicate(doctor_box, color=GOLD, scale_factor=1.03),
                Write(doctor_order),
                run_time=max(1.0, tracker.duration - 1.4),
            )

        # Beat B — tech asks the physician
        tech_q = Text(
            '"Sure, doctor.\nWhat sampling rate\ndo you want?"',
            font_size=22, color=WHITE, line_spacing=0.9,
        ).move_to(tech_box.get_center())

        with self.voiceover(
            text="The E E G technician turns to the physician. Sure doctor — what sampling rate do you want me to use?"
        ) as tracker:
            self.play(
                Indicate(tech_box, color=GREEN_B, scale_factor=1.03),
                Write(tech_q),
                run_time=max(1.0, tracker.duration - 0.2),
            )

        # Beat C — physician doesn't know
        doctor_pause = Text(
            '"...what sampling rate?"',
            font_size=24, color=RED_B,
        ).move_to(doctor_box.get_center())

        with self.voiceover(
            text="The physician pauses. What sampling rate?"
        ) as tracker:
            self.play(
                FadeOut(doctor_order),
                run_time=0.3,
            )
            self.play(
                Indicate(doctor_box, color=RED_B, scale_factor=1.03),
                Write(doctor_pause),
                run_time=max(0.9, tracker.duration - 0.3),
            )

        # Beat D — the hook
        hook = Text(
            "Every ordering physician should be able to answer.",
            font_size=28, color=GOLD,
        ).move_to(UP * 0.2)
        hook_sub = Text(
            "By the end of this video, you will be.",
            font_size=30, color=GREEN_B,
        ).next_to(hook, DOWN, buff=0.4)

        with self.voiceover(
            text="This is a question every ordering physician should be able to answer. By the end of this video, you will be."
        ) as tracker:
            self.play(
                FadeOut(scene_title),
                FadeOut(doctor_box), FadeOut(doctor_label), FadeOut(doctor_pause),
                FadeOut(tech_box), FadeOut(tech_label), FadeOut(tech_q),
                run_time=0.5,
            )
            self.play(Write(hook), run_time=1.0)
            self.play(
                FadeIn(hook_sub, shift=UP * 0.15),
                run_time=max(0.8, tracker.duration - 1.5),
            )

        # Beat E — the three physician-facing questions
        questions = VGroup(
            Text("Why is 256 Hz the standard for routine EEG?",
                 font_size=26, color=GOLD),
            Text("When should you ask for 512, 1024, or 2048 Hz?",
                 font_size=26, color=BLUE_B),
            Text("What goes wrong if you pick too low?",
                 font_size=26, color=RED_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(ORIGIN)

        with self.voiceover(
            text="Three questions. Why is two hundred and fifty six hertz the standard for routine E E G? When should you ask for higher — five twelve, ten twenty four, or two thousand forty eight? And what goes wrong if you pick too low?"
        ) as tracker:
            self.play(
                FadeOut(hook), FadeOut(hook_sub),
                run_time=0.4,
            )
            self.play(
                LaggedStart(*[FadeIn(q, shift=UP * 0.2) for q in questions], lag_ratio=0.35),
                run_time=max(2.0, tracker.duration - 0.6),
            )
            self.play(FadeOut(questions), run_time=0.5)

        # ══════════════════════════════════════════════════════════════
        # PHASE 2 — Introduce the test signal (top panel only)
        # ══════════════════════════════════════════════════════════════

        f_sig = 10
        duration = 1.0
        omega = 2 * np.pi * f_sig

        ax_top = Axes(
            x_range=[0, duration, 0.2],
            y_range=[-1.5, 1.5, 0.5],
            x_length=11, y_length=2.2,
            tips=False,
            axis_config={"include_numbers": False, "stroke_width": 1.5, "color": GREY_C},
        ).shift(UP * 1.8)
        ax_bot = Axes(
            x_range=[0, duration, 0.2],
            y_range=[-1.5, 1.5, 0.5],
            x_length=11, y_length=2.2,
            tips=False,
            axis_config={"include_numbers": False, "stroke_width": 1.5, "color": GREY_C},
        ).shift(DOWN * 1.5)

        top_label = Text(
            "Continuous signal (10 Hz)", font_size=22, color=BLUE_B
        ).next_to(ax_top, UP, buff=0.1)

        continuous = ax_top.plot(
            lambda t: np.sin(omega * t),
            x_range=[0, duration, 0.001],
            color=BLUE,
            stroke_width=3,
        )

        bot_label_tracker = Text(
            "Samples (—)", font_size=22, color=GREY_A
        ).next_to(ax_bot, UP, buff=0.1)

        with self.voiceover(
            text="To answer all three, start with the simplest possible signal: a ten hertz sine wave."
        ) as tracker:
            self.play(
                Create(ax_top), FadeIn(top_label), run_time=0.7,
            )
            self.play(
                Create(continuous),
                run_time=max(1.0, tracker.duration - 0.7),
            )

        # Bring in the empty bottom panel now that it's about to be used
        self.play(
            Create(ax_bot),
            FadeIn(bot_label_tracker),
            run_time=0.6,
        )

        # ══════════════════════════════════════════════════════════════
        # PHASE 3 — Three sampling experiments in the bottom panel
        # ══════════════════════════════════════════════════════════════

        def make_samples_bot(fs, color):
            ts = np.arange(0, duration + 1e-9, 1.0 / fs)
            ts = ts[ts <= duration]
            dots = VGroup()
            stems = VGroup()
            drops = VGroup()
            for t_i in ts:
                y_i = float(np.sin(omega * t_i))
                bottom_pt = ax_bot.c2p(t_i, 0)
                top_pt = ax_bot.c2p(t_i, y_i)
                stems.add(
                    Line(bottom_pt, top_pt, stroke_width=2.2,
                         color=color, stroke_opacity=0.75)
                )
                dots.add(Dot(top_pt, radius=0.07, color=color, z_index=3))
                # Drop line: from the continuous signal point in the TOP
                # panel down to the sample dot in the BOTTOM panel.
                top_signal_pt = ax_top.c2p(t_i, y_i)
                bot_sample_pt = ax_bot.c2p(t_i, y_i)
                drop = DashedLine(
                    top_signal_pt, bot_sample_pt,
                    dash_length=0.08,
                    stroke_width=1,
                    color=color,
                    stroke_opacity=0.4,
                )
                drops.add(drop)
            return ts, dots, stems, drops

        def make_reconstruction_bot(ts, color):
            t_fine = np.linspace(0, duration, 2000)
            y_samples = np.sin(omega * ts)
            y_recon = np.zeros_like(t_fine)
            T_s = ts[1] - ts[0] if len(ts) > 1 else 1.0
            for i, t_s in enumerate(ts):
                y_recon += y_samples[i] * np.sinc((t_fine - t_s) / T_s)
            y_recon = np.clip(y_recon, -1.5, 1.5)
            points = [ax_bot.c2p(t_fine[j], y_recon[j]) for j in range(len(t_fine))]
            line = DashedVMobject(
                VMobject().set_points_smoothly(points),
                num_dashes=80, dashed_ratio=0.5,
            )
            line.set_color(color).set_stroke(width=2.2, opacity=0.7)
            return line

        def update_bot_label(new_text, new_color):
            new_label = Text(new_text, font_size=22, color=new_color).next_to(
                ax_bot, UP, buff=0.1
            )
            return new_label

        # ── 50 Hz (good) ──
        fs_good = 50
        ts_g, dots_g, stems_g, drops_g = make_samples_bot(fs_good, GREEN)
        recon_g = make_reconstruction_bot(ts_g, GREEN)
        label_g = update_bot_label("Samples at 50 Hz — faithful", GREEN)

        with self.voiceover(
            text="Sample it at fifty hertz. The samples trace the shape faithfully — nothing is lost."
        ) as tracker:
            self.play(
                ReplacementTransform(bot_label_tracker, label_g), run_time=0.4,
            )
            self.play(
                LaggedStart(*[Create(s) for s in stems_g], lag_ratio=0.025),
                LaggedStart(*[GrowFromCenter(d) for d in dots_g], lag_ratio=0.025),
                LaggedStart(*[Create(dl) for dl in drops_g], lag_ratio=0.025),
                run_time=max(1.4, tracker.duration - 1.4),
            )
            self.play(Create(recon_g), run_time=max(0.8, tracker.duration - 2.0))
        bot_label_tracker = label_g

        # ── 22 Hz (just above Nyquist) ──
        # For a 10 Hz signal, Nyquist rate = 20 Hz. 22 Hz is just above it,
        # so there is no aliasing: the reconstruction tracks the true 10 Hz
        # sine, just wobbly due to few samples per cycle.
        fs_close = 22
        ts_c, dots_c, stems_c, drops_c = make_samples_bot(fs_close, YELLOW)
        recon_c = make_reconstruction_bot(ts_c, YELLOW)
        label_c = update_bot_label("Samples at 22 Hz — just above Nyquist", YELLOW)

        with self.voiceover(
            text="Drop to twenty-two hertz — just above two times the signal frequency. The reconstruction is wobbly, but the frequency is still correct."
        ) as tracker:
            self.play(
                FadeOut(dots_g), FadeOut(stems_g), FadeOut(drops_g), FadeOut(recon_g),
                ReplacementTransform(bot_label_tracker, label_c),
                run_time=0.5,
            )
            self.play(
                LaggedStart(*[Create(s) for s in stems_c], lag_ratio=0.06),
                LaggedStart(*[GrowFromCenter(d) for d in dots_c], lag_ratio=0.06),
                LaggedStart(*[Create(dl) for dl in drops_c], lag_ratio=0.06),
                run_time=max(1.2, tracker.duration - 1.5),
            )
            self.play(Create(recon_c), run_time=max(0.8, tracker.duration - 2.5))
        bot_label_tracker = label_c

        # ── 8 Hz (aliased) ──
        fs_bad = 8
        ts_b, dots_b, stems_b, drops_b = make_samples_bot(fs_bad, RED)
        label_b = update_bot_label("Samples at 8 Hz — below 2 · f", RED)

        # Aliased wave drawn through the sample points
        f_alias = abs(f_sig - round(f_sig / fs_bad) * fs_bad)
        t_test = 1.0 / fs_bad
        true_val = np.sin(omega * t_test)
        alias_val = np.sin(2 * np.pi * f_alias * t_test)
        sign = 1.0 if (true_val * alias_val >= 0) else -1.0
        alias_wave = ax_bot.plot(
            lambda t: sign * np.sin(2 * np.pi * f_alias * t),
            x_range=[0, duration, 0.001],
            color=RED,
            stroke_width=3,
        )

        with self.voiceover(
            text="Now eight hertz — below two times the signal. Watch carefully."
        ) as tracker:
            self.play(
                FadeOut(dots_c), FadeOut(stems_c), FadeOut(drops_c), FadeOut(recon_c),
                ReplacementTransform(bot_label_tracker, label_b),
                run_time=0.5,
            )
            self.play(
                LaggedStart(*[Create(s) for s in stems_b], lag_ratio=0.1),
                LaggedStart(*[GrowFromCenter(d) for d in dots_b], lag_ratio=0.1),
                LaggedStart(*[Create(dl) for dl in drops_b], lag_ratio=0.1),
                run_time=max(1.2, tracker.duration - 1.0),
            )
        bot_label_tracker = label_b

        # Alias callout
        alias_note = MathTex(
            r"f_{\text{alias}} = |f_{\text{sig}} - f_s| = |10 - 8| = 2\;\text{Hz}",
            font_size=30, color=RED,
        ).next_to(ax_bot, DOWN, buff=0.25)

        with self.voiceover(
            text="The samples now trace a two hertz phantom wave — a signal that doesn't exist in the real recording. This is aliasing."
        ) as tracker:
            self.play(Create(alias_wave), run_time=max(1.2, tracker.duration - 1.2))
            self.play(FadeIn(alias_note), run_time=0.6)
            self.play(
                Indicate(alias_wave, color=RED, scale_factor=1.05),
                run_time=max(0.6, tracker.duration - 2.0),
            )

        # ══════════════════════════════════════════════════════════════
        # PHASE 4 — The Nyquist rule (expanded)
        # ══════════════════════════════════════════════════════════════

        to_fade = VGroup(
            ax_top, top_label, continuous,
            ax_bot, bot_label_tracker,
            dots_b, stems_b, drops_b, alias_wave, alias_note,
        )

        # ── Nyquist–Shannon theorem introduction ──
        theorem_title = Text(
            "Nyquist–Shannon Sampling Theorem",
            font_size=38, color=GOLD,
        ).move_to(UP * 1.2)
        theorem_attrib = Text(
            "(Harry Nyquist, 1928  ·  Claude Shannon, 1949)",
            font_size=22, color=GREY_A, slant=ITALIC,
        ).next_to(theorem_title, DOWN, buff=0.3)

        with self.voiceover(
            text="This is formalized by the Nyquist–Shannon sampling theorem: a signal can be perfectly reconstructed if and only if it is sampled at more than twice its highest frequency."
        ) as tracker:
            self.play(FadeOut(to_fade), run_time=0.6)
            self.play(Write(theorem_title), run_time=1.0)
            self.play(
                FadeIn(theorem_attrib, shift=UP * 0.15),
                run_time=max(0.6, tracker.duration - 1.6),
            )

        nyquist_label = Text(
            "The Nyquist Rule", font_size=36, color=GOLD
        ).move_to(UP * 2.2)
        nyquist_tex = MathTex(
            r"f_s \;\geq\; 2 \cdot f_{\max}",
            font_size=64, color=GOLD,
        ).move_to(UP * 0.9)

        with self.voiceover(
            text="In practice, the rule boils down to one inequality."
        ) as tracker:
            self.play(
                FadeOut(theorem_title), FadeOut(theorem_attrib),
                run_time=0.5,
            )
            self.play(
                Write(nyquist_label), Write(nyquist_tex),
                run_time=max(1.0, tracker.duration - 0.5),
            )

        # EEG specific calc
        eeg_calc = MathTex(
            r"f_{\max} = 80\;\text{Hz}\;\;\Longrightarrow\;\;f_s \geq 160\;\text{Hz}",
            font_size=40, color=WHITE,
        ).move_to(DOWN * 0.3)

        with self.voiceover(
            text="If the maximum frequency in your E E G signal is eighty hertz, you must sample at at least one hundred and sixty hertz to reconstruct it faithfully."
        ) as tracker:
            self.play(Write(eeg_calc), run_time=max(1.2, tracker.duration - 0.2))

        # 256 Hz headroom
        clinical_line = MathTex(
            r"256\;\text{Hz}\;\;>\;\;2 \cdot 80\;\text{Hz}",
            font_size=40, color=GREEN,
        ).move_to(DOWN * 1.5)
        headroom = Text(
            "→ headroom for anti-aliasing filters",
            font_size=24, color=GREEN_B,
        ).next_to(clinical_line, DOWN, buff=0.2)

        with self.voiceover(
            text="That's why two hundred and fifty six hertz is the clinical standard for routine E E G. Comfortable headroom above two times eighty, leaving room for anti-aliasing filters. For high-frequency oscillations in an epilepsy surgery workup, you step up to ten twenty four or higher."
        ) as tracker:
            self.play(Write(clinical_line), run_time=1.0)
            self.play(
                FadeIn(headroom, shift=UP * 0.15),
                run_time=max(0.6, tracker.duration - 1.2),
            )

        # Generalize
        generalize_group = VGroup(
            Text("Same rule everywhere:", font_size=26, color=WHITE),
            Text("EEG · ECG · EMG · audio · arterial BP", font_size=26, color=BLUE_B),
            Text("The math doesn't care what the biology is.",
                 font_size=24, color=GREY_A, slant=ITALIC),
        ).arrange(DOWN, buff=0.25).move_to(ORIGIN)

        with self.voiceover(
            text="This isn't just E E G. E C G, E M G, audio, arterial blood pressure — every biosignal follows the same rule. The math doesn't care what the biology is."
        ) as tracker:
            self.play(
                FadeOut(nyquist_label), FadeOut(nyquist_tex),
                FadeOut(eeg_calc), FadeOut(clinical_line), FadeOut(headroom),
                run_time=0.6,
            )
            self.play(
                LaggedStart(*[FadeIn(g, shift=UP * 0.15) for g in generalize_group],
                            lag_ratio=0.3),
                run_time=max(1.5, tracker.duration - 0.6),
            )

        # ══════════════════════════════════════════════════════════════
        # PHASE 5 — Circle back: the physician now answers the tech
        # ══════════════════════════════════════════════════════════════

        # Rebuild the two-box vignette layout so the callback is visual
        doctor_label2 = Text("Attending Physician", font_size=22, color=GOLD)
        tech_label2 = Text("EEG Tech", font_size=22, color=GREEN_B)

        doctor_box2 = RoundedRectangle(
            corner_radius=0.15, width=5.6, height=2.2,
            stroke_color=GOLD, stroke_width=2, fill_opacity=0.05, fill_color=GOLD,
        ).move_to(LEFT * 3.3 + DOWN * 0.2)
        tech_box2 = RoundedRectangle(
            corner_radius=0.15, width=5.6, height=2.2,
            stroke_color=GREEN_B, stroke_width=2, fill_opacity=0.05, fill_color=GREEN_B,
        ).move_to(RIGHT * 3.3 + DOWN * 0.2)

        doctor_label2.next_to(doctor_box2, UP, buff=0.12).align_to(doctor_box2, LEFT).shift(RIGHT * 0.15)
        tech_label2.next_to(tech_box2, UP, buff=0.12).align_to(tech_box2, LEFT).shift(RIGHT * 0.15)

        doctor_answer = Text(
            '"256 Hz for routine —\nmore than 2× the highest\nfrequency on scalp EEG.\nFor HFOs in surgery workup,\n1024 or higher."',
            font_size=18, color=WHITE, line_spacing=0.9,
        ).move_to(doctor_box2.get_center())

        tech_ok = Text('"Got it."', font_size=24, color=WHITE).move_to(tech_box2.get_center())

        with self.voiceover(
            text="Back in room four. The physician can answer now. Two fifty six hertz for routine — that's more than twice the highest frequency on scalp E E G. If we're mapping high-frequency oscillations for a surgery workup, go to ten twenty four or higher."
        ) as tracker:
            self.play(FadeOut(generalize_group), run_time=0.5)
            self.play(
                FadeIn(doctor_box2, shift=RIGHT * 0.2),
                FadeIn(tech_box2, shift=LEFT * 0.2),
                FadeIn(doctor_label2), FadeIn(tech_label2),
                run_time=0.6,
            )
            self.play(
                Indicate(doctor_box2, color=GOLD, scale_factor=1.03),
                Write(doctor_answer),
                run_time=max(1.2, tracker.duration - 1.1),
            )

        with self.voiceover(text="Got it.") as tracker:
            self.play(
                Indicate(tech_box2, color=GREEN_B, scale_factor=1.03),
                Write(tech_ok),
                run_time=max(0.8, tracker.duration),
            )

        final_line = Text(
            "Every biosignal follows the same rule.",
            font_size=30, color=BLUE_B, slant=ITALIC,
        ).move_to(ORIGIN)

        with self.voiceover(
            text="Every biosignal follows the same rule."
        ) as tracker:
            self.play(
                FadeOut(doctor_box2), FadeOut(doctor_label2), FadeOut(doctor_answer),
                FadeOut(tech_box2), FadeOut(tech_label2), FadeOut(tech_ok),
                run_time=0.6,
            )
            self.play(
                Write(final_line),
                run_time=max(1.0, tracker.duration - 0.4),
            )
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
        "SamplingAliasingV2",
    ]))
