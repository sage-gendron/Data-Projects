from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.safari.options import Options as SafariOptions
from bs4 import BeautifulSoup
import json


data_loc = '/Users/Sage/PycharmProjects/Data-Projects/Coffee FlavorsxOrigin/data/coffee_data.json'
site = 'SM'


def start_driver():
    options = SafariOptions()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    driver = webdriver.Safari(options=options)

    return driver


def load_data(loc):
    try:
        with open(loc, 'r') as infile:
            data = json.load(infile)
    except FileNotFoundError:
        data = {}
    return data


def save_data(data):
    with open(data_loc, 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4)


def insert_data(coffee_data, site, title, description, oa_score, process, cupping_csv, flavor_csv):
    title_split = title.split()
    country = title_split[0]
    loc = title_split[1]
    name = title_split[2:]

    if name not in coffee_data:
        coffee_data[name] = {
            'site': site
            'location': loc,
            'country': country,
            'description': description,
            'overall_score': oa_score,
            'process': process,
        }

        if cupping_csv:
            cupping_doc = {}
            for cat in cupping_csv.split(','):
                cat_split = cat.split(':')
                cupping_doc[cat_split[0]] = cat_split[1]
            coffee_data[name]['cupping'] = cupping_doc

        if flavor_csv:
            flavor_doc = {}
            for cat in flavor_csv.split(','):
                cat_split = cat.split(':')
                flavor_doc[cat_split[0]] = cat_split[1]
            coffee_data[name]['flavors'] = flavor_doc


def get_links(url):
    driver = start_driver()

    driver.get(url)

    driver.implicitly_wait(1.0)

    links = driver.find_elements(by=By.TAG_NAME, value='a')

    driver.close()

    return links


if __name__ == '__main__':

    links = get_links('https://www.sweetmarias.com/green-coffee.html')

    data = load_data(data_loc)

    driver = start_driver()

    i = 0
    for link in links:
        if i > 5: break
        try:
            i += 1
            driver.get(link.get_attribute('href'))
        except:
            continue

        driver.implicitly_wait(0.5)

        try:
            title = driver.find_element(by=By.XPATH, value='/html/body/div/main/div/div/div/div/div/h1/span')
            description = driver.find_element(by=By.XPATH, value='/html/body/div/main/div/div/div/div/div/div/p')
        except:
            continue

        try:
            total_score = driver.find_element(by=By.CLASS_NAME, value='score-value')
        except:
            total_score = None

        try:
            cupping_notes = driver.find_element(by=By.XPATH, value='/html/body/div/main/div/div/div/div/div/div/div/div'
                                                                   '/div/div/div/p')
        except:
            cupping_notes = None

        try:
            process_method = driver.find_element(by=By.XPATH, value='/html/body/div/main/div/div/div/div/div/div/div'
                                                                    '/div/div/div/div/ul/li/span')
        except:
            process_method = None

            charts = driver.find_elements(by=By.CLASS_NAME, value='forix-chartjs')
            for chart in charts:
                if chart.get_attribute('data-chart-id') == 'cupping-chart':
                    cupping = chart.get_attribute('data-chart-value')
                elif chart.get_attribute('data-chart-id') == 'flavor-chart':
                    flavor = chart.get_attribute('data-chart-value')

        insert_data(data, title.text, description.text, total_score.text, process_method.text, cupping, flavor)

    driver.quit()

    save_data(data)
