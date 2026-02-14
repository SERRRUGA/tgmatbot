import asyncio
import re
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ChatMemberAdministrator, ChatMemberOwner, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ========== ТВОИ ДАННЫЕ ==========
TOKEN = "8592081785:AAHRkTcL4VQoFesxIr09aAEAqv88mUs3QSE"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1PL1b0m35HPkWftzzRQlBG-sHswpPgk2l8jZ0zcgETVE/edit?usp=sharing"
OWNER_ID = 2126256213  # ТВОЙ ID - СЮДА ПРИХОДЯТ ВСЕ ЗАПРОСЫ

# ========== ПОДКЛЮЧЕНИЕ К ГУГЛ ТАБЛИЦЕ ==========
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google-key.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_url(SHEET_URL).sheet1

# ========== СПИСОК МАТА ==========
BAD_WORDS = [
    r"ахуе", r"ахуел", r"ахуеть", r"ахуенно", r"ахуенный", r"ахуительный", r"говно", r"жопа",
    r"бля", r"бляд", r"бляди", r"блядина", r"блядища", r"блядка", r"блядский", r"блядство", r"блядун", r"блядь", r"блять",
    r"вздроч", r"вздрочить", r"выеб", r"выебанный", r"выебать", r"выебаться",
    r"гандон", r"гандонка", r"гандонский",
    r"долбоеб", r"долбоебина", r"долбоебизм", r"долбоебка", r"долбоебский", r"дроч", r"дрочер", r"дрочила", r"дрочить", r"дрочка",
    r"еб", r"еба", r"ебал", r"ебало", r"ебальник", r"ебанат", r"ебанатик", r"ебанашка", r"ебаная", r"ебанный", r"ебанутый", r"ебанько", r"ебаный", r"ебать", r"ебаться", r"ебатория", r"ебена", r"ебеня", r"ебина", r"еблак", r"еблан", r"ебланище", r"ебланка", r"ебло", r"еблоид", r"еблысь", r"ебля", r"ебнуть", r"ебнутый", r"ебнуться", r"ебукентий", r"ебун", r"ебучий", r"ебучка", r"ебуша", r"ебырь", r"ёб", r"ёбанный", r"ёбанутый", r"ёбаный", r"ёбнутый", r"ёпт", r"ёпта", r"ёпти",
    r"заеб", r"заебалово", r"заебанный", r"заебатый", r"заебать", r"заебаться", r"заебись", r"заёб", r"залупа", r"залупаться", r"залупить", r"залупка", r"залупленный", r"залупонский", r"запиздить",
    r"манда", r"мандавошка", r"мандавошник", r"мандей", r"мандец", r"мандища", r"мандюк", r"муда", r"мудак", r"мудацкий", r"мудачина", r"мудачок", r"мудачьё", r"муде", r"мудель", r"мудик", r"мудила", r"мудило", r"мудня", r"мудовоз", r"мудозвон", r"мудоклюй", r"мудорвач", r"мудохват", r"мудошлеп",
    r"наеб", r"наебалово", r"наебанный", r"наебать", r"наебаться", r"наебнуть", r"наебнуться", r"напиздить", r"нахуй", r"нахуя",
    r"объеб", r"объебать", r"объебос", r"опизденелый", r"отъеб", r"отъебать", r"отъебаться", r"отъебись", r"отъебнуться", r"охуе", r"охуевать", r"охуевший", r"охуел", r"охуенно", r"охуенный", r"охуеть", r"охуительный", r"охуй",
    r"педераст", r"педерастия", r"педик", r"педила", r"педрила", r"педрило", r"педрик", r"петух", r"петушара", r"петушиный", r"пидор", r"пидорасия", r"пидорасина", r"пидорас", r"пидорган", r"пидорила", r"пидорить", r"пидорка", r"пидорня", r"пидорок", r"пидорский", r"пидрила", r"пидрило", r"пизда", r"пиздабол", r"пиздаватый", r"пиздакрылый", r"пиздануть", r"пизданутый", r"пиздатый", r"пиздёж", r"пиздёнка", r"пиздец", r"пиздилово", r"пиздища", r"пиздка", r"пиздлить", r"пиздобрат", r"пиздовка", r"пиздодыр", r"пиздолиз", r"пиздолюб", r"пиздомет", r"пиздорез", r"пиздос", r"пиздосос", r"пиздострадатель", r"пиздун", r"пиздюга", r"пиздюк", r"пиздюлей", r"пиздюль", r"пиздюха", r"пиздятина", r"пиздячить", r"пизды", r"подпиздник", r"подъеб", r"подъебать", r"подъебка", r"поеб", r"поебать", r"поебень", r"поеботина", r"похую", r"приеб", r"приебаться", r"проеб", r"проебать", r"проебаться", r"пропиздить",
    r"разпизд", r"разпиздяй", r"разъеб", r"разъебай", r"разъебать", r"распизд", r"распиздай", r"распиздеть", r"распиздон", r"распиздяй", r"распиж", r"распижон",
    r"сука", r"сукин", r"суки", r"сучара", r"сучий", r"сучка", r"сучок", r"сучонок", r"сучье",
    r"уеб", r"уебан", r"уебать", r"уебище", r"уебанский", r"уёбок",
    r"хайль", r"хуе", r"хуё", r"хуева", r"хуевать", r"хуеверт", r"хуеглот", r"хуегрыз", r"хуедрыга", r"хуек", r"хуекрат", r"хуеман", r"хуеморд", r"хуемыслие", r"хуепук", r"хуерга", r"хуета", r"хуетень", r"хуефикация", r"хуецирк", r"хуешник", r"хуи", r"хуила", r"хуист", r"хуище", r"хуй", r"хуйло", r"хуйня", r"хуйовать", r"хуйчик", r"хуя", r"хуяк", r"хуякать", r"хуякнуть", r"хуярить", r"хуясе", r"хуячить",
    r"шлюха", r"шлюшка", r"шлюхи", r"шлюхин", r"шлюшечка",
]
BAD_PATTERNS = [re.compile(w, re.IGNORECASE) for w in BAD_WORDS]

