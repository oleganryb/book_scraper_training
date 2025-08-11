import os
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://books.toscrape.com/"
START_URL = urljoin(BASE_URL, "catalogue/page-1.html")

# --- СЕССИЯ С РЕТРАЯМИ И USER-AGENT ---
session = requests.Session()
retries = Retry(
    total=5,                # до 5 повторов на ошибку
    backoff_factor=0.8,     # экспоненциальная пауза 0.8, 1.6, 3.2, ...
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=retries)
session.mount("http://", adapter)
session.mount("https://", adapter)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                  " AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/124.0.0.0 Safari/537.36"
}

def get_soup(url, *, timeout=20):
    r = session.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

def scrape_books():
    books = []
    url = START_URL
    skipped = 0

    while url:
        print(f"Scraping: {url}")
        soup = get_soup(url)
        items = soup.select(".product_pod")

        for item in items:
            title = item.h3.a["title"]
            price = item.select_one(".price_color").text.strip()
            availability = item.select_one(".availability").text.strip()

            # картинка (относительный -> абсолютный URL)
            img_relative = item.find("img")["src"]
            img_url = urljoin(BASE_URL, img_relative)

            # ссылка на карточку книги
            book_href = item.h3.a["href"]
            book_url = urljoin(url, book_href)

            # иногда detail-страница может отвалиться — пробуем несколько раз
            try:
                book_soup = get_soup(book_url)
                # категория берём из хлебных крошек на детальной
                crumbs = book_soup.select("ul.breadcrumb li a")
                category = crumbs[-1].text.strip() if crumbs else ""
            except Exception as e:
                skipped += 1
                print(f"  ! Skip detail ({e.__class__.__name__}): {book_url}")
                category = ""

            books.append({
                "Title": title,
                "Category": category,
                "Price": price,
                "Availability": availability,
                "Image URL": img_url
            })

            time.sleep(0.25)  # небольшая пауза между запросами

        # пагинация
        next_btn = soup.select_one("li.next a")
        if next_btn:
            next_page = next_btn["href"]
            url = urljoin(url, next_page)
        else:
            url = None

        time.sleep(0.5)  # пауза между страницами

    if skipped:
        print(f"⚠️ Skipped {skipped} detail pages due to transient errors.")
    return books

def save_to_csv(data, path="data/books.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df = pd.DataFrame(data)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"✅ Data saved to {path} ({len(df)} rows)")

if __name__ == "__main__":
    data = scrape_books()
    save_to_csv(data)
