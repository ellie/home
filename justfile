default: build

# Generate git-based "updated" dates for wiki pages
_git-dates:
    #!/bin/bash
    echo "{" > content/_git-dates.json
    first=true
    for section in motorcycles projects; do
      for file in content/$section/*.md; do
        [ "$(basename "$file")" = "_index.md" ] && continue
        [ ! -f "$file" ] && continue
        git_date=$(git log -1 --format="%b %d, %Y" -- "$file" 2>/dev/null || true)
        if [ -n "$git_date" ]; then
          key="$section/$(basename "$file")"
          [ "$first" = true ] && first=false || echo "," >> content/_git-dates.json
          printf '  "%s": "%s"' "$key" "$git_date" >> content/_git-dates.json
        fi
      done
    done
    echo "" >> content/_git-dates.json
    echo "}" >> content/_git-dates.json

# Build the site
build: _git-dates
    zola build

# Serve for local development
serve: _git-dates
    zola serve

# Clean build artifacts
clean:
    rm -rf public content/_git-dates.json
