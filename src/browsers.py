from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


class SeleniumBrowser(webdriver.Chrome):

    def __init__(self,
                 options: list = ["--headless"],
                 prefs: dict = {},
                 cookies: dict = {}
                 ) -> None:

        self.options = webdriver.ChromeOptions()
        self.cookies = cookies
        for option in options:
            self.options.add_argument(option)
        self.options.add_experimental_option('prefs', prefs)

    def __enter__(self) -> None:
        self.begin()

    def __exit__(self, *args, **kwargs) -> None:
        self.close()

    def begin(self) -> None:
        service = Service(executable_path=ChromeDriverManager().install())
        super(SeleniumBrowser, self).__init__(service=service,
                                              options=self.options
                                              )

    def insert_cookies(self):
        for k, v in self.cookies.items():
            self.add_cookie({"name": k, "value": v})
        self.refresh()

    def get_status(self) -> str:
        status = ""
        for entry in self.get_log("performance"):
            status += f"{entry}\n\n"
        return status
