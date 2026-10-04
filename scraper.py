"""Catalog scraper: collects product data from a paginated site and exports
clean, deduplicated CSV and Excel files.

Demo target: https://books.toscrape.com (a public sandbox site built for scraping practice).

Usage:
    python scraper.py --pages 5 --out books
"""
import argparse
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE = "https://books.toscrape.com/catalogue/"
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def fetch(session: requests.Session, url: str, retries: int = 3) -> str:
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, timeout=15)
            resp.raise_for_status()
            resp.encoding = "utf-8"
            return resp.text
        except requests.RequestException:
            if attempt == retries:
                raise
            time.sleep(2 * attempt)


def parse_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for card in soup.select("article.product_pod"):
        link = card.h3.a
        price = re.sub(r"[^\d.]", "", card.select_one(".price_color").text)
        rating_cls = next(c for c in card.select_one(".star-rating")["class"] if c != "star-rating")
        rows.append(
            {
                "title": link["title"],
                "price_gbp": float(price),
                "rating": RATINGS.get(rating_cls),
                "in_stock": "In stock" in card.select_one(".availability").text,
                "url": BASE + link["href"].replace("../", ""),
            }
        )
    return rows


def scrape(pages: int, delay: float = 0.5) -> pd.DataFrame:
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (compatible; catalog-scraper-demo/1.0)"
    rows = []
    for n in range(1, pages + 1):
        rows += parse_page(fetch(session, f"{BASE}page-{n}.html"))
        time.sleep(delay)
    df = pd.DataFrame(rows).drop_duplicates(subset="url").reset_index(drop=True)
    return df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=5)
    ap.add_argument("--out", default="books")
    args = ap.parse_args()

    df = scrape(args.pages)
    df.to_csv(f"{args.out}.csv", index=False, encoding="utf-8-sig")
    with pd.ExcelWriter(f"{args.out}.xlsx") as xl:
        df.to_excel(xl, sheet_name="books", index=False)
        summary = df.groupby("rating").agg(count=("title", "size"), avg_price=("price_gbp", "mean")).round(2)
        summary.to_excel(xl, sheet_name="summary_by_rating")
    print(f"{len(df)} rows -> {args.out}.csv, {args.out}.xlsx")


if __name__ == "__main__":
    main()
