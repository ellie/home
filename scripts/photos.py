#!/usr/bin/env python3
"""Collect photos for /photos into content/_photos.json.

Sources:
  * Post images whose URL ends in "#photos", e.g. ![Caption](https://…jpg#photos)
    or <img src="https://…jpg#photos" alt="Caption">. Alt text is the caption.
  * photos.toml at the repo root, for shots that aren't in a post.
"""
import json
import re
import subprocess
import tomllib
from pathlib import Path

root = Path(__file__).resolve().parent.parent
content = root / "content"

# "#photos" marks an image for the gallery; "#photos:2022" or "#photos:2022-07-14"
# also sets its date (for images without EXIF).
DATE = r'(?::(\d{4}(?:-\d{2}){0,2}))?'
MD_IMG = re.compile(r'!\[([^\]]*)\]\(([^)\s]+?)#photos' + DATE + r'(?:\s+"[^"]*")?\)')
HTML_IMG = re.compile(r'<img\b[^>]*?\bsrc="([^"]+?)#photos' + DATE + r'"[^>]*>')
ALT = re.compile(r'\balt="([^"]*)"')
FRONT = re.compile(r'^\+\+\+\n(.*?)\n\+\+\+', re.S)

# EXIF capture dates cached by scripts/image-meta.py on a previous build.
meta_path = root / "image-meta.json"
meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}


def taken(src):
    return meta.get(src.split("#")[0], {}).get("taken")


def exif(src, key="exif"):
    return meta.get(src.split("#")[0], {}).get(key, "")


photos = []

for md in sorted(content.rglob("*.md")):
    if md.name == "_index.md":
        continue
    text = md.read_text()
    fm = FRONT.match(text)
    if not fm:
        continue
    fm_meta = tomllib.loads(fm.group(1))
    if not fm_meta.get("date"):
        continue
    section = md.parent if md.name != "index.md" else md.parent.parent
    slug = fm_meta.get("slug") or (md.parent.name if md.name == "index.md" else md.stem)
    href = "/" + str(section.relative_to(content) / slug) + "/"

    # Date precedence: per-image #photos:DATE, EXIF, [extra] photos_date, post date.
    default_date = str(fm_meta.get("extra", {}).get("photos_date") or fm_meta["date"])[:10]
    found = [(m.group(2), m.group(1), m.group(3)) for m in MD_IMG.finditer(text)]
    found += [(m.group(1), (ALT.search(m.group(0)) or [None, ""])[1], m.group(2)) for m in HTML_IMG.finditer(text)]
    for src, caption, date in found:
        photos.append({
            "src": src,
            "caption": caption,
            "date": (date + "-01-01"[len(date) - 4:]) if date else None,
            "fallback": default_date,
            "href": href,
            "title": fm_meta.get("title", ""),
        })

toml_path = root / "photos.toml"
if toml_path.exists():
    for p in tomllib.loads(toml_path.read_text()).get("photo", []):
        photos.append({
            "src": p["src"],
            "caption": p.get("caption", ""),
            "date": str(p["date"])[:10] if p.get("date") else None,
            "fallback": "",
            "href": p.get("href", ""),
            "title": p.get("title", ""),
        })

# Fetch metadata for images not yet in the cache, then fill in EXIF-derived fields.
missing = sorted({p["src"].split("#")[0] for p in photos} - set(meta))
if missing:
    subprocess.run([str(root / "scripts" / "image-meta.py"), "--fetch", *missing], check=True)
    meta = json.loads(meta_path.read_text())
for p in photos:
    p["exif"] = exif(p["src"])
    p["camera"] = exif(p["src"], "camera")
    p["lens"] = exif(p["src"], "lens")
    p["date"] = p["date"] or taken(p["src"]) or p.pop("fallback")
    p.pop("fallback", None)

photos.sort(key=lambda p: p["date"], reverse=True)

years = []
for p in photos:
    year = p["date"][:4]
    if not years or years[-1]["year"] != year:
        years.append({"year": year, "photos": []})
    years[-1]["photos"].append(p)

(content / "_photos.json").write_text(json.dumps({"years": years}, indent=2) + "\n")
print(f"photos: {len(photos)} photo(s) across {len(years)} year(s)")
