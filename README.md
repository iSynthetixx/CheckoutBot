Automated E-Commerce Purchase Bot
This project is an automation tool built in Python that uses Selenium WebDriver to simulate purchasing and checkout processes on an e-commerce platform. The primary goal is to streamline the online transaction process by automating tasks such as logging in, handling popups, adding products to the cart, and completing the checkout procedure.

Features
Automated Login:
Automatically logs into the target website by securely retrieving credentials from environment variables.

Dynamic Popup Handling:
Detects and closes random popups that may interfere with the user flow, ensuring smooth navigation.

Product Selection and Cart Management:
Navigates to a specified product page, selects shipping options, and adds the product to the shopping cart.

Checkout Automation:
Automates the checkout process by inputting necessary details (e.g., CSV code) and placing the order, with post-purchase confirmation through screenshots.

Robust Error Handling:
Implements comprehensive error handling and logging throughout the workflow to assist with debugging and ensure the process can recover gracefully from unexpected issues.

Proxy Support:
Includes functionality to load, validate, and manage proxies to help enhance anonymity or bypass network restrictions (proxy integration is available but optional).

Prerequisites
Python 3.7 or higher

Google Chrome browser installed

ChromeDriver compatible with your installed Chrome version

A virtual environment (recommended)
