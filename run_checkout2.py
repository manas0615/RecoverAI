from playwright.sync_api import sync_playwright
import time
import os

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(f"file:///{os.path.abspath('fake_merchant.html')}")
    page.click("#rzp-button1")
    
    time.sleep(3)
    frame_element = page.locator("iframe.razorpay-checkout-frame")
    frame = frame_element.content_frame
    if frame:
        print("Found frame!")
        # Let's dump the text content of the frame to see what it has
        print("Frame text:", frame.inner_text("body")[:500])
        # Usually test mode checkout has "Netbanking" -> "SBI"
        try:
            frame.click("text=Netbanking", timeout=5000)
            time.sleep(1)
            frame.click("text=SBI")
            time.sleep(1)
            frame.click("button:has-text('Pay')")
            time.sleep(5)
            # The simulator pops up, maybe in the same page or new tab?
            for p in page.context.pages:
                print("Page URL:", p.url)
                if "simulator" in p.url.lower() or "bank" in p.url.lower() or "test" in p.url.lower():
                    print("Found simulator popup:", p.url)
                    p.click("button:has-text('Failure')")
                    time.sleep(2)
        except Exception as e:
            print("Error clicking:", e)
    else:
        print("Frame not found!")
    
    browser.close()
