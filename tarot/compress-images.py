"""Convert all PNG images to WebP for smaller file size."""
import os, sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
WEBP_QUALITY = 85
THUMBNAIL_SIZE = (400, 600)  # for grid view

total_before = 0
total_after = 0
count = 0

for fn in sorted(os.listdir(IMAGES_DIR)):
    if not fn.endswith(".png"):
        continue

    png_path = os.path.join(IMAGES_DIR, fn)
    webp_path = os.path.join(IMAGES_DIR, fn.replace(".png", ".webp"))

    before = os.path.getsize(png_path)
    total_before += before

    img = Image.open(png_path)
    img.save(webp_path, "WEBP", quality=WEBP_QUALITY)

    after = os.path.getsize(webp_path)
    total_after += after
    ratio = (1 - after / before) * 100
    count += 1
    print(f"  {fn} -> {fn.replace('.png','.webp')} ({before//1024}KB -> {after//1024}KB, -{ratio:.0f}%)")

print(f"\nConverted {count} images")
print(f"Total: {total_before/1024/1024:.1f} MB -> {total_after/1024/1024:.1f} MB ({(1-total_after/total_before)*100:.0f}% reduction)")
