import asyncio
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from minecraft import MinecraftServer
from secret_token import TOKEN
from config import TIME_LOGIN_AVAILABILITY, ALLOWED_USER_IDS


# Dictionary for storing registered users' nicknames
user_nicks = {}

minecraft_server = MinecraftServer()


# Command /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = update.effective_chat.username
    except:
        user_id = update.effective_chat.id

    if user_id in ALLOWED_USER_IDS:
        button = KeyboardButton("Register")
        reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True)
        await update.message.reply_text("Choose a button:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("To use the bot, send your username to @v0r0bi0v. " + 
                                        "If your username is hidden, send your ID, which you can find in @userinfobot.")

# Handling button press for Register
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Enter your nickname:")
    return "WAITING_FOR_NICK"

# Handling the entered nickname
async def handle_nick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = update.effective_chat.username
    except:
        user_id = update.effective_chat.id
    nick = update.message.text
    user_nicks[user_id] = nick

    button = KeyboardButton("Login")
    reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True)
    await update.message.reply_text("Your nickname has been saved. Press the button to log in:", reply_markup=reply_markup)

# Handling button press for Login
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = update.effective_chat.username
    except:
        user_id = update.effective_chat.id

    if user_id in user_nicks:
        await update.message.reply_text("You have two minutes to log in to the server.")
        minecraft_server.add_to_whitelist(user_nicks[user_id])
        # Wait for 2 minutes without blocking
        await asyncio.sleep(TIME_LOGIN_AVAILABILITY)
        # After 2 minutes, show the Login button again
        button = KeyboardButton("Login")
        reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True)
        await update.message.reply_text("Time is up. Press the button to log in again:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Please register first!")

async def main() -> None:
    # Create the bot
    app = ApplicationBuilder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex('^Register$'), register))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_nick))
    app.add_handler(MessageHandler(filters.Regex('^Login$'), login))

    # Start the bot
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