# ========== ХРАНИЛИЩЕ ПОДОЗРИТЕЛЬНЫХ СЛОВ И ЗАПРОСОВ ==========
suspicious_words = {}
pending_requests = {}  # {request_id: {"type": "add"/"del", "word": str, "admin": user, "chat": chat}}

bot = Bot(token=TOKEN)
dp = Dispatcher()

def check_profanity(text):
    if not text: return False
    return any(p.search(text) for p in BAD_PATTERNS)

def is_admin(chat_member):
    """Проверка на админа"""
    return chat_member.status in ["administrator", "creator"]

def is_owner(user_id):
    """Проверка на владельца бота"""
    return user_id == OWNER_ID

# ========== КОМАНДА ДЛЯ ЗАПРОСА ДОБАВЛЕНИЯ МАТА (АДМИНЫ ЧАТОВ) ==========
@dp.message(Command("addmat"))
async def request_add_mat(msg: types.Message):
    # Проверяем, админ ли в группе
    try:
        chat_member = await bot.get_chat_member(msg.chat.id, msg.from_user.id)
        if not is_admin(chat_member):
            await msg.reply("❌ Только админы могут отправлять запросы на добавление слов")
            return
    except:
        await msg.reply("❌ Ошибка проверки прав")
        return
    
    word = msg.text.replace("/addmat", "").strip()
    if not word:
        await msg.reply("❌ Укажите слово: /addmat слово")
        return
    
    # Проверяем, есть ли уже слово в базе
    if check_profanity(word):
        await msg.reply(f"❌ Слово '{word}' уже есть в базе матов")
        return
    
    # Создаем ID запроса
    request_id = f"add_{datetime.now().timestamp()}_{msg.from_user.id}"
    
    # Сохраняем запрос
    pending_requests[request_id] = {
        "type": "add",
        "word": word,
        "admin": msg.from_user,
        "chat": msg.chat,
        "message_id": msg.message_id
    }
    
    # Создаем кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ ПРИНЯТЬ", callback_data=f"approve_{request_id}"),
            InlineKeyboardButton(text="❌ ОТКЛОНИТЬ", callback_data=f"reject_{request_id}")
        ]
    ])
    
    # Отправляем запрос владельцу
    await bot.send_message(
        OWNER_ID,
        f"🔔 ЗАПРОС НА ДОБАВЛЕНИЕ МАТА\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"Админ: @{msg.from_user.username or msg.from_user.id}\n"
        f"Чат: {msg.chat.title}\n"
        f"ID чата: {msg.chat.id}\n"
        f"Слово: {word}\n"
        f"━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=keyboard
    )
    
    await msg.reply(f"✅ Запрос на добавление слова '{word}' отправлен владельцу бота")

