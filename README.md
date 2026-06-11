# 🛒 Amazon UK Price Tracker

A Python automation project that scrapes an Amazon UK product page every 10 seconds, logs the price to CSV, and sends an email alert when the price drops below a set threshold.

**Product tracked:** Data Science T-Shirt (Amazon UK) — £17.49  
**Data collected:** 100 price records over ~18 minutes on 11 June 2026

---

## 📸 Sample Output

```
🚀 Tracker started | Every 10s | Adding 100 rows
──────────────────────────────────────────────────────────────────────
[001/100] 2026-06-11 22:38:05  |  £17.49  |  ✓ saved  |  row 1/100
[002/100] 2026-06-11 22:38:17  |  £17.49  |  ✓ saved  |  row 2/100
[003/100] 2026-06-11 22:38:28  |  £17.49  |  ✓ saved  |  row 3/100
...
[100/100] 2026-06-11 22:56:54  |  £17.49  |  ✓ saved  |  row 100/100
──────────────────────────────────────────────────────────────────────
✅ Done! 100 rows reached. CSV saved on Desktop.
```

---

## 📊 Sample CSV Output (actual data)

| Title | Price (£) | Date | Time |
|-------|-----------|------|------|
| Data Science T-Shirt Funny Definition Gift | 17.49 | 2026-06-11 | 22:38:05 |
| Data Science T-Shirt Funny Definition Gift | 17.49 | 2026-06-11 | 22:38:17 |
| Data Science T-Shirt Funny Definition Gift | 17.49 | 2026-06-11 | 22:56:54 |

100 rows · stable price · ~11 second intervals · logged 22:38 → 22:56

---

## 🔍 What It Does

- Scrapes **product title and price** from any Amazon UK product page
- Checks price every **10 seconds** and logs to CSV automatically
- Stores **Date and Time in separate columns** for easy analysis
- Detects **price changes** between checks (up ▲ / down ▼ / same)
- Sends a **Gmail email alert** when price drops below a set threshold
- Stops automatically at **100 rows** (configurable)
- Handles **bot detection**, **connection resets**, and **file lock errors** gracefully
- Saves CSV to **Desktop** to avoid permission errors

---

## 🛠️ Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| `curl_cffi` | ≥0.6 | HTTP requests with Chrome TLS fingerprint — bypasses Amazon UK 503 bot block |
| `beautifulsoup4` | ≥4.12 | HTML parsing and CSS selector-based price extraction |
| `pandas` | ≥2.0 | Reading, analysing, and displaying logged CSV data |
| `matplotlib` | ≥3.7 | Price history chart with min/max/threshold markers |
| `smtplib` | built-in | Email alerts via Gmail SMTP SSL |
| `csv` | built-in | Append-only CSV logging with UTF-8 BOM encoding |
| `datetime` | built-in | Timestamping each check with separate Date and Time |

---

## ⚙️ Setup & Run

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/amazon-uk-price-tracker.git
cd amazon-uk-price-tracker
```

### 2. Install dependencies
```bash
pip install curl_cffi beautifulsoup4 pandas matplotlib
```

### 3. Open the notebook
```bash
jupyter notebook Amazon_UK_Price_Tracker.ipynb
```

### 4. Set your product URL in Cell 02
```python
URL = 'https://www.amazon.co.uk/dp/YOUR_PRODUCT_ASIN'
```

### 5. Run all cells top to bottom
CSV saves automatically to your Desktop.

---

## 📁 Repository Structure

```
amazon-uk-price-tracker/
│
├── Amazon_UK_Price_Tracker.ipynb   ← Main notebook (interactive, dark theme)
├── amazon_price_log.csv            ← Sample output: 100 real price records
├── requirements.txt                ← Python dependencies
└── README.md                       ← This file
```

---

## 🔧 Technical Challenges Solved

### 1 · Amazon Bot Detection (503 Error)
The standard `requests` library triggers Amazon UK's bot detection and returns a 503 error. Fixed by switching to `curl_cffi` with `impersonate='chrome124'`, which replicates a real Chrome browser's TLS fingerprint at the network layer.

### 2 · Connection Reset / DNSError
Long-running loops occasionally drop the network connection, raising a `DNSError` and crashing the tracker. Fixed with a retry function that creates a fresh session on each failure, with exponential backoff (3s → 6s) between attempts.

### 3 · CSV Encoding Bug (Â£ in Excel)
Using `encoding='UTF8'` caused Excel to display `Â£` instead of `£` due to missing BOM. Fixed by switching to `encoding='utf-8-sig'`, which includes the byte-order mark Excel expects.

### 4 · PermissionError on CSV Save
When the CSV is open in Excel, Python raises a `PermissionError` and cannot write. Fixed with retry logic that waits 2 seconds and retries up to 3 times before skipping.

### 5 · Dynamic Price Selectors
Amazon uses different CSS selectors for price depending on product type, deal state, and page variant. Fixed with a priority list of 9 fallback selectors plus a raw text scan for any `£` value as a last resort.

---

## 📧 Email Alert Setup (Optional)

1. Enable **2-Step Verification** on your Google account
2. Google Account → Security → **App Passwords** → Generate
3. In notebook Cell 02, set:

```python
ENABLE_EMAIL    = True
YOUR_EMAIL      = 'your@gmail.com'
APP_PASSWORD    = 'xxxx xxxx xxxx xxxx'
PRICE_THRESHOLD = 14.99
```

---

## 🚀 Possible Extensions

- Track multiple products simultaneously using threading
- Plot live price chart updating in real time with `matplotlib` animation
- Deploy as a Windows scheduled task or Linux `cron` job
- Store data in SQLite for longer-term tracking across multiple products
- Build a Streamlit dashboard for visual price monitoring

---

## 👤 Author

**Vrutant Vaghela**  
MSc Data Science — University of East London (graduating September 2026)  
Background: 6 years in Operations & Inventory Analytics, Ahmedabad

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat&logo=linkedin)](https://linkedin.com/in/YOUR_LINKEDIN)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=flat&logo=github)](https://github.com/YOUR_USERNAME)

---

## 📄 License

MIT — free to use and modify with attribution.
