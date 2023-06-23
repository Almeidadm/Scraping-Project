from abc import ABC, abstractmethod
import pandas as pd
from scrapers.browsers import SeleniumBrowser
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from playwright.sync_api import sync_playwright
import requests
from bs4 import BeautifulSoup
from scrapers.logger import detailed_logging
import logging

# Base scraper class
class Scraper(ABC):

    def __init__(
            self,
            search_url: str,
            title_selector: str,
            price_selector: str,
            url_selector: str,
            type_element: str = "css selector",
            **kwargs
    ):
        self.search_url = search_url
        self.title_selector = title_selector
        self.price_selector = price_selector
        self.url_selector = url_selector
        self.type_element = type_element

    @abstractmethod
    def locate_elements(self, selector, href: bool = False):
        pass

    @abstractmethod
    def goto(self, url):
        pass

    def iteration(self, query):
        url = self.search_url.replace("{query}", query)
        if "{page}" in url:
            i = 1
            while i < 20:
                yield url.replace("{page}", str(i))
                i += 1
        else:
            yield url

    @detailed_logging
    def scrape(self, query):

        df = pd.DataFrame({"title": [], "price": [], "url": []})
        for current_url in self.iteration(query):

            self.goto(current_url)

            titles = self.locate_elements(self.title_selector)
            prices = self.locate_elements(self.price_selector)
            urls = self.locate_elements(self.url_selector, href=True)

            if len(prices) == 0:
                break

            limit = min([len(li) for li in [titles, prices, urls]])

            aux = pd.DataFrame({"title": titles[:limit], "price": prices[:limit], "url": urls[:limit]})
            df = pd.concat([df, aux], ignore_index=True)
        df = df.drop_duplicates("url", ignore_index=True)
        return df


class SeleniumScraper(Scraper):

    def __init__(
            self,
            search_url: str,
            title_selector: str,
            price_selector: str,
            url_selector: str,
            type_element: str = "css selector",
            **kwargs
    ):
        super().__init__(search_url, title_selector, price_selector, url_selector, type_element, **kwargs)
        self.driver = SeleniumBrowser()
        self.wait = WebDriverWait(self.driver, 5)

    def locate_elements(self, selector, href: bool = False):
        try:
            elements = self.wait.until(
                ec.visibility_of_all_elements_located((self.type_element, selector))
            )
            elements = list(set([e.get_attribute("href").strip() for e in elements])) if href else [e.text.strip()
                                                                                                    for e in elements]
        except TimeoutException:
            elements = []

        return elements

    def goto(self, url):
        self.driver.get(url)
    
    def scrape(self, query):
        with self.driver:
            df = super().scrape(query)
        return df


class PlaywrightScraper(Scraper):

    def __init__(
            self,
            search_url: str,
            title_selector: str,
            price_selector: str,
            url_selector: str,
            type_element: str = "css selector",
            **kwargs
    ):
        super().__init__(search_url, title_selector, price_selector, url_selector, type_element, **kwargs)
        self.page = None

    def locate_elements(self, selector, href: bool = False):
        elements = self.page.query_selector_all(selector)
        elements = list(set([e.get_attribute("href").strip() for e in elements])) if href else [e.text_content().strip()
                                                                                                for e in elements]
        return elements

    def goto(self, url):
        self.page.goto(url, timeout=0)

    def scrape(self, query):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            context = browser.new_context()
            self.page = context.new_page()
            result = super().scrape(query)
            context.close()
            browser.close()
        return result


class RequestsScraper(Scraper):

    def __init__(
            self,
            search_url: str,
            title_selector: str,
            price_selector: str,
            url_selector: str,
            type_element: str = "css selector",
            **kwargs
    ):
        super().__init__(search_url, title_selector, price_selector, url_selector, type_element, **kwargs)
        self.response = None

    def locate_elements(self, selector, href: bool = False):
        soup = BeautifulSoup(self.response.text, 'html.parser')
        elements = soup.select(selector)
        elements = list(set([e['href'].strip() for e in elements])) if href else [e.get_text().strip()
                                                                                  for e in elements]
        return elements

    def goto(self, url):
        self.response = requests.get(url)

    def scrape(self, query):
        # action
        df = super().scrape(query)
        return df
