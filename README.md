# Automated E-Commerce Purchase Bot 🚀

This project is an automation tool built in Python that uses Selenium WebDriver to simulate purchasing and checkout processes on an e-commerce platform. The primary goal is to streamline the online transaction process by automating tasks such as logging in, handling popups, adding products to the cart, and completing the checkout procedure.

## ✨ Features

- **🔐 Automated Login:** Automatically logs into the target website by securely retrieving credentials from environment variables.
- **👻 Dynamic Popup Handling:** Detects and closes random popups that may interfere with the user flow, ensuring smooth navigation.
- **🛒 Product Selection & Cart Management:** Navigates to a specified product page, selects shipping options, and adds the product to the shopping cart.
- **💳 Checkout Automation:** Automates the checkout process by inputting necessary details (e.g., CSV code) and placing the order, with post-purchase confirmation through screenshots.
- **🛠️ Robust Error Handling:** Implements comprehensive error handling and logging throughout the workflow to assist with debugging and ensure graceful recovery from unexpected issues.
- **🌐 Proxy Support:** Includes functionality to load, validate, and manage proxies to help enhance anonymity or bypass network restrictions (proxy integration is available but optional).

## ⚙️ Prerequisites

- Python 3.7 or higher
- Google Chrome browser installed
- ChromeDriver compatible with your installed Chrome version
- A virtual environment (recommended)

## 📦 Installation

1. **Clone the repository:**

  git clone https://github.com/yourusername/automated-ecommerce-purchase-bot.git
  cd automated-ecommerce-purchase-bot

2. **Set up a virtual environment and install dependencies:**
  
  python -m venv venv
  source venv/bin/activate   # On Windows use: venv\Scripts\activate
  pip install -r requirements.txt

3. **Configure Environment Variables:**

  Create a .env file in the root directory with the following keys:
  BASE_URL=<target website base URL>
  PRODUCT_URL=<product URL>
  CHECKOUT_URL=<checkout URL>
  EMAIL=<your email address>
  PASSWORD=<your password>
  CSV_NUMBER=<your CSV/security code>
  LOG_FILE_PATH=<path to your log file>
  PROXY_FILE_PATH=<path to your proxy list file>
  SCREENSHOT_PATH=<path to save screenshots>

  ## 🚀 **Usage**

    Run the main script to execute the automation process:
    python main.py
    The script will automatically log in, handle popups, add a product to the cart, and proceed to checkout.

 ## 🗂️ **Project Structure**
  
  main.py: Entry point for the application, orchestrating the overall automation workflow.

  helpers: Functions for element interactions, cookie management, logging, and proxy handling.

  .env: Environment file for sensitive configuration variables (should not be committed to version control).

  requirements.txt: Python dependencies required to run the project.

## 🤝 **Contributing**

  Contributions are welcome! Please open an issue or submit a pull request with your suggestions, improvements, or bug fixes.

## ⚠️**Disclaimer**
This tool is intended for educational and testing purposes only. Ensure you have proper authorization before automating interactions with any website, and use it responsibly in compliance with the target website’s terms of service.    

    
