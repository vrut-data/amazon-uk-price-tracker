"""
============================================================
  Amazon UK Price Tracker
  Author  : Vrutant Vaghela
  Course  : MSc Data Science — University of East London
  Tools   : curl_cffi, BeautifulSoup, pandas, smtplib
============================================================
  HOW TO RUN:
    1. pip install curl_cffi beautifulsoup4 pandas
    2. Set your URL and settings in the CONFIG section below
    3. python amazon_price_tracker.py
============================================================
"""

# ──────────────────────────────────────────────
# IMPORTS
# ──────────────────────────────────────────────
from curl_cffi import requests as cf_requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import datetime
import time
import os
import smtplib


# ──────────────────────────────────────────────
# CONFIG — Change only this section
# ──────────────────────────────────────────────
URL = 'https://www.amazon.co.uk/Data-Scientist-Science-Tshirt-Definition/dp/B0B1XYS794'

CHECK_INTERVAL  = 10     # seconds between each price check
MAX_ROWS        = 100    # stop tracker after this many CSV rows
PRICE_THRESHOLD = 14.99  # send email alert if price drops below this (£)

# Email alert (optional) — set ENABLE_EMAIL_ALERT = True to activate
ENABLE_EMAIL_ALERT = False
YOUR_EMAIL   = 'youremail@gmail.com'
APP_PASSWORD = 'your_gmail_app_password'   # Gmail App Password (not your real password)

# CSV saved to Desktop automatically — avoids PermissionError
DESKTOP  = os.path.join(os.path.expanduser('~'), 'Desktop')
CSV_FILE = os.path.join(DESKTOP, 'amazon_price_log.csv')

# HTTP headers — mimics real Chrome browser
HEADERS = {
    'User-Agent'     : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'en-GB,en;q=0.9',
    'Accept'         : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Referer'        : 'https://www.google.com/',
}

# CSS selector for price — auto-fallback list used if this misses
PRICE_SELECTOR = '.a-price .a-offscreen'


# ──────────────────────────────────────────────
# SESSION SETUP
# ──────────────────────────────────────────────
def create_session():
    """Create a new curl_cffi session that impersonates Chrome 124."""
    return cf_requests.Session(impersonate='chrome124')


session = create_session()


# ──────────────────────────────────────────────
# FETCH PAGE
# ──────────────────────────────────────────────
class FetchResult:
    """Dummy response object returned when all retries fail."""
    def __init__(self):
        self.status_code = 0
        self.text = ''


def get_page(url, retries=3, timeout=25):
    """
    Fetch a page with retry logic.
    - Retries up to 3 times on connection errors
    - Creates a fresh session on each retry (fixes DNSError / connection reset)
    - Returns FetchResult with status_code=0 if all retries fail
    """
    global session

    for attempt in range(1, retries + 1):
        try:
            response = session.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
            return response
        except Exception as e:
            print(f'  ⚠  Attempt {attempt}/{retries} failed: {type(e).__name__} — reconnecting...')
            session = create_session()
            if attempt < retries:
                time.sleep(3 * attempt)  # exponential backoff: 3s, 6s

    print('  ✗  All retries failed — skipping this check')
    return FetchResult()


# ──────────────────────────────────────────────
# EXTRACT TITLE & PRICE
# ──────────────────────────────────────────────
def extract_product_data(page):
    """
    Parse HTML and extract product title and price.
    Tries PRICE_SELECTOR first, then falls back through 8 other selectors,
    then does a raw text scan for any £ value as a last resort.
    """
    soup = BeautifulSoup(page.text, 'html.parser')

    # Title
    title_tag = soup.find(id='productTitle')
    title = title_tag.get_text(strip=True) if title_tag else 'Title not found'

    # Price — try selectors in priority order
    price_text = None
    fallback_selectors = [
        PRICE_SELECTOR,
        '#priceblock_ourprice',
        '#priceblock_dealprice',
        '#corePrice_feature_div .a-offscreen',
        '#corePriceDisplay_desktop_feature_div .a-offscreen',
        '#price_inside_buybox',
        '.a-color-price',
        '.a-price-whole',
        '#newBuyBoxPrice',
    ]

    for selector in fallback_selectors:
        tag = soup.select_one(selector)
        if tag:
            price_text = tag.get_text(strip=True)
            break

    # Last resort: scan raw page text for any £ value
    if not price_text:
        candidates = [
            t.strip() for t in soup.find_all(string=True)
            if '£' in t and len(t.strip()) < 15
        ]
        if candidates:
            price_text = candidates[0]

    # Clean price string → float
    try:
        price = float(price_text.replace('£', '').replace(',', '').strip())
    except Exception:
        price = None

    return title, price


# ──────────────────────────────────────────────
# CSV FUNCTIONS
# ──────────────────────────────────────────────
def get_row_count():
    """Return number of data rows already in the CSV (excluding header)."""
    if not os.path.isfile(CSV_FILE):
        return 0
    with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
        return max(0, sum(1 for _ in f) - 1)


def save_to_csv(title, price, date_str, time_str):
    """
    Append one row to CSV.
    - encoding='utf-8-sig' fixes the Â£ display bug in Excel
    - Date and Time saved as separate columns
    - Retries 3 times if file is locked (open in Excel)
    """
    file_exists = os.path.isfile(CSV_FILE)

    for attempt in range(3):
        try:
            with open(CSV_FILE, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['Title', 'Price (£)', 'Date', 'Time'])
                writer.writerow([title, price, date_str, time_str])
            return True
        except PermissionError:
            if attempt < 2:
                print('  ⚠  CSV is open in Excel — close it. Retrying in 2s...')
                time.sleep(2)
            else:
                print('  ✗  CSV save failed — please close the file in Excel!')
                return False


