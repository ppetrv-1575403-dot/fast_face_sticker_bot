from PIL import Image, ImageDraw
import os

output_dir = "stickers_512"
os.makedirs(output_dir, exist_ok=True)

# Зона лица (x, y, width, height)
FACE_ZONE = (0.25, 0.05, 0.5, 0.65)


def draw_nerd_glasses(draw, fx, fy, fw, fh):
    """Очки как у Гарри Поттера."""
    # Окуляры
    draw.ellipse([fx-10, fy+80, fx+fw//2, fy+180], outline=(0,0,0,255), width=8)
    draw.ellipse([fx+fw//2, fy+80, fx+fw+10, fy+180], outline=(0,0,0,255), width=8)
    # Переносица
    draw.line([(fx+fw//2, fy+130), (fx+fw//2, fy+130)], fill=(0,0,0,255), width=6)
    # Дужки
    draw.line([(fx-10, fy+130), (fx-40, fy+110)], fill=(0,0,0,255), width=5)
    draw.line([(fx+fw+10, fy+130), (fx+fw+40, fy+110)], fill=(0,0,0,255), width=5)


def draw_heart_eyes(draw, fx, fy, fw, fh):
    """Сердечки вместо глаз."""
    # Рисуем сердечки вручную (два круга + треугольник)
    for heart_x in [fx+40, fx+fw-60]:
        # Левый круг
        draw.ellipse([heart_x-20, fy+90, heart_x, fy+110], fill=(255,0,0,255))
        # Правый круг
        draw.ellipse([heart_x, fy+90, heart_x+20, fy+110], fill=(255,0,0,255))
        # Треугольник снизу
        draw.polygon([heart_x-20, fy+100, heart_x+20, fy+100,
                      heart_x, fy+130], fill=(255,0,0,255))


def draw_rage_scream(draw, fx, fy, fw, fh):
    """Красное лицо, пар из ушей."""
    # Красная заливка лица
    draw.ellipse([fx, fy, fx+fw, fy+fh], fill=(255,80,80,180))
    # Злые брови
    draw.line([(fx+20, fy+60), (fx+100, fy+30)], fill=(0,0,0,255), width=8)
    draw.line([(fx+fw-20, fy+60), (fx+fw-100, fy+30)], fill=(0,0,0,255), width=8)
    # Пар из ушей
    for dx in [60, 120, 180]:
        draw.arc([fx+dx, fy-40, fx+dx+30, fy], start=180, end=360,
                 fill=(200,200,200,255), width=3)


def draw_mona_lisa(draw, fx, fy, fw, fh):
    """Золотая рама картины."""
    draw.rectangle([fx-15, fy-15, fx+fw+15, fy+fh+15],
                   outline=(139, 107, 35, 255), width=12)
    draw.rectangle([fx-30, fy-30, fx+fw+30, fy+fh+30],
                   outline=(80, 60, 20, 255), width=8)


def draw_cat_ears(draw, fx, fy, fw, fh):
    """Кошачьи уши и усы."""
    # Левое ухо (внешнее + внутреннее)
    draw.polygon([fx-20, fy+60, fx+30, fy-50, fx+60, fy+40],
                 fill=(255,150,100,255))
    draw.polygon([fx-15, fy+55, fx+30, fy-35, fx+55, fy+40],
                 fill=(255,220,220,255))
    # Правое ухо
    draw.polygon([fx+fw-60, fy+40, fx+fw-30, fy-50, fx+fw+20, fy+60],
                 fill=(255,150,100,255))
    draw.polygon([fx+fw-55, fy+40, fx+fw-30, fy-35, fx+fw+15, fy+55],
                 fill=(255,220,220,255))
    # Усы
    for dy in [160, 180, 200]:
        draw.line([(fx-30, fy+dy), (fx+30, fy+dy-10)], fill=(0,0,0,255), width=2)
        draw.line([(fx+fw-30, fy+dy-10), (fx+fw+30, fy+dy)], fill=(0,0,0,255), width=2)


def draw_astronaut(draw, fx, fy, fw, fh):
    """Шлем космонавта."""
    draw.ellipse([fx-20, fy-20, fx+fw+20, fy+fh+20],
                 outline=(200,200,210,255), width=15)
    draw.ellipse([fx-10, fy-10, fx+fw+10, fy+fh+10],
                 outline=(160,160,170,255), width=5)
    # Антенна
    draw.line([(fx+fw//2, fy-20), (fx+fw//2-20, fy-70)],
              fill=(180,180,190,255), width=5)
    draw.ellipse([fx+fw//2-25, fy-80, fx+fw//2-15, fy-70],
                 fill=(255,50,50,255))


def draw_cowboy(draw, fx, fy, fw, fh):
    """Ковбойская шляпа."""
    # Поля
    draw.ellipse([fx-50, fy-10, fx+fw+50, fy+40], fill=(139,90,43,255))
    # Тулья
    draw.rectangle([fx+20, fy-60, fx+fw-20, fy+10], fill=(139,90,43,255))
    # Верх полей (светлее)
    draw.ellipse([fx-40, fy-5, fx+fw+40, fy+35], fill=(160,110,60,255))
    # Красная лента
    draw.rectangle([fx+20, fy-10, fx+fw-20, fy+10], fill=(180,30,30,255))


def draw_cry_river(draw, fx, fy, fw, fh):
    """Слёзы водопадом."""
    # Слёзы из глаз
    for dx in [40, 80]:
        draw.ellipse([fx+dx-10, fy+140, fx+dx+10, fy+200],
                     fill=(100,150,255,255))
        draw.ellipse([fx+dx-15, fy+190, fx+dx+15, fy+280],
                     fill=(100,150,255,255))
    # Лужа слёз
    draw.ellipse([fx+30, fy+fh-20, fx+90, fy+fh+30],
                 fill=(200,200,255,180))


def draw_king(draw, fx, fy, fw, fh):
    """Корона и мантия."""
    # Корона
    pts = [
        (fx-20, fy-20),
        (fx+20, fy-90),
        (fx+fw//2, fy-30),
        (fx+fw-20, fy-90),
        (fx+fw+20, fy-20)
    ]
    draw.polygon(pts, fill=(255,215,0,255))
    draw.polygon(pts, outline=(200,160,0,255), width=4)
    # Рубин на короне
    draw.ellipse([fx+fw//2-8, fy-35, fx+fw//2+8, fy-20], fill=(255,0,0,255))
    # Мантия
    draw.rectangle([fx-10, fy+fh-10, fx+fw+10, fy+fh+80],
                   fill=(139,0,0,200))
    draw.rectangle([fx-10, fy+fh-10, fx+fw+10, fy+fh+80],
                   outline=(100,0,0,255), width=3)
    # Горностай
    for dy in range(fy+fh, fy+fh+70, 20):
        draw.ellipse([fx+fw//2-15, dy-5, fx+fw//2+15, dy+5],
                     fill=(240,240,240,255), outline=(0,0,0,255))


def draw_pixel(draw, fx, fy, fw, fh):
    """Пиксельная рамка."""
    # Толстая чёрная рамка
    draw.rectangle([fx-25, fy-25, fx+fw+25, fy+fh+25],
                   outline=(0,0,0,255), width=25)
    # Белая внутренняя
    draw.rectangle([fx-25, fy-25, fx+fw+25, fy+fh+25],
                   outline=(255,255,255,255), width=18)
    # Тонкая чёрная
    draw.rectangle([fx-25, fy-25, fx+fw+25, fy+fh+25],
                   outline=(0,0,0,255), width=10)
    # Надпись 8-BIT
    draw.rectangle([fx-25, fy+fh+30, fx+fw+25, fy+fh+80],
                   fill=(0,0,0,255))
    draw.text((fx-10, fy+fh+40), "8-BIT", fill=(255,255,0,255))


# Список всех масок
MASKS = [
    ("01_nerd_glasses", draw_nerd_glasses),
    ("02_heart_eyes", draw_heart_eyes),
    ("03_rage_scream", draw_rage_scream),
    ("04_mona_lisa", draw_mona_lisa),
    ("05_cat_ears", draw_cat_ears),
    ("06_astronaut", draw_astronaut),
    ("07_cowboy", draw_cowboy),
    ("08_cry_river", draw_cry_river),
    ("09_king", draw_king),
    ("10_pixel", draw_pixel),
]

# Генерация
for name, draw_func in MASKS:
    img = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    fx, fy, fw, fh = [int(v * 512) for v in FACE_ZONE]

    # Рисуем графику маски (лицо будет ПОД этим)
    draw_func(draw, fx, fy, fw, fh)

    path = os.path.join(output_dir, f"{name}.png")
    img.save(path)
    print(f"✔ {name}.png")

print(f"\n✅ Создано {len(MASKS)} масок в папке {output_dir}/")