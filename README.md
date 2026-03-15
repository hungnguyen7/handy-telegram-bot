# 📱 QR Code Telegram Bot

A simple Telegram bot that generates QR codes from any given text. This bot allows you to create and send QR codes directly through Telegram, making it easy to share information quickly and efficiently.

## ✨ Features

- **Generate QR Codes**: Input any text, and the bot will generate a corresponding QR code.
- **Send QR Codes**: Easily share generated QR codes in your Telegram chats.
- **Customizable Size**: Specify the size of the generated QR code for better visibility.

## 📋 Prerequisites

- Python 3.8+
- A Telegram account and a Telegram Bot API token


## Command notes:
- python3 -m venv .venv && source .venv/bin/activate
- pip install -r requirements.txt
- nohup .venv/bin/python bot.py > bot.log 2>&1 & echo $! > bot.pid
