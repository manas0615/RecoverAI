from playwright.sync_api import sync_playwright
import time
import os

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(f"file:///{os.path.abspath('fake_merchant.html')}")
    page.click("#rzp-button1")
    
    time.sleep(3)
    frame = page.locator("iframe.razorpay-checkout-frame")
    
    try:
        # Wait for iframe to load content
        time.sleep(2)
        # Click the "Netbanking" option
        # In new Razorpay checkout, it's a list of methods
        frame.locator("text=Netbanking").click()
        time.sleep(1)
        # Click SBI
        frame.locator("text=SBI").click()
        time.sleep(1)
        # Click Pay Now
        frame.locator("button:has-text('Pay Now')").click()
        time.sleep(5)
        
        # Now find the simulator page
        simulator_page = None
        for p in page.context.pages:
            if "simulator" in p.url.lower() or "bank" in p.url.lower():
                simulator_page = p
                break
                
        if simulator_page:
            print("Found simulator! URL:", simulator_page.url)
            simulator_page.locator("button:has-text('Failure')").click()
            print("Clicked Failure!")
            time.sleep(5)
        else:
            print("Simulator not found. Pages:", [p.url for p in page.context.pages])
            
    except Exception as e:
        print("Error:", e)
        
    browser.close()
