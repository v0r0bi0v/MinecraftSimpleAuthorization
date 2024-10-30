import asyncio
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from minecraft import MinecraftServer
from secret_token import TOKEN
from secret_password import PASSWORD
from config import TIME_LOGIN_AVAILABILITY


minecraft_server = MinecraftServer()

id_to_nickname = {}

# Command /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Enter the password to access the registration:")
    return "WAITING_FOR_PASSWORD"


# Handling password input
async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    entered_password = update.message.text
    if entered_password == PASSWORD:
        button = KeyboardButton("Register")
        reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True)
        await update.message.reply_text("Password correct. Press the button to register:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Incorrect password. Please try again by sending /start.")


# Handling button press for Register
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Enter your nickname:")
    return "WAITING_FOR_NICK"


# Handling the entered nickname
async def handle_nick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    id_to_nickname[update.effective_chat.id] = update.message.text
    button = KeyboardButton("Login")
    reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True)
    await update.message.reply_text("Your nickname has been saved. Press the button to log in:", reply_markup=reply_markup)


# Handling button press for Login
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("You have 2 minutes to log in to the server.")
    minecraft_server.add_to_whitelist(id_to_nickname[update.effective_chat.id])
    # Wait for 2 minutes without blocking
    await asyncio.sleep(TIME_LOGIN_AVAILABILITY)
    # After 2 minutes, show the Login button again
    button = KeyboardButton("Login")
    reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True)
    await update.message.reply_text("Time is up. Press the button to log in again:", reply_markup=reply_markup)


async def main() -> None:
    # Create the bot
    app = ApplicationBuilder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(PASSWORD), check_password))
    app.add_handler(MessageHandler(filters.Regex('^Register$'), register))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_nick))
    app.add_handler(MessageHandler(filters.Regex('^Login$'), login))

    # Start the bot
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
