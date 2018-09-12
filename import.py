#!/usr/bin/env python

from datetime import datetime

import csv
import json

month_mapping = {
    'ene': 'Jan',
    'feb': 'Feb',
    'mar': 'Mar',
    'abr': 'Apr',
    'may': 'May',
    'jun': 'Jun',
    'jul': 'Jul',
    'ago': 'Aug',
    'sep': 'Sep',
    'oct': 'Oct',
    'nov': 'Nov',
    'dic': 'Dec',
}


def convert_month(month):
    return month_mapping[month]


def to_date_object(date_str):
    date_parts = date_str.split(' ')
    day = date_parts[0]
    month = convert_month(date_parts[1])
    year = date_parts[2]
    date_str = '{} {} {}'.format(year, month, day)
    date_fmt = '%Y %b %d'
    date = datetime.strptime(date_str, date_fmt)
    return date


def get_zone_prices(row, zone_prefix):
    diesel_field = '{}_DO'.format(zone_prefix)
    diesel = row[diesel_field]

    diesel_low_sulfur_field = '{}_DOLS'.format(zone_prefix)
    diesel_low_sulfur = row[diesel_low_sulfur_field]

    special_field = '{}_GS'.format(zone_prefix)
    special = row[special_field]

    regular_field = '{}_GR'.format(zone_prefix)
    regular = row[regular_field]
    return {
        'diesel': diesel,
        'diesel_low_sulfur': diesel_low_sulfur,
        'special': special,
        'regular': regular,
    }


def parse_zones(row):
    central = {
        'name': 'central',
        'prices': get_zone_prices(row, 'ZCE'),
    }
    western = {
        'name': 'western',
        'prices': get_zone_prices(row, 'ZOC'),
    }
    eastern = {
        'name': 'eastern',
        'prices': get_zone_prices(row, 'ZOR'),
    }
    return [
        central,
        western,
        eastern,
    ]


def parse_row(row):
    year = row['ANHO']
    from_date_str = '{} {}'.format(row['FECHA_INIPREC'], year)
    to_date_str = '{} {}'.format(row['FECHA_FINPREC'], year)
    from_date = to_date_object(from_date_str)
    to_date = to_date_object(to_date_str)
    zones = parse_zones(row)
    return {
        'from': from_date,
        'to': to_date,
        'zones': zones
    }


filename = './all.csv'
with open(filename, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        row_dict = parse_row(row)
        row_json = json.dumps(row_dict, indent=2, default=str)
        print(row_json)
