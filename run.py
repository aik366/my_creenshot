import asyncio
import io
import logging
import socket
import pyautogui
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import TOKEN

# --- КОНФИГУРАЦИЯ ---
# TOKEN = "ВАШ_ТОКЕН_ОТ_BOTFATHER"
INTERNET_CHECK_HOST = "8.8.8.8"  # DNS Google
INTERNET_CHECK_PORT = 53
CHECK_INTERVAL = 10  # Проверка каждые 10 секунд
MAX_WAIT_TIME = 600  # Максимальное время ожидания (600 сек = 10 минут)
# ---------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- Функция проверки интернета ---
def check_internet_connection(host=INTERNET_CHECK_HOST, port=INTERNET_CHECK_PORT, timeout=3):
    """
    Проверяет наличие интернета через TCP-соединение.
    Возвращает True, если соединение успешно, иначе False.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

async def wait_for_internet():
    """
    Ждёт появления интернета. Проверяет каждые CHECK_INTERVAL секунд.
    """
    logger.info("🌐 Проверка подключения к интернету...")
    waited_time = 0
    
    while not check_internet_connection():
        if waited_time >= MAX_WAIT_TIME:
            logger.error("❌ Интернет не появился за %d секунд. Выход.", MAX_WAIT_TIME)
            return False
        
        logger.info(f"⏳ Интернета нет. Ожидание {CHECK_INTERVAL} сек... (Прошло: {waited_time}/{MAX_WAIT_TIME})")
        await asyncio.sleep(CHECK_INTERVAL)
        waited_time += CHECK_INTERVAL
    
    logger.info("✅ Интернет подключен! Запуск бота...")
    return True

# --- Функция для создания скриншота ---
async def get_screenshot():
    """Делает скриншот экрана и возвращает байты изображения"""
    image = await asyncio.to_thread(pyautogui.screenshot)
    bio = io.BytesIO()
    image.save(bio, format='PNG')
    bio.seek(0)
    return bio

# --- Обработчики команд ---
@dp.message((F.from_user.id == 428030603) & (F.text == '/start'))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🖼️ Как фото", callback_data="screen_photo"),
        InlineKeyboardButton(text="📁 Как файл", callback_data="screen_file")
    )
    
    await message.answer(
        "Выберите формат отправки скриншота:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.in_(["screen_photo", "screen_file"]))
async def process_screenshot(callback: types.CallbackQuery):
    await callback.answer("Делаю скриншот...⏳")
    
    try:
        screenshot_buffer = await get_screenshot()
        screenshot_bytes = screenshot_buffer.read()
        
        file = BufferedInputFile(
            file=screenshot_bytes, 
            filename=f"screenshot_{int(asyncio.get_event_loop().time())}.png"
        )
        
        builder = InlineKeyboardBuilder()
        builder.row(
        InlineKeyboardButton(text="🖼️ Как фото", callback_data="screen_photo"),
        InlineKeyboardButton(text="📁 Как файл", callback_data="screen_file")
        )
        
        if callback.data == "screen_photo":
            await callback.message.answer_photo(
                photo=file,
                reply_markup=builder.as_markup(),
                parse_mode="Markdown"
            )
        else:
            await callback.message.answer_document(
                document=file,
                reply_markup=builder.as_markup(),
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error(f"Ошибка при создании скриншота: {e}")
        await callback.answer("❌ Ошибка при создании скриншота!", show_alert=True)

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "📖 **Помощь**\n\n"
        "/start - Запустить бота и показать кнопки\n"
        "/help - Показать эту справку\n\n"
        "Бот делает скриншот вашего рабочего стола Windows 10."
    )

# --- Запуск бота ---
async def main():
    # 1. Ждём появления интернета
    internet_ok = await wait_for_internet()
    
    if not internet_ok:
        logger.error("🛑 Бот не запущен из-за отсутствия интернета.")
        await bot.close()
        return
    
    # 2. Запускаем опросник
    logger.info("🚀 Запуск polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n🛑 Бот выключен пользователем")
    finally:
        # Гарантированная очистка ресурсов
        try:
            asyncio.run(bot.close())
        except:
            pass