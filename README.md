# 📱 Multi-Tool Telegram Bot

A simple Telegram bot that supports multiple tools. It currently includes a QR code generator and a discount optimizer, with more tools planned.

## ✨ Features

- **Tool Menu**: List and select tools with `/tools` or `/use <tool>`.
- **QR Codes**: Generate a QR code from any text.
- **Discount Optimizer**: Calculate the purchase amount needed to reach a max discount cap.
- **URL Shortener**: Shorten URLs with the TinyURL service.

## 📋 Prerequisites

- Python 3.8+
- A Telegram account and a Telegram Bot API token

## ⚙️ Configuration

Set your bot token in an environment variable:

- `BOT_TOKEN`

## 🧭 Commands

- `/start`: Welcome message and tool menu
- `/help`: Show current tool and help text
- `/tools`: Show available tools
- `/use <tool>`: Select a tool by key or label

## 🧪 Usage

### QR Code tool

1. Select the tool: `/use qr`
2. Send any text, and the bot will return a QR code image.

### Discount Optimizer tool

Find the optimal purchase amount to reach the maximum discount cap.

1. Select the tool: `/use discount`
2. Send input as: `<percent> <max VND>`

Examples:

- `10 50000`
- `10% (max 50000 VND)`

Output example:

```
Optimal purchase amount: 500,000 VND
Max discount applied: 50,000 VND at 10%
```

### URL Shortener tool

1. Select the tool: `/use shorten`
2. Send a URL, and the bot will return a shortened link.

Examples:

- `https://example.com/some/long/path`
- `example.com/some/long/path`

## Command notes:

- python3 -m venv .venv && source .venv/bin/activate
- pip install -r requirements.txt
- kill $(cat bot.pid)
- nohup .venv/bin/python bot.py > bot.log 2>&1 & echo $! > bot.pid
- tail -f bot.log
