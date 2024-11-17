import time
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from telegram import Bot
from telegram.error import TelegramError

# Telegram Bot Setup
TELEGRAM_TOKEN = '7433576884:AAFvpFgu482Q1XmhatNKMuRCW6YYOQ_L4C4'  # Replace with your bot token
CHAT_ID = '2024606424'  # Replace with your chat ID
bot = Bot(token=TELEGRAM_TOKEN)

# Function to send messages via Telegram bot (asynchronous)
async def send_telegram_message(message):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except TelegramError as e:
        print(f"Error sending message: {e}")

# Headless Chrome setup
chrome_options = Options()
chrome_options.add_argument('--headless')  # Run Chrome in headless mode
chrome_options.add_argument('--no-sandbox')  # Required for environments like Render
chrome_options.add_argument('--disable-dev-shm-usage')  # Fixes some issues in headless mode
chrome_options.add_argument('--remote-debugging-port=9222')  # Optional: Enable remote debugging if needed

# Create WebDriver instance
driver = webdriver.Chrome(options=chrome_options)

# Start the script
async def main():
    await send_telegram_message("Script has started!")

    try:
        # Access the website betpawa.co.zm
        driver.get("https://betpawa.co.zm")
        time.sleep(3)  # Wait for the page to load

        # Notify that the website has been accessed
        await send_telegram_message("Successfully accessed the website betpawa.co.zm!")

    except Exception as e:
        await send_telegram_message(f"Error occurred: {e}")

    finally:
        # Close the WebDriver after completing the task
        driver.quit()

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
