import asyncio
import json
import os
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, simpledialog
import winreg
import discord
import telebot
from PIL import Image, ImageDraw
import pystray

# Имя файла конфигурации
CONFIG_FILE = "config.json"
REG_KEY_NAME = "DiscordTelegramNotifier"

def get_base_path():
    """Определяет путь к папке, где запущен скрипт или .exe"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(get_base_path(), CONFIG_FILE)

def get_icon_path():
    """Определяет правильный путь к иконке (работает и в .py, и внутри собранного .exe)"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, "icon.ico")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None
    return None

def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def get_autostart_status():
    """Проверяет, находится ли скрипт в автозагрузке"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, REG_KEY_NAME)
        winreg.CloseKey(key)
        return True
    except:
        return False

def toggle_autostart(icon, item):
    """Включает или выключает автозагрузку и обновляет галочку в трее"""
    is_exe = hasattr(sys, '_MEIPASS')
    path_to_run = sys.executable if is_exe else os.path.abspath(sys.argv[0])
    
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE | winreg.KEY_COMMANDS)
    if get_autostart_status():
        try:
            winreg.DeleteValue(key, REG_KEY_NAME)
            messagebox.showinfo("Автозагрузка", "Скрипт удален из автозагрузки.")
        except:
            pass
    else:
        winreg.SetValueEx(key, REG_KEY_NAME, 0, winreg.REG_SZ, f'"{path_to_run}"')
        messagebox.showinfo("Автозагрузка", "Скрипт успешно добавлен в автозагрузку!")
    winreg.CloseKey(key)
    
    # Принудительно обновляем меню в трее, чтобы визуально переключить галочку
    icon.update_menu()

def request_config_gui():
    """Графический интерфейс ввода настроек без пера tkinter"""
    root = tk.Tk()
    root.withdraw()  # Прячем основное окно
    
    # Устанавливаем иконку для окон tkinter (убираем перо)
    icon_path = get_icon_path()
    if os.path.exists(icon_path):
        try:
            root.iconbitmap(icon_path)
        except:
            pass
    
    current = load_config() or {"DISCORD_TOKEN": "", "TELEGRAM_TOKEN": "", "TELEGRAM_CHAT_ID": ""}
    
    d_token = simpledialog.askstring("Настройка", "Введите токен Discord (User Token):", initialvalue=current["DISCORD_TOKEN"], parent=root)
    if not d_token: return False
    
    tg_token = simpledialog.askstring("Настройка", "Введите токен Telegram-бота:", initialvalue=current["TELEGRAM_TOKEN"], parent=root)
    if not tg_token: return False
    
    tg_id = simpledialog.askstring("Настройка", "Введите ваш Telegram Chat ID (число):", initialvalue=str(current["TELEGRAM_CHAT_ID"]), parent=root)
    if not tg_id or not tg_id.strip().isdigit():
        messagebox.showerror("Ошибка", "ID должен состоять только из цифр!", parent=root)
        return False
        
    new_config = {
        "DISCORD_TOKEN": d_token.strip(),
        "TELEGRAM_TOKEN": tg_token.strip(),
        "TELEGRAM_CHAT_ID": int(tg_id.strip())
    }
    save_config(new_config)
    
    # При первом создании конфига — автоматически включаем автозагрузку
    if not current["DISCORD_TOKEN"] and not get_autostart_status():
        try:
            is_exe = hasattr(sys, '_MEIPASS')
            path_to_run = sys.executable if is_exe else os.path.abspath(sys.argv[0])
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, REG_KEY_NAME, 0, winreg.REG_SZ, f'"{path_to_run}"')
            winreg.CloseKey(key)
        except:
            pass
            
    messagebox.showinfo("Успех", "Настройки сохранены! Если вы меняли токены, приложение сейчас перезапустится.", parent=root)
    return True

# Проверка конфига перед стартом ядра
config = load_config()
if not config:
    if not request_config_gui():
        sys.exit(0)
    config = load_config()

# Инициализация шлюзов
tg_bot = telebot.TeleBot(config["TELEGRAM_TOKEN"])
loop = asyncio.new_event_loop()
CALL_TIMEOUT = 180 

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active_calls = {}

    def send_tg_message(self, text):
        try:
            tg_bot.send_message(config["TELEGRAM_CHAT_ID"], text, parse_mode="Markdown")
        except Exception as e:
            print(f"Ошибка отправки в TG: {e}")

    async def on_ready(self):
        print(f"Скрипт успешно запущен под аккаунтом: {self.user}")

    async def on_message(self, message):
        if message.guild is not None or message.author.id == self.user.id or message.author.bot:
            return

        author_name = message.author.name
        channel_id = message.channel.id

        if message.type == discord.MessageType.call or getattr(message.type, "value", None) == 3:
            is_call_start = True
            if hasattr(message, 'call') and message.call:
                if message.call.ended_timestamp:
                    is_call_start = False

            if is_call_start and channel_id not in self.active_calls:
                self.active_calls[channel_id] = {"user": author_name, "start_time": time.time()}
                deadline = time.strftime("%M:%S", time.gmtime(CALL_TIMEOUT))
                msg = f"🔔 *Входящий звонок!*\n👤 От: `{author_name}`\n⏳ Время до автосброса: ~{deadline} мин."
                await self.loop.run_in_executor(None, self.send_tg_message, msg)
            return

        if message.type == discord.MessageType.default:
            if message.content.strip():
                msg = f"✉️ *Новое сообщение*\n👤 От: `{author_name}`\n💬 Текст: {message.content}"
            elif message.attachments:
                msg = f"📁 *Новое вложение*\n👤 От: `{author_name}`\n📎 Отправлен медиафайл."
            else:
                return
            await self.loop.run_in_executor(None, self.send_tg_message, msg)

    async def on_private_channel_update(self, channel, before, after):
        channel_id = channel.id
        if channel_id in self.active_calls and not after.call:
            call_info = self.active_calls.pop(channel_id)
            duration = time.time() - call_info["start_time"]
            if duration < (CALL_TIMEOUT - 5): 
                msg = f"❌ *Вы пропустили входящий звонок*\n👤 От: `{call_info['user']}`"
                await self.loop.run_in_executor(None, self.send_tg_message, msg)

# Избавились от loop=loop в конструкторе
client = MyClient()

def create_tray_icon():
    icon_path = get_icon_path()
    if os.path.exists(icon_path):
        try: return Image.open(icon_path)
        except: pass
    image = Image.new('RGB', (64, 64), color=(32, 102, 230))
    d = ImageDraw.Draw(image)
    d.rectangle([(20, 20), (44, 44)], fill=(255, 255, 255))
    return image

def run_discord():
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(client.start(config["DISCORD_TOKEN"]))
    except Exception as e:
        print(f"Ошибка шлюза: {e}")

def on_edit_settings(icon, item):
    if request_config_gui():
        icon.stop()
        os.execv(sys.executable, [sys.executable] + sys.argv)

def on_exit(icon, item):
    icon.stop()
    future = asyncio.run_coroutine_threadsafe(client.close(), loop)
    try: future.result(timeout=2)
    except: pass
    loop.call_soon_threadsafe(loop.stop)
    sys.exit(0)

def main():
    discord_thread = threading.Thread(target=run_discord, daemon=True)
    discord_thread.start()

    # Корректное статическое меню pystray с динамическим lambda-чекбоксом
    menu_items = pystray.Menu(
        pystray.MenuItem("Изменить настройки", on_edit_settings),
        pystray.MenuItem("Автозагрузка", toggle_autostart, checked=lambda item: get_autostart_status()),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Выход", on_exit)
    )

    icon = pystray.Icon(
        "discord_notifier",
        icon=create_tray_icon(),
        title="Discord to Telegram",
        menu=menu_items
    )
    icon.run()

if __name__ == "__main__":
    main()