#!/usr/bin/env python3
"""Fix React SPA routing on GitHub Pages for all repos."""

import subprocess
import json
import base64
import re
import sys

OWNER = "eliajhmauve"
REPOS = [
    "astral-compass",
    "celestial-compass",
    "celestial-compass-12",
    "yi-compass",
    "app-...-3c4b4447",
    "blueprint-explorer",
    "cosmic-compass-67",
    "app-...-44494674",
    "app-...",
    "name-fortune-teller",
    "palmistry-insights",
    "moonbeam-insights",
    "star-chart-studio",
    "auspicious-golden-dates",
    "birthday-decoder",
    "annual-fortune-weaver",
    "holy-light-portal",
    "personality-playground",
    "your-color-story",
    "heartsync-match",
    "daily-fortune-draw",
    "daily-inspiration-draw",
    "soul-gems",
    "life-s-weeks",
    "lunar-charm",
    "quantum-console",
]

FOUR04_HTML = r'''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script>
    // SPA redirect for GitHub Pages
    var pathSegmentsToKeep = 1;
    var l = window.location;
    l.replace(
      l.protocol + '//' + l.hostname + (l.port ? ':' + l.port : '') +
      l.pathname.split('/').slice(0, 1 + pathSegmentsToKeep).join('/') + '/?/' +
      l.pathname.slice(1).split('/').slice(pathSegmentsToKeep).join('/').replace(/&/g, '~and~') +
      (l.search ? '&' + l.search.slice(1).replace(/&/g, '~and~') : '') +
      l.hash
    );
  </script>
</head>
<body></body>
</html>'''

SPA_REDIRECT_SCRIPT = '''    <script>
      // SPA redirect handler for GitHub Pages
      (function(l) {
        if (l.search[1] === '/') {
          var decoded = l.search.slice(1).split('&').map(function(s) {
            return s.replace(/~and~/g, '&')
          }).join('?');
          window.history.replaceState(null, null,
            l.pathname.slice(0, -1) + decoded + l.hash
          );
        }
      }(window.location))
    </script>'''


