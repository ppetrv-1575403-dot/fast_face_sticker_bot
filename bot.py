import asyncio
import os
import uuid
from io import BytesIO
from pathlib import Path

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFilter

# ------------------------------
# Настройки
# ------------------------------
load_dotenv()
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")  # опционально

MASK_DIR = Path("stickers_512")
OUTPUT_DIR = Path("output_stickers")
TEMP_DIR = Path("temp")

OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

FACE_ZONE = (128, 26, 256, 332)  # x, y, w, h для 512x512

# Режим: "neural" или "pil"
# Если REPLICATE_API_TOKEN не задан, автоматом переключится на PIL
PROCESSING_MODE = "neural" if REPLICATE_API_TOKEN else "pil"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# ------------------------------
# PIL-обработка (fallback)
# ------------------------------
def pil_extract_face_oval(face_img: Image.Image) -> Image.Image:
    w, h = face_img.size
    size = min(w, h)
    left = (w - size) // 2
    top = (h - size) // 2
    face_crop = face_img.crop((left, top, left + size, top + size))

    oval_mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(oval_mask)
    margin = int(size * 0.03)
    draw.ellipse([margin, margin, size - margin, size - margin], fill=255)
    oval_mask = oval_mask.filter(ImageFilter.GaussianBlur(radius=10))

    face_crop = face_crop.convert("RGBA")
    face_crop.putalpha(oval_mask)
    return face_crop


def pil_insert_face(mask_path: Path, face_img: Image.Image, zone: tuple) -> Image.Image:
    mask = Image.open(mask_path).convert("RGBA")
    fx, fy, fw, fh = zone

    face_oval = pil_extract_face_oval(face_img)
    face_resized = face_oval.resize((fw, fh), Image.LANCZOS)

    result = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    result.paste(face_resized, (fx, fy), face_resized)
    result.paste(mask, (0, 0), mask)
    return result


def process_all_stickers_pil(face_path: Path) -> list[Path]:
    face = Image.open(face_path).convert("RGB")
    mask_files = sorted(MASK_DIR.glob("*.png"))
    result_paths = []

    for i, mask_path in enumerate(mask_files, 1):
        sticker = pil_insert_face(mask_path, face, FACE_ZONE)
        out_path = OUTPUT_DIR / f"sticker_{i:02d}_{mask_path.stem}.png"
        sticker.save(out_path, format="PNG")
        result_paths.append(out_path)

    return result_paths


# ------------------------------
# Нейросеть: Replicate (InsightFace)
# ------------------------------
def process_all_stickers_neural(face_path: Path) -> list[Path]:
    import replicate

    client = replicate.Client(api_token=REPLICATE_API_TOKEN)

    mask_files = sorted(MASK_DIR.glob("*.png"))
    result_paths = []

    # Сначала загружаем фото лица на Replicate (однократно)
    with open(face_path, "rb") as f:
        face_upload = client.files.create(file=f)

    for i, mask_path in enumerate(mask_files, 1):
        # Загружаем маску
        with open(mask_path, "rb") as f:
            mask_upload = client.files.create(file=f)

        # Вызываем модель faceswap
        # Модель: yorickvp/insightface-swap (бесплатная, быстрая)
        output = client.run(
            "yorickvp/insightface-swap:7e70d2a94c6b0a4b4f2a8a4b1f3a7c0d9e8f6b5a4c3d2e1f0a9b8c7d6e5f4",
            input={
                "source": face_upload.url,
                "target": mask_upload.url,
                "face_restore": True,      # улучшение качества лица
                "upscale": 1,
            }
        )

        # output — это URL готового изображения
        import requests
        response = requests.get(output, timeout=30)
        response.raise_for_status()

        out_path = OUTPUT_DIR / f"sticker_{i:02d}.png"
        out_path.write_bytes(response.content)
        result_paths.append(out_path)
        print(f"  ✔ Нейро-стикер {i}/{len(mask_files)}: {mask_path.name}")

    return result_paths


# ------------------------------
# Главный диспетчер
# ------------------------------
async def make_stickers(face_path: Path, mode: str) -> list[Path]:
    if mode == "neural":
        try:
            return process_all_stickers_neural(face_path)
        except Exception as e:
            print(f"⚠ Ошибка нейросети: {e}")
            print("  Переключаюсь на PIL...")
            return process_all_stickers_pil(face_path)
    else:
        return process_all_stickers_pil(face_path)


# ------------------------------
# Telegram-обработчики
# ------------------------------
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    mode_emoji = "🧠 Нейросеть" if PROCESSING_MODE == "neural" else "✂️ Геометрия (PIL)"
    await message.answer(
        "👋 Привет! Отправь мне своё селфи, и я сделаю 10 стикеров с твоим лицом.\n\n"
        f"Режим обработки: {mode_emoji}\n\n"
        "Совет: фото анфас, без очков, хорошее освещение."
    )


@router.message(F.photo)
async def handle_photo(message: types.Message, bot: Bot):
    photo = message.photo[-1]
    user_temp = TEMP_DIR / str(message.from_user.id)
    user_temp.mkdir(parents=True, exist_ok=True)
    face_path = user_temp / f"face_{uuid.uuid4()}.jpg"
    await bot.download(file=photo.file_id, destination=face_path)

    wait_msg = await message.answer(
        "⏳ Создаю стикеры...\n"
        f"Режим: {'🧠 нейросеть (10-20 сек)' if PROCESSING_MODE == 'neural' else '✂️ геометрия (2-3 сек)'}"
    )

    try:
        sticker_paths = await make_stickers(face_path, PROCESSING_MODE)

        if not sticker_paths:
            await wait_msg.edit_text("❌ Не удалось создать стикеры. Попробуйте другое фото.")
            return

        # Отправляем первые 10 как галерею
        album = MediaGroupBuilder()
        caption = "✨ Твои стикеры готовы!"
        if PROCESSING_MODE == "neural":
            caption += " (нейросеть)"

        for i, sp in enumerate(sticker_paths[:10]):
            if i == 0:
                album.add_photo(media=FSInputFile(sp), caption=caption)
            else:
                album.add_photo(media=FSInputFile(sp))

        await message.answer_media_group(media=album.build())

        # Всё, что больше 10 — документами
        for sp in sticker_paths[10:]:
            await message.answer_document(FSInputFile(sp))

        await message.answer(
            "📦 Добавь их в стикерпак через @Stickers — отправь любое "
            "из этих изображений боту @Stickers и следуй инструкции."
        )

    except Exception as e:
        await wait_msg.edit_text(f"❌ Ошибка: {e}")

    finally:
        face_path.unlink(missing_ok=True)
        for f in OUTPUT_DIR.iterdir():
            f.unlink(missing_ok=True)


# ------------------------------
# Запуск
# ------------------------------
async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)

    mode_str = "🧠 НЕЙРОСЕТЬ (InsightFace)" if PROCESSING_MODE == "neural" else "✂️ ГЕОМЕТРИЯ (PIL fallback)"
    print(f"🤖 Бот запущен...")
    print(f"   Режим: {mode_str}")
    print(f"   Маски: {len(list(MASK_DIR.glob('*.png')))} шт.")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())