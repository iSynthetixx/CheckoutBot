import os
from dotenv import load_dotenv
import logging
import colorlog
from logging.handlers import RotatingFileHandler
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
BASE_URL = os.getenv("BASE_URL")
PRODUCT_URL = os.getenv("PRODUCT_URL")
CHECKOUT_URL = os.getenv("CHECKOUT_URL")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
CSV_NUMBER = os.getenv("CSV_NUMBER")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH")
PROXY_FILE_PATH = os.getenv("PROXY_FILE_PATH")
SCREENSHOT_PATH = os.getenv("SCREENSHOT_PATH")

# HTML Element Selectors
selectors = {
    "age_verification": (By.CSS_SELECTOR, 'button[aria-label="Yes, Enter into the site"]'),
    "login_button": (By.CSS_SELECTOR, 'button.modal-header-login.link'),
    "account_login": (By.CSS_SELECTOR, 'button[aria-label="LOGIN"]'),
    "email_popup_close": (By.CSS_SELECTOR, 'a.ltkpopup-close'),
    "availability": (By.XPATH, '//button[text()="Click to see availability."]'),
    "pick_up": (By.XPATH, '//button[p[text()="Pick Up"]]'),
    "ship_to_me": (By.XPATH, '//button[p[text()="To Me or My Store"]]'),
    "add_to_cart": (By.CSS_SELECTOR, 'button.add-to-cart-button.button.full-width'),
    "checkout": (By.CSS_SELECTOR, 'button.button.cart-link'),
    "place_order": (By.CSS_SELECTOR, '[aria-label="Place order"]'),
    "cart_count": (By.CSS_SELECTOR, 'div.miniCart-numberOfItems'),
}


def initialize_logging():
    """Configures logging."""
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    log_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red"
        }
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    file_handler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=10 * 1024 * 1024, backupCount=5)
    file_handler.setFormatter(log_formatter)
    logging.basicConfig(level=logging.INFO, handlers=[console_handler, file_handler])


def handle_proxies(file_path):
    """Handles loading, validating, and saving proxies."""
    valid_proxies = []

    # Load proxies from the file
    try:
        with open(file_path, 'r') as f:
            proxies = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        logging.error(f"Proxy file {file_path} not found.")
        return []

    # Validate each proxy
    for proxy in proxies:
        try:
            response = requests.get('https://httpbin.org/ip', proxies={"http": proxy, "https": proxy}, timeout=10)
            if response.status_code == 200:
                valid_proxies.append(proxy)
            else:
                logging.warning(f"Proxy {proxy} failed with status code {response.status_code}")
        except requests.RequestException as e:
            logging.error(f"Error with proxy {proxy}: {e}")

    # Save only the valid proxies back to the file
    with open(file_path, 'w') as f:
        for proxy in valid_proxies:
            f.write(f"{proxy}\n")

    logging.info(f"Proxy file updated. {len(valid_proxies)} valid proxies remaining.")

    return valid_proxies


def element_click(driver, selector, timeout=10):
    """Waits for an element to be clickable and clicks it."""
    try:
        element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(selector))
        element.click()
        return True
    except Exception as e:
        logging.error(f"Failed to interact with element {selector}: {e}")
        return False


def element_input(driver, selector, value, timeout=10):
    """Waits for an input field and enters text."""
    try:
        element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located(selector))
        element.clear()
        element.send_keys(value)
        return True
    except Exception as e:
        logging.error(f"Failed to input text in {selector}: {e}")
        return False


def check_cart_item_count(driver, max_items):
    """Checks the current cart item count and verifies it is within valid range."""
    try:
        # Find the element by its class name
        cart_item_count_element = driver.find_element(By.CLASS_NAME, "miniCart-numberOfItems")

        # Get the text inside the div
        item_count = cart_item_count_element.text

        # Check if the item count is a valid integer and within the range (0, max_items)
        if item_count.isdigit():
            item_count_int = int(item_count)
            if 0 < item_count_int <= max_items:
                return item_count_int
            else:
                raise ValueError(f"Item count is not in the expected range (1 to {max_items}).")
        else:
            raise ValueError("Invalid item count value.")

    except Exception as e:
        # Log the error and return None or raise error as needed
        logging.error(f"Cart check error: {e}")
        return None


def main():
    """Main function to automate the purchase of liquor."""
    start_time = time.time()
    initialize_logging()

    # Main Code Here:
    options = Options()
    options.page_load_strategy = 'normal'
    # options.add_argument("--headless=new")
    # chrome_options.add_argument('--proxy-server=%s' % PROXY)
    driver = webdriver.Chrome(options=options)
    # driver.maximize_window()

    # Load the website
    driver.get(BASE_URL)
    time.sleep(3)

    # Age verification
    element_click(driver, selectors["age_verification"])

    # Log in to the site
    element_click(driver, selectors["login_button"])
    element_input(driver, (By.ID, "authentication_header_login_form_email"), EMAIL)
    element_input(driver, (By.ID, "authentication_header_login_form_password"), PASSWORD)
    element_click(driver, selectors["account_login"])

    # Go to desired product page
    # Makers Mark Mini test product
    test_product = "000006283"
    driver.get(PRODUCT_URL + test_product)
    time.sleep(5)

    # Close email address pop up box, if it exists
    element_click(driver, selectors["email_popup_close"])
    time.sleep(3)

    # Add to cart
    element_click(driver, selectors["availability"])
    element_click(driver, selectors["ship_to_me"])
    element_click(driver, selectors["add_to_cart"])

    # Could add a verification that item added to cart successfully
    tmp = selectors["cart_count"]

    # Define the maximum allowed items in the cart
    max_items = 2

    # Call the function to check the cart item count with the maximum item count
    item_count = check_cart_item_count(driver, max_items)

    # Check if the value is valid (non-None and within the expected range)
    if item_count is not None:
        logging.info(f"Current number of items in the cart: {item_count}.")
    else:
        logging.warning(f"Error: Unable to retrieve or validate the number of items in the cart.")

    # Checkout
    driver.get(CHECKOUT_URL)
    time.sleep(7)
    element_input(driver, (By.ID, "csv-code"), CSV_NUMBER)
    element_click(driver, selectors["place_order"])

    # Take a Screenshot
    driver.save_screenshot(SCREENSHOT_PATH)
    logging.info(f"Screenshot taken and saved to {SCREENSHOT_PATH}")

    # send telegram message with order confirmation and details
    # add logic to prevent repeat orders

    # Close the driver
    driver.quit()

    # End time tracking and print the execution time
    elapsed_time = time.time() - start_time
    logging.info(f"Execution completed in {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    main()
