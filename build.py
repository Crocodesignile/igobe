"""Bundle index.html + assets into one double-clickable file: ../IGOBE-film.html

Run:  python3 build.py
- every assets/... image is inlined as a data URI
- the logo SVG is inlined (so it can take the ink colour)
- the film frames are inlined as window.__FRAMES (the page reads them instead of assets/frames/)
Fonts still load from the web (Switzer, Pretendard).
"""
import base64
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
OUT = ROOT.parent / "IGOBE-film.html"
MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp", ".svg": "image/svg+xml"}


def data_uri(path: pathlib.Path) -> str:
    return f"data:{MIME[path.suffix.lower()]};base64," + base64.b64encode(path.read_bytes()).decode()


html = (ROOT / "index.html").read_text()

# logo: inline SVG
svg = (ROOT / "assets/logo.svg").read_text()
svg = svg.replace("<svg ", '<svg aria-hidden="true" ', 1)
html = re.sub(r"<!--LOGO-->.*?<!--/LOGO-->", svg, html, flags=re.S)

# images
html = re.sub(r'src="(assets/[^"]+)"', lambda m: f'src="{data_uri(ROOT / m.group(1))}"', html)

# frames
frames = sorted((ROOT / "assets/frames").glob("f*.webp"))
arr = ",".join(f'"{data_uri(f)}"' for f in frames)
html = html.replace("<script type=\"module\">", f"<script>window.__FRAMES=[{arr}]</script>\n<script type=\"module\">", 1)

OUT.write_text(html)
print(f"{OUT}  {OUT.stat().st_size / 1e6:.1f} MB, {len(frames)} frames")
