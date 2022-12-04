# scraper.py
"""
author: Sage Gendron

"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.safari.options import Options as SafariOptions
from bs4 import BeautifulSoup
import json
import time


data_loc = '/Users/Sage/PycharmProjects/Data-Projects/Coffee FlavorsxOrigin/data/coffee_data.json'
site = 'SM'
url = 'https://www.sweetmarias.com/green-coffee.html?product_list_limit=all&sm_status=1'


def start_driver():
    """

    :return: driver -
    :rtype:
    """
    options = SafariOptions()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    driver = webdriver.Safari(options=options)

    return driver


def load_data(loc):
    """

    :param str loc:
    :return: loaded_data
    :rtype: dict
    """
    try:
        with open(loc, 'r') as infile:
            loaded_data = json.load(infile)
    except FileNotFoundError:
        loaded_data = {}
    return loaded_data


def save_data(saved_data):
    """
    Saves data as data_loc from global variables,

    :param dict saved_data:
    :return: None
    """
    with open(data_loc, 'w') as outfile:
        json.dump(saved_data, outfile, sort_keys=True, indent=4)


def insert_data(coffee_data, link, title, description, oa_score, process, cupping_csv, flavor_csv):

    if title not in coffee_data:
        coffee_data[title] = {
            'site': site,
            'link': link,
            'description': description,
            'overall_score': oa_score,
            'process': process,
        }

        if cupping_csv:
            cupping_doc = {}
            for cat in cupping_csv.split(','):
                cat_split = cat.split(':')
                cupping_doc[cat_split[0]] = cat_split[1]
            coffee_data[title]['cupping'] = cupping_doc

        if flavor_csv:
            flavor_doc = {}
            for cat in flavor_csv.split(','):
                cat_split = cat.split(':')
                flavor_doc[cat_split[0]] = cat_split[1]
            coffee_data[title]['flavors'] = flavor_doc


def get_links(driver):
    """

    :param selenium.WebDriver driver:
    :return: links
    :rtype: list
    """
    driver.get(url)

    driver.implicitly_wait(3.0)

    link_elements = driver.find_elements(by=By.TAG_NAME, value='a')

    links = []
    for element in link_elements:
        link = element.get_attribute('href')

        if link is None or 'javascript' in link:
            continue

        links.append(link)

    return links


if __name__ == '__main__':
    # initiate webdriver
    driver = start_driver()

    # get all links from anchor tags, removing Javascript calls
    links = get_links(driver)

    # load data file if exists, otherwise returns an empty dictionary
    data = load_data(data_loc)

    # loop through scraped links to extract data
    visited = []
    for link in links:

        print(link)
        if not link.split('.')[-2][-4:].isdigit() or link in visited:
            continue

        time.sleep(5)

        driver.get(link)
        visited.append(link)
        driver.implicitly_wait(2)

        # look for the title and short description from the webpage, if not found, skip the page
        try:
            title = driver.find_element(by=By.XPATH, value='/html/body/div/main/div/div/div/div/div/h1/span').text
            description = driver.find_element(by=By.XPATH, value='/html/body/div/main/div/div/div/div/div/div/p').text
            print(title)
        except:
            continue

        try:
            total_score = driver.find_element(by=By.CLASS_NAME, value='score-value').text
        except:
            total_score = None

        try:
            cupping_notes = driver.find_element(by=By.XPATH, value='/html/body/div/main/div/div/div/div/div/div/div/div'
                                                                   '/div/div/div/p').text
        except:
            cupping_notes = None

        try:
            process_method = driver.find_element(by=By.XPATH, value='/html/body/div/main/div/div/div/div/div/div/div'
                                                                    '/div/div/div/div/ul/li/span').text
        except:
            process_method = None

        try:
            charts = driver.find_elements(by=By.CLASS_NAME, value='forix-chartjs')
            for chart in charts:
                if chart.get_attribute('data-chart-id') == 'cupping-chart':
                    cupping = chart.get_attribute('data-chart-value')
                elif chart.get_attribute('data-chart-id') == 'flavor-chart':
                    flavor = chart.get_attribute('data-chart-value')
        except:
            cupping = flavor = None

        insert_data(data, link, title, description, total_score, process_method, cupping, flavor)

    driver.quit()

    save_data(data)
