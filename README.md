# 🛒 Amazon UK Price Tracker

A Python automation project that monitors Amazon UK product prices in real time, logs data to CSV, and sends email alerts when prices drop below a set threshold.

Built as part of my learnig and .

---

## 📸 Sample Output

```
Tracker started. It will add 100 rows.
======================================================================
[001/100] 2026-06-10 15:28:05 | £17.49 | saved | row 1/100
[002/100] 2026-06-10 15:28:17 | £17.49 | saved | row 2/100
[003/100] 2026-06-10 15:28:28 | £17.49 | saved | row 3/100
...
[100/100] 2026-06-10 15:47:11 | £17.49 | saved | row 100/100
======================================================================
Done. CSV saved on Desktop.
```

---

## 🔍 What It Does

- Scrapes **product title and price** from any Amazon UK product page
- Checks every **10 seconds** and logs to a structured CSV file
- Separates **Date** and **Time** into individual columns for easy analysis
- Detects **price changes** between checks (up / down / same)
- Sends a **Gmail email alert** when price drops below a custom threshold
- Automatically **stops at 100 rows** — configurable
- Handles **connection resets and DNS errors** with retry logic
- Saves CSV to **Desktop** to avoid file permission errors

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| `curl_cffi` | HTTP requests with Chrome browser fingerprint — bypasses Amazon UK's 503 bot block |
| `BeautifulSoup` | HTML parsing and CSS selector-based data extraction |
| `pandas` | Reading and analysing logged CSV data |
| `csv` | Appending rows with UTF-8 BOM encoding fix |
| `smtplib` | Email alerts via Gmail SMTP SSL |
| `datetime` | Timestamping each price check |

---

## Setup & Usage

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/amazon-uk-price-tracker.git
cd amazon-uk-price-tracker
```

### 2. Install dependencies
```bash
pip install curl_cffi beautifulsoup4 pandas
```

### 3. Open the notebook
```bash
jupyter notebook Amazon_UK_Price_Tracker.ipynb
```

### 4. Set your configuration (Cell 2)
```python
URL             = 'https://www.amazon.co.uk/dp/YOUR_PRODUCT_ASIN'
CHECK_INTERVAL  = 10      # seconds between checks
MAX_ROWS        = 100     # stop after this many rows
PRICE_THRESHOLD = 14.99   # email alert if price drops below this
```

### 5. Run cells top to bottom
The tracker will save `amazon_price_log.csv` directly to your Desktop.

---

## 📁 Project Structure

```
amazon-uk-price-tracker/
│
├── Amazon_UK_Price_Tracker.ipynb   # Main notebook
├── amazon_price_log.csv            # Sample output data (100 rows)
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## 📊 Sample CSV Output

| Title | Price (£) | Date | Time |
|-------|-----------|------|------|
| Data Science T-Shirt Funny Definition Gift | £17.49 | 10/06/2026 | 03:28:05 PM |
| Data Science T-Shirt Funny Definition Gift | £17.49 | 10/06/2026 | 03:28:17 PM |
| Data Science T-Shirt Funny Definition Gift | £17.49 | 10/06/2026 | 03:47:11 PM |

---

## 🔧 Key Technical Challenges Solved

**1. Amazon Bot Detection (503 Error)**
Standard `requests` library returns a 503 error on Amazon UK. Solved using `curl_cffi` with `impersonate='chrome124'` which replicates a real Chrome browser's TLS fingerprint.

**2. Connection Reset / DNSError**
Long-running loops can drop connections. Solved with a retry function that creates a fresh session on failure with exponential backoff.

**3. CSV Encoding Bug (Â£ instead of £)**
Writing CSV with `encoding='UTF8'` caused Excel to display `Â£`. Fixed by switching to `encoding='utf-8-sig'` which includes the BOM marker Excel expects.

**4. PermissionError on CSV Save**
When the CSV was open in Excel, Python could not write to it. Solved with retry logic that waits 2 seconds and retries up to 3 times.

**5. Multiple Price Selectors**
Amazon uses different CSS selectors for price depending on product type. Solved with a priority list of 9 fallback selectors plus a raw text scan.

---

## 📧 Email Alert Setup (Optional)

1. Enable **2-Step Verification** on your Google account
2. Google Account → Security → **App Passwords** → Generate
3. Set in notebook Cell 2:
```python
YOUR_EMAIL         = 'your@gmail.com'
APP_PASSWORD       = 'xxxx xxxx xxxx xxxx'
ENABLE_EMAIL_ALERT = True
```

---

## 🚀 Possible Extensions

- Track multiple products simultaneously
- Plot price history chart using `matplotlib`
- Deploy as a scheduled task using Windows Task Scheduler or `cron`
- Add a Streamlit dashboard for live price visualisation
- Store data in SQLite instead of CSV for larger datasets

---

## 👤 Author

**Vrutant Vaghela**
MSc Data Science — University of East London (graduating September 2026)
Previously: Operations & Inventory Analytics, Grip Gears, Ahmedabad (6 years)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://linkedin.com/in/YOUR_LINKEDIN)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black)](https://github.com/YOUR_USERNAME)

---

## 📄 License

MIT License — free to use and modify.
