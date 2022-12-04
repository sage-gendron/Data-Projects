from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.safari.options import Options as SafariOptions
import json


class Scraper:
    def __init__(self, data_loc, site, url):
        self.data = {}
        self.data_loc = data_loc
        self.links = []
        self.site = site
        self.url = url
        self.visited = []

        self.load_data(data_loc)
        self.start_driver()

    def start_driver(self):
        """

        :return: driver -
        :rtype:
        """
        options = SafariOptions()
        options.headless = True
        options.add_argument("--window-size=1920,1200")
        self.driver = webdriver.Safari(options=options)

    def stop_driver(self):
        self.driver.quit()

    def load_data(self, loc):
        """

        :param str loc: coffee data location
        :return: loaded_data - dictionary containing previously scraped coffee_data file (if found)
        :rtype: dict
        """
        try:
            with open(loc, 'r') as infile:
                self.data = json.load(infile)
        except FileNotFoundError:
            print(f"No existing data file found. New data file will be created.")

    def save_data(self):
        """
        Saves data as data_loc from global variables,

        :return: None
        """
        with open(self.data_loc, 'w') as outfile:
            json.dump(self.data, outfile, sort_keys=True, indent=4)

    def get_links(self, url):
        """

        :param str url:
        :return: links
        :rtype: list
        """
        self.driver.get(url)

        self.driver.implicitly_wait(3.0)

        link_elements = self.driver.find_elements(by=By.TAG_NAME, value='a')

        for element in link_elements:
            link = element.get_attribute('href')

            if link is None or 'javascript' in link:
                continue

            self.links.append(link)

        return self.links

    def find_text(self, find_type, elem):
        try:
            return self.driver.find_element(by=find_type, value=elem).text
        except:
            return None

    def find_list(self, find_type, elem):
        try:
            return self.driver.find_elements(by=find_type, value=elem)
        except:
            return None

    def scrape(self, sublink):
        self.visit(sublink)
        self.driver.get(sublink)

    def visit(self, sublink):
        self.visited.append(sublink)

    def wait(self, t):
        self.driver.implicitly_wait(t)

