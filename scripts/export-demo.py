"""Export the Playwright walkthrough as a compact, broadly compatible MP4."""
import json
from pathlib import Path
import subprocess
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / (sys.argv[1] if len(sys.argv)>1 else 'docs/demo-video-v2')
recording = json.loads((OUT / 'recording.json').read_text())
encoder = next((ROOT / '.runtime/video-tools/imageio_ffmpeg/binaries').glob('ffmpeg-*'))
destination = OUT / 'the-pick-demo.mp4'
wait_start, wait_end = recording['waitStart'], recording['waitEnd']
if recording['errors'] or wait_end is None or not recording.get('completed'):
    raise RuntimeError('Recording did not complete successfully')

# Preserve seven seconds at the start and two at the end of actual inference.
# Every UI result comes from the live local app; no responses are mocked.
removed = max(0, wait_end - wait_start - 9)
if removed:
    cut_start, cut_end = wait_start + 7, wait_end - 2
    video_filter = (
        f'[0:v]split=2[a][b];[a]trim=end={cut_start},setpts=PTS-STARTPTS[a1];'
        f'[b]trim=start={cut_end},setpts=PTS-STARTPTS[b1];'
        '[a1][b1]concat=n=2:v=1:a=0,fps=25,format=yuv420p[v]'
    )
else:
    video_filter = '[0:v]fps=25,format=yuv420p[v]'

subprocess.run([
    str(encoder), '-hide_banner', '-loglevel', 'warning', '-y',
    '-i', recording['raw'], '-filter_complex', video_filter, '-map', '[v]',
    '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
    '-movflags', '+faststart', '-metadata', 'title=The Pick — Redesigned Local App Demo',
    '-metadata', 'comment=Actual local app walkthrough. AI waiting time shortened. Illustrative event scenarios.',
    str(destination),
], check=True)

metadata = subprocess.run([str(encoder), '-hide_banner', '-i', str(destination)], capture_output=True, text=True).stderr
match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', metadata)
actual_seconds = sum(float(value)*factor for value,factor in zip(match.groups(), [3600,60,1])) if match else None

def timestamp(seconds):
    whole = max(0, round(seconds))
    return f'{whole // 60}:{whole % 60:02d}'

chapters = []
for chapter in recording['chapters']:
    adjusted = chapter['at'] - (removed if chapter['at'] >= wait_end else 0)
    chapters.append(f"- {timestamp(adjusted)} — {chapter['label']}: {chapter['message']}")

(OUT / 'README.md').write_text(
    '# The Pick demo video\n\n'
    'Share `the-pick-demo.mp4`. H.264 MP4, 1440 × 1000, 25 fps, with on-screen captions and no audio.\n\n'
    'Recorded from the running local application using its real Ollama agent. '
    'The middle of the AI waiting period is cut for pacing; all other interactions play at normal speed. '
    'Event scenarios, dates and prices are illustrative, not live listings. '
    'Venue guidance comes from the app’s stored sources.\n\n'
    f'Duration: {actual_seconds:.1f} seconds. File size: {destination.stat().st_size / 1000000:.1f} MB.\n\n'
    '## Walkthrough\n\n' + '\n'.join(chapters) + '\n\n'
    '## Re-record\n\n'
    'Start the frontend, backend and Ollama, then run `node scripts/record-demo.mjs` from `frontend/`. '
    'Run `backend/.venv/bin/python scripts/export-demo.py` from the repository root. '
    'The export script uses the project-local imageio-ffmpeg binary in `.runtime/video-tools/`.\n'
)
print(json.dumps({'file': str(destination), 'bytes': destination.stat().st_size,
                  'duration_seconds': actual_seconds,
                  'inference_wait_removed_seconds': removed}, indent=2))
