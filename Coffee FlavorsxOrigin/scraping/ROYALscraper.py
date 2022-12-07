# scraping/ROYALscraper.py
"""
author: Sage Gendron

"""
from Scraper.Scraper import Scraper
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
import time


class ROYALScraper(Scraper):
    def __init__(self, data_loc, site, url):
        super().__init__(data_loc, site, url)

    def insert_data(self, link, title, background, flavors, about):
        """

        :param link: url for this page if needed for future reference
        :param title: name of the datum
        :param background: full description of the background of this particular coffee, needs to be digested at length
        :param flavors: small list of noteworthy flavors
        :param about: about coffee section extracted as a chunk as no unique identifiers exist on site
        :return: None
        """
        # initialize datum entry with None values for about categories
        title = '–'.join(title.split('–')[:-1])
        if title not in self.data:
            self.data[title] = {
                'site': self.site,
                'link': link,
                'background': background,
                'listed_flavors': flavors,
                'region': None,
                'process': None,
                'grower': None,
                'altitude': None,
                'variety': None
            }

            # look for about category values and fill in accordingly
            if about is not None:
                category = about.find_elements(By.TAG_NAME, 'h4')
                value = about.find_elements(By.TAG_NAME, 'p')

                for c, v in zip(category, value):
                    c = c.text.lower()
                    v = v.text
                    if c == 'region':
                        self.data[title]['region'] = v
                    elif c == 'process':
                        self.data[title]['process'] = v
                    elif c == 'grower':
                        self.data[title]['grower'] = v
                    elif c == 'altitude':
                        self.data[title]['altitude'] = v
                    elif c == 'variety':
                        self.data[title]['variety'] = v

            print(self.data[title])

    def next_page(self):
        """

        :return:
        :rtype: str
        """
        try:
            self.driver.get(self.url)
            self.wait(5)
            return self.driver.find_element(By.CLASS_NAME, 'next.page-numbers').get_attribute('href')
        except NoSuchElementException:
            return None
        except TimeoutException:
            return None


if __name__ == '__main__':
    # first page of all coffees marked as for sale online
    url_page_1 = 'https://royalcoffee.com/online-sales/online/'

    # instantiate scraper object
    scraper = ROYALScraper(
        data_loc='/Users/Sage/PycharmProjects/Data-Projects/Coffee FlavorsxOrigin/data/royal_coffee_data.json',
        site='Royal Coffee',
        url=url_page_1
    )

    i = 0
    # continue looping through pages until no next page button found
    while True:
        # loop through links located in url
        for link in scraper.links:
            print(link)

            # ensure the link is a product link
            if '/product/' not in link:
                continue
            i += 1

            time.sleep(3)
            scraper.scrape(link)
            scraper.wait(5)

            title = scraper.find_text(By.CLASS_NAME, 'product_title')
            if title is None:
                continue
            print(title)

            background = scraper.find_text(By.XPATH, '//*[@id="page-container"]/div/div[2]/div[4]/div')

            try:
                flavors = scraper.driver.\
                    find_element(By.CLASS_NAME, "single-product__details-characteristics").\
                    find_element(By.CLASS_NAME, 'value').text
                print(flavors)
            except NoSuchElementException:
                flavors = None
            except TimeoutException:
                flavors = None

            about_parents = scraper.find_list(By.XPATH, '//*[@id="page-container"]/div/div[2]/div[3]/div')[0]

            try:
                scraper.insert_data(link, title, background, flavors, about_parents)
            except NoSuchElementException:
                continue
            except TimeoutException:
                continue

            # save data at intervals of 10
            if i % 10 == 0:
                print(f"Saving data... {i} links scraped successfully.")
                scraper.save_data()

        # look for the next page link for the next link scrape
        next_page = scraper.next_page()
        if next_page:
            scraper.get_links(next_page)
        else:
            break

    scraper.stop_driver()

    scraper.save_data()
