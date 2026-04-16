"""Post-hoc narration: synthesize timed voice segments and mux onto video.

Usage:
    python narrate.py                          # process all 3 videos
    python narrate.py --only fft               # just one
    python narrate.py --only sampling
    python narrate.py --only filtering
"""

import asyncio
import json
import os
import subprocess
import sys
import tempfile
import argparse
from pathlib import Path

# ── Narration segments: (timestamp_seconds, text) ──────────────────────

SEGMENTS = {
    "fft": [
        (0.0, "This signal looks complex, but it's actually made of just three hidden frequencies."),
        (3.0, "The FFT, Fast Fourier Transform, reveals what's inside."),
        (7.0, "A slow theta wave at four hertz."),
        (10.0, "A mid-range alpha wave at ten hertz."),
        (13.0, "And a fast beta wave at thirty hertz."),
        (18.0, "Add them all back together..."),
        (22.0, "and you get the original signal. Every complex waveform is just a sum of simple sine waves."),
    ],
    "sampling": [
        (0.0, "Here's a ten hertz sine wave, a smooth, continuous signal."),
        (3.0, "Sample it at fifty hertz, five times the signal frequency, and the reconstruction is nearly perfect."),
        (8.0, "Now try twelve hertz, barely above the Nyquist limit. The shape is preserved, but it's rough."),
        (14.0, "Eight hertz, below Nyquist. The samples now trace a completely different frequency. This is aliasing."),
        (21.0, "The alias frequency is two hertz, a phantom that doesn't exist in the original signal."),
        (25.0, "The rule: always sample at least twice the highest frequency."),
    ],
    "filtering": [
        (0.0, "This is raw E.E.G., contaminated with slow drift and sixty hertz power line noise."),
        (4.0, "The frequency spectrum shows three peaks: half a hertz drift, ten hertz alpha, and sixty hertz noise."),
        (10.0, "A bandpass filter keeps only the frequencies we care about, one to forty hertz."),
        (16.0, "Everything outside the green band gets blocked."),
        (21.0, "The result: a clean alpha rhythm, free of drift and line noise."),
        (26.0, "This is what filtering does in every E.E.G. machine, every day."),
    ],
}

# Map video key -> (input mp4 glob pattern, output filename)
SCRIPT_DIR = Path(__file__).parent
MEDIA_BASE = SCRIPT_DIR / "media" / "videos"

VIDEO_MAP = {
    "fft": {
        "input_dir": MEDIA_BASE / "fft_decomposition_video" / "720p30",
        "class_name": "FFTDecomposition",
        "output_name": "fft_decomposition.mp4",
    },
    "sampling": {
        "input_dir": MEDIA_BASE / "sampling_aliasing_video" / "720p30",
        "class_name": "SamplingAliasing",
        "output_name": "sampling_aliasing.mp4",
    },
    "filtering": {
        "input_dir": MEDIA_BASE / "filtering_video" / "720p30",
        "class_name": "FilteringDemo",
        "output_name": "filtering_demo.mp4",
    },
}

VOICE = "en-US-AndrewMultilingualNeural"


async def synthesize_segment(text: str, output_path: str):
    """Synthesize one text segment to MP3 via edge-tts."""
    import edge_tts
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(output_path)


def get_audio_duration(path: str) -> float:
    """Get duration of an audio file in seconds via ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def get_video_duration(path: str) -> float:
    """Get duration of a video file in seconds via ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def generate_silence(duration: float, output_path: str):
    """Generate a silent MP3 of given duration."""
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi",
         "-i", f"anullsrc=r=24000:cl=mono",
         "-t", f"{duration:.3f}",
         "-q:a", "9", "-acodec", "libmp3lame",
         output_path],
        capture_output=True, check=True,
    )


