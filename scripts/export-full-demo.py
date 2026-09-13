"""Synchronize speech with real browser footage, shortening only AI waits."""
import json
from pathlib import Path
import re
import subprocess
import textwrap
import wave

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/demo-video-v3"
FFMPEG = next((ROOT / ".runtime/video-tools/imageio_ffmpeg/binaries").glob("ffmpeg-*"))
recording = json.loads((OUT / "recording.json").read_text())
if not recording.get("completed") or recording["errors"]:
    raise RuntimeError("Only a successfully completed recording can be exported.")
cuts = [(w["start"] + w["keep_start"], w["end"] - w["keep_end"]) for w in recording["waits"]
        if w["end"] - w["start"] > w["keep_start"] + w["keep_end"]]
cuts.sort()
end = recording.get("contentEnd") or recording["duration"]


def adjusted(t):
    return t - sum(max(0, min(t, b) - a) for a, b in cuts if t > a)


def timestamp(t, subtitle=False):
    milliseconds = max(0, round(t * 1000))
    seconds, ms = divmod(milliseconds, 1000)
    minutes, sec = divmod(seconds, 60)
    if subtitle:
        hours, minute = divmod(minutes, 60)
        return f"{hours:02}:{minute:02}:{sec:02},{ms:03}"
    return f"{minutes}:{sec:02}"


duration = adjusted(end)
rate = 24000
track = bytearray(round((duration + .5) * rate) * 2)
previous_end = 0
chapters, subtitles = [], []
for n, scene in enumerate(recording["chapters"], 1):
    at = adjusted(scene["at"])
    with wave.open(scene["audio"], "rb") as audio:
        if (audio.getframerate(), audio.getnchannels(), audio.getsampwidth()) != (rate, 1, 2):
            raise ValueError("Narration format differs from timeline format.")
        samples = audio.readframes(audio.getnframes())
    if at < previous_end - .03:
        raise ValueError("Narration scenes overlap.")
    for a, b in cuts:
        if scene["at"] < b and scene["at"] + scene["audio_seconds"] > a:
            raise ValueError("An inference edit would cut narration.")
    offset = round(at * rate) * 2
    track[offset:offset + len(samples)] = samples
    previous_end = at + len(samples) / (2 * rate)
    chapters.append(f"- {timestamp(at)} — **{scene['label']}**: {scene['caption']}")
    lines = textwrap.wrap(scene["narration"], width=46)
    blocks = ["\n".join(lines[i:i+2]) for i in range(0, len(lines), 2)]
    total_words = sum(len(block.split()) for block in blocks)
    spoken_words = 0
    for block in blocks:
        cue_start = at + scene["audio_seconds"] * spoken_words / total_words
        spoken_words += len(block.split())
        cue_end = at + scene["audio_seconds"] * spoken_words / total_words
        subtitles.append(f"{len(subtitles)+1}\n{timestamp(cue_start, True)} --> {timestamp(cue_end, True)}\n{block}\n")

audio_path = OUT / "narration-track.wav"
with wave.open(str(audio_path), "wb") as audio:
    audio.setnchannels(1)
    audio.setsampwidth(2)
    audio.setframerate(rate)
    audio.writeframes(track)
(OUT / "the-pick-demo.srt").write_text("\n".join(subtitles))
(OUT / "transcript.md").write_text("# The Pick demo narration\n\n" + "\n\n".join(
    f"**{timestamp(adjusted(s['at']))} · {s['label']}**\n\n{s['narration']}" for s in recording["chapters"]) + "\n")

segments, cursor = [], 0
for a, b in cuts:
    segments.append((cursor, a))
    cursor = b
segments.append((cursor, end))
filters = []
if len(segments) > 1:
    filters.append(f"[0:v]split={len(segments)}" + "".join(f"[s{i}]" for i in range(len(segments))))
for i, (a, b) in enumerate(segments):
    source = f"s{i}" if len(segments) > 1 else "0:v"
    filters.append(f"[{source}]trim=start={a}:end={b},setpts=PTS-STARTPTS[v{i}]")
filters.append("".join(f"[v{i}]" for i in range(len(segments))) +
               f"concat=n={len(segments)}:v=1:a=0,fps=25,format=yuv420p[v]")
filters.append("[1:a]loudnorm=I=-16:TP=-1.5:LRA=11[a]")
destination = OUT / "the-pick-demo.mp4"
subprocess.run([str(FFMPEG), "-hide_banner", "-loglevel", "warning", "-y", "-i", recording["raw"], "-i", str(audio_path),
                "-filter_complex", ";".join(filters), "-map", "[v]", "-map", "[a]", "-t", str(duration),
                "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
                "-movflags", "+faststart", "-metadata", "title=The Pick — Family and Iconic Experience Demo",
                "-metadata", "comment=Real local app and Ollama agent. Synthetic narration. AI waits shortened. Illustrative event listings.",
                str(destination)], check=True)
metadata = subprocess.run([str(FFMPEG), "-hide_banner", "-i", str(destination)], capture_output=True, text=True).stderr
if "Audio: aac" not in metadata or "Video: h264" not in metadata:
    raise RuntimeError("Final video must include H.264 video and AAC narration.")
match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", metadata)
actual = sum(float(v)*f for v, f in zip(match.groups(), [3600, 60, 1]))
if abs(actual-duration)>1:
    raise RuntimeError("Export duration differs from the narration timeline.")
summary = dict(file=str(destination), duration_seconds=actual, bytes=destination.stat().st_size,
               narration_seconds=sum(s["audio_seconds"] for s in recording["chapters"]),
               removed_wait_seconds=sum(b-a for a,b in cuts), chapters=len(chapters),
               video="H.264, 1440×1000, 25 fps", audio="AAC, synthetic Samantha narration")
(OUT / "export.json").write_text(json.dumps(summary, indent=2)+"\n")
(OUT / "README.md").write_text(
    "# The Pick — full narrated demo\n\n"
    f"Share **the-pick-demo.mp4**: {timestamp(actual)}, {destination.stat().st_size/1000000:.1f} MB. "
    "H.264 video, 1440 × 1000, 25 fps, AAC audio. Includes synthetic spoken narration and on-screen chapter captions. "
    "A full transcript and optional SRT subtitles are included.\n\n"
    "Both searches use the real local app and Ollama agent. Only the middle of long inference waits is removed; "
    "results are not mocked. Event dates, matchups and prices are illustrative. Venue guidance retains source links and review dates; "
    "weather uses the live provider when a forecast is available. Narration is generated locally with the macOS Samantha voice.\n\n"
    "## Chapters\n\n"+"\n".join(chapters)+"\n\n"
    "## Re-record\n\n"
    "1. Start the frontend, backend and Ollama.\n"
    "2. From the root, run `backend/.venv/bin/python scripts/prepare-demo-narration.py`.\n"
    "3. From `frontend`, run `node scripts/record-full-demo.mjs`. Use `DEMO_REHEARSAL=1` for a short rehearsal saved separately.\n"
    "4. From the root, run `backend/.venv/bin/python scripts/export-full-demo.py`.\n\n"
    "Forecasts and source freshness can change; review the script before a future recording. Earlier demo versions are preserved.\n")
print(json.dumps(summary, indent=2))