# ========== КОМАНДА ДЛЯ ЗАПРОСА УДАЛЕНИЯ МАТА (АДМИНЫ ЧАТОВ) ==========
@dp.message(Command("delmat"))
async def request_del_mat(msg: types.Message):
    # Проверяем, админ ли в группе
    try:
        chat_member = await bot.get_chat_member(msg.chat.id, msg.from_user.id)
        if not is_admin(chat_member):
            await msg.reply("❌ Только админы могут отправлять запросы на удаление слов")
            return
    except:
        await msg.reply("❌ Ошибка проверки прав")
        return
    
    word = msg.text.replace("/delmat", "").strip()
    if not word:
        await msg.reply("❌ Укажите слово: /delmat слово")
        return
    
    # Проверяем, есть ли слово в базе
    if not check_profanity(word):
        await msg.reply(f"❌ Слова '{word}' нет в базе матов")
        return
    
    # Создаем ID запроса
    request_id = f"del_{datetime.now().timestamp()}_{msg.from_user.id}"
    
    # Сохраняем запрос
    pending_requests[request_id] = {
        "type": "del",
        "word": word,
        "admin": msg.from_user,
        "chat": msg.chat,
        "message_id": msg.message_id
    }
    
    # Создаем кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ ПРИНЯТЬ", callback_data=f"approve_{request_id}"),
            InlineKeyboardButton(text="❌ ОТКЛОНИТЬ", callback_data=f"reject_{request_id}")
        ]
    ])
    
    # Отправляем запрос владельцу
    await bot.send_message(
        OWNER_ID,
        f"🔔 ЗАПРОС НА УДАЛЕНИЕ МАТА\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"Админ: @{msg.from_user.username or msg.from_user.id}\n"
        f"Чат: {msg.chat.title}\n"
        f"ID чата: {msg.chat.id}\n"
        f"Слово: {word}\n"
        f"━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=keyboard
    )
    
    await msg.reply(f"✅ Запрос на удаление слова '{word}' отправлен владельцу бота")

# ========== КОМАНДЫ ТОЛЬКО ДЛЯ ВЛАДЕЛЬЦА (БЕЗ ЗАПРОСОВ) ==========
@dp.message(Command("owneradd"))
async def owner_add_mat(msg: types.Message):
    if not is_owner(msg.from_user.id):
        await msg.reply("❌ Эта команда только для владельца бота")
        return
    
    word = msg.text.replace("/owneradd", "").strip()
    if not word:
        await msg.reply("❌ Укажите слово: /owneradd слово")
        return
    
    global BAD_WORDS, BAD_PATTERNS
    BAD_WORDS.append(word)
    BAD_PATTERNS = [re.compile(w, re.IGNORECASE) for w in BAD_WORDS]
    await msg.reply(f"✅ Слово '{word}' добавлено в базу матов")
    
    # Запись в таблицу
    try:
        now = datetime.now()
        sheet.append_row([
            now.strftime("%d.%m.%Y"),           # A: Дата
            now.strftime("%H:%M:%S"),           # B: Время
            "👑 ВЛАДЕЛЕЦ",                     # C: Ник (от)
            "OWNER",                           # D: Имя (от)
            str(OWNER_ID),                    # E: ID (от)
            f"ДОБАВЛЕНО: {word}",             # F: Сообщение
            "БАЗА МАТОВ",                     # G: Чат
            "➕ ДОБАВЛЕНИЕ",                  # H: Действие
            "",                               # I: Ник (на кого)
            "",                               # J: Имя (на кого)
            "ВЫПОЛНЕНО"                      # K: Статус
        ])
    except:
        pass

