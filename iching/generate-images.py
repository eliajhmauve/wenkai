import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import os
import time
import json
import io
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
from google import genai
from google.genai import types

# Change working directory to the script's parent directory (iching/)
os.chdir(Path(__file__).resolve().parent)

# ---------------------------------------------------------------------------
# Gemini client
# ---------------------------------------------------------------------------
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    sys.exit("ERROR: GEMINI_API_KEY 未設定。請在 .env 檔案或環境變數中設定。")
client = genai.Client(api_key=api_key)

# ---------------------------------------------------------------------------
# Master style prompt
# ---------------------------------------------------------------------------
MASTER_STYLE = """Traditional Chinese ink wash painting (水墨畫) style with splashes of vivid color,
Journey to the West (西遊記) themed illustration,
flowing brush strokes, ink texture, rice paper background feel,
featuring iconic mythological characters in dynamic poses,
I Ching hexagram divination card layout with ornate traditional Chinese border frame,
cloud patterns and auspicious motifs decorating the borders,
hexagram trigram symbols subtly incorporated,
high quality illustration, professional divination card design,
vertical card format 2:3 aspect ratio,
NO TEXT, NO WORDS, NO LETTERS, NO CHARACTERS on the image"""

# ---------------------------------------------------------------------------
# Image generation
# ---------------------------------------------------------------------------

def generate_image(prompt_text, output_path, retries=3):
    """Call Gemini image generation and save the result as WebP."""
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.1-flash-image-preview",
                contents=prompt_text,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    temperature=1.0,
                ),
            )
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    img = Image.open(io.BytesIO(part.inline_data.data))
                    img.save(str(output_path), "WEBP", quality=85)
                    print(f"  Saved: {output_path}")
                    return True
            print(f"  No image in response, retrying...")
        except Exception as e:
            print(f"  Error: {e}")
            if attempt < retries - 1:
                time.sleep(10)
    return False


def build_prompt(hexagram):
    """Combine master style with hexagram-specific details."""
    number = hexagram["number"]
    name_zh = hexagram["name_zh"]
    name_en = hexagram["name_en"]
    character = hexagram["character"]
    scene = hexagram["scene"]
    upper = hexagram["upper"]
    lower = hexagram["lower"]
    keywords = hexagram["keywords"]
    element = hexagram["element"]

    card_prompt = (
        f"Hexagram #{number} {name_zh} ({name_en}):\n"
        f"Character: {character} from Journey to the West\n"
        f"Scene: {scene}\n"
        f"Upper trigram: {upper}, Lower trigram: {lower}\n"
        f"Mood/Keywords: {keywords}\n"
        f"Color theme based on {element} element"
    )

    return f"{MASTER_STYLE}\n\n{card_prompt}"


def main():
    # Ensure images/ directory exists
    images_dir = Path("images")
    images_dir.mkdir(exist_ok=True)

    # Load hexagram data
    data_path = Path("data/hexagrams.json")
    if not data_path.exists():
        print(f"Error: {data_path.resolve()} not found.")
        sys.exit(1)

    with open(data_path, "r", encoding="utf-8") as f:
        hexagrams = json.load(f)

    total = len(hexagrams)

    # Optional: generate a single hexagram by number
    target_number = None
    if len(sys.argv) > 1:
        try:
            target_number = int(sys.argv[1])
        except ValueError:
            print(f"Error: invalid hexagram number '{sys.argv[1]}'")
            sys.exit(1)

    success_count = 0
    skip_count = 0
    fail_count = 0

    for hexagram in hexagrams:
        number = hexagram["number"]

        # If a specific hexagram was requested, skip others
        if target_number is not None and number != target_number:
            continue

        name_zh = hexagram["name_zh"]
        name_en = hexagram["name_en"]
        character = hexagram["character"]

        filename = f"{number:02d}-{name_zh}.webp"
        output_path = images_dir / filename

        print(f"[{number}/{total}] {name_zh} ({name_en}) - {character}...")

        # Skip if image already exists (allow resuming)
        if output_path.exists():
            print(f"  Already exists, skipping.")
            skip_count += 1
            continue

        prompt = build_prompt(hexagram)
        ok = generate_image(prompt, output_path)

        if ok:
            success_count += 1
        else:
            fail_count += 1
            print(f"  FAILED after retries!")

        # Wait between requests to avoid rate limiting
        time.sleep(6)

    # Summary
    print("\n--- Done ---")
    print(f"Generated: {success_count}  Skipped: {skip_count}  Failed: {fail_count}")


if __name__ == "__main__":
    main()
