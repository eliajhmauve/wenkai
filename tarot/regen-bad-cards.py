"""Regenerate only Pentacles (金幣) and Swords (劍) cards with corrected Chinese."""
import json, os, sys, time, base64, urllib.request, urllib.error
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL = "gemini-3.1-flash-image-preview"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(SCRIPT_DIR, "images")

STYLE = """Chiikawa-style illustration, super cute kawaii Japanese character design,
rounded simple outlines, big sparkly eyes, tiny mouth, soft pastel colors
(pink, white, light blue, cream yellow), chibi proportions with oversized head,
minimal clean background with soft gradient, tarot card layout with
decorative border frame, golden ornamental edges, card name text area at bottom,
high quality 2K illustration, professional tarot card design"""

# Pentacles: use 金幣 instead of 錢幣
PENTACLES = [
    ("pentacles-ace", "Ace", "金幣王牌", "A tiny cute animal receiving a large golden pentacle coin from a cloud hand, lush garden path below, flowers and archway"),
    ("pentacles-02", "Two", "金幣二", "A tiny cute animal juggling two large pentacle coins playfully, ocean waves in background, infinity symbol above"),
    ("pentacles-03", "Three", "金幣三", "A tiny cute animal working with small tools on a cathedral arch, three pentacle coins embedded in the stonework"),
    ("pentacles-04", "Four", "金幣四", "A tiny cute animal sitting on a treasure chest hugging a pentacle coin, three coins under feet, city in background"),
    ("pentacles-05", "Five", "金幣五", "Two tiny cute animals walking through snow past a lit church window, five pentacle coins in the stained glass"),
    ("pentacles-06", "Six", "金幣六", "A tiny cute animal giving pentacle coins to smaller animals, a scale, warm market setting"),
    ("pentacles-07", "Seven", "金幣七", "A tiny cute animal leaning on a garden hoe looking at a bush with seven pentacle coins growing like fruit"),
    ("pentacles-08", "Eight", "金幣八", "A tiny cute animal diligently crafting pentacle coins at a workbench, eight coins displayed, tools around"),
    ("pentacles-09", "Nine", "金幣九", "A tiny cute animal in a beautiful garden surrounded by nine pentacle coins on vines, wearing a luxurious robe"),
    ("pentacles-10", "Ten", "金幣十", "A tiny cute animal family in front of a grand cozy house, ten pentacle coins arranged as an arch above"),
    ("pentacles-page", "Page", "金幣侍者", "A young tiny cute animal standing in a field, holding up a pentacle coin and examining it closely"),
    ("pentacles-knight", "Knight", "金幣騎士", "A tiny cute animal on a steady dark horse, holding a pentacle coin, plowed fields in background"),
    ("pentacles-queen", "Queen", "金幣王后", "A tiny cute animal queen on a throne in a garden, holding a pentacle coin, surrounded by flowers and a small rabbit"),
    ("pentacles-king", "King", "金幣國王", "A tiny cute animal king on a throne decorated with bull carvings, holding pentacle coin scepter, grapes and castle"),
]

# Swords: use 劍 instead of 寶劍
SWORDS = [
    ("swords-ace", "Ace", "劍王牌", "A tiny cute animal holding up a single gleaming sword with a crown and laurel wreath on top, mountain peaks"),
    ("swords-02", "Two", "劍二", "A tiny cute animal blindfolded, balancing two crossed swords, sitting on a bench by the sea"),
    ("swords-03", "Three", "劍三", "A tiny cute animal with a sad expression, three swords near a red heart shape in rainy background"),
    ("swords-04", "Four", "劍四", "A tiny cute animal sleeping peacefully on a small bed, three swords on the wall, stained glass window"),
    ("swords-05", "Five", "劍五", "A tiny cute animal picking up scattered swords while two other animals walk away, stormy sky clearing"),
    ("swords-06", "Six", "劍六", "A tiny cute animal in a small boat with six swords standing upright, heading toward calmer waters"),
    ("swords-07", "Seven", "劍七", "A tiny cute animal sneaking away tiptoeing, carrying a bundle of swords, mischievous expression"),
    ("swords-08", "Eight", "劍八", "A tiny cute animal loosely tied with ribbon, eight swords planted around in a circle, blindfolded"),
    ("swords-09", "Nine", "劍九", "A tiny cute animal sitting up in bed with paws over face, nine swords hanging on dark wall, nighttime"),
    ("swords-10", "Ten", "劍十", "A tiny cute animal lying flat with ten small swords around on ground nearby, sunrise on horizon"),
    ("swords-page", "Page", "劍侍者", "A young tiny cute animal holding a sword up high, standing on windy hilltop, clouds swirling"),
    ("swords-knight", "Knight", "劍騎士", "A tiny cute animal charging on a white horse through wind, sword raised, clouds rushing past"),
    ("swords-queen", "Queen", "劍王后", "A tiny cute animal queen sitting on a tall throne in the clouds, holding a sword upright, butterflies"),
    ("swords-king", "King", "劍國王", "A tiny cute animal king on a throne, holding a large sword, wearing blue robes with cloud patterns"),
]

ALL_CARDS = PENTACLES + SWORDS

def generate_image(prompt):
    data = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]}
    }).encode()
    req = urllib.request.Request(API_URL, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode())
    for part in result.get("candidates", [{}])[0].get("content", {}).get("parts", []):
        if "inlineData" in part:
            return base64.b64decode(part["inlineData"]["data"])
    return None

def main():
    print(f"Regenerating {len(ALL_CARDS)} cards...", flush=True)
    success = 0
    failed = []

    for i, (card_id, rank_en, zh_name, desc) in enumerate(ALL_CARDS):
        label = f"{rank_en} - {zh_name}"
        prompt = (
            f"Generate a single tarot card image. "
            f"IMPORTANT: The card name text at the bottom MUST read exactly: \"{label}\". "
            f"Do NOT change or substitute any Chinese characters.\n\n"
            f"{STYLE}\n\n"
            f"Card: {label}\n"
            f"The text at the bottom of the card MUST read exactly: \"{label}\"\n\n"
            f"{desc}"
        )

        png_path = os.path.join(IMAGES_DIR, f"{card_id}.png")
        webp_path = os.path.join(IMAGES_DIR, f"{card_id}.webp")

        for attempt in range(1, 4):
            try:
                print(f"  [{i+1}/{len(ALL_CARDS)}] {card_id}...", end="", flush=True)
                img_data = generate_image(prompt)
                if img_data:
                    with open(png_path, "wb") as f:
                        f.write(img_data)
                    # Convert to WebP
                    img = Image.open(png_path)
                    img.save(webp_path, "WEBP", quality=85)
                    os.remove(png_path)
                    size = os.path.getsize(webp_path)
                    print(f" OK ({size//1024} KB)", flush=True)
                    success += 1
                    break
                else:
                    print(f" no image", flush=True)
            except Exception as e:
                print(f" error: {e}", flush=True)
                if attempt < 3:
                    time.sleep(10 * attempt)
        else:
            failed.append(card_id)

        if i < len(ALL_CARDS) - 1:
            time.sleep(6)

    print(f"\nDone! Success: {success} | Failed: {len(failed)}")
    if failed:
        print(f"Failed: {', '.join(failed)}")

if __name__ == "__main__":
    main()
