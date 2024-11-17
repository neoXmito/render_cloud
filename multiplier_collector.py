import datetime
import time
import csv
import os
import logging
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, NoSuchWindowException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(filename='aviator_script.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Telegram configuration
telegram_bot_token = "7433576884:AAFvpFgu482Q1XmhatNKMuRCW6YYOQ_L4C4"
telegram_chat_id = "2024606424"

# ChromeDriver setup
chrome_options = Options()
chrome_options.add_argument('--headless')  # Run Chrome in headless mode
chrome_options.add_argument('--no-sandbox')  # Required for Render and other headless environments
chrome_options.add_argument('--disable-dev-shm-usage')  # Fixes some issues in headless mode

# Set WebDriver path (adjust this as per Render's file system or use a more dynamic path)
webdriver_path = "/usr/local/bin/chromedriver"  # This is an example for Render
os.environ["PATH"] += os.pathsep + webdriver_path

bwalya = '975779902'
bwalya_pw = 'chalison'
phone_number = bwalya
password = bwalya_pw

# Initialize WebDriver
driver = None
hourly_multipliers = []

# Function to initialize WebDriver
def initialize_driver():
    global driver
    driver = webdriver.Chrome(options=chrome_options)
    send_telegram_message("driver has been initialised")

# Function to send Telegram message
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    data = {"chat_id": telegram_chat_id, "text": message}
    response = requests.post(url, data=data)
    if response.status_code != 200:
        logging.error(f"Failed to send Telegram message: {response.text}")

# Function to log error and notify
def handle_error(message, exc_info=True):
    logging.error(message, exc_info=exc_info)
    send_telegram_message(message)
    if "Browser window closed unexpectedly." in message:
        save_multipliers_on_close(hourly_multipliers)

# Function to save multiplier data to CSV file
def save_multipliers_on_close(hourly_multipliers):
    try:
        current_time = datetime.datetime.now()
        minute_of_close = current_time.minute
        start_hour = current_time.hour
        end_hour = start_hour
        filename = f"{start_hour}-{end_hour}_{minute_of_close}.csv"
        
        # Define CSV file path for Render environment (adjust path)
        csv_folder = os.path.join('/mnt/data', 'aviator_data', current_time.strftime("%Y"), current_time.strftime("%m"), current_time.strftime("%d"))
        os.makedirs(csv_folder, exist_ok=True)
        file_path = os.path.join(csv_folder, filename)
        
        # Write data to CSV file
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Multiplier'])  # Write header
            for multiplier in hourly_multipliers:
                writer.writerow([multiplier])
        
        logging.info(f"Multipliers saved to CSV file: {file_path}")
        send_telegram_message(f"Multipliers for {current_time.strftime('%Y-%m-%d %H:%M')} saved to CSV file.")
    
    except Exception as e:
        logging.error(f"Error saving multipliers to CSV file: {e}", exc_info=True)
        send_telegram_message(f"Error saving multipliers to CSV file: {e}")

# Login function with error handling
def login(driver):
    try:
        driver.get("https://www.betpawa.co.zm/login")
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'login-form-phoneNumber'))).send_keys(phone_number)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'login-form-password-input'))).send_keys(password)
        time.sleep(2)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test-id="logInButton"]'))).click()
        time.sleep(2)
        send_telegram_message("successfully logged in ")
    except Exception as e:
        handle_error(f"Error during login: {e}")
        return_to_home_page()


def navigate_to_aviator(driver):
    try:
        # Open the specified URL first
        driver.get("https://www.betpawa.co.zm/casino?filter=all")

        # Wait for the Aviator icon to be clickable and click it
        aviator_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='card-item-text' and contains(text(), 'Aviator')]"))
        )
        aviator_link.click()
        send_telegram_message("successfully navigated to aviator")

    except Exception as e:
        handle_error(f"Error navigating to Aviator: {e}")
        # Handle error, possibly return to home page or retry

# Function to return to home page of BetPawa
def return_to_home_page():
    try:
        driver.get("https://www.betpawa.co.zm/")
    except WebDriverException as e:
        handle_error(f"WebDriverException occurred: {e}")
    except Exception as e:
        handle_error(f"Error returning to home page: {e}")

# Function to check if the browser window is closed
def is_browser_closed():
    try:
        driver.find_element(By.TAG_NAME, 'html')
        return False
    except NoSuchElementException:
        return True
    except NoSuchWindowException:
        return True

# Main execution with error handling and graceful exit
def main():
    global driver, hourly_multipliers
    try:
        initialize_driver()
        
        login(driver)
        navigate_to_aviator(driver)
        
        start_hour = datetime.datetime.now().hour
        start_hour2=start_hour
        while True:
            try:
                first_multiplier_div = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.payouts-block app-bubble-multiplier.payout:first-child div.bubble-multiplier'))
                )
                current_value = float(first_multiplier_div.text.strip()[:-1])
                msg=str(current_value)
                send_telegram_message(msg)
                if len(hourly_multipliers) == 0:
                    hourly_multipliers.append(current_value)
                    print(f"New multiplier detected: {current_value}")
                elif current_value != hourly_multipliers[-1]:
                    hourly_multipliers.append(current_value)
                    print(f"New multiplier detected: {current_value}")
                
                # Check if current time has passed the end hour
                current_time = datetime.datetime.now()
                if current_time.hour != start_hour2:
                    end_hour = current_time.hour
                    if hourly_multipliers:
                        print(hourly_multipliers)
                        save_multipliers_on_close(hourly_multipliers)
                        hourly_multipliers = []  # Clear multipliers for the next cycle
                    start_hour2 = end_hour
                
                time.sleep(2)
            
            except TimeoutException:
                handle_error("TimeoutException occurred, returning to home page then refreshing page.")
                return_to_home_page()
                navigate_to_aviator(driver)
            except NoSuchElementException as e:
                handle_error(f"NoSuchElementException occurred: {e}")
                return_to_home_page()
                navigate_to_aviator(driver)
            except WebDriverException as e:
                handle_error(f"WebDriverException occurred: {e}")
                return_to_home_page()
                navigate_to_aviator(driver)
            except Exception as e:
                handle_error(f"Unexpected error occurred: {e}")
                return_to_home_page()
                navigate_to_aviator(driver)
            
            # Check if browser window is closed
            if is_browser_closed():
                handle_error("Browser window closed unexpectedly.")
                break
        
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
    except Exception as e:
        handle_error(f"Main script error: {e}")
    finally:
        if driver:
            driver.quit()
            send_telegram_message("The Aviator script has stopped.")
            print("Script exited gracefully.")

if __name__ == "__main__":
    main()
