from scrapers.base_scrapers import PlaywrightScraper, RequestsScraper, SeleniumScraper


class FactoryLoader:

    __instance = None

    def __init__(self):
        if FactoryLoader.__instance is not None:
            raise Exception(
                "FactoryLoader is a singleton class, use get_instance() method to get the instance.")
        else:
            FactoryLoader.__instance = self
        pass

    @staticmethod
    def get_instance():
        if FactoryLoader.__instance is None:
            FactoryLoader()
        return FactoryLoader.__instance

    @staticmethod
    def load_factory(factory_name):
        factory_module = __import__(factory_name)
        return getattr(factory_module, f"{factory_name}")


# Abstract Factory for creating web scrapers
class ScraperFactory:
    @staticmethod
    def create_scraper(scraper_type, **kwargs):
        if scraper_type == "selenium":
            return SeleniumScraper(**kwargs)
        elif scraper_type == "playwright":
            return PlaywrightScraper(**kwargs)
        elif scraper_type == "requests":
            return RequestsScraper(**kwargs)
        else:
            raise ValueError("Invalid scraper type")