def concat_audio_files(file_list: list, output_path: str):
    """Concatenate audio files using ffmpeg concat demuxer."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for fpath in file_list:
            f.write(f"file '{fpath}'\n")
        concat_list = f.name

    try:
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
             "-i", concat_list, "-c", "copy", output_path],
            capture_output=True, check=True,
        )
    finally:
        os.unlink(concat_list)


def mux_audio_video(video_path: str, audio_path: str, output_path: str):
    """Mux audio onto video, keeping video codec, encoding audio as AAC."""
    subprocess.run(
        ["ffmpeg", "-y",
         "-i", video_path,
         "-i", audio_path,
         "-c:v", "copy",
         "-c:a", "aac", "-b:a", "192k",
         "-map", "0:v:0", "-map", "1:a:0",
         "-shortest",
         output_path],
        capture_output=True, check=True,
    )


async def process_video(key: str, tmpdir: str):
    """Process one video: synthesize segments, build audio track, mux."""
    segments = SEGMENTS[key]
    info = VIDEO_MAP[key]

    # Find the rendered video
    input_dir = info["input_dir"]
    mp4_files = sorted(input_dir.glob("*.mp4"))
    if not mp4_files:
        print(f"  ERROR: No .mp4 found in {input_dir}")
        return None
    video_path = str(mp4_files[0])
    video_dur = get_video_duration(video_path)
    print(f"  Input video: {video_path} ({video_dur:.1f}s)")

    # Synthesize each segment
    audio_parts = []  # list of (timestamp, mp3_path)
    for i, (ts, text) in enumerate(segments):
        seg_path = os.path.join(tmpdir, f"{key}_seg{i:02d}.mp3")
        print(f"    Synthesizing segment {i} @ {ts:.1f}s: {text[:50]}...")
        await synthesize_segment(text, seg_path)
        audio_parts.append((ts, seg_path))

    # Build the full audio track with correct timing
    # Strategy: for each segment, prepend silence to hit its timestamp
    ordered_files = []
    current_time = 0.0

    for ts, seg_path in audio_parts:
        # Insert silence gap before this segment
        gap = ts - current_time
        if gap > 0.05:  # only if meaningful gap
            silence_path = os.path.join(tmpdir, f"{key}_silence_{len(ordered_files):02d}.mp3")
            generate_silence(gap, silence_path)
            ordered_files.append(silence_path)
            current_time += gap

        # Add the speech segment
        ordered_files.append(seg_path)
        seg_dur = get_audio_duration(seg_path)
        current_time += seg_dur

    # Pad with silence to match video duration if audio is shorter
    if current_time < video_dur:
        tail_silence = os.path.join(tmpdir, f"{key}_tail_silence.mp3")
        generate_silence(video_dur - current_time, tail_silence)
        ordered_files.append(tail_silence)

    # Concatenate all parts
    combined_audio = os.path.join(tmpdir, f"{key}_combined.mp3")
    concat_audio_files(ordered_files, combined_audio)
    audio_dur = get_audio_duration(combined_audio)
    print(f"  Combined audio: {audio_dur:.1f}s")

    # Mux onto video
    output_path = os.path.join(tmpdir, info["output_name"])
    mux_audio_video(video_path, combined_audio, output_path)
    print(f"  Muxed output: {output_path}")
    return output_path


async def main():
    parser = argparse.ArgumentParser(description="Add narration to manim tutorial videos")
    parser.add_argument("--only", choices=["fft", "sampling", "filtering"],
                        help="Process only one video")
    args = parser.parse_args()

    keys = [args.only] if args.only else ["fft", "sampling", "filtering"]

    # Output directories
    base = SCRIPT_DIR.parent.parent  # interactive_tutorial/
    assets_videos = base / "assets" / "videos"
    docs_videos = base / "docs" / "assets" / "videos"
    assets_videos.mkdir(parents=True, exist_ok=True)
    docs_videos.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="narrate_") as tmpdir:
        for key in keys:
            print(f"\n{'='*60}")
            print(f"Processing: {key}")
            print(f"{'='*60}")

            output_path = await process_video(key, tmpdir)
            if output_path is None:
                print(f"  SKIPPED (no input video found)")
                continue

            # Copy to both output locations
            output_name = VIDEO_MAP[key]["output_name"]
            for dest_dir in [assets_videos, docs_videos]:
                dest = dest_dir / output_name
                subprocess.run(["cp", output_path, str(dest)], check=True)
                print(f"  Copied to: {dest}")

    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
