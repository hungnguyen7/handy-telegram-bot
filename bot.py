from dotenv import load_dotenv
from io import BytesIO
import os
import telebot
from telebot import types

from utils.currency import build_currency_response
from utils.discount import build_discount_response
from utils.bg_remove import build_background_removed_image
from utils.qr import generate_qr_code
from utils.shortener import build_shortener_response

# Load environment variables from the .env file
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

user_tool_selection = {}


def register_bot_commands():
    commands = [
        types.BotCommand("start", "Start the bot"),
        types.BotCommand("help", "Show help for the current tool"),
        types.BotCommand("tools", "List available tools"),
        types.BotCommand("use", "Select a tool by key or label"),
    ]
    try:
        bot.set_my_commands(commands)
    except telebot.apihelper.ApiTelegramException:
        pass


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


def handle_background_remove(message):
    if not message.photo:
        bot.reply_to(message, "Please send a photo to remove the background.")
        return

    file_info = bot.get_file(message.photo[-1].file_id)
    image_bytes = bot.download_file(file_info.file_path)
    output_bytes, error = build_background_removed_image(image_bytes)
    if error:
        bot.reply_to(message, error)
        return

    output_stream = BytesIO(output_bytes)
    output_stream.name = "background_removed.png"
    bot.send_photo(message.chat.id, output_stream)


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
        "description": "Shorten a URL using the TinyURL service.",
        "handler": handle_shortener,
    },
    "bgremove": {
        "label": "Background Remover",
        "description": "Remove the background from a photo.",
        "handler": handle_background_remove,
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


@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    tool_key = normalize_tool_key(message.caption)
    if tool_key:
        set_selected_tool(message.chat.id, tool_key)

    selected_tool = get_selected_tool(message.chat.id)
    if not selected_tool:
        bot.reply_to(message, "Please choose a tool first.")
        send_tools_menu(message)
        return

    if selected_tool != "bgremove":
        bot.reply_to(message, "This tool expects text input. Use /use bgremove for photos.")
        return

    handle_background_remove(message)


@bot.message_handler(content_types=["text"])
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


register_bot_commands()
bot.infinity_polling()
