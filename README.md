# Book Scraper (Training Project)

This script scrapes book data from https://books.toscrape.com and saves it to a CSV file.

## Extracted Fields

* Title
* Category
* Price
* Availability
* Image URL

## Tech Stack

* Python
* requests
* BeautifulSoup
* pandas

## How to run

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scraper.py

## Output

- CSV file: data/books.csv (1000 rows)
- Screenshot: screenshots/table\_preview.png


## Notes

- This project is for educational purposes only and uses an open training website.
- You can adapt the code to scrape other websites (respecting their terms of service).





