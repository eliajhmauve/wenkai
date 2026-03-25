"""Generate 78 tarot card prompt files and batch config."""
import json, os, sys

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "prompts")
os.makedirs(PROMPTS_DIR, exist_ok=True)

# Read master style
with open(os.path.join(PROMPTS_DIR, "_style.md"), "r", encoding="utf-8") as f:
    STYLE = f.read().strip()

# === Major Arcana ===
MAJOR = [
    ("00", "fool", "The Fool", "愚者",
     "A tiny cute animal with a small backpack standing at the edge of a cliff, butterflies dancing around, looking up at the sky with innocent sparkly eyes, a small white dog companion beside"),
    ("01", "magician", "The Magician", "魔術師",
     "A tiny cute animal wearing a starry wizard cloak standing behind a small table, four tiny elemental items on the table (a cup, a coin, a tiny sword, a small wand), one paw raised pointing up, magical sparkles"),
    ("02", "high-priestess", "The High Priestess", "女祭司",
     "A tiny cute animal wearing a crescent moon headdress, sitting between two pillars (one white one dark), holding a small book, mysterious soft blue-purple background, serene expression"),
    ("03", "empress", "The Empress", "皇后",
     "A tiny cute animal wearing a flower crown, sitting in a lush flower garden, surrounded by roses and wheat, soft pink and green colors, nurturing warm expression, small heart-shaped cushion"),
    ("04", "emperor", "The Emperor", "皇帝",
     "A tiny cute animal sitting on a small golden throne, wearing a tiny crown, holding a small orb, determined expression, red and gold color scheme, mountains in background"),
    ("05", "hierophant", "The Hierophant", "教皇",
     "A tiny cute animal wearing a long ceremonial robe, holding a small golden staff, two tiny animals looking up as students, temple pillars background, soft golden light"),
    ("06", "lovers", "The Lovers", "戀人",
     "Two tiny cute animals holding hands under a blooming tree, floating hearts above them, a tiny angel blessing from above, soft pink and warm sunset colors, flower petals falling"),
    ("07", "chariot", "The Chariot", "戰車",
     "A tiny cute animal riding a decorated small chariot pulled by two tiny creatures (one white one black), wearing a star crown, determined expression, city walls in background"),
    ("08", "strength", "Strength", "力量",
     "A tiny cute animal gently hugging a lion plush toy, flower crown on head, infinite symbol above, gentle and brave expression, soft golden meadow background"),
    ("09", "hermit", "The Hermit", "隱者",
     "A tiny cute animal wearing a hooded cloak, carrying a small lantern in one paw, walking under a beautiful starry night sky, on a snowy mountain path, peaceful solitary expression"),
    ("10", "wheel-of-fortune", "Wheel of Fortune", "命運之輪",
     "Tiny cute animals sitting around a colorful spinning wheel decorated with zodiac symbols, clouds and stars in background, one animal at top looking happy, mystical atmosphere"),
    ("11", "justice", "Justice", "正義",
     "A tiny cute animal sitting on a throne, holding a small balance scale in one paw and a tiny upright sword in the other, wearing a red cape, serious but cute expression"),
    ("12", "hanged-man", "The Hanged Man", "倒吊人",
     "A tiny cute animal hanging upside down from a tree branch by one foot, completely relaxed peaceful expression, golden halo around head, autumn leaves falling, serene background"),
    ("13", "death", "Death", "死神",
     "A tiny cute animal wearing an adorable skeleton costume, riding a small white hobby horse, rose petals falling everywhere, sunrise in background, transformative not scary"),
    ("14", "temperance", "Temperance", "節制",
     "A tiny cute angel animal with small wings, pouring water between two cups creating a rainbow stream, one foot in water one on land, iris flowers around, peaceful expression"),
    ("15", "devil", "The Devil", "惡魔",
     "A tiny cute animal wearing a playful little devil costume with tiny horns and bat wings, hands on hips sassily, two small chains (loosely hanging, easily removable), dark but cute background"),
    ("16", "tower", "The Tower", "高塔",
     "A tiny cute animal sliding down from a cute crumbling tower like a slide, lightning bolt in sky shaped like a zigzag, another tiny animal falling with surprised expression, crown flying off"),
    ("17", "star", "The Star", "星星",
     "A tiny cute animal kneeling by a sparkling pond under a brilliant starry sky with one large 8-pointed star, pouring water from two small jugs, naked with peaceful expression, lush nature"),
    ("18", "moon", "The Moon", "月亮",
     "A tiny cute animal gazing up at a large luminous full moon, a small path between two towers, a tiny crayfish in a pool, two small dogs howling cutely, dreamy misty atmosphere"),
    ("19", "sun", "The Sun", "太陽",
     "A tiny cute animal riding on a giant sunflower, brilliant warm sunshine, a small white horse below, colorful garden in background, the happiest most joyful expression, confetti"),
    ("20", "judgement", "Judgement", "審判",
     "A tiny cute angel animal blowing a small golden trumpet from clouds, tiny animals rising joyfully from below with arms raised, golden light streaming down, mountains in background"),
    ("21", "world", "The World", "世界",
     "A tiny cute animal dancing in the center of a laurel wreath, holding two small wands, four elemental symbols in corners (angel, eagle, bull, lion as cute versions), ribbon wrapped around, cosmic background"),
]

