#!/bin/bash
# Fix React SPA routing on GitHub Pages for all repos
# Usage: bash fix-spa-routing.sh

OWNER="eliajhmauve"
REPOS=(
  "astral-compass"
  "celestial-compass"
  "celestial-compass-12"
  "yi-compass"
  "app-...-3c4b4447"
  "blueprint-explorer"
  "cosmic-compass-67"
  "app-...-44494674"
  "app-..."
  "name-fortune-teller"
  "palmistry-insights"
  "moonbeam-insights"
  "star-chart-studio"
  "auspicious-golden-dates"
  "birthday-decoder"
  "annual-fortune-weaver"
  "holy-light-portal"
  "personality-playground"
  "your-color-story"
  "heartsync-match"
  "daily-fortune-draw"
  "daily-inspiration-draw"
  "soul-gems"
  "life-s-weeks"
  "lunar-charm"
  "quantum-console"
)

# 404.html content
FOUR04_CONTENT='<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script>
    // SPA redirect for GitHub Pages
    var pathSegmentsToKeep = 1;
    var l = window.location;
    l.replace(
      l.protocol + '"'"'//'"'"' + l.hostname + (l.port ? '"'"':'"'"' + l.port : '"'"''"'"') +
      l.pathname.split('"'"'/'"'"').slice(0, 1 + pathSegmentsToKeep).join('"'"'/'"'"') + '"'"'/?/'"'"' +
      l.pathname.slice(1).split('"'"'/'"'"').slice(pathSegmentsToKeep).join('"'"'/'"'"').replace(/&/g, '"'"'~and~'"'"') +
      (l.search ? '"'"'&'"'"' + l.search.slice(1).replace(/&/g, '"'"'~and~'"'"') : '"'"''"'"') +
      l.hash
    );
  </script>
</head>
<body></body>
</html>'

# SPA redirect handler script to inject into index.html
SPA_SCRIPT='    <script>
      // SPA redirect handler for GitHub Pages
      (function(l) {
        if (l.search[1] === '"'"'/'"'"') {
          var decoded = l.search.slice(1).split('"'"'&'"'"').map(function(s) {
            return s.replace(/~and~/g, '"'"'&'"'"')
          }).join('"'"'?'"'"');
          window.history.replaceState(null, null,
            l.pathname.slice(0, -1) + decoded + l.hash
          );
        }
      }(window.location))
    </script>'

LOG_FILE="/c/Users/User/Desktop/wenkai/spa-fix-log.txt"
> "$LOG_FILE"

log() {
  echo "$1" | tee -a "$LOG_FILE"
}

# Function to create or update a file via GitHub API
create_or_update_file() {
  local repo="$1"
  local path="$2"
  local content_b64="$3"
  local message="$4"

  # Check if file exists and get SHA
  local existing
  existing=$(gh api "repos/$OWNER/$repo/contents/$path" 2>/dev/null)
  local sha=""
  if [ $? -eq 0 ]; then
    sha=$(echo "$existing" | python3 -c "import sys,json; print(json.load(sys.stdin).get('sha',''))" 2>/dev/null)
  fi

  if [ -n "$sha" ]; then
    # Update existing file
    gh api -X PUT "repos/$OWNER/$repo/contents/$path" \
      -f message="$message" \
      -f content="$content_b64" \
      -f sha="$sha" > /dev/null 2>&1
  else
    # Create new file
    gh api -X PUT "repos/$OWNER/$repo/contents/$path" \
      -f message="$message" \
      -f content="$content_b64" > /dev/null 2>&1
  fi
  return $?
}

# Function to get file content from GitHub
get_file_content() {
  local repo="$1"
  local path="$2"
  gh api "repos/$OWNER/$repo/contents/$path" --jq '.content' 2>/dev/null | base64 -d 2>/dev/null
}

