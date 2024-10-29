import asyncio
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from minecraft import MinecraftServer
from secret_token import TOKEN
from config import TIME_LOGIN_AVAILABILITY, ALLOWED_USER_IDS


# Заранее заданный список id пользователей

# Словарь для хранения никнеймов пользователей
user_nicks = {}

minecraft_server = MinecraftServer()


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = update.effective_chat.username
    except:
        user_id = update.effective_chat.id

    if user_id in ALLOWED_USER_IDS:
        button = KeyboardButton("Register")
        reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True)
        await update.message.reply_text("Выберите кнопку:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Напишите @v0r0bi0v, чтобы пользоваться ботом.")

# Обработка нажатия кнопки Register
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Введите ваш ник:")
    return "WAITING_FOR_NICK"

# Обработка введенного ника
async def handle_nick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = update.effective_chat.username
    except:
        user_id = update.effective_chat.id
    nick = update.message.text
    user_nicks[user_id] = nick

    button = KeyboardButton("Login")
    reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True)
    await update.message.reply_text("Ваш ник сохранен. Нажмите кнопку, чтобы войти:", reply_markup=reply_markup)

# Обработка нажатия кнопки Login
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = update.effective_chat.username
    except:
        user_id = update.effective_chat.id

    if user_id in user_nicks:
        await update.message.reply_text("У вас есть две минуты, чтобы войти на сервер.")
        minecraft_server.add_to_whitelist(user_nicks[user_id])
        # Ждем 2 минуты без блокировки
        await asyncio.sleep(TIME_LOGIN_AVAILABILITY)
        # После 2 минут снова показываем кнопку Login
        button = KeyboardButton("Login")
        reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True)
        await update.message.reply_text("Время вышло. Нажмите кнопку, чтобы снова войти:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Сначала зарегистрируйтесь!")

async def main() -> None:
    # Создаем бота
    app = ApplicationBuilder().token(TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex('^Register$'), register))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_nick))
    app.add_handler(MessageHandler(filters.Regex('^Login$'), login))

    # Запускаем бота
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())