@dp.message(Command("ownerdel"))
async def owner_del_mat(msg: types.Message):
    if not is_owner(msg.from_user.id):
        await msg.reply("❌ Эта команда только для владельца бота")
        return
    
    word = msg.text.replace("/ownerdel", "").strip()
    if not word:
        await msg.reply("❌ Укажите слово: /ownerdel слово")
        return
    
    global BAD_WORDS, BAD_PATTERNS
    
    # Ищем и удаляем слово из списка
    found = False
    for w in BAD_WORDS[:]:
        if w == word:
            BAD_WORDS.remove(w)
            found = True
    
    if found:
        BAD_PATTERNS = [re.compile(w, re.IGNORECASE) for w in BAD_WORDS]
        await msg.reply(f"✅ Слово '{word}' удалено из базы матов")
        
        # Запись в таблицу
        try:
            now = datetime.now()
            sheet.append_row([
                now.strftime("%d.%m.%Y"),           # A: Дата
                now.strftime("%H:%M:%S"),           # B: Время
                "👑 ВЛАДЕЛЕЦ",                     # C: Ник (от)
                "OWNER",                           # D: Имя (от)
                str(OWNER_ID),                    # E: ID (от)
                f"УДАЛЕНО: {word}",               # F: Сообщение
                "БАЗА МАТОВ",                     # G: Чат
                "➖ УДАЛЕНИЕ",                    # H: Действие
                "",                               # I: Ник (на кого)
                "",                               # J: Имя (на кого)
                "ВЫПОЛНЕНО"                      # K: Статус
            ])
        except:
            pass
    else:
        await msg.reply(f"❌ Слово '{word}' не найдено в базе")

