markdown
# 🤖 Face Sticker Bot — Telegram бот для создания стикеров с лицом

Бот для Telegram, который превращает ваше селфи в набор из 10 забавных стикеров.  
Отправьте фото — получите готовые стикеры с вашим лицом в разных образах:  
очки Гарри Поттера, шлем космонавта, корона, кошачьи уши и многое другое.

Работает **без нейросетей**, только Python + Pillow.  
Быстро, бесплатно, полностью локально.

---

## 📸 Демо
Пользователь: отправляет селфи
Бот: ⏳ Обрабатываю...
Бот: присылает 10 стикеров:
🧐 с очками
😍 с сердечками в глазах
👨‍🚀 в шлеме космонавта
🤠 в ковбойской шляпе
... и ещё 6 стикеров

## 🛠 Технологии

- **Python 3.10+**
- **Aiogram 3.x** — фреймворк для Telegram Bot API
- **Pillow (PIL)** — обработка изображений, вырезание лиц, наложение масок
- **python-dotenv** — хранение токена бота

### Как работает

1. Бот получает фото от пользователя
2. Вырезает квадратную область с лицом (центр фото)
3. Создаёт овальную маску с мягкими краями
4. Вписывает лицо в зону на маске (256×332 px)
5. Накладывает графику маски (очки, шлем, корону и т.д.) поверх лица
6. Отправляет пользователю 10 готовых стикеров в формате PNG

**Никаких нейросетей** — чистая геометрия и композитинг изображений.

## 📁 Структура проекта
face_sticker_bot/
│
├── bot.py # Главный файл бота (запуск)
├── generate_masks.py # Генератор 10 масок (запустить 1 раз)
├── requirements.txt # Зависимости Python
├── .env # Токен бота (создать вручную)
├── README.md # Этот файл
│
├── stickers_512/ # Папка с масками (создаётся автоматически)
│ ├── 01_nerd_glasses.png
│ ├── 02_heart_eyes.png
│ ├── 03_rage_scream.png
│ ├── 04_mona_lisa.png
│ ├── 05_cat_ears.png
│ ├── 06_astronaut.png
│ ├── 07_cowboy.png
│ ├── 08_cry_river.png
│ ├── 09_king.png
│ └── 10_pixel.png
│
├── output_stickers/ # Готовые стикеры (создаётся автоматически)
│ └── (временные файлы)
│
└── temp/ # Временные фото пользователей
└── (автоочистка)

## 🚀 Быстрый старт

### 1. Клонируйте проект

