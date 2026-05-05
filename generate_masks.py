from PIL import Image, ImageDraw, ImageFont
import os

output_dir = "stickers_512"
os.makedirs(output_dir, exist_ok=True)

masks = [
    ("01_nerd_glasses",      "🧐 очки Гарри Поттера"),
    ("02_heart_eyes",        "😍 сердечки вместо глаз"),
    ("03_rage_scream",       "🤬 красное лицо, пар из ушей"),
    ("04_mona_lisa_smile",   "🖼 рама картины"),
    ("05_cat_ears",          "🐱 кошачьи уши и усы"),
    ("06_astronaut_helmet",  "👨‍🚀 шлем космонавта"),
    ("07_cowboy_hat",        "🤠 ковбойская шляпа"),
    ("08_cry_river",         "😭 слёзы водопадом"),
    ("09_king_crown",        "👑 корона и мантия"),
    ("10_pixel_8bit",        "👾 пиксельная ретро-рамка"),
]

face_zone = (0.25, 0.05, 0.5, 0.65)

for name, detail in masks:
    img = Image.new("RGBA", (512, 512), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    fx, fy, fw, fh = [int(v * 512) for v in face_zone]

    # Овал — зона лица (будет замещена)
    draw.ellipse([fx, fy, fx+fw, fy+fh],
                 outline=(200, 200, 200, 180),
                 fill=(255, 255, 255, 40),
                 width=3)

    # Эмодзи и подпись
    draw.text((fx + 10, fy + fh + 10), f"{detail}",
              fill=(50, 50, 50, 255))

    path = os.path.join(output_dir, f"{name}.png")
    img.save(path)
    print(f"✔ {name}.png")

print(f"Готово: {len(os.listdir(output_dir))} масок в папке {output_dir}/")