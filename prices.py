#!/usr/bin/env python

import re
import json
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup


def build_driver():
    driver_path = './selenium/chromedriver'
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(driver_path, chrome_options=options)
    return driver


def get_html(driver, url):
    driver.get(url)
    # TODO:
    # Change for a better element to wait for
    wait_text = 'Precios de referencia para los combustibles'
    xpath_expr = "//div[contains(text(),'{}')]".format(wait_text)
    WebDriverWait(driver, 60).until(EC.visibility_of_element_located(
        (By.XPATH, xpath_expr)))
    html = driver.page_source
    return html


def parse_dates(dates_row):
    tds = dates_row.find_all('td')
    dates_cell = tds[2].div.table.tbody.tr.td.div.div
    date_text = dates_cell.find_all('span')
    date_from = datetime.strptime(date_text[1].text, '%d/%m/%Y')
    date_to = datetime.strptime(date_text[3].text, '%d/%m/%Y')
    return {"from": date_from, "to": date_to}


def parse_gas_types(gas_types_row):
    tds = gas_types_row.find_all('td')
    gas_types_mapping = [
        ('special', 2),
        ('regular', 4),
        ('diesel', 6),
        ('diesel_low_sulfur', 8),
    ]

    def get_gas_types(mapping):
        gas_type = mapping[0]
        td_index = mapping[1]
        gas_type_name = tds[td_index].div.text
        return {
            "slug": gas_type,
            "name": gas_type_name
        }

    gas_types = list(map(get_gas_types, gas_types_mapping))
    return gas_types


def parse_zone(zone_row):
    tds = zone_row.find_all('td')
    special_price = tds[2].div.text.replace('$', '')
    regular_price = tds[5].div.text.replace('$', '')
    diesel_price = tds[8].div.text.replace('$', '')
    diesel_low_sulfur = tds[11].div.text.replace('$', '')
    return {
        "special": float(special_price),
        "regular": float(regular_price),
        "diesel": float(diesel_price),
        "diesel_low_sulfur": float(diesel_low_sulfur),
    }


def parse_price_table(price_table):
    tds = price_table.find_all('td')
    data_trs = tds[2].table.tbody.find_all('tr')

    gas_types_row = data_trs[1]
    zones_mapping = [
        ('central', 2),
        ('western', 3),
        ('eastern', 4),
    ]

    def get_zone_prices(mapping):
        zone = mapping[0]
        tr_index = mapping[1]
        zone_row = data_trs[tr_index]
        zone_prices = parse_zone(zone_row)
        return {
            "name": zone,
            "prices": zone_prices
        }

    gas_types = parse_gas_types(gas_types_row)
    zone_prices = (list(map(get_zone_prices, zones_mapping)))

    return {
        "gas_types": gas_types,
        "zones": zone_prices
    }


def parse_prices(html):
    soup_parser = 'html.parser'
    soup = BeautifulSoup(html, soup_parser)

    def is_report_div(x):
        end = '_1_oReportDiv'
        return x and x.endswith(end)

    report_divs = soup.find_all('div', id=is_report_div)
    report_div = report_divs[0]

    report_cell = report_div.table.tbody.tr.td
    info_table = report_cell.table.tbody.tr.td.table

    info_rows = info_table.tbody.find_all('tr', valign='top')

    dates_row = info_rows[1]
    dates = parse_dates(dates_row)

    prices_row = info_rows[2]
    prices = parse_price_table(prices_row)

    return {
        "from": dates['from'],
        "to": dates['to'],
        "prices": prices
    }


driver = build_driver()

try:
    prices_url = 'http://www.edrhym.gob.sv/drhm/precios.aspx'

    print('Requesting {}...'.format(prices_url))
    html = get_html(driver, prices_url)

    print('Parsing prices...')
    prices = parse_prices(html)

    print(json.dumps(prices, indent=2, default=str))

finally:
    driver.quit()
