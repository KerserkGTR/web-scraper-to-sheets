# Catalog scraper -> CSV / Excel

Collects product data from a paginated catalog and exports clean, deduplicated files.

- Retries with backoff, polite delay between requests
- Dedup by URL, typed fields (price as number, rating 1-5, stock flag)
- Output: `books.csv` (Excel-friendly UTF-8) and `books.xlsx` with a summary sheet

Demo target: [books.toscrape.com](https://books.toscrape.com), a public sandbox for scraping practice.

```bash
pip install requests beautifulsoup4 pandas openpyxl
python scraper.py --pages 5 --out books
```

Easy to adapt: swap the selectors in `parse_page` for another site, or push the DataFrame to Google Sheets / a database.