def gh_api(method, endpoint, data=None):
    """Call GitHub API via gh CLI."""
    cmd = ["gh", "api"]
    if method != "GET":
        cmd += ["-X", method]
    cmd.append(endpoint)
    if data:
        for k, v in data.items():
            cmd += ["-f", f"{k}={v}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return result.stdout


def get_file(repo, path):
    """Get file content and SHA from repo."""
    resp = gh_api("GET", f"repos/{OWNER}/{repo}/contents/{path}")
    if resp and isinstance(resp, dict) and "content" in resp:
        content = base64.b64decode(resp["content"]).decode("utf-8", errors="replace")
        return content, resp.get("sha", "")
    return None, None


def put_file(repo, path, content, message, sha=None):
    """Create or update a file in repo."""
    content_b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")
    data = {"message": message, "content": content_b64}
    if sha:
        data["sha"] = sha
    return gh_api("PUT", f"repos/{OWNER}/{repo}/contents/{path}", data)


def repo_exists(repo):
    """Check if repo exists."""
    return gh_api("GET", f"repos/{OWNER}/{repo}") is not None


def fix_404(repo):
    """Fix 1: Create public/404.html."""
    existing, sha = get_file(repo, "public/404.html")
    if existing and "SPA redirect for GitHub Pages" in existing:
        return "already present"
    result = put_file(repo, "public/404.html", FOUR04_HTML,
                      "fix: add 404.html for SPA redirect on GitHub Pages", sha)
    return "created" if result else "FAILED"


def fix_index(repo):
    """Fix 2: Add redirect script to index.html."""
    content, sha = get_file(repo, "index.html")
    if content is None:
        return "no index.html found"
    if "SPA redirect handler" in content:
        return "already present"

    # Insert after meta charset if it exists, otherwise after <head>
    if re.search(r'<meta\s+charset[^>]*>', content):
        new_content = re.sub(
            r'(<meta\s+charset[^>]*>)',
            r'\1\n' + SPA_REDIRECT_SCRIPT,
            content,
            count=1
        )
    elif '<head>' in content:
        new_content = content.replace('<head>', '<head>\n' + SPA_REDIRECT_SCRIPT, 1)
    elif '<HEAD>' in content:
        new_content = content.replace('<HEAD>', '<HEAD>\n' + SPA_REDIRECT_SCRIPT, 1)
    else:
        return "no <head> tag found"

    result = put_file(repo, "index.html", new_content,
                      "fix: add SPA redirect handler to index.html", sha)
    return "updated" if result else "FAILED"


def fix_router(repo):
    """Fix 3: Update React Router basename."""
    results = []
    for file_path in ["src/App.tsx", "src/main.tsx", "src/App.jsx", "src/main.jsx"]:
        content, sha = get_file(repo, file_path)
        if content is None:
            continue

        has_router = any(p in content for p in ["<BrowserRouter", "<Router", "createBrowserRouter"])
        if not has_router:
            continue

        new_content = content
        changed = False
        basename_val = f"/{repo}"

        # Pattern 1: <BrowserRouter> without any props
        if "<BrowserRouter>" in new_content:
            new_content = new_content.replace(
                "<BrowserRouter>",
                f'<BrowserRouter basename="{basename_val}">'
            )
            changed = True

        # Pattern 2: <BrowserRouter basename="..."> already has basename - update it
        elif re.search(r'<BrowserRouter\s+basename="[^"]*"', new_content):
            new_content = re.sub(
                r'<BrowserRouter\s+basename="[^"]*"',
                f'<BrowserRouter basename="{basename_val}"',
                new_content
            )
            changed = True

        # Pattern 2b: basename with single quotes
        elif re.search(r"<BrowserRouter\s+basename='[^']*'", new_content):
            new_content = re.sub(
                r"<BrowserRouter\s+basename='[^']*'",
                f'<BrowserRouter basename="{basename_val}"',
                new_content
            )
            changed = True

        # Pattern 2c: <BrowserRouter with other props but no basename
        elif re.search(r'<BrowserRouter\s', new_content) and 'basename' not in new_content:
            new_content = re.sub(
                r'<BrowserRouter\s',
                f'<BrowserRouter basename="{basename_val}" ',
                new_content,
                count=1
            )
            changed = True

        # Pattern 3: <Router> without basename
        if not changed and "<Router>" in new_content:
            new_content = new_content.replace(
                "<Router>",
                f'<Router basename="{basename_val}">'
            )
            changed = True

        # Pattern 4: createBrowserRouter
        if not changed and "createBrowserRouter" in new_content:
            if "basename" in new_content:
                # Update existing basename
                new_content = re.sub(
                    r"""basename:\s*['"][^'"]*['"]""",
                    f"basename: '{basename_val}'",
                    new_content
                )
                changed = True
            else:
                # Add basename as second arg
                # Match createBrowserRouter(routeVar) or createBrowserRouter([...])
                # We need to add , { basename: '/repo' } before the closing )
                match = re.search(r'createBrowserRouter\(([^)]+)\)', new_content)
                if match:
                    old = match.group(0)
                    inner = match.group(1).strip()
                    new = f"createBrowserRouter({inner}, {{ basename: '{basename_val}' }})"
                    new_content = new_content.replace(old, new, 1)
                    changed = True
                else:
                    # Multi-line createBrowserRouter - try a different approach
                    # Look for createBrowserRouter(\n...\n)
                    # Add basename option after the closing bracket of routes
                    pass

        if changed and new_content != content:
            result = put_file(repo, file_path, new_content,
                              "fix: add basename to Router for GitHub Pages subdirectory", sha)
            if result:
                results.append(f"{file_path}: updated")
            else:
                results.append(f"{file_path}: FAILED")
        elif not changed:
            results.append(f"{file_path}: router found but no matching pattern")

    if not results:
        return "no router files found"
    return "; ".join(results)


def process_repo(repo):
    """Process a single repo."""
    print(f"\n{'='*50}")
    print(f"Processing: {repo}")
    print(f"{'='*50}")

    if not repo_exists(repo):
        print(f"  [SKIP] Repo does not exist")
        return {"repo": repo, "status": "NOT FOUND", "fix1": "-", "fix2": "-", "fix3": "-"}

    # Fix 1
    r1 = fix_404(repo)
    print(f"  [Fix 1] 404.html: {r1}")

    # Fix 2
    r2 = fix_index(repo)
    print(f"  [Fix 2] index.html: {r2}")

    # Fix 3
    r3 = fix_router(repo)
    print(f"  [Fix 3] Router: {r3}")

    return {"repo": repo, "status": "OK", "fix1": r1, "fix2": r2, "fix3": r3}


def main():
    results = []
    for repo in REPOS:
        try:
            result = process_repo(repo)
            results.append(result)
        except Exception as e:
            print(f"  [ERROR] {e}")
            results.append({"repo": repo, "status": f"ERROR: {e}", "fix1": "-", "fix2": "-", "fix3": "-"})

    # Summary
    print(f"\n\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"{'Repo':<30} {'Fix1 (404)':<18} {'Fix2 (index)':<18} {'Fix3 (Router)'}")
    print(f"{'-'*30} {'-'*18} {'-'*18} {'-'*30}")
    for r in results:
        if r["status"] == "NOT FOUND":
            print(f"{r['repo']:<30} NOT FOUND")
        else:
            print(f"{r['repo']:<30} {r['fix1']:<18} {r['fix2']:<18} {r['fix3']}")


if __name__ == "__main__":
    main()
