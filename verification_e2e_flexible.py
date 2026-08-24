import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Navigate to monitoring UI
        await page.goto("http://localhost:8000")

        # Set API Key in input and click Connect
        await page.fill("#apiKey", "testkey")
        await page.click("#connectBtn")
        await page.wait_for_timeout(1000)

        # Enter arbitrary flexible requirement in executive chat and send
        flexible_req = "Deploy a Kubernetes microservice cluster on AWS with automated CI/CD pipeline and Prometheus monitoring"
        await page.fill("#chatInput", flexible_req)
        await page.click("#sendChatBtn")
        await page.wait_for_timeout(1500)

        # Click Approve & Initiate Engineering Execution
        await page.click("#approveExecutionBtn")
        await page.wait_for_timeout(2000)

        # Full page screenshot proving execution launched with flexible objective
        await page.screenshot(path="/home/jules/verification/screenshots/flexible_requirement_execution.png", full_page=True)
        print("Playwright E2E verification completed successfully!")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
