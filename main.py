import pandas as pd
from src.database import DataFrameDB
from src.scrapers_factory import ScraperFactory
import yaml
import logging


def scrape(query, method):
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    df = pd.DataFrame({"title": [], "price": [], "url": [], "website": []})
    for website in config:
        logging.info(f"Collecting website {website} with method {method}")
        print("Scraping ", website)
        scraper = ScraperFactory.create_scraper(method, **config[website])
        aux = scraper.scrape(query)
        aux['website'] = website
        df = pd.concat([df, aux], ignore_index=True)
    print("collected:")
    print(df.groupby("website").count())

    db = DataFrameDB()
    db.save_dataframe(df)


def main():
    query = input("Query: ")
    method = input("Scraping method (selenium, playwright, requests): ")
    scrape(query, method)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    main()
