#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow"]
# ///
"""Annotate <img> tags in public/ with dimensions and EXIF.

Every image gets width/height/--ar (for justified photo grids) and, when the
file carries EXIF, data-exif (camera/lens/exposure, shown in the lightbox).
Metadata is fetched once per URL and cached in image-meta.json (commit it).
"""
import io
import json
import re
import sys
import urllib.request
from pathlib import Path

from PIL import Image

root = Path(__file__).resolve().parent.parent
cache_path = root / "image-meta.json"
cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

IMG = re.compile(r'<img\b([^>]*?)\s*/?>')
SRC = re.compile(r'\bsrc\s*=\s*"([^"]+)"')
FIGURE = re.compile(r'<figure\b((?:(?!style=)[^>])*)>(\s*<img\b[^>]*--ar:([\d.]+)[^>]*>)')


def read(img):
    w, h = img.size
    ex = img.getexif()
    if ex.get(0x0112) in (5, 6, 7, 8):  # EXIF orientation: browsers rotate these
        w, h = h, w
    meta = {"width": w, "height": h}

    d = ex.get_ifd(0x8769)
    model = (ex.get(0x0110) or "").strip(" \x00")
    make = (ex.get(0x010F) or "").strip(" \x00")
    lens = (d.get(0xA434) or "").strip(" \x00")
    if lens and model and model in lens:
        lens = ""  # phones: "iPhone 13 Pro back triple camera 5.7mm f/1.5" — noise
    if make.isupper():
        make = make.title()  # "SONY" -> "Sony"
    if model and make and make.split()[0].lower() not in model.lower() and make.lower() != "apple":
        model = f"{make} {model}"
    if model:
        meta["camera"] = model
    if lens:
        meta["lens"] = lens
    parts = [p for p in (model, lens) if p]

    # Real focal length for a named lens; 35mm-equivalent for phones.
    focal = (d.get(0x920A) if lens else d.get(0xA405)) or d.get(0x920A)
    if focal:
        parts.append(f"{float(focal):g}mm")
    if d.get(0x829D):
        parts.append(f"f/{round(float(d[0x829D]), 1):g}")
    t = d.get(0x829A)
    if t:
        t = float(t)
        parts.append(f"1/{round(1 / t)}" if t < 1 else f"{t:g}s")
    iso = d.get(0x8827)
    if iso:
        parts.append(f"ISO {iso[0] if isinstance(iso, tuple) else iso}")
    if parts:
        meta["exif"] = " · ".join(parts)

    taken = d.get(0x9003) or ex.get(0x0132)
    if taken:
        # "YYYY:MM:DD HH:MM:SS" -> "YYYY-MM-DD HH:MM:SS" (sorts chronologically as a string)
        meta["taken"] = taken[:10].replace(":", "-") + taken[10:19]
    return meta


def fetch(url):
    url = url.split("#")[0]
    if url in cache:
        return cache[url]
    try:
        if "://" in url:
            # EXIF and dimensions sit at the start; fall back to the whole file.
            for rng in ("bytes=0-262143", None):
                headers = {"User-Agent": "ellie.wtf-build/1.0"}
                if rng:
                    headers["Range"] = rng
                with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
                    data = r.read()
                try:
                    meta = read(Image.open(io.BytesIO(data)))
                    break
                except Exception:
                    if rng is None:
                        raise
        else:
            meta = read(Image.open(root / "public" / url.lstrip("/")))
    except Exception as e:
        print(f"image-meta: could not read {url}: {e}", file=sys.stderr)
        return None
    cache[url] = meta
    print(f"image-meta: {url} -> {meta['width']}x{meta['height']}" + (f" ({meta['exif']})" if "exif" in meta else ""))
    return meta


def annotate(m, page_dir):
    attrs = m.group(1)
    s = SRC.search(attrs)
    if not s or "--ar" in attrs:
        return m.group(0)
    url = s.group(1)
    if "://" not in url and not url.startswith("/"):
        # Relative path (page-bundle asset): resolve against the page's directory.
        url = "/" + str((page_dir / url).resolve().relative_to(root / "public"))
    meta = fetch(url)
    if not meta:
        return m.group(0)
    extra = f' data-exif="{meta["exif"]}"' if "exif" in meta and "data-exif" not in attrs else ""
    return f'<img{attrs} width="{meta["width"]}" height="{meta["height"]}" style="--ar:{meta["width"] / meta["height"]:.4f}"{extra}>'


# `image-meta.py --fetch URL...` only populates the cache (used by photos.py).
if len(sys.argv) > 1 and sys.argv[1] == "--fetch":
    for url in sys.argv[2:]:
        fetch(url)
    cache_path.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n")
    sys.exit(0)

changed = 0
for html in (root / "public").rglob("*.html"):
    text = html.read_text()
    new = IMG.sub(lambda m: annotate(m, html.parent), text)
    # A <figure> wrapping an image inherits its --ar so it can be a grid item.
    new = FIGURE.sub(lambda m: f'<figure{m.group(1)} style="--ar:{m.group(3)}">{m.group(2)}', new)
    if new != text:
        html.write_text(new)
        changed += 1

cache_path.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n")
print(f"image-meta: updated {changed} file(s)")
