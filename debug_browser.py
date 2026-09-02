from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto("http://localhost:5173")
        page.wait_for_selector("text=RecoverAI")
        page.click("text=Approvals")
        page.wait_for_timeout(2000)
        
        rows = page.locator("tr").all_inner_texts()
        print("Approvals Rows:")
        for r in rows:
            print(r)
            
        page.screenshot(path="approvals.png")
        
        browser.close()

if __name__ == "__main__":
    run()
