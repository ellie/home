#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

# Generate git-based "updated" dates for wiki pages
json="{"
first=true
for section in motorcycles projects; do
  for file in content/$section/*.md; do
    [ "$(basename "$file")" = "_index.md" ] && continue
    [ ! -f "$file" ] && continue
    git_date=$(git log -1 --format=%ad --date=format:"%b %d, %Y" -- "$file" 2>/dev/null || true)
    if [ -n "$git_date" ]; then
      key="$section/$(basename "$file")"
      if [ "$first" = true ]; then
        first=false
      else
        json="$json,"
      fi
      json="$json \"$key\": \"$git_date\""
    fi
  done
done
json="$json }"
echo "$json" > content/_git-dates.json

# Collect tagged post images + photos.toml into content/_photos.json for /photos
./scripts/photos.py

zola build "$@"

# Annotate images with dimensions (justified grids) and EXIF (lightbox)
# Cloudflare Pages has python3/pip but not uv; install it there.
if command -v uv >/dev/null 2>&1; then
  ./scripts/image-meta.py
else
  python3 -m pip install --quiet uv
  python3 -m uv run --quiet --script scripts/image-meta.py
fi
