import io
import json
import requests 
import sys
from collections import defaultdict

import pandas as pd


# List of all crop budgets.
# Moving forward, this should come from the API.

from grocropclient.crop_budgets_data import METRIC_MAPPING

from io import StringIO

API_HOST = "api.gro-intelligence.com"

# To get all crop budget tables from the CSV above.
def get_all_crop_budgets(api_host, api_token, crop='', state=''):
  try:
    crop = crop.lower()
    state = state.lower()
  except AttributeError as e:
    raise TypeError(f'crop and state parameters must be strings') from e
  if state:
      state = state.replace(' ', '_') # the source name uses underscore for multiword US states.
  headers = { 'Authorization' : f'Bearer {api_token}' }
  endpoint = 'crop-budget-available-series'
  url = "/".join(["https:", "", api_host, endpoint])
  resp = requests.get(url=url,
                    headers=headers)
  json_resp = json.dumps(resp.json()['data'])
  df = pd.read_json(json_resp, orient='records')
  for col in df.columns:
    camel_case_col = col
    snake_case_col = __camel_case_to_snake_case(col)
    df.rename(columns = {camel_case_col: snake_case_col}, inplace=True)
  return df.loc[df.item_name.apply(lambda x: x.split(',')[0]).str.lower().str.contains(crop) & df.source_name.str.contains(state, case=False)]


# To convert JSON from the API into a Pandas that looks like a Crop Budget Table.
def __crop_budget_json_to_df(crop_budget_as_json):
  index = [key for key in crop_budget_as_json]
  df_data = defaultdict(list)
  min_year = 2050
  max_year = 1900
  for metric in crop_budget_as_json:
    min_year = min(min_year, min([int(k) for k in crop_budget_as_json[metric]['data']]))
    max_year = max(max_year, max([int(k) for k in crop_budget_as_json[metric]['data']]))

  for metric in crop_budget_as_json:
    for year in range(min_year, max_year+1):
      df_data[year].append(crop_budget_as_json[metric]['data'].setdefault(str(year), None))

  return pd.DataFrame(df_data, index)

# New code from API team.
def __crop_budget_json_to_df2(crop_budget_as_json):
    flattened_metrics = __flatten_to_list(METRIC_MAPPING)
    csv_str = __json_to_csv(crop_budget_as_json, flattened_metrics)
    csv_string_io = io.StringIO(csv_str)
    return pd.read_csv(csv_string_io, sep=',')


# To get a single crop budget, converted into a Pandas dataframe.
def get_crop_budget_as_df(api_host, api_token, source_name, item_name, region_name):
  headers = { 'Authorization' : f'Bearer {api_token}' }
  params = {'sourceName': source_name, 'itemName': item_name, 'regionName': region_name }
  endpoint = 'crop-budget'
  url = "/".join(["https:", "", api_host, endpoint])
  resp = requests.get(url=url,
                    headers=headers,
                    params=params)
  return __crop_budget_json_to_df2(resp.json())

def __flatten_to_list(obj, parent = None, res = []):
    for key in obj:
        res.append(key)
        if parent:
            prop_name = parent + '.' + key
        else:
            prop_name = key
        
        if isinstance(obj[key], list):
            for item in obj[key]:
                res.append(item)
        elif isinstance(obj[key], dict):
            __flatten_to_list(obj[key], prop_name, res)

    return res


def __json_to_csv(json_input, row_order):
    csv_rows = []
    title = '"Crop Budget"'
    csv_data = []
    
    first_key = list(json_input.keys())[0]
    first_row = json_input[first_key]['data']
    keys = list(first_row.keys())
    header = [title] + keys
    header_str = ','.join(header)
    csv_rows.append(header_str)
    
    for name in row_order:
        if name in json_input:
            row_name = [f'"{name}"']
            row = json_input[name]['data']
            values = list(row.values())
            values_str = [str(value) for value in values]
            row_data = row_name + values_str
            row_str = ','.join(row_data)
            csv_rows.append(row_str)
    
    return '\n'.join(csv_rows)


def __camel_case_to_snake_case(col):
    res = [col[0].lower()]
    for c in col[1:]:
        if c in ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            res.append('_')
            res.append(c.lower())
        else:
            res.append(c)
     
    return ''.join(res)
