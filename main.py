import pandas as pd
from utils.database import DataFrameDB
from utils.DataCleaner import DataPreparer
from scraper.src.scrapers_factory import ScraperFactory
import yaml
import concurrent.futures
import logging

dfs = []
db = DataFrameDB("data.db")
preparer = DataPreparer()


def scrape(query, method):
    with open("./scraper/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    df = pd.DataFrame({"title": [], "price": [], "url": [], "website": []})
    for website in config:
        logging.info(f"Collecting website {website} with method {method}")
        print("Scraping ", website)
        scraper = ScraperFactory.create_scraper(method, **config[website])
        aux = scraper.scrape(query)
        aux['website'] = website
        aux['query'] = query
        aux = preparer.prepare_data(aux, config[website])
        print("aux", aux)
        df = pd.concat([df, aux], ignore_index=True)

    print("AAAAAAAAAA")
    return df


def process_query(query, method):
    logging.info(f">>Scraping the query {query}")
    df = scrape(query, method)
    logging.info(f">>>df size{len(df)}")
    dfs.append(df)


def main():
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    queries = config['query']
    method = config['method']

    # Create a ThreadPoolExecutor with the desired number of workers
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit the tasks to the executor
        #  The executor will schedule the tasks across multiple threads
        futures = [executor.submit(process_query, query, method) for query in queries]

        # Wait for the tasks to complete
        concurrent.futures.wait(futures)

    logging.info("All queries scraped successfully.")

    df = pd.concat(dfs, ignore_index=True)
    db.insert_data(df)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    db.connect()
    db.create_table()
    main()