# ========== ОБРАБОТЧИК КНОПОК ==========
@dp.callback_query()
async def handle_request(callback: types.CallbackQuery):
    if callback.from_user.id != OWNER_ID:
        await callback.answer("❌ Только владелец бота может решать запросы", show_alert=True)
        return
    
    data = callback.data
    request_id = data.split("_", 1)[1]
    
    if request_id not in pending_requests:
        await callback.message.edit_text("❌ Запрос устарел или уже обработан")
        await callback.answer()
        return
    
    request = pending_requests[request_id]
    action = "approve" if data.startswith("approve") else "reject"
    
    if action == "approve":
        if request["type"] == "add":
            # Добавляем слово
            global BAD_WORDS, BAD_PATTERNS
            BAD_WORDS.append(request["word"])
            BAD_PATTERNS = [re.compile(w, re.IGNORECASE) for w in BAD_WORDS]
            
            # Уведомляем админа
            try:
                await bot.send_message(
                    request["chat"].id,
                    f"✅ Владелец бота ОДОБРИЛ добавление слова '{request['word']}' в базу матов"
                )
            except:
                pass
            
            # Запись в таблицу - ИСПРАВЛЕНО!
            try:
                now = datetime.now()
                sheet.append_row([
                    now.strftime("%d.%m.%Y"),           # A: Дата
                    now.strftime("%H:%M:%S"),           # B: Время
                    f"@{request['admin'].username or request['admin'].id}",  # C: Ник (от)
                    request['admin'].first_name or "",  # D: Имя (от)
                    str(request['admin'].id),          # E: ID (от)
                    f"ЗАПРОС ОДОБРЕН: {request['word']}",  # F: Сообщение
                    request['chat'].title or "чат",    # G: Чат
                    "➕ ДОБАВЛЕНИЕ",                   # H: Действие
                    "👑 ВЛАДЕЛЕЦ",                    # I: Ник (на кого)
                    "ОДОБРЕНО",                       # J: Имя (на кого)
                    "В БАЗЕ"                          # K: Статус
                ])
            except:
                pass
            
            await callback.message.edit_text(
                f"{callback.message.text}\n\n✅ ЗАПРОС ОДОБРЕН\nСлово '{request['word']}' добавлено в базу"
            )
            
        elif request["type"] == "del":
            # Удаляем слово
            found = False
            for w in BAD_WORDS[:]:
                if w == request["word"]:
                    BAD_WORDS.remove(w)
                    found = True
            
            if found:
                BAD_PATTERNS = [re.compile(w, re.IGNORECASE) for w in BAD_WORDS]
                
                # Уведомляем админа
                try:
                    await bot.send_message(
                        request["chat"].id,
                        f"✅ Владелец бота ОДОБРИЛ удаление слова '{request['word']}' из базы матов"
                    )
                except:
                    pass
                
                # Запись в таблицу - ИСПРАВЛЕНО!
                try:
                    now = datetime.now()
                    sheet.append_row([
                        now.strftime("%d.%m.%Y"),           # A: Дата
                        now.strftime("%H:%M:%S"),           # B: Время
                        f"@{request['admin'].username or request['admin'].id}",  # C: Ник (от)
                        request['admin'].first_name or "",  # D: Имя (от)
                        str(request['admin'].id),          # E: ID (от)
                        f"ЗАПРОС ОДОБРЕН: {request['word']}",  # F: Сообщение
                        request['chat'].title or "чат",    # G: Чат
                        "➖ УДАЛЕНИЕ",                     # H: Действие
                        "👑 ВЛАДЕЛЕЦ",                    # I: Ник (на кого)
                        "ОДОБРЕНО",                       # J: Имя (на кого)
                        "УДАЛЕНО"                         # K: Статус
                    ])
                except:
                    pass
                
                await callback.message.edit_text(
                    f"{callback.message.text}\n\n✅ ЗАПРОС ОДОБРЕН\nСлово '{request['word']}' удалено из базы"
                )
            else:
                await callback.message.edit_text(
                    f"{callback.message.text}\n\n❌ ОШИБКА\nСлово '{request['word']}' не найдено в базе"
                )
    
    else:  # reject
        # Уведомляем админа
        try:
            await bot.send_message(
                request["chat"].id,
                f"❌ Владелец бота ОТКЛОНИЛ запрос на {'добавление' if request['type'] == 'add' else 'удаление'} слова '{request['word']}'"
            )
        except:
            pass
        
        # Запись в таблицу - ИСПРАВЛЕНО!
        try:
            now = datetime.now()
            action_type = "➕ ДОБАВЛЕНИЕ" if request["type"] == "add" else "➖ УДАЛЕНИЕ"
            
            sheet.append_row([
                now.strftime("%d.%m.%Y"),           # A: Дата
                now.strftime("%H:%M:%S"),           # B: Время
                f"@{request['admin'].username or request['admin'].id}",  # C: Ник (от)
                request['admin'].first_name or "",  # D: Имя (от)
                str(request['admin'].id),          # E: ID (от)
                f"ЗАПРОС ОТКЛОНЕН: {request['word']}",  # F: Сообщение
                request['chat'].title or "чат",    # G: Чат
                action_type,                       # H: Действие
                "👑 ВЛАДЕЛЕЦ",                    # I: Ник (на кого)
                "ОТКЛОНЕНО",                      # J: Имя (на кого)
                "НЕ ВЫПОЛНЕНО"                    # K: Статус
            ])
        except:
            pass
        
        await callback.message.edit_text(
            f"{callback.message.text}\n\n❌ ЗАПРОС ОТКЛОНЕН"
        )
    
    # Удаляем запрос из хранилища
    del pending_requests[request_id]
    await callback.answer()

