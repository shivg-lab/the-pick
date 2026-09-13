"""Export the silent walkthrough and a separately timed optional voiceover script."""
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/demo-video-v4"
FFMPEG = next((ROOT / ".runtime/video-tools/imageio_ffmpeg/binaries").glob("ffmpeg-*"))
recording = json.loads((OUT / "recording.json").read_text())
if not recording.get("completed") or recording["errors"]:
    raise RuntimeError("Only a successfully completed recording can be exported.")
cuts = sorted((w["start"] + w["keep_start"], w["end"] - w["keep_end"])
              for w in recording["waits"]
              if w["end"] - w["start"] > w["keep_start"] + w["keep_end"])
end = recording.get("contentEnd") or recording["duration"]


def adjusted(t):
    return t - sum(max(0, min(t, b) - a) for a, b in cuts if t > a)


def timestamp(t, subtitle=False):
    seconds, ms = divmod(max(0, round(t * 1000)), 1000)
    minutes, sec = divmod(seconds, 60)
    if subtitle:
        hours, minute = divmod(minutes, 60)
        return f"{hours:02}:{minute:02}:{sec:02},{ms:03}"
    return f"{minutes}:{sec:02}"


duration = adjusted(end)
if not 180 <= duration <= 240:
    raise RuntimeError(f"The requested edit must be 3–4 minutes; timeline is {duration:.2f}s.")
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
destination = OUT / "the-pick-demo.mp4"
subprocess.run([str(FFMPEG), "-hide_banner", "-loglevel", "warning", "-y", "-i", recording["raw"],
                "-filter_complex", ";".join(filters), "-map", "[v]", "-an", "-t", str(duration),
                "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-movflags", "+faststart",
                "-metadata", "title=The Pick — Family and Iconic Experience Demo",
                "-metadata", "comment=Silent walkthrough of the local app. AI waiting time shortened.",
                str(destination)], check=True)
metadata = subprocess.run([str(FFMPEG), "-hide_banner", "-i", str(destination)], capture_output=True, text=True).stderr
if "Audio:" in metadata or "Video: h264" not in metadata:
    raise RuntimeError("Final video must be H.264 with no audio stream.")
match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", metadata)
actual = sum(float(v)*f for v, f in zip(match.groups(), [3600, 60, 1]))
if abs(actual-duration) > 1 or not 180 <= actual <= 240:
    raise RuntimeError("Export duration differs from the requested timeline.")

chapters = [{**s, "at": adjusted(s["at"])} for s in recording["chapters"]]
for i, s in enumerate(chapters):
    s["end"] = chapters[i+1]["at"] if i+1 < len(chapters) else duration
(OUT / "chapters.json").write_text(json.dumps(chapters, indent=2)+"\n")
(OUT / "voiceover-script.md").write_text(
    "# Optional voiceover — The Pick\n\n"
    "The MP4 is silent. These are suggested narration windows for a later voiceover. "
    "Use a warm, conversational delivery, approximately 140–150 words per minute, "
    "and align each paragraph to its chapter; leave the remaining time for natural pauses.\n\n" +
    "\n\n".join(f"**{timestamp(s['at'])}–{timestamp(s['end'])} · {s['label']}**\n\n{s['narration']}" for s in chapters) + "\n")
(OUT / "voiceover-script.txt").write_text("\n\n".join(s["narration"] for s in chapters)+"\n")
(OUT / "the-pick-demo.srt").write_text("\n".join(
    f"{i+1}\n{timestamp(s['at'], True)} --> {timestamp(s['end'], True)}\n{s['caption']}\n"
    for i, s in enumerate(chapters)))
summary = dict(file=str(destination), duration_seconds=actual, bytes=destination.stat().st_size,
               removed_wait_seconds=sum(b-a for a, b in cuts), chapters=len(chapters),
               video="H.264, 1440×1000, 25 fps", audio="None — no audio stream")
(OUT / "export.json").write_text(json.dumps(summary, indent=2)+"\n")
(OUT / "README.md").write_text(
    "# The Pick — silent demo\n\n"
    f"Share **the-pick-demo.mp4**: {timestamp(actual)}, {destination.stat().st_size/1000000:.1f} MB. "
    "H.264 video, 1440 × 1000, 25 fps. No audio track. On-screen chapter captions are included.\n\n"
    "The family search includes the winner, alternatives, score breakdown and full venue guide: "
    "bags, food, arrival, parking, seating, weather, attire, sources and feedback. "
    "The iconic search shows the changed winner, reasons and alternatives without repeating the guide.\n\n"
    "Both searches use the real local app and Ollama agent. Only long AI waits are shortened. "
    "The app's event fixtures and source labels remain unchanged. Previous recordings are preserved.\n\n"
    "## Optional voiceover\n\n"
    "Use `voiceover-script.md` for chapter timing and `voiceover-script.txt` for clean copy. "
    "These files are suggestions for adding a voiceover later; no speech was generated for this version. "
    "`the-pick-demo.srt` contains the on-screen captions, not a spoken transcript.\n\n"
    "## Chapters\n\n" + "\n".join(f"- {timestamp(s['at'])} — {s['label']}" for s in chapters) + "\n\n"
    "## Re-record\n\n"
    "1. Start the frontend, backend and Ollama.\n"
    "2. From `frontend`, run `node scripts/record-silent-demo.mjs`.\n"
    "3. From the root, run `backend/.venv/bin/python scripts/export-silent-demo.py`.\n")
print(json.dumps(summary, indent=2))
