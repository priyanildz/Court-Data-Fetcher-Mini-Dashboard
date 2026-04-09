import asyncio
from playwright.async_api import async_playwright, TimeoutError
import re
import os
from datetime import datetime
from urllib.parse import urljoin  # <--- ADD THIS IMPORT

# Base URL for Delhi High Court Case Status
BASE_URL = "https://delhihighcourt.nic.in/app/get-case-type-status"


async def fetch_case_details_async(case_type, case_number, filing_year):
    raw_html_response = None
    case_data = {
        "parties": None,
        "filingDate": None,
        "nextHearingDate": None,
        "orders": [],
    }
    error_message = None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                executable_path="/opt/render/.cache/ms-playwright/chromium-1181/chrome-linux/chrome",
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--single-process",
                ],
            )
            page = await browser.new_page()

            page.on(
                "console",
                lambda msg: print(f"Browser Console [{msg.type}]: {msg.text}"),
            )
            page.on("pageerror", lambda err: print(f"Browser Page Error: {err}"))

            print(f"Navigating to {BASE_URL}...")
            await page.goto(BASE_URL, wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)

            # --- Automated CAPTCHA Handling ---
            captcha_code_span = page.locator("span#captcha-code")
            captcha_input_field = page.locator("input#captchaInput")

            try:
                await captcha_code_span.wait_for(state="visible", timeout=15000)
                await captcha_input_field.wait_for(state="visible", timeout=15000)

                captcha_value = await captcha_code_span.text_content()
                print(f"CAPTCHA detected: {captcha_value}. Filling automatically...")

                await page.evaluate(
                    """
                    ([selector, value]) => {
                        const element = document.querySelector(selector);
                        if (element) {
                            element.value = value;
                            element.dispatchEvent(new Event('input', { bubbles: true }));
                            element.dispatchEvent(new Event('change', { bubbles: true }));
                            console.log('JS: CAPTCHA input set to', element.value);
                        } else {
                            console.log('JS: CAPTCHA input element not found for selector', selector);
                        }
                    }
                """,
                    ["input#captchaInput", captcha_value.strip()],
                )
                print("CAPTCHA filled.")
                await asyncio.sleep(0.5)

            except TimeoutError:
                error_message = "CAPTCHA elements not found within timeout. Site structure might have changed or page loaded slow."
                print(error_message)
                return case_data, raw_html_response, error_message
            except Exception as e:
                error_message = f"Error reading/filling CAPTCHA: {e}"
                print(error_message)
                return case_data, raw_html_response, error_message

            # --- Fill in the form fields ---
            print("Attempting to fill form details...")

            # Case Type dropdown - REFINED KEYBOARD INTERACTION
            case_type_selector = "select#case_type"
            await page.wait_for_selector(
                case_type_selector, state="visible", timeout=10000
            )

            available_options = await page.evaluate(
                f"""
                (selector) => Array.from(document.querySelector(selector).options).map(option => ({{ value: option.value, text: option.text }}))
            """,
                case_type_selector,
            )
            print(f"DEBUG: Available Case Type options on page: {available_options}")
            print(
                f"DEBUG: Attempting to select Case Type with value: '{case_type}' (keyboard interaction)"
            )

            try:
                target_index = -1
                for i, option in enumerate(available_options):
                    if option["value"] == case_type.strip():
                        target_index = i
                        break

                if target_index == -1:
                    error_message = f"CRITICAL ERROR: Case Type option with value '{case_type}' not found in available options list for keyboard selection."
                    print(error_message)
                    return case_data, raw_html_response, error_message

                await page.focus(case_type_selector)
                await asyncio.sleep(0.2)

                print(f"DEBUG: Pressing ArrowDown {target_index} time(s)...")
                for _ in range(target_index):
                    await page.keyboard.press("ArrowDown")
                    await asyncio.sleep(0.1)

                print(f"DEBUG: Reached target position. Pressing Enter...")
                await page.keyboard.press("Enter")
                await asyncio.sleep(0.5)

                selected_value_after_attempt = await page.evaluate(
                    f"document.querySelector('{case_type_selector}').value"
                )
                if selected_value_after_attempt == case_type.strip():
                    print(
                        f"SUCCESS: Case Type confirmed as '{selected_value_after_attempt}' via keyboard interaction."
                    )
                else:
                    error_message = f"CRITICAL WARNING: Case Type selection failed even with keyboard interaction. Expected '{case_type.strip()}', but actual selected value is '{selected_value_after_attempt}'."
                    print(error_message)
                    return case_data, raw_html_response, error_message

            except Exception as e:
                error_message = f"Unhandled error during Case Type keyboard selection: {e}. Target value: '{case_type}'"
                print(error_message)
                return case_data, raw_html_response, error_message

            # Case Number input
            case_number_selector = "input#case_number"
            await page.wait_for_selector(
                case_number_selector, state="visible", timeout=10000
            )

            await page.focus(case_number_selector)
            await asyncio.sleep(0.1)
            await page.type(case_number_selector, case_number, delay=50)

            filled_case_number = await page.evaluate(
                f"document.querySelector('{case_number_selector}').value"
            )
            if filled_case_number == case_number:
                print(f"SUCCESS: Case Number confirmed as '{filled_case_number}'")
            else:
                error_message = f"WARNING: Case Number filling failed. Expected '{case_number}', but actual value is '{filled_case_number}'."
                print(error_message)
            await asyncio.sleep(2)

            # Filing Year dropdown
            filing_year_selector = "select#case_year"
            await page.wait_for_selector(
                filing_year_selector, state="visible", timeout=10000
            )

            print(
                f"DEBUG: Attempting to select Filing Year with value: '{str(filing_year)}'"
            )
            try:
                await page.select_option(filing_year_selector, value=str(filing_year))
                print(f"Filing Year (Playwright native) attempted: {filing_year}")
                await asyncio.sleep(0.1)

                selected_year_after_attempt = await page.evaluate(
                    f"document.querySelector('{filing_year_selector}').value"
                )
                if selected_year_after_attempt == str(filing_year):
                    print(
                        f"SUCCESS: Filing Year confirmed as '{selected_year_after_attempt}'"
                    )
                else:
                    error_message = f"WARNING: Filing Year selection failed. Expected '{filing_year}', but actual selected value is '{selected_year_after_attempt}'."
                    print(error_message)

            except Exception as e:
                error_message = f"Error during Filing Year selection: {e}. Ensure the value '{filing_year}' is an exact match for an option's 'value' attribute."
                print(error_message)
                return case_data, raw_html_response, error_message
            await asyncio.sleep(0.5)

            # Click the submit button
            print("Clicking search button...")
            submit_button_locator = page.locator("button#search.btn")
            await submit_button_locator.wait_for(state="visible", timeout=10000)

            try:
                await submit_button_locator.click()
                await asyncio.sleep(2)
                print("Waiting for results table or error message...")

                results_row_selector = 'div.tab-pane.container.active tr:has(a[href*="case-type-status-details"])'

                try:
                    await page.wait_for_selector(results_row_selector, timeout=30000)
                    print("Results container found.")
                except TimeoutError:
                    no_results_selector = (
                        'div.tab-pane.container.active p:has-text("No records found")'
                    )
                    try:
                        await page.wait_for_selector(no_results_selector, timeout=5000)
                        error_message = "No case found with the provided details."
                        print(error_message)
                        return case_data, raw_html_response, error_message
                    except TimeoutError:
                        error_message = "Search timed out. The website may be slow or the case does not exist."
                        print(error_message)
                        return case_data, raw_html_response, error_message

                await page.wait_for_load_state("networkidle")
                print(
                    f"Navigated to results or results loaded on page. Current URL: {page.url}"
                )

            except Exception as e:
                error_message = f"Error submitting form or waiting for results: {e}. Current URL: {page.url}"
                print(error_message)
                return case_data, raw_html_response, error_message

            # Get the raw HTML response
            raw_html_response = await page.content()

            # --- FINAL PARSING LOGIC ---
            print("Parsing scraped data...")
            try:
                result_row = page.locator(
                    'div.tab-pane.container.active tr:has(a[href*="case-type-status-details"])'
                ).first
                if await result_row.count() > 0:
                    # Parties are in the 3rd column (0-indexed 2)
                    parties_td = result_row.locator("td").nth(2)
                    parties_html = await parties_td.inner_html()
                    parties_text = (
                        parties_html.replace("<br>", " ").replace("&nbsp;", " ").strip()
                    )
                    parties_names = [
                        p.strip()
                        for p in re.split(
                            r"\s+V\.S\.\s+|\s+V\.S\.\s+",
                            parties_text,
                            flags=re.IGNORECASE,
                        )
                        if p.strip()
                    ]
                    case_data["parties"] = (
                        " vs. ".join(parties_names) if parties_names else "N/A"
                    )

                    # Dates are in the 4th column (0-indexed 3)
                    dates_td = result_row.locator("td").nth(3)
                    dates_text = await dates_td.inner_text()

                    next_date_match = re.search(
                        r"NEXT DATE: (.*?)(?:<br>|\n|$)", dates_text
                    )
                    last_date_match = re.search(
                        r"Last Date: (\d{2}/\d{2}/\d{4})", dates_text
                    )

                    if next_date_match and next_date_match.group(1).strip() != "NA":
                        case_data["nextHearingDate"] = next_date_match.group(1).strip()
                    else:
                        case_data["nextHearingDate"] = "NA"

                    if last_date_match:
                        case_data["filingDate"] = last_date_match.group(1).strip()

                    # For orders, we'll just parse the details link for this demo.
                    order_link_locator = result_row.locator(
                        'a[href*="case-type-status-details"]'
                    ).first
                    if await order_link_locator.count() > 0:
                        href = await order_link_locator.get_attribute("href")
                        if href:
                            order_link = urljoin(page.url, href)  # <-- CORRECTED LINE
                            order_desc = await order_link_locator.text_content()
                            case_data["orders"] = [
                                {
                                    "date": case_data["filingDate"],
                                    "description": (
                                        order_desc.strip()
                                        if order_desc.strip()
                                        else "Case Details"
                                    ),
                                    "link": order_link,
                                    "filename": f"order_details_{case_number}.html",
                                }
                            ]
                    else:
                        case_data["orders"] = []

            except Exception as e:
                error_message = f"Error during final parsing: {e}"
                print(error_message)
                return case_data, raw_html_response, error_message

    except Exception as e:
        error_message = f"An unexpected error occurred during scraping: {e}. Current URL: {page.url if 'page' in locals() else 'N/A'}"
        print(error_message)
    finally:
        if "browser" in locals():
            await browser.close()
        print("Browser closed.")
    return case_data, raw_html_response, error_message


def fetch_case_details(case_type, case_number, filing_year):
    """Synchronous wrapper for the async scraping function."""
    return asyncio.run(fetch_case_details_async(case_type, case_number, filing_year))


if __name__ == "__main__":
    print("Testing scraper directly for Delhi High Court (browser will open)...")
    test_case_type = "W.P.(C)"
    test_case_number = "1423"
    test_filing_year = "2023"

    print(f"Attempting to fetch {test_case_type} {test_case_number}/{test_filing_year}")
    details, raw_response, err = fetch_case_details(
        test_case_type, test_case_number, test_filing_year
    )

    if err:
        print(f"\nScraping failed: {err}")
    else:
        print("\n--- Scraped Details ---")
        print(f"Parties: {details['parties']}")
        print(f"Filing Date: {details['filingDate']}")
        print(f"Next Hearing Date: {details['nextHearingDate']}")
        print("Orders:")
        if details["orders"]:
            for order in details["orders"]:
                print(
                    f"  - {order['date']}: {order['description']} ({order['link']}) ({order['filename']})"
                )
        else:
            print("  No orders found.")
        print("\n--- Raw HTML (first 500 chars) ---")
        print(raw_response[:500] if raw_response else "No raw response.")