# === Minor Arcana ===
SUITS = {
    "wands": {
        "name_en": "Wands", "name_zh": "權杖",
        "element": "small flowering branches and wands",
        "colors": "warm orange, cream yellow, soft coral",
        "ace_desc": "A tiny cute animal holding a single blooming wand/branch sprouting with flowers and leaves, standing on a hilltop, new adventure feeling, warm sunrise",
        "cards": {
            "02": ("Two", "二", "A tiny cute animal holding two crossed wands, looking out from a castle wall at the sea, planning expression, globe in one paw"),
            "03": ("Three", "三", "A tiny cute animal standing with back turned, watching three wands planted in ground, ships on distant sea, waiting patiently"),
            "04": ("Four", "四", "Two tiny cute animals dancing under a garland of four wands decorated with flowers, celebration scene, castle in background"),
            "05": ("Five", "五", "Five tiny cute animals playfully batting at each other with small wands, competitive but friendly, chaotic fun energy"),
            "06": ("Six", "六", "A tiny cute animal riding a small horse triumphantly, wearing a flower crown, holding a wand with ribbon, five animals cheering below"),
            "07": ("Seven", "七", "A tiny cute animal on a hill defending with a wand, six wands poking up from below, determined brave expression"),
            "08": ("Eight", "八", "Eight small wands flying through the air diagonally, a tiny cute animal watching them zoom past, blue sky, sense of speed and momentum"),
            "09": ("Nine", "九", "A tiny cute animal with a small bandage, standing guard before nine wands arranged as a fence, tired but vigilant expression"),
            "10": ("Ten", "十", "A tiny cute animal struggling to carry a bundle of ten wands on its back, walking toward a small village, perseverance expression"),
            "page": ("Page", "侍者", "A young tiny cute animal holding up a wand and looking at it with wonder and curiosity, desert background with pyramids, adventurous outfit"),
            "knight": ("Knight", "騎士", "A tiny cute animal galloping on a small horse, holding a wand boldly, cape flowing, desert landscape, passionate determined expression"),
            "queen": ("Queen", "王后", "A tiny cute animal queen sitting on a throne decorated with sunflowers, holding a wand with a flower, a black cat beside, warm confident expression"),
            "king": ("King", "國王", "A tiny cute animal king on a throne, holding a blooming wand as scepter, a small salamander at feet, cape with fire patterns, wise leader expression"),
        }
    },
    "cups": {
        "name_en": "Cups", "name_zh": "聖杯",
        "element": "cute teacups and water droplets",
        "colors": "soft blue, aqua, lavender, water tones",
        "ace_desc": "A tiny cute animal catching a overflowing golden cup from a cloud, water lilies on a pond below, dove above, gentle rain of sparkles",
        "cards": {
            "02": ("Two", "二", "Two tiny cute animals facing each other, each holding a cup, a caduceus symbol between them, sharing drinks, romantic soft pink background"),
            "03": ("Three", "三", "Three tiny cute animals raising cups in a toast, flower garlands above, harvest celebration, dancing joyfully together"),
            "04": ("Four", "四", "A tiny cute animal sitting under a tree looking bored, three cups in front, a cloud hand offering a fourth cup, contemplative expression"),
            "05": ("Five", "五", "A tiny cute animal looking sadly at three spilled cups, two cups still standing behind, a bridge and river in background, melancholy but hopeful"),
            "06": ("Six", "六", "Two tiny cute animals in a garden, one offering a cup of flowers to the other, six cups with flowers, nostalgic warm childhood feeling"),
            "07": ("Seven", "七", "A tiny cute animal looking at seven floating cups in clouds, each containing a different treasure (jewels, castle, dragon, etc), dreamy imagination"),
            "08": ("Eight", "八", "A tiny cute animal walking away from eight neatly stacked cups, heading toward mountains under a moon, leaving comfort zone, contemplative"),
            "09": ("Nine", "九", "A tiny cute animal sitting smugly with arms crossed, nine golden cups arranged on a shelf behind, satisfied happy expression, luxurious setting"),
            "10": ("Ten", "十", "A tiny cute animal family (two big, two small) under a rainbow, ten cups arranged in an arc above, cozy house in background, pure happiness"),
            "page": ("Page", "侍者", "A young tiny cute animal holding a cup with a small fish jumping out, standing by the sea, dreamy expression, scarf flowing in wind"),
            "knight": ("Knight", "騎士", "A tiny cute animal on a graceful white horse, holding a cup carefully, flowing river landscape, romantic dreamy expression, wings on helmet"),
            "queen": ("Queen", "王后", "A tiny cute animal queen on an ornate shell-shaped throne by the sea, holding an elaborate cup, crown with sea motifs, compassionate expression"),
            "king": ("King", "國王", "A tiny cute animal king on a throne floating on water, holding a cup, wearing ocean-colored robes, a fish jumping nearby, wise emotional expression"),
        }
    },
    "swords": {
        "name_en": "Swords", "name_zh": "寶劍",
        "element": "small wooden swords and stars",
        "colors": "soft purple, silver white, cool lavender",
        "ace_desc": "A tiny cute animal holding up a single gleaming sword with a crown and laurel wreath on top, mountain peaks in background, clouds parting, victorious moment",
        "cards": {
            "02": ("Two", "二", "A tiny cute animal blindfolded, balancing two crossed swords, sitting on a bench by the sea, calm moonlit night, careful balance"),
            "03": ("Three", "三", "A tiny cute animal with a sad expression, three swords piercing a red heart shape in rainy background, storm clouds, tears like raindrops"),
            "04": ("Four", "四", "A tiny cute animal sleeping peacefully on a small bed, three swords on the wall, one sword beneath the bed, stained glass window, resting"),
            "05": ("Five", "五", "A tiny cute animal picking up scattered swords while two other animals walk away sadly, stormy sky clearing, aftermath of conflict"),
            "06": ("Six", "六", "A tiny cute animal in a small boat with six swords standing upright, heading toward calmer waters, bundled passenger, hopeful journey"),
            "07": ("Seven", "七", "A tiny cute animal sneaking away tiptoeing, carrying a bundle of swords (five), two swords still in ground, mischievous but cute expression"),
            "08": ("Eight", "八", "A tiny cute animal loosely tied with ribbon, eight swords planted around in a circle, puddles on ground, blindfolded but almost free"),
            "09": ("Nine", "九", "A tiny cute animal sitting up in bed with paws over face, nine swords hanging on dark wall, nighttime, worried but it is just a bad dream"),
            "10": ("Ten", "十", "A tiny cute animal lying flat with ten small swords around (not stabbing, just resting on ground nearby), sunrise on horizon, darkest before dawn"),
            "page": ("Page", "侍者", "A young tiny cute animal holding a sword up high, standing on windy hilltop, clouds swirling, curious intellectual expression, ready to learn"),
            "knight": ("Knight", "騎士", "A tiny cute animal charging on a white horse through wind, sword raised, clouds rushing past, trees bending, swift determined expression"),
            "queen": ("Queen", "王后", "A tiny cute animal queen sitting on a tall throne in the clouds, holding a sword upright, one paw raised, stern but fair expression, butterflies"),
            "king": ("King", "國王", "A tiny cute animal king on a throne, holding a large sword, wearing blue robes with cloud patterns, throne decorated with angels and butterflies, authoritative wise expression"),
        }
    },
    "pentacles": {
        "name_en": "Pentacles", "name_zh": "錢幣",
        "element": "small golden coins and cookies",
        "colors": "soft green, golden yellow, earthy warm tones",
        "ace_desc": "A tiny cute animal receiving a large golden pentacle coin from a cloud hand, lush garden path below, flowers and archway, prosperous beginning",
        "cards": {
            "02": ("Two", "二", "A tiny cute animal juggling two large pentacle coins playfully, ocean waves in background, infinity symbol above, balancing act, cheerful"),
            "03": ("Three", "三", "A tiny cute animal working with small tools on a cathedral arch, three pentacle coins embedded in the stonework, focused craftsman expression"),
            "04": ("Four", "四", "A tiny cute animal sitting on a treasure chest hugging a pentacle coin, three coins under feet, city in background, protective but cute expression"),
            "05": ("Five", "五", "Two tiny cute animals walking through snow past a lit church window, five pentacle coins in the stained glass pattern, cold but hope nearby"),
            "06": ("Six", "六", "A tiny cute animal giving pentacle coins to smaller animals, a scale showing generosity, warm market setting, kind sharing expression"),
            "07": ("Seven", "七", "A tiny cute animal leaning on a garden hoe looking at a bush with seven pentacle coins growing like fruit, patient waiting expression, lush garden"),
            "08": ("Eight", "八", "A tiny cute animal diligently crafting pentacle coins at a workbench, eight coins displayed, tools around, focused dedicated craftsman expression"),
            "09": ("Nine", "九", "A tiny cute animal in a beautiful garden surrounded by nine pentacle coins on vines, wearing a luxurious robe, a small bird on hand, content abundance"),
            "10": ("Ten", "十", "A tiny cute animal family in front of a grand cozy house, ten pentacle coins arranged as an arch above, multiple generations, dogs and children, ultimate security"),
            "page": ("Page", "侍者", "A young tiny cute animal standing in a field, holding up a pentacle coin and examining it closely, flowers at feet, studious curious expression"),
            "knight": ("Knight", "騎士", "A tiny cute animal on a steady dark horse, holding a pentacle coin, plowed fields in background, patient methodical expression, harvest season"),
            "queen": ("Queen", "王后", "A tiny cute animal queen on a throne in a garden, holding a pentacle coin in lap, surrounded by flowers and a small rabbit, nurturing abundant expression"),
            "king": ("King", "國王", "A tiny cute animal king on a throne decorated with bull carvings, holding pentacle coin scepter, grapes and castle in background, prosperous wise expression"),
        }
    },
}

