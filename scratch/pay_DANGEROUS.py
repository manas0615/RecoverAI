from playwright.sync_api import sync_playwright
import time


def pay_razorpay_link(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        print("Navigated to Razorpay link")

        # Wait for the email/phone form
        page.wait_for_selector("input[id='contact']")
        page.fill("input[id='contact']", "9999999999")

        if page.locator("input[id='email']").is_visible():
            page.fill("input[id='email']", "test@example.com")

        page.click("button:has-text('Proceed')")
        print("Clicked Proceed")

        time.sleep(3)

        # Choose Netbanking
        page.wait_for_selector("text='Netbanking'")
        page.click("text='Netbanking'")
        print("Selected Netbanking")

        time.sleep(1)
        # Select first bank (usually has a Success/Failure option in Test mode)
        page.click(".bank-list-item:nth-child(1)")

        time.sleep(2)
        # Pay button
        page.click("button:has-text('Pay Now')")
        print("Clicked Pay Now")

        time.sleep(3)
        # Handle the mock bank page popup
        # This opens in a new tab in Razorpay, but Playwright handles popups differently.
        # Let's see if we can get the new page
        print("Finished.")
        browser.close()


if __name__ == "__main__":
    pay_razorpay_link("https://rzp.io/rzp/z2J8rYyr")
