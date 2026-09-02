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

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(plink["short_url"])
    time.sleep(5)
    
    frame = page.locator("iframe.razorpay-checkout-frame").content_frame
    
    try:
        # Click Continue if it exists
        continue_btn = frame.locator("button:has-text('Continue')")
        if continue_btn.count() > 0:
            continue_btn.first.click()
            time.sleep(3)
        
        page.screenshot(path="plink_step2.png")
        
        # Click Netbanking
        nb_btn = frame.locator("text=Netbanking")
        if nb_btn.count() > 0:
            nb_btn.first.click()
            time.sleep(2)
            
        page.screenshot(path="plink_step3.png")
            
        # Click SBI
        sbi_btn = frame.locator("text=SBI")
        if sbi_btn.count() > 0:
            sbi_btn.first.click()
            time.sleep(2)
            
        # Click Pay
        pay_btn = frame.locator("button:has-text('Pay')")
        if pay_btn.count() > 0:
            pay_btn.first.click()
            time.sleep(5)
            
        page.screenshot(path="plink_step4.png")
            
        # Handle simulator
        for p in page.context.pages:
            if "simulator" in p.url.lower() or "bank" in p.url.lower():
                p.screenshot(path="plink_simulator.png")
                p.locator("button:has-text('Failure')").click()
                time.sleep(3)
                
    except Exception as e:
        print("Error:", e)
        
    browser.close()