tasks = []

def write_prompt(filename, content):
    path = os.path.join(PROMPTS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# Generate Major Arcana prompts
for num, slug, name_en, name_zh, desc in MAJOR:
    filename = f"major-{num}-{slug}.md"
    card_label = f"{num} - {name_zh} {name_en}"
    content = (
        f"Card: {card_label}\n"
        f"The text at the bottom of the card MUST read exactly: \"{card_label}\"\n\n"
        f"{desc}"
    )
    write_prompt(filename, content)
    tasks.append({
        "id": f"major-{num}-{slug}",
        "prompt": f"{STYLE}\n\n{content}",
        "image": f"images/major-{num}-{slug}.png",
    })

# Generate Minor Arcana prompts
for suit_key, suit in SUITS.items():
    # Ace
    filename = f"{suit_key}-ace.md"
    card_label = f"Ace - {suit['name_zh']}王牌"
    content = (
        f"Card: Ace of {suit['name_en']} - {suit['name_zh']}王牌\n"
        f"The text at the bottom of the card MUST read exactly: \"{card_label}\"\n"
        f"Colors: {suit['colors']}\n\n{suit['ace_desc']}"
    )
    write_prompt(filename, content)
    tasks.append({
        "id": f"{suit_key}-ace",
        "prompt": f"{STYLE}\n\n{content}",
        "image": f"images/{suit_key}-ace.png",
    })

    # 2-10 and court cards
    for rank_key, (rank_en, rank_zh, desc) in suit['cards'].items():
        filename = f"{suit_key}-{rank_key}.md"
        card_label = f"{rank_en} - {suit['name_zh']}{rank_zh}"
        content = (
            f"Card: {rank_en} of {suit['name_en']} - {suit['name_zh']}{rank_zh}\n"
            f"The text at the bottom of the card MUST read exactly: \"{card_label}\"\n"
            f"Colors: {suit['colors']}\n\n{desc}"
        )
        write_prompt(filename, content)
        tasks.append({
            "id": f"{suit_key}-{rank_key}",
            "prompt": f"{STYLE}\n\n{content}",
            "image": f"images/{suit_key}-{rank_key}.png",
        })

# Write batch config
batch = {
    "jobs": 5,
    "tasks": tasks,
}
batch_path = os.path.join(os.path.dirname(__file__), "batch-tarot.json")
with open(batch_path, "w", encoding="utf-8") as f:
    json.dump(batch, f, indent=2, ensure_ascii=False)

print(f"Generated {len(tasks)} prompt files in prompts/")
print(f"Generated batch-tarot.json with {len(tasks)} tasks")

# List all files
for fn in sorted(os.listdir(PROMPTS_DIR)):
    print(f"  {fn}")
