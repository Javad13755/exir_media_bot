import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

# گرفتن متغیرها از Secrets گیت‌هاب
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Add it to GitHub Secrets.")

# تعریف استیت‌ها
class Form(StatesGroup):
    name = State()
    contact = State()
    service = State()
    link = State()

# کیبورد خدمات
services_kb = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="تولید ویدئو و تیزر تبلیغاتی")],
        [types.KeyboardButton(text="مدیریت محتوا برای شبکه‌های اجتماعی")],
        [types.KeyboardButton(text="برگزاری کنگره و رویداد")],
        [types.KeyboardButton(text="دنتال فتوگرافی")],
        [types.KeyboardButton(text="طراحی سایت")],
        [types.KeyboardButton(text="سایر خدمات")]
    ],
    resize_keyboard=True
)

# هندلر شروع
async def start_cmd(message: types.Message, state: FSMContext):
    await message.answer("سلام! لطفاً نام خود را وارد کنید:")
    await state.set_state(Form.name)

async def name_handler(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("شماره تماس خود را وارد کنید:")
    await state.set_state(Form.contact)

async def contact_handler(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await message.answer("لطفاً یکی از خدمات زیر را انتخاب کنید:", reply_markup=services_kb)
    await state.set_state(Form.service)

async def service_handler(message: types.Message, state: FSMContext):
    await state.update_data(service=message.text)
    await message.answer("لینک یا توضیحات تکمیلی را وارد کنید:")
    await state.set_state(Form.link)

async def link_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data["link"] = message.text

    text = (
        f"📨 درخواست جدید:\n"
        f"👤 نام: {data['name']}\n"
        f"📞 تماس: {data['contact']}\n"
        f"🛠 خدمت: {data['service']}\n"
        f"🔗 لینک: {data['link']}"
    )
    await message.answer("✅ درخواست شما ثبت شد. با شما تماس می‌گیریم.")
    await message.bot.send_message(ADMIN_ID, text)
    await state.clear()

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.register(start_cmd, Command("start"))
    dp.message.register(name_handler, Form.name)
    dp.message.register(contact_handler, Form.contact)
    dp.message.register(service_handler, Form.service)
    dp.message.register(link_handler, Form.link)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
