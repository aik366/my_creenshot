# pip install aiogram pyautogui pillow
import asyncio
import io
import logging
import pyautogui
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import TOKEN


logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Функция для создания скриншота
async def get_screenshot():
    """Делает скриншот экрана и возвращает байты изображения"""
    image = await asyncio.to_thread(pyautogui.screenshot)
    bio = io.BytesIO()
    image.save(bio, format='PNG')
    bio.seek(0)
    return bio

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Создаем две кнопки в одном ряду
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🖼️ Как фото", callback_data="screen_photo"),
        InlineKeyboardButton(text="📁 Как файл", callback_data="screen_file")
    )
    
    await message.answer(
        "🖥 **Бот скриншотов для Windows 10**\n\n"
        "Выберите формат отправки скриншота:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

# Обработчик нажатия на кнопки
@dp.callback_query(F.data.in_(["screen_photo", "screen_file"]))
async def process_screenshot(callback: types.CallbackQuery):
    await callback.answer("Делаю скриншот...⏳")
    
    try:
        # Делаем скриншот
        screenshot_buffer = await get_screenshot()
        screenshot_bytes = screenshot_buffer.read()
        
        # Создаём файл для отправки
        file = BufferedInputFile(
            file=screenshot_bytes, 
            filename=f"screenshot_{int(asyncio.get_event_loop().time())}.png"
        )
        
        # Отправляем в выбранном формате
        if callback.data == "screen_photo":
            await callback.message.answer_photo(
                photo=file,
                caption="🖼️ Скриншот вашего Windows 10 (как изображение)"
            )
        else:  # screen_file
            await callback.message.answer_document(
                document=file,
                caption="📁 Скриншот вашего Windows 10 (как файл)",
            )
            
    except Exception as e:
        logging.error(f"Ошибка при создании скриншота: {e}")
        await callback.answer("❌ Ошибка при создании скриншота!", show_alert=True)

# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "📖 **Помощь**\n\n"
        "/start - Запустить бота и показать кнопки\n"
        "/help - Показать эту справку\n\n"
        "Бот делает скриншот вашего рабочего стола Windows 10."
    )

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        print("🚀 Бот запущен")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Бот выключен пользователем")
        