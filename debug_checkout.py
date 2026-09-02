from playwright.sync_api import sync_playwright
import time
import os

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(f"file:///{os.path.abspath('fake_merchant.html')}")
    page.click("#rzp-button1")
    
    time.sleep(3)
    page.screenshot(path="checkout.png")
    
    with open("checkout.html", "w", encoding="utf-8") as f:
        f.write(page.content())
    
    browser.close()