```bash
git clone https://github.com/your-username/face-sticker-bot.git
cd face-sticker-bot

2. Установите зависимости
bash
pip install -r requirements.txt
Состав requirements.txt:

aiogram>=3.0
python-dotenv
Pillow

3. Создайте бота в Telegram
Напишите @BotFather в Telegram

Отправьте команду /newbot

Придумайте имя (например, Face Sticker Maker)

Придумайте username (например, my_face_sticker_bot)

Скопируйте полученный токен (выглядит так: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz)

4. Настройте .env файл
Создайте файл .env в корне проекта:

# .env
BOT_TOKEN=ваш_токен_от_BotFather
5. Сгенерируйте маски
Это нужно сделать один раз:

bash
python generate_masks.py
Вывод в консоли:

text
✔ 01_nerd_glasses.png
✔ 02_heart_eyes.png
✔ 03_rage_scream.png
...
✅ Создано 10 масок в папке stickers_512/
6. Запустите бота
bash
python bot.py
Успешный запуск:

🤖 Бот запущен...

7. Отправьте селфи боту
Найдите вашего бота в Telegram по username,
отправьте команду /start и затем пришлите фото.

Через 2-3 секунды получите 10 стикеров.

🎨 Доступные маски
#	Название	Описание	Эмодзи
1	nerd_glasses	Очки как у Гарри Поттера	🧐
2	heart_eyes	Сердечки вместо глаз	😍
3	rage_scream	Красное лицо, пар из ушей	🤬
4	mona_lisa	Золотая рама картины	🖼
5	cat_ears	Кошачьи уши и усы	🐱
6	astronaut	Шлем космонавта	👨‍🚀
7	cowboy	Ковбойская шляпа	🤠
8	cry_river	Слёзы водопадом	😭
9	king	Корона и мантия	👑
10	pixel	Пиксельная ретро-рамка 8-BIT	👾
⚙️ Как добавить свои маски

Добавьте новую функцию в generate_masks.py:

python
def draw_my_mask(draw, fx, fy, fw, fh):
    """Моя уникальная маска."""
    draw.rectangle([fx-10, fy-10, fx+fw+10, fy+fh+10], 
                   outline=(255,0,255,255), width=15)
    draw.text((fx+fw//2-20, fy-40), "COOL", fill=(0,0,0,255))
Добавьте маску в список MASKS:

```python
MASKS = [
    ...
    ("11_my_mask", draw_my_mask),
]
```
Пересоздайте маски:

```bash
python generate_masks.py
```
Перезапустите бота

🔧 Настройка размера лица
В файле bot.py найдите константу FACE_ZONE:

python
# Формат: (x, y, width, height)
FACE_ZONE = (128, 26, 256, 332)
Измените координаты, если лицо на стикерах слишком большое или маленькое.

🚢 Деплой на сервер
Вариант 1: PythonAnywhere (бесплатно)
Зарегистрируйтесь на pythonanywhere.com

Загрузите файлы через Web-консоль

Установите зависимости:

bash
pip install --user aiogram python-dotenv Pillow
Запустите бота как "Always-on task"

Вариант 2: VPS (Ubuntu)
bash

# Установка
ssh user@your-server
git clone https://github.com/your-username/face-sticker-bot.git
cd face-sticker-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Создайте systemd-сервис
sudo nano /etc/systemd/system/face-sticker-bot.service
Содержимое сервиса:

ini
[Unit]
Description=Face Sticker Bot
After=network.target

[Service]
User=your-user
WorkingDirectory=/home/your-user/face-sticker-bot
ExecStart=/home/your-user/face-sticker-bot/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
Запуск:

bash
sudo systemctl enable face-sticker-bot
sudo systemctl start face-sticker-bot
sudo systemctl status face-sticker-bot
📝 Как добавить нейросеть (опционально)
Функция process_all_stickers() в bot.py сейчас использует PIL.
Чтобы подключить реальную замену лиц через нейросеть:

Установите replicate:

bash
pip install replicate
Получите API-ключ на replicate.com

Замените функцию:

python
import replicate
```
def process_all_stickers_neuro(face_path: Path) -> list[Path]:
    face = open(face_path, "rb")
    mask_files = sorted(MASK_DIR.glob("*.png"))
    
    result_paths = []
    for i, mask_path in enumerate(mask_files, 1):
        output = replicate.run(
            "lucataco/faceswap:...",  # выберите модель
            input={
                "target_image": open(mask_path, "rb"),
                "source_image": face,
            }
        )
        # output — URL, нужно скачать
        import requests
        response = requests.get(output)
        out_path = OUTPUT_DIR / f"sticker_{i:02d}.png"
        out_path.write_bytes(response.content)
        result_paths.append(out_path)
    
    return result_paths
```

❓ Частые вопросы
В: Почему лицо не распознаётся?
О: Бот использует геометрическое вырезание (центр фото).
Для лучшего результата: фото анфас, хорошее освещение, без очков и масок.

В: Можно ли использовать готовые стикеры в Telegram?
О: Да! Отправьте любое изображение боту @Stickers
и создайте свой стикерпак.

В: Сколько времени занимает обработка?
О: 2-3 секунды на обычном компьютере.

В: Хранятся ли мои фото?
О: Нет, все временные файлы удаляются сразу после отправки стикеров.

В: Почему без нейросетей?
О: Чтобы бот работал бесплатно и без ограничений.
Вы можете подключить нейросеть самостоятельно (см. раздел выше).

📄 Лицензия
MIT License — используйте как угодно, делитесь с друзьями, модифицируйте.

Telegram: @your_telegram

Наслаждайтесь стикерами! 🎉
