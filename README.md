# Discord-to-telegram

choose your language:

# 🔔 Discord to Telegram Notifier

**Discord to Telegram** is a lightweight, self-contained background script (gateway) that forwards incoming direct messages, calls, and media attachments from your personal Discord account straight to a Telegram bot.

It is the perfect solution for anyone who frequently leaves Discord on **"Do Not Disturb" (DND)** mode but doesn't want to miss important calls or messages from friends while away from the computer!

---

## ✨ Features

* **Completely Standalone (All-in-One EXE):** The script is compiled into a single, compact executable file. No need to install Python, libraries, or dependencies—it works right out of the box.
* **Call Notifications:** The bot instantly sends a notification to Telegram when there is an incoming call, showing the caller's username and a countdown timer until the call auto-disconnects.
* **Missed Call Alerts:** If you miss a call, the script will send a dedicated alert so you know who tried to reach you.
* **Text & Media Forwarding:** It forwards regular text messages and alerts you about incoming media attachments (files, images).
* **System Tray Management (Tray Icon):** The app runs quietly in the background and minimizes to the Windows system tray (near the clock).
* **Quick Configuration:** Right from the tray menu, you can change your tokens on the fly, restart the gateway, or exit the application completely.
* **Smart Autostart:** A built-in startup toggle with a dynamic checkmark is integrated into the tray menu. The script automatically registers itself in the Windows Registry to launch on system boot.
* **Custom GUI Windows:** Initial setup dialogs are fully customized to match the application's aesthetic, replacing the default Windows/Tkinter look with the app's custom icon.

---

## 🚀 Setup Instructions

The application configuration takes less than 5 minutes.

### Step 1. Run the App and Get Your Discord Token
1. Download the `discord_notifier.exe` file from the `dist` folder (or the Releases section) and launch it.
2. The app will prompt you to enter your **Discord User Token**. To obtain it:
   * Log into your Discord account via a **web browser**.
   * Open the *Developer Tools* by pressing **F12** (or `Ctrl + Shift + I`).
   * Switch to the **Network** tab.
   * In the filter box (top left), type the word `science`.
   * Refresh the page (press **F5**).
   * You will see several rows named `science`. Click on any of them.
   * In the detailed menu on the right, scroll down to find the **Authorization** header.
   * Copy the long string next to it—this is your personal account token. Paste it into the application window.

### Step 2. Create a Telegram Bot
Next, the app will ask for a Telegram Bot Token:
1. Open Telegram and search for **@BotFather** (the official bot creator).
2. Type the `/newbot` command and follow the simple instructions (choose a display name and a unique username for your bot).
3. Copy the HTTP API token provided by the bot (looks like `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`) and paste it into the application window.

### Step 3. Get Your Telegram ID
Finally, the program will ask for your personal numeric user ID:
1. Search for the **@userinfobot** in Telegram.
2. Send it any message (or just click `/start`).
3. The bot will instantly reply with your numeric **Id**. Copy these numbers and paste them into the program.

🎉 **All set!** Your settings are securely saved into a `config.json` file right next to the executable. The script will now minimize to the system tray and start forwarding your notifications.

---

## ⚠️ DISCLAIMER

> **WARNING!** Discord officially strictly prohibits the use of self-bots (automating personal user accounts). Using this (or any other similar) script violates the Discord Terms of Service and **can lead to your account being permanently banned!**
> 
> **Recommendation:** Run this script only on the device where you normally use Discord. Avoid running it on multiple computers simultaneously to minimize detection risks by Discord's automated anti-bot algorithms. Use this software at your own risk.
