import asyncio
import re
from datetime import datetime
from aiogram import Bot, Dispatcher, types
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ========== ТВОИ ДАННЫЕ ==========
TOKEN = "8592081785:AAHRkTcL4VQoFesxIr09aAEAqv88mUs3QSE"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1PL1b0m35HPkWftzzRQlBG-sHswpPgk2l8jZ0zcgETVE/edit?usp=sharing"

# ========== ПОДКЛЮЧЕНИЕ К ГУГЛ ТАБЛИЦЕ ==========
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google-key.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_url(SHEET_URL).sheet1

# ========== СПИСОК МАТА ==========
BAD_WORDS = [
    r"ху[йеяию]", r"пизд", r"бля[дт]", r"еба[нт]", r"сука", r"нахуй",
    r"ахуе", r"охуе", r"мудак", r"долбоеб", r"гандон", r"пидор", r"шлюха"
]
BAD_PATTERNS = [re.compile(w, re.IGNORECASE) for w in BAD_WORDS]

bot = Bot(token=TOKEN)
dp = Dispatcher()

def check_profanity(text):
    if not text: return False
    return any(p.search(text) for p in BAD_PATTERNS)

@dp.message()
async def handle_message(msg: types.Message):
    if not msg.text or msg.text.startswith('/'): return
    
    if check_profanity(msg.text):
        user = msg.from_user
        now = datetime.now()
        
        # Записываем в Гугл таблицу
        sheet.append_row([
            now.strftime("%d.%m.%Y"),
            now.strftime("%H:%M:%S"),
            f"@{user.username}" if user.username else f"id{user.id}",
            user.first_name or "",
            str(user.id),
            msg.text[:200],
            msg.chat.title or "личка"
        ])
        
        # Опционально: пишем в консоль
        print(f"🚫 {now.strftime('%H:%M')} @{user.username}: {msg.text[:30]}...")

async def main():
    print("✅ Бот запущен и слушает чаты...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())