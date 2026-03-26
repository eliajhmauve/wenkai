"""Batch generate 12 numerology character images using Google Gemini API.
Uses gemini-3.1-flash-image-preview with image output capability.

Usage: GEMINI_API_KEY=xxx python images/generate-numerology.py
"""
import json, os, sys, time, base64, urllib.request, urllib.error

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("ERROR: Set GEMINI_API_KEY environment variable first")
    sys.exit(1)

MODEL = "gemini-3.1-flash-image-preview"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
MAX_RETRIES = 3
REQUEST_DELAY = 6

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
IMAGES_DIR = os.path.join(SCRIPT_DIR, "numerology")
os.makedirs(IMAGES_DIR, exist_ok=True)

with open(os.path.join(SCRIPT_DIR, "batch-numerology.json"), "r", encoding="utf-8") as f:
    batch = json.load(f)


def generate_image(prompt):
    full_prompt = (
        "Generate a single illustration. "
        "IMPORTANT: The text at the bottom MUST use the EXACT Chinese characters as specified. "
        "Do NOT change, substitute, or approximate any Chinese characters.\n\n"
        f"{prompt}"
    )
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

    candidates = result.get("candidates", [])
    if not candidates:
        return None

    parts = candidates[0].get("content", {}).get("parts", [])
    for part in parts:
        if "inlineData" in part:
            b64 = part["inlineData"]["data"]
            return base64.b64decode(b64)

    return None


def main():
    total = len(batch)
    success = 0
    failed = []

    print(f"=== Generating {total} numerology images ===\n")

    for i, task in enumerate(batch, 1):
        task_id = task["id"]
        output_path = os.path.join(ROOT_DIR, task["image"])

        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            print(f"[{i}/{total}] {task_id} — skip (exists)")
            success += 1
            continue

        ok = False
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                print(f"[{i}/{total}] {task_id} attempt {attempt}/{MAX_RETRIES}...", end=" ", flush=True)
                img_data = generate_image(task["prompt"])

                if img_data:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, "wb") as f:
                        f.write(img_data)
                    print(f"OK ({len(img_data)//1024}KB)")
                    ok = True
                    break
                else:
                    print("no image in response")
            except urllib.error.HTTPError as e:
                body = e.read().decode()[:200] if hasattr(e, 'read') else ''
                print(f"HTTP {e.code}: {body}")
                if e.code == 429:
                    print("  Rate limited, waiting 30s...")
                    time.sleep(30)
            except Exception as e:
                print(f"error: {e}")

            time.sleep(REQUEST_DELAY)

        if ok:
            success += 1
        else:
            failed.append(task_id)

        time.sleep(REQUEST_DELAY)

    print(f"\n=== Done: {success}/{total} success ===")
    if failed:
        print(f"Failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
