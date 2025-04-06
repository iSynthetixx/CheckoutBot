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

# Environment variables
BASE_URL = os.getenv("BASE_URL")
LOGIN_URL = os.getenv("LOGIN_URL")
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
    "ship_to_me": (By.XPATH, "//button[contains(., 'To Me or My Store')]"),
    "add_to_cart": (By.CSS_SELECTOR, 'button.add-to-cart-button.button.full-width'),
    "checkout": (By.CSS_SELECTOR, 'button.button.cart-link'),
    "place_order": (By.CSS_SELECTOR, '[aria-label="Place order"]'),
    "cart_count": (By.CSS_SELECTOR, 'div.miniCart-numberOfItems'),
    # Added login modal selector
    "login_modal": (By.CSS_SELECTOR, 'div.modal-content[aria-labelledby="Account Login"]')
}


def initialize_logging():
    """Configures logging."""
    try:
        os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    except Exception as e:
        print(f"Error creating log directory: {e}")
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
    try:
        with open(file_path, 'r') as f:
            proxies = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        logging.error(f"Proxy file {file_path} not found.")
        return []

    for proxy in proxies:
        try:
            response = requests.get('https://httpbin.org/ip', proxies={"http": proxy, "https": proxy}, timeout=10)
            if response.status_code == 200:
                valid_proxies.append(proxy)
            else:
                logging.warning(f"Proxy {proxy} failed with status code {response.status_code}")
        except requests.RequestException as e:
            logging.error(f"Error with proxy {proxy}: {e}")

    try:
        with open(file_path, 'w') as f:
            for proxy in valid_proxies:
                f.write(f"{proxy}\n")
    except Exception as e:
        logging.error(f"Error writing to proxy file: {e}")

    logging.info(f"Proxy file updated. {len(valid_proxies)} valid proxies remaining.")
    return valid_proxies


def element_click(driver, selector, timeout=10):
    """Waits for an element's presence and clicks it.
       Falls back to a JavaScript click if the standard click fails.
    """
    try:
        # Wait for the element to be present in the DOM
        element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located(selector))
        element.click()
        logging.info(f"{selector} button pressed successfully.")
        return True
    except Exception as e:
        logging.error(f"Standard click failed for {selector}: {e}. Trying JavaScript click...")
        try:
            element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located(selector))
            driver.execute_script("arguments[0].click();", element)
            logging.info(f"{selector} button pressed using JAVASCRIPT successfully.")
            return True
        except Exception as e_js:
            logging.error(f"JavaScript click also failed for {selector}: {e_js}")
            return False


