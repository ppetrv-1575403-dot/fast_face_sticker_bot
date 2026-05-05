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
MASK_DIR = Path("stickers_512")
OUTPUT_DIR = Path("output_stickers")
TEMP_DIR = Path("temp")

OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Зона лица в маске (x, y, w, h) для холста 512x512
FACE_ZONE = (128, 26, 256, 332)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()


# ------------------------------
# Логика обработки лица (PIL)
# ------------------------------
def extract_face_oval(face_img: Image.Image) -> Image.Image:
    """Вырезает квадратное лицо, делает овальную маску с мягким краем."""
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


# def insert_face_into_mask(mask_path: Path, face_img: Image.Image, zone: tuple) -> Image.Image:
#     """Вставляет лицо в маску в заданную зону."""
#     mask = Image.open(mask_path).convert("RGBA")
#     fx, fy, fw, fh = zone
#
#     face_oval = extract_face_oval(face_img)
#     face_resized = face_oval.resize((fw, fh), Image.LANCZOS)
#
#     result = Image.new("RGBA", mask.size, (0, 0, 0, 0))
#     result.paste(mask, (0, 0), mask)
#     result.paste(face_resized, (fx, fy), face_resized)
#     return result

def insert_face_into_mask(mask_path: Path, face_img: Image.Image, zone: tuple) -> Image.Image:
    """
    Вставляет лицо ПОД графику маски.
    Маска — это PNG с прозрачностью, где графика уже нарисована.
    """
    mask = Image.open(mask_path).convert("RGBA")
    fx, fy, fw, fh = zone

    # Получаем овал лица
    face_oval = extract_face_oval(face_img)
    face_resized = face_oval.resize((fw, fh), Image.LANCZOS)

    # Создаём холст размером с маску
    result = Image.new("RGBA", mask.size, (0, 0, 0, 0))

    # СНАЧАЛА вставляем лицо (будет сзади)
    result.paste(face_resized, (fx, fy), face_resized)

    # ПОТОМ накладываем маску поверх (графика маски перекроет лицо)
    result.paste(mask, (0, 0), mask)

    return result

def process_all_stickers(face_path: Path) -> list[Path]:
    """Создаёт стикеры из одного фото и всех масок."""
    face = Image.open(face_path).convert("RGB")
    mask_files = sorted(MASK_DIR.glob("*.png"))

    result_paths = []
    for i, mask_path in enumerate(mask_files, 1):
        sticker = insert_face_into_mask(mask_path, face, FACE_ZONE)
        out_path = OUTPUT_DIR / f"sticker_{i:02d}_{mask_path.stem}.png"
        sticker.save(out_path, format="PNG")
        result_paths.append(out_path)
    return result_paths


# ------------------------------
# Telegram-обработчики
# ------------------------------
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Отправь мне своё селфи, и я сделаю 10 стикеров с твоим лицом.\n\n"
        "Совет: фото анфас, без очков, хорошее освещение."
    )


@router.message(F.photo)
async def handle_photo(message: types.Message, bot: Bot):
    # Скачиваем фото
    photo = message.photo[-1]
    user_temp = TEMP_DIR / str(message.from_user.id)
    user_temp.mkdir(parents=True, exist_ok=True)
    face_path = user_temp / f"face_{uuid.uuid4()}.jpg"
    await bot.download(file=photo.file_id, destination=face_path)

    wait_msg = await message.answer("⏳ Создаю стикеры... ~3 секунды")

    try:
        sticker_paths = process_all_stickers(face_path)

        # Отправляем первые 10 картинок как галерею
        album = MediaGroupBuilder()
        for i, sp in enumerate(sticker_paths[:10]):
            if i == 0:
                album.add_photo(media=FSInputFile(sp),
                                caption="✨ Твои стикеры готовы!")
            else:
                album.add_photo(media=FSInputFile(sp))
        await message.answer_media_group(media=album.build())

        # Всё, что больше 10 — документами
        for sp in sticker_paths[10:]:
            await message.answer_document(FSInputFile(sp))

        await message.answer(
            "📦 Добавь их в стикерпак через @Stickers — просто отправь любое "
            "из этих изображений этому боту."
        )

    except Exception as e:
        await wait_msg.edit_text(f"❌ Ошибка: {e}")

    finally:
        # Удаляем фото пользователя
        face_path.unlink(missing_ok=True)
        # Очищаем output (можно закомментировать, чтобы хранить)
        for f in OUTPUT_DIR.iterdir():
            f.unlink(missing_ok=True)


# ------------------------------
# Запуск
# ------------------------------
async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("🤖 Бот запущен...")
    asyncio.run(main())