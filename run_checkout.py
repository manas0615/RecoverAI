from playwright.sync_api import sync_playwright
import time
import os

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(f"file:///{os.path.abspath('fake_merchant.html')}")
    page.click("#rzp-button1")
    
    # Wait for Razorpay iframe
    time.sleep(3)
    frame = page.frame(name="razorpay-checkout")
    if frame:
        print("Found frame!")
        # Netbanking -> SBI -> Fail
        # In the new razorpay test mode, we can select "Netbanking", then "SBI", then click "Pay", then select "Failure"
        frame.click("text=Netbanking")
        time.sleep(1)
        frame.click("text=SBI")
        time.sleep(1)
        frame.click("button:has-text('Pay')")
        time.sleep(3)
        # It opens a simulator popup! Wait, popups in playwright?
        print("Payment triggered!")
    else:
        print("Frame not found!")
    
    time.sleep(5) # give time to complete
    
    # Let's see if there are any popups
    for p in page.context.pages:
        if "simulator" in p.url.lower() or "bank" in p.url.lower():
            print("Found simulator popup:", p.url)
            p.click("text=Failure")
            time.sleep(2)
            
    browser.close()