# ========== КОМАНДА ПОМОЩИ ==========
@dp.message(Command("help"))
async def help_command(msg: types.Message):
    try:
        chat_member = await bot.get_chat_member(msg.chat.id, msg.from_user.id)
        is_admin_user = is_admin(chat_member)
    except:
        is_admin_user = False
    
    if is_owner(msg.from_user.id):
        help_text = (
            "👑 ВЛАДЕЛЕЦ БОТА\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "• /owneradd слово — добавить мат в базу (мгновенно)\n"
            "• /ownerdel слово — удалить мат из базы (мгновенно)\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "📌 Админы чатов могут отправлять запросы:\n"
            "• /addmat слово — запрос на добавление\n"
            "• /delmat слово — запрос на удаление\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "❓ @SERRRUGA"
        )
    elif is_admin_user:
        help_text = (
            "🛡️ АДМИН ЧАТА\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "• /addmat слово — запрос на добавление мата в базу\n"
            "• /delmat слово — запрос на удаление мата из базы\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "📌 После запроса владелец бота рассмотрит его\n"
            "Для большего функционала с ботом, зайдите в его лс и пропишите /start\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "❓ @SERRRUGA"
        )
    else:
        help_text = (
            "🛡️ БОТ МОДЕРАЦИИ\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "📌 ДЛЯ ВСЕХ:\n"
            "• Ответь на сообщение и напиши «мат» — репорт уйдёт админу\n"
            "• Бот автоматически ловит мат и записывает в таблицу\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "❓ @SERRRUGA"
        )
    
    await msg.reply(help_text)

@dp.message(Command("start"))
async def start_command(msg: types.Message):
    help_text = (
        "🛡️ БОТ МОДЕРАЦИИ\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "Бот создан для модерации нецензурной лексики\n"
        "Команда /help — подробная информация\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "❓ @SERRRUGA"
    )
    await msg.reply(help_text)

