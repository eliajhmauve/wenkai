"""Batch generate 78 tarot card images using Google Gemini API (free tier).
Uses gemini-2.0-flash-exp with image output capability.
"""
import json, os, sys, time, base64, urllib.request, urllib.error

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("ERROR: GEMINI_API_KEY not set")
    sys.exit(1)

MODEL = "gemini-2.5-flash-image"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
MAX_RETRIES = 3
REQUEST_DELAY = 6  # free tier rate limit safety margin

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(SCRIPT_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

with open(os.path.join(SCRIPT_DIR, "batch-tarot.json"), "r", encoding="utf-8") as f:
    batch = json.load(f)


def generate_image(prompt):
    """Call Gemini API to generate an image from a text prompt."""
    # Prefix prompt with instruction for image generation
    full_prompt = f"Generate an image: {prompt}"
    data = json.dumps({
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
        }
    }).encode()

    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(API_URL, data=data, headers=headers, method="POST")

    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode())

    # Extract image from response
    candidates = result.get("candidates", [])
    if not candidates:
        return None

    parts = candidates[0].get("content", {}).get("parts", [])
    for part in parts:
        if "inlineData" in part:
            mime = part["inlineData"].get("mimeType", "image/png")
            b64 = part["inlineData"]["data"]
            return base64.b64decode(b64), mime

    return None


def generate_card(task):
    task_id = task["id"]
    output_path = os.path.join(SCRIPT_DIR, task["image"])
    prompt = task["prompt"]

    if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
        return task_id, True, "skip"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"  [{attempt}/{MAX_RETRIES}] {task_id}...", end="", flush=True)
            result = generate_image(prompt)

            if result:
                img_data, mime = result
                with open(output_path, "wb") as f:
                    f.write(img_data)
                size_kb = len(img_data) / 1024
                ext = "webp" if "webp" in mime else "png" if "png" in mime else "jpg"
                print(f" OK ({size_kb:.0f} KB, {ext})", flush=True)
                return task_id, True, "ok"
            else:
                print(f" no image in response", flush=True)

        except urllib.error.HTTPError as e:
            body = e.read().decode() if e.fp else ""
            if e.code == 429:
                wait = 20 * attempt
                print(f" rate limited, waiting {wait}s...", flush=True)
                time.sleep(wait)
                continue
            elif e.code == 400 and "SAFETY" in body.upper():
                print(f" safety filter, softening prompt...", flush=True)
                # Try with softened prompt
                task = dict(task)
                task["prompt"] = prompt.replace("skeleton costume", "cute ghost costume").replace("devil costume", "cute imp costume")
                prompt = task["prompt"]
                continue
            else:
                print(f" HTTP {e.code}: {body[:150]}", flush=True)

        except Exception as e:
            print(f" error: {e}", flush=True)

        if attempt < MAX_RETRIES:
            time.sleep(5 * attempt)

    return task_id, False, "fail"


def main():
    tasks = batch["tasks"]

    pending = []
    skipped = 0
    for t in tasks:
        path = os.path.join(SCRIPT_DIR, t["image"])
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            skipped += 1
        else:
            pending.append(t)

    total = len(tasks)
    print(f"Total: {total} | Done: {skipped} | Pending: {len(pending)}", flush=True)

    if not pending:
        print("All images already generated!")
        return

    success = 0
    failed = []
    start_time = time.time()

    for i, task in enumerate(pending):
        task_id, ok, status = generate_card(task)
        if ok:
            success += 1
        else:
            failed.append(task_id)

        done = skipped + success + len(failed)
        elapsed = time.time() - start_time
        avg = elapsed / (i + 1) if i > 0 else 0
        remaining = avg * (len(pending) - i - 1)
        print(f"  [{done}/{total}] elapsed={elapsed/60:.1f}m ETA={remaining/60:.1f}m", flush=True)

        if i < len(pending) - 1 and status != "skip":
            time.sleep(REQUEST_DELAY)

    elapsed = time.time() - start_time
    print(f"\nDone in {elapsed/60:.1f} min! Success: {success} | Failed: {len(failed)}")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        print("Re-run to retry.")


if __name__ == "__main__":
    main()
