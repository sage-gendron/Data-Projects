# scraping/Scraper/Scraper.py
"""
author: Sage Gendron
Base scraper class with methods that all individual site scrapers will use. Ultimately won't be used on its own, but
will be inherited per website to be scraped so the find_text/find_list functions can be customized.

Some other options to scrape:
- https://burmancoffee.com/green-coffee-beans/
- https://happymugcoffee.com/collections/green-coffee
- https://www.roastmasters.com/green_coffee.html
- https://millcityroasters.com/product-category/green-coffee/
"""
from selenium import webdriver
from selenium.common.exceptions import NoSuchAttributeException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.safari.options import Options as SafariOptions
import json


class Scraper:
    def __init__(self, data_loc, site, url):
        self.data = {}
        self.data_loc = data_loc
        self.driver = None
        self.links = []
        self.site = site
        self.url = url
        self.visited = []

        self.load_data(data_loc)
        self.start_driver()
        self.get_links(url)

    def start_driver(self):
        """
        Instantiates a Safari webdriver with basic, headless options.

        :return: None
        """
        options = SafariOptions()
        options.headless = True
        options.add_argument("--window-size=1920,1200")
        self.driver = webdriver.Safari(options=options)

    def stop_driver(self):
        """
        Calls driver.quit() to dissociate from browser.

        :return: None
        """
        self.driver.quit()

    def load_data(self, loc):
        """
        Loads the existing coffee data file (if present) in the location provided.

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
        Grabs all anchored URLs in the DOM of the provided URL. Attempts to reduce errors by removing javascript calls
        and None-type links.

        :param str url: url to scrape anchor-tagged hyperlinks from
        :return: None
        """
        if self.links:
            self.links = []

        self.url = url

        self.driver.get(url)

        self.wait(3)

        link_elements = self.driver.find_elements(by=By.TAG_NAME, value='a')

        for element in link_elements:
            try:
                link = element.get_attribute('href')
            except NoSuchAttributeException:
                continue

            if link is None or 'javascript' in link:
                continue

            self.links.append(link)

    def find_text(self, find_type, elem):
        """
        Looks for a specific element as specified by the find type and element being searched for.

        :param selenium.webdriver.common.By find_type: class of search method
        :param str elem: string corresponding to search method being used
        :return: the text contained in the searched-for element if found, otherwise returns None
        :rtype: str
        """
        try:
            return self.driver.find_element(by=find_type, value=elem).text
        except NoSuchElementException:
            return None

    def find_list(self, find_type, elem):
        """
        Grabs all elements based on search criteria and returns them as a list.

        :param selenium.common.By find_type: class of search method
        :param str elem: string corresponding to search method being used
        :return: a list of elements that were found using the By class and elem search methods
        :rtype: list
        """
        try:
            return self.driver.find_elements(by=find_type, value=elem)
        except NoSuchElementException:
            return None

    def scrape(self, sublink):
        """
        Opens the sublink in a browser for HTML parsing

        :param str sublink: link to be loaded by the driver
        :return: None
        """
        self.visit(sublink)
        self.driver.get(sublink)

    def visit(self, sublink):
        """
        'Visits' a link by adding it to self.visited to ensure the link will not be visited again.

        :param str sublink: link that was visited by the driver
        :return: None
        """
        self.visited.append(sublink)

    def wait(self, t):
        """
        Calls selenium's implicitly_wait() function on the driver to allow some buffer time between server requests.

        :param int t: amount of time to implicitly wait for
        :return: None
        """
        self.driver.implicitly_wait(t)