# Function to get file SHA
get_file_sha() {
  local repo="$1"
  local path="$2"
  gh api "repos/$OWNER/$repo/contents/$path" --jq '.sha' 2>/dev/null
}

process_repo() {
  local repo="$1"
  log ""
  log "========================================="
  log "Processing: $repo"
  log "========================================="

  # Check repo exists
  if ! gh api "repos/$OWNER/$repo" > /dev/null 2>&1; then
    log "  [SKIP] Repo does not exist"
    return
  fi

  # --- Fix 1: Create public/404.html ---
  log "  [Fix 1] Creating public/404.html..."
  local four04_b64
  four04_b64=$(echo -n '<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script>
    // SPA redirect for GitHub Pages
    var pathSegmentsToKeep = 1;
    var l = window.location;
    l.replace(
      l.protocol + '\''//'\'' + l.hostname + (l.port ? '\'':'\'' + l.port : '\'''\'') +
      l.pathname.split('\''/'\'').slice(0, 1 + pathSegmentsToKeep).join('\''/'\'') + '\''/?/'\'' +
      l.pathname.slice(1).split('\''/'\'').slice(pathSegmentsToKeep).join('\''/'\'').replace(/&/g, '\''~and~'\'') +
      (l.search ? '\''&'\'' + l.search.slice(1).replace(/&/g, '\''~and~'\'') : '\'''\'') +
      l.hash
    );
  </script>
</head>
<body></body>
</html>' | base64 -w 0)

  if create_or_update_file "$repo" "public/404.html" "$four04_b64" "fix: add 404.html for SPA redirect on GitHub Pages"; then
    log "  [Fix 1] Done"
  else
    log "  [Fix 1] FAILED"
  fi

  # --- Fix 2: Update index.html with SPA redirect script ---
  log "  [Fix 2] Updating index.html..."
  local index_content
  index_content=$(get_file_content "$repo" "index.html")
  if [ -z "$index_content" ]; then
    log "  [Fix 2] No index.html in root, skipping"
  else
    # Check if script already exists
    if echo "$index_content" | grep -q "SPA redirect handler"; then
      log "  [Fix 2] Script already present, skipping"
    else
      # Insert after <head> and any meta charset
      local new_index
      if echo "$index_content" | grep -q '<meta charset'; then
        # Insert after meta charset line
        new_index=$(echo "$index_content" | sed '/<meta charset/a\    <script>\n      // SPA redirect handler for GitHub Pages\n      (function(l) {\n        if (l.search[1] === '"'"'/'"'"') {\n          var decoded = l.search.slice(1).split('"'"'\&'"'"').map(function(s) {\n            return s.replace(/~and~/g, '"'"'\&'"'"')\n          }).join('"'"'?'"'"');\n          window.history.replaceState(null, null,\n            l.pathname.slice(0, -1) + decoded + l.hash\n          );\n        }\n      }(window.location))\n    </script>')
      else
        # Insert after <head>
        new_index=$(echo "$index_content" | sed '/<head>/a\    <script>\n      // SPA redirect handler for GitHub Pages\n      (function(l) {\n        if (l.search[1] === '"'"'/'"'"') {\n          var decoded = l.search.slice(1).split('"'"'\&'"'"').map(function(s) {\n            return s.replace(/~and~/g, '"'"'\&'"'"')\n          }).join('"'"'?'"'"');\n          window.history.replaceState(null, null,\n            l.pathname.slice(0, -1) + decoded + l.hash\n          );\n        }\n      }(window.location))\n    </script>')
      fi

      local index_sha
      index_sha=$(get_file_sha "$repo" "index.html")
      local index_b64
      index_b64=$(echo -n "$new_index" | base64 -w 0)

      if [ -n "$index_sha" ]; then
        if gh api -X PUT "repos/$OWNER/$repo/contents/index.html" \
          -f message="fix: add SPA redirect handler to index.html" \
          -f content="$index_b64" \
          -f sha="$index_sha" > /dev/null 2>&1; then
          log "  [Fix 2] Done"
        else
          log "  [Fix 2] FAILED"
        fi
      else
        log "  [Fix 2] Could not get SHA for index.html"
      fi
    fi
  fi

  # --- Fix 3: Update React Router basename ---
  log "  [Fix 3] Updating Router basename..."
  local router_fixed=false

  for file_path in "src/App.tsx" "src/main.tsx" "src/App.jsx" "src/main.jsx"; do
    local file_content
    file_content=$(get_file_content "$repo" "$file_path")
    if [ -z "$file_content" ]; then
      continue
    fi

    # Check for BrowserRouter or Router
    if echo "$file_content" | grep -qE '<BrowserRouter|<Router|createBrowserRouter'; then
      log "  [Fix 3] Found router in $file_path"
      local new_content="$file_content"
      local changed=false

      # Pattern 1: <BrowserRouter> without basename
      if echo "$new_content" | grep -q '<BrowserRouter>' ; then
        new_content=$(echo "$new_content" | sed "s|<BrowserRouter>|<BrowserRouter basename=\"/$repo\">|g")
        changed=true
      fi

      # Pattern 2: <BrowserRouter basename="..."> - update existing
      if echo "$new_content" | grep -qE '<BrowserRouter basename="[^"]*"' && [ "$changed" = false ]; then
        new_content=$(echo "$new_content" | sed "s|<BrowserRouter basename=\"[^\"]*\"|<BrowserRouter basename=\"/$repo\"|g")
        changed=true
      fi

      # Pattern 3: <Router> without basename (less common)
      if echo "$new_content" | grep -q '<Router>' && [ "$changed" = false ]; then
        new_content=$(echo "$new_content" | sed "s|<Router>|<Router basename=\"/$repo\">|g")
        changed=true
      fi

      # Pattern 4: createBrowserRouter with basename option
      if echo "$new_content" | grep -q 'createBrowserRouter' && [ "$changed" = false ]; then
        # Check if basename already set
        if echo "$new_content" | grep -qE 'basename.*:'; then
          new_content=$(echo "$new_content" | sed "s|basename:[[:space:]]*['\"][^'\"]*['\"]|basename: '/$repo'|g")
        else
          # Add basename option - look for the second argument of createBrowserRouter
          # createBrowserRouter(routes, { basename: "/repo" })
          # or createBrowserRouter(routes) -> createBrowserRouter(routes, { basename: "/repo" })
          if echo "$new_content" | grep -qE 'createBrowserRouter\([^,]+\)'; then
            new_content=$(echo "$new_content" | sed "s|createBrowserRouter(\([^)]*\))|createBrowserRouter(\1, { basename: '/$repo' })|g")
          fi
        fi
        changed=true
      fi

      if [ "$changed" = true ]; then
        local file_sha
        file_sha=$(get_file_sha "$repo" "$file_path")
        local file_b64
        file_b64=$(echo -n "$new_content" | base64 -w 0)

        if [ -n "$file_sha" ]; then
          if gh api -X PUT "repos/$OWNER/$repo/contents/$file_path" \
            -f message="fix: add basename to Router for GitHub Pages subdirectory" \
            -f content="$file_b64" \
            -f sha="$file_sha" > /dev/null 2>&1; then
            log "  [Fix 3] Updated $file_path - Done"
            router_fixed=true
          else
            log "  [Fix 3] FAILED to update $file_path"
          fi
        fi
      else
        log "  [Fix 3] No matching router pattern in $file_path"
      fi
    fi
  done

  if [ "$router_fixed" = false ]; then
    log "  [Fix 3] No router found in App.tsx/main.tsx"
  fi

  log "  Completed: $repo"
}

# Process all repos
for repo in "${REPOS[@]}"; do
  process_repo "$repo"
done

log ""
log "========================================="
log "ALL DONE"
log "========================================="
