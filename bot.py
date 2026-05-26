from dotenv import load_dotenv
import os
import telebot
from telebot import types

from utils.currency import build_currency_response
from utils.discount import build_discount_response
from utils.qr import generate_qr_code
from utils.shortener import build_shortener_response

# Load environment variables from the .env file
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

user_tool_selection = {}


def handle_qr(message):
    qr_code = generate_qr_code(message.text, "qr_code.png")
    with open(qr_code, "rb") as qr_file:
        bot.send_photo(message.chat.id, qr_file)


def handle_discount(message):
    response, error = build_discount_response(message.text)
    if error:
        bot.reply_to(message, error)
        return

    bot.reply_to(message, response)


def handle_currency(message):
    response, error = build_currency_response(message.text)
    if error:
        bot.reply_to(message, error)
        return

    bot.reply_to(message, response)


def handle_shortener(message):
    response, error = build_shortener_response(message.text)
    if error:
        bot.reply_to(message, error)
        return

    bot.reply_to(message, response)


TOOLS = {
    "qr": {
        "label": "QR Code",
        "description": "Generate a QR code from text.",
        "handler": handle_qr,
    },
    "discount": {
        "label": "Discount Optimizer",
        "description": "Find purchase amount to reach max discount (X% capped at Y VND).",
        "handler": handle_discount,
    },
    "currency": {
        "label": "Currency Converter",
        "description": "Convert USD, EUR, JPY, or CNY amounts to VND.",
        "handler": handle_currency,
    },
    "shorten": {
        "label": "URL Shortener",
        "description": "Shorten a URL using the is.gd service.",
        "handler": handle_shortener,
    },
}


def set_selected_tool(chat_id, tool_key):
    user_tool_selection[chat_id] = tool_key


def get_selected_tool(chat_id):
    return user_tool_selection.get(chat_id)


def normalize_tool_key(text):
    if not text:
        return None

    normalized = text.strip().lower()
    for key, tool in TOOLS.items():
        if normalized == key.lower() or normalized == tool["label"].lower():
            return key

    return None


def build_tools_keyboard():
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False)
    for tool in TOOLS.values():
        keyboard.add(types.KeyboardButton(tool["label"]))
    return keyboard


def format_tools_list():
    lines = ["Available tools:"]
    for key, tool in TOOLS.items():
        lines.append(f"- {tool['label']} ({key}): {tool['description']}")
    lines.append("Use /use <tool> or tap a button to select.")
    return "\n".join(lines)


def send_tools_menu(message):
    bot.send_message(
        message.chat.id,
        format_tools_list(),
        reply_markup=build_tools_keyboard(),
    )


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Choose a tool to get started.")
    send_tools_menu(message)


@bot.message_handler(commands=["help"])
def send_help(message):
    selected_tool = get_selected_tool(message.chat.id)
    if selected_tool:
        tool = TOOLS[selected_tool]
        help_text = (
            f"Current tool: {tool['label']}. {tool['description']}\n"
            "Use /tools to see all tools or /use <tool> to switch."
        )
    else:
        help_text = "Use /tools to see available tools and /use <tool> to select one."

    bot.reply_to(message, help_text)


@bot.message_handler(commands=["tools"])
def list_tools(message):
    send_tools_menu(message)


@bot.message_handler(commands=["use"])
def use_tool(message):
    parts = message.text.split(maxsplit=1)
    tool_text = parts[1] if len(parts) > 1 else None
    tool_key = normalize_tool_key(tool_text)

    if not tool_text:
        bot.reply_to(message, "Tell me which tool to use. Example: /use qr")
        send_tools_menu(message)
        return

    if not tool_key:
        bot.reply_to(message, "Unknown tool. Choose from the list below.")
        send_tools_menu(message)
        return

    set_selected_tool(message.chat.id, tool_key)
    bot.reply_to(
        message, f"Selected tool: {TOOLS[tool_key]['label']}. Send me the input.")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not message.text:
        bot.reply_to(message, "Please send text input.")
        return

    tool_key = normalize_tool_key(message.text)
    if tool_key:
        set_selected_tool(message.chat.id, tool_key)
        bot.reply_to(
            message, f"Selected tool: {TOOLS[tool_key]['label']}. Send me the input.")
        return

    selected_tool = get_selected_tool(message.chat.id)
    if not selected_tool:
        bot.reply_to(message, "Please choose a tool first.")
        send_tools_menu(message)
        return

    TOOLS[selected_tool]["handler"](message)


bot.infinity_polling()