def element_input(driver, selector, value, timeout=10):
    """Waits for an input field to be visible, scrolls it into view, clears it, and enters text."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(selector)
        )
        # Scroll the element into view
        # driver.execute_script("arguments[0].scrollIntoView(true);", element)
        element.clear()
        element.send_keys(value)
        return True
    except Exception as e:
        logging.error(f"Failed to input text in {selector}: {e}")
        return False


def check_and_verify_cart_count(driver, max_items=2, timeout=10):
    """
    Waits for the cart count element to be visible, retrieves and verifies that the number
    of items is a valid integer within the expected range (1 to max_items).
    Returns True if the cart count is valid; otherwise logs an error and returns False.
    """
    try:
        cart_item_count_element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(selectors["cart_count"])
        )
        item_count_str = cart_item_count_element.text.strip()
        if item_count_str.isdigit():
            item_count_int = int(item_count_str)
            if 0 < item_count_int <= max_items:
                logging.info(f"Current number of items in the cart: {item_count_int}.")
                return True
            else:
                logging.error(f"Item count {item_count_int} is not in the expected range (1 to {max_items}).")
                return False
        else:
            logging.error("Invalid cart item count value.")
            return False
    except Exception as e:
        logging.exception("Exception during cart count verification: %s", e)
        return False


def login_site(driver):
    """Handles the login and initial navigation steps."""
    try:
        # Age verification
        if not element_click(driver, selectors["age_verification"]):
            logging.error("Age verification failed.")
            return False

        # Open login modal
        if not element_click(driver, selectors["login_button"]):
            logging.error("Login button click failed.")
            return False

        # Input email and password
        if not element_input(driver, (By.ID, "authentication_header_login_form_email"), EMAIL):
            logging.error("Email input failed.")
            return False
        if not element_input(driver, (By.ID, "authentication_header_login_form_password"), PASSWORD):
            logging.error("Password input failed.")
            return False

        # Submit login
        if not element_click(driver, selectors["account_login"]):
            logging.error("Login submission failed.")
            return False

        # Wait until the login dialog disappears to ensure authentication is complete
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located(selectors["login_modal"]))

        # Wait for the account popover element to be visible as a verification step
        account_popover_selector = (By.ID, "account-popover-open")
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(account_popover_selector))

        logging.info("Login successful.")
        return True
    except Exception as e:
        logging.exception("Exception during login: %s", e)
        return False


def is_shipping_available(driver, timeout=10):
    """
    Checks the availability-info element to determine if the item is available for shipping.
    Returns True if available, False if out of stock.
    """
    try:
        availability_info = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.availability-info"))
        )
        availability_text = availability_info.text.strip().lower()
        logging.info(f"Availability text: {availability_text}")
        if "out of stock" in availability_text or "unavailable for shipping" in availability_text:
            logging.info("Item is not available for shipping (Out of Stock).")
            return False
        else:
            logging.info("Item is available for shipping.")
            return True
    except Exception as e:
        logging.error(f"Error checking shipping availability: {e}")
        return False


def add_to_cart(driver):
    """Navigates to the product page and adds the product to the cart.
       Handles cases where clicking the availability/ship-to-me buttons is required,
       as well as when the item can be added directly.
    """
    try:
        # Hard-coded product id for test purposes
        # test_product = "000006283"
        test_product = "000096059"
        product_url = PRODUCT_URL + test_product
        driver.get(product_url)
        time.sleep(5)

        # Check shipping availability before proceeding
        if not is_shipping_available(driver):
            logging.error("Item is not available for shipping.")
            return False

        # Close email popup if it exists
        element_click(driver, selectors["email_popup_close"])
        time.sleep(3)

        # Attempt to click the availability button if it exists.
        # If the availability button isn't found or interactable, proceed directly.
        if element_click(driver, selectors["availability"]):
            logging.info("Clicked availability button.")
            # Attempt to click the "ship to me" option.
            if element_click(driver, selectors["ship_to_me"]):
                logging.info("Clicked ship-to-me option.")
            else:
                logging.warning("Ship-to-me option not clickable or not required; proceeding.")
        else:
            logging.info("Availability button not present or not required; proceeding directly.")

        # Click the add-to-cart button
        if not element_click(driver, selectors["add_to_cart"]):
            logging.error("Add to cart action failed.")
            return False

        # Verify cart item count using the combined check
        if check_and_verify_cart_count(driver):
            return True
        else:
            logging.error("Failed to verify cart item count.")
            return False

    except Exception as e:
        logging.exception("Exception during add to cart: %s", e)
        return False


def proceed_to_checkout(driver):
    """Handles the checkout process."""
    try:
        driver.get(CHECKOUT_URL)
        # time.sleep(7)

        if not element_input(driver, (By.ID, "csv-code"), CSV_NUMBER):
            logging.error("Failed to input CSV number.")
            return False

        if not element_click(driver, selectors["place_order"]):
            logging.error("Failed to click on 'Place order'.")
            return False

        try:
            driver.save_screenshot(SCREENSHOT_PATH)
            logging.info(f"Screenshot taken and saved to {SCREENSHOT_PATH}")
        except Exception as e:
            logging.error(f"Failed to save screenshot: {e}")

        logging.info("Checkout process completed successfully.")
        return True
    except Exception as e:
        logging.exception("Exception during checkout: %s", e)
        return False


def main():
    """Main function to automate the purchase process."""
    start_time = time.time()
    initialize_logging()
    driver = None
    try:
        options = Options()
        options.page_load_strategy = 'normal'
        # Uncomment and set proxy if needed:
        # options.add_argument('--proxy-server=%s' % PROXY)
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()

        driver.get(BASE_URL)
        # time.sleep(3)

        if not login_site(driver):
            logging.error("Login process failed. Exiting.")
            return

        if not add_to_cart(driver):
            logging.error("Add to cart process failed. Exiting.")
            return

        if not proceed_to_checkout(driver):
            logging.error("Checkout process failed. Exiting.")
            return

    except Exception as e:
        logging.exception("An unexpected error occurred: %s", e)
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logging.error(f"Error while quitting the driver: {e}")
        elapsed_time = time.time() - start_time
        logging.info(f"Execution completed in {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    main()
