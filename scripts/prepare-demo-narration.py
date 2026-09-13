"""Create local synthetic narration without sending text to a cloud service."""
import json
from pathlib import Path
import subprocess
import wave

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/demo-video-v3"
encoder = next((ROOT / ".runtime/video-tools/imageio_ffmpeg/binaries").glob("ffmpeg-*"))
scenes = json.loads((OUT / "storyboard.json").read_text())
(OUT / "audio").mkdir(exist_ok=True, parents=True)
for scene in scenes:
    base = OUT / "audio" / scene["id"]
    base.with_suffix(".txt").write_text(scene["narration"])
    subprocess.run(["say", "-v", "Samantha", "-r", "175", "-f", str(base.with_suffix(".txt")),
                    "-o", str(base.with_suffix(".aiff"))], check=True)
    subprocess.run([str(encoder), "-hide_banner", "-loglevel", "error", "-y", "-i", str(base.with_suffix(".aiff")),
                    "-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le", str(base.with_suffix(".wav"))], check=True)
    with wave.open(str(base.with_suffix(".wav"))) as audio:
        scene["audio_seconds"] = audio.getnframes() / audio.getframerate()
    if scene["audio_seconds"] < 1:
        raise RuntimeError("Speech synthesis produced empty audio; check macOS speech access.")
    scene["audio"] = str(base.with_suffix(".wav"))
(OUT / "narration.json").write_text(json.dumps(scenes, indent=2) + "\n")
print(f"Prepared {len(scenes)} scenes; {sum(s['audio_seconds'] for s in scenes):.1f} seconds of narration.")
