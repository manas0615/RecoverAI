from playwright.sync_api import sync_playwright
import time
import requests

auth = ("rzp_test_TURMnQDelKdhAj", "OrVS1leayjv74bcG5JzA1lEr")

payload = {
  "amount": 10000,
  "currency": "INR",
  "accept_partial": False,
  "description": "Test Failure",
  "customer": {
    "name": "Test Customer",
    "email": "test@example.com",
    "contact": "+919000090000"
  },
  "notify": {"sms": False, "email": False},
  "reminder_enable": False,
}
resp = requests.post("https://api.razorpay.com/v1/payment_links", json=payload, auth=auth)
plink = resp.json()
print("Created payment link:", plink.get("short_url"))

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(plink["short_url"])
    time.sleep(5)
    
    page.screenshot(path="plink_loaded.png")
    with open("plink_loaded.html", "w", encoding="utf-8") as f:
        f.write(page.content())
    
    browser.close()