# ========== ОСНОВНОЙ ОБРАБОТЧИК СООБЩЕНИЙ ==========
@dp.message()
async def handle_message(msg: types.Message):
    if not msg.text or msg.text.startswith('/'): 
        return
    
    now = datetime.now()
    
    # ========== ПРОВЕРКА НА МАТ ==========
    if check_profanity(msg.text):
        user = msg.from_user
        
        # РАНДОМНОЕ СООБЩЕНИЕ
        import random
        messages = [
            f"❌ @{user.username or 'Пользователь'}, выражайтесь культурнее!",
            f"❌ @{user.username or 'Пользователь'}, без мата пожалуйста!",
            f"❌ @{user.username or 'Пользователь'}, в чате не материмся!",
            f"❌ @{user.username or 'Пользователь'}, следите за языком!",
            f"❌ @{user.username or 'Пользователь'}, нарушение записано!",
            f"❌ @{user.username or 'Пользователь'}, это чат, а не подворотня!",
            f"❌ @{user.username or 'Пользователь'}, культурное общение приветствуется!",
        ]
        
        try:
            await msg.reply(random.choice(messages), allow_sending_without_reply=True)
        except:
            pass
        
        # Запись в таблицу - ИСПРАВЛЕНО!
        try:
            sheet.append_row([
                now.strftime("%d.%m.%Y"),           # A: Дата
                now.strftime("%H:%M:%S"),           # B: Время
                f"@{user.username}" if user.username else f"id{user.id}",  # C: Ник (от)
                user.first_name or "",              # D: Имя (от)
                str(user.id),                      # E: ID (от)
                msg.text[:200],                    # F: Сообщение
                msg.chat.title or "личка",         # G: Чат
                "🚫 МАТ",                          # H: Действие
                "",                                # I: Ник (на кого)
                "",                                # J: Имя (на кого)
                "ЗАПИСАН"                         # K: Статус
            ])
        except Exception as e:
            print(f"Ошибка записи мата: {e}")
        
        print(f"🚫 {now.strftime('%H:%M')} @{user.username}: {msg.text[:30]}...")
    
    # ========== АВТОРАСПОЗНАВАНИЕ НОВЫХ МАТОВ ==========
    else:
        words = msg.text.lower().split()
        chat_id = msg.chat.id
        
        for word in words:
            word = word.strip('.,!?;:"\'()[]{}')
            
            if len(word) > 3 and not check_profanity(word):
                key = f"{chat_id}:{word}"
                
                if key in suspicious_words:
                    suspicious_words[key]['count'] += 1
                    suspicious_words[key]['users'].add(msg.from_user.id)
                    
                    if (suspicious_words[key]['count'] >= 3 and 
                        len(suspicious_words[key]['users']) >= 2):
                        
                        await bot.send_message(
                            OWNER_ID,
                            f"⚠️ ПОДОЗРИТЕЛЬНОЕ СЛОВО!\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"Слово: {word}\n"
                            f"Чат: {msg.chat.title}\n"
                            f"Упоминаний: {suspicious_words[key]['count']}\n"
                            f"Команда: /owneradd {word}"
                        )
                        
                        # Запись в таблицу - ИСПРАВЛЕНО!
                        try:
                            sheet.append_row([
                                now.strftime("%d.%m.%Y"),           # A: Дата
                                now.strftime("%H:%M:%S"),           # B: Время
                                "🔍 АВТОРАСПОЗНАВАНИЕ",            # C: Ник (от)
                                "СИСТЕМА",                         # D: Имя (от)
                                word,                              # E: ID (от) - сюда слово
                                f"Частота: {suspicious_words[key]['count']}",  # F: Сообщение
                                msg.chat.title or "чат",           # G: Чат
                                "⚠️ ТРЕБУЕТ ПРОВЕРКИ",            # H: Действие
                                "",                                # I: Ник (на кого)
                                "",                                # J: Имя (на кого)
                                "НЕ В БАЗЕ"                        # K: Статус
                            ])
                        except:
                            pass
                        
                        del suspicious_words[key]
                else:
                    suspicious_words[key] = {
                        'count': 1,
                        'users': {msg.from_user.id},
                        'first_seen': now.strftime("%d.%m.%Y %H:%M")
                    }
    
    # ========== РЕПОРТ ОТ ПОЛЬЗОВАТЕЛЕЙ ==========
    if msg.reply_to_message and msg.text and "мат" in msg.text.lower():
        reported_msg = msg.reply_to_message
        reported_user = reported_msg.from_user
        reporter = msg.from_user
        
        has_mat = check_profanity(reported_msg.text) if reported_msg.text else False
        
        report_text = (
            f"🚨 РЕПОРТ\n"
            f"━━━━━━━━━━━━━━━\n"
            f"От: @{reporter.username or reporter.id}\n"
            f"На: @{reported_user.username or 'нет'}\n"
            f"Чат: {msg.chat.title}\n"
            f"Текст: {reported_msg.text[:200]}\n"
            f"Ссылка: https://t.me/c/{str(msg.chat.id)[4:]}/{reported_msg.message_id}\n"
            f"Статус: {'✅ В базе' if has_mat else '❌ Нет в базе'}"
        )
        
        await bot.send_message(OWNER_ID, report_text)
        
        # Запись в таблицу - ИСПРАВЛЕНО!
        try:
            sheet.append_row([
                now.strftime("%d.%m.%Y"),           # A: Дата
                now.strftime("%H:%M:%S"),           # B: Время
                f"@{reporter.username or reporter.id}",  # C: Ник (от)
                reporter.first_name or "",          # D: Имя (от)
                str(reporter.id),                  # E: ID (от)
                f"РЕПОРТ: {reported_msg.text[:100]}",  # F: Сообщение
                msg.chat.title or "чат",           # G: Чат
                "🚨 РЕПОРТ",                       # H: Действие
                f"@{reported_user.username or 'нет'}",  # I: Ник (на кого)
                reported_user.first_name or "",    # J: Имя (на кого)
                "✅ В БАЗЕ" if has_mat else "❌ НЕТ В БАЗЕ"  # K: Статус
            ])
        except Exception as e:
            print(f"Ошибка записи репорта: {e}")
        
        await msg.reply("✅ Репорт отправлен!")

async def main():
    print("✅ БОТ ЗАПУЩЕН")
    print(f"   • ID владельца: {OWNER_ID}")
    print(f"   • @SERRRUGA")
    print(f"   • Команды:")
    print(f"     - /addmat  (запрос на добавление от админов)")
    print(f"     - /delmat  (запрос на удаление от админов)") 
    print(f"     - /owneradd (мгновенно для владельца)")
    print(f"     - /ownerdel (мгновенно для владельца)")
    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())