# ──────────────────────────────────────────────
# EMAIL ALERT
# ──────────────────────────────────────────────
def send_email_alert(title, price):
    """Send a Gmail alert when price drops below PRICE_THRESHOLD."""
    if not ENABLE_EMAIL_ALERT:
        return
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(YOUR_EMAIL, APP_PASSWORD)
        subject = f'Price Drop Alert! {title[:50]} is now £{price:.2f}'
        body    = (
            f'Product : {title}\n'
            f'Price   : £{price:.2f}\n'
            f'Link    : {URL}\n\n'
            f'Buy now before the price goes back up!'
        )
        server.sendmail(YOUR_EMAIL, YOUR_EMAIL, f'Subject: {subject}\n\n{body}')
        server.quit()
        print('  ✉  Email alert sent!')
    except Exception as e:
        print(f'  ✗  Email error: {e}')


# ──────────────────────────────────────────────
# SUMMARY REPORT
# ──────────────────────────────────────────────
def print_summary():
    """Read CSV and print a price summary report."""
    if not os.path.isfile(CSV_FILE):
        print('No CSV file found.')
        return

    df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
    df['Price (£)'] = pd.to_numeric(df['Price (£)'], errors='coerce')

    print('\n' + '=' * 50)
    print(f'  PRICE SUMMARY  ({len(df)} records)')
    print('=' * 50)
    print(f'  Highest  : £{df["Price (£)"].max():.2f}')
    print(f'  Lowest   : £{df["Price (£)"].min():.2f}')
    print(f'  Average  : £{df["Price (£)"].mean():.2f}')
    print(f'  From     : {df["Date"].iloc[0]}  {df["Time"].iloc[0]}')
    print(f'  To       : {df["Date"].iloc[-1]}  {df["Time"].iloc[-1]}')
    print('=' * 50)
    print('\nLast 5 records:')
    print(df.tail(5).to_string(index=False))


# ──────────────────────────────────────────────
# MAIN TRACKER LOOP
# ──────────────────────────────────────────────
def run_tracker():
    """Main function — warms up session then runs the price check loop."""

    print('\n' + '=' * 60)
    print('  Amazon UK Price Tracker')
    print('  Author: Vrutant Vaghela | MSc Data Science, UEL')
    print('=' * 60)
    print(f'  Product  : {URL[:70]}...')
    print(f'  Interval : every {CHECK_INTERVAL} seconds')
    print(f'  Max rows : {MAX_ROWS}')
    print(f'  CSV path : {CSV_FILE}')
    print('=' * 60)

    # Warm up session — visit homepage first (human-like behaviour)
    print('\n🌐 Warming up session...')
    try:
        session.get('https://www.amazon.co.uk', headers=HEADERS, timeout=15)
        time.sleep(2)
    except Exception:
        pass

    # Count existing rows
    existing_rows = get_row_count()
    rows_to_add   = MAX_ROWS - existing_rows

    if rows_to_add <= 0:
        print(f'\n⚠  CSV already has {existing_rows} rows (max {MAX_ROWS}).')
        print('   Delete the CSV file on your Desktop to start fresh.')
        return

    print(f'\n🚀 Starting tracker — adding {rows_to_add} more rows (total will be {existing_rows + rows_to_add})')
    print('-' * 60)

    price_history = []

    for check_count in range(1, rows_to_add + 1):
        now      = datetime.datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')

        page = get_page(URL)

        if page.status_code != 200:
            print(f'[{check_count:03d}/{rows_to_add}] {date_str} {time_str} | ✗ HTTP {page.status_code} — skipped')
        else:
            title, price = extract_product_data(page)
            saved = save_to_csv(title, price, date_str, time_str)
            price_history.append(price)

            # Price change indicator
            arrow = ''
            if len(price_history) >= 2:
                p_now, p_prev = price_history[-1], price_history[-2]
                if p_now and p_prev:
                    diff = p_now - p_prev
                    if   diff < 0: arrow = f'  ▼ -£{abs(diff):.2f}'
                    elif diff > 0: arrow = f'  ▲ +£{diff:.2f}'
                    else:          arrow = '  — same'

            price_str   = f'£{price:.2f}' if price else 'N/A'
            save_status = '✓ saved' if saved else '✗ not saved'
            total_rows  = existing_rows + check_count

            print(f'[{check_count:03d}/{rows_to_add}] {date_str} {time_str} | {price_str}{arrow} | {save_status} | row {total_rows}/{MAX_ROWS}')

            # Email alert
            if price and price < PRICE_THRESHOLD:
                print(f'  🔔 ALERT: £{price:.2f} is below threshold £{PRICE_THRESHOLD}')
                send_email_alert(title, price)

        # Sleep between checks (skip on last iteration)
        if check_count < rows_to_add:
            time.sleep(CHECK_INTERVAL)

    print('-' * 60)
    print(f'✅ Done! {MAX_ROWS} rows reached. CSV saved on Desktop.')

    # Print summary at end
    print_summary()


# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────
if __name__ == '__main__':
    run_tracker()
