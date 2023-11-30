import sqlite3
from ast import literal_eval

import pandas as pd
import plotly.graph_objs as go

# Display options in order not to be constrained in some cases of printing
pd.set_option('display.max_columns', 15)
pd.set_option('display.max_rows', 120)
pd.set_option('display.width', None)

# Connecting to the data source, creating dataframes for each table
connection = sqlite3.connect("data/sample.sqlite")
account = pd.read_sql_query('select * from account', connection)
iap_purchase = pd.read_sql_query('select * from iap_purchase', connection)

# Deleting null values from the dataframe because they would conflict when mapping the country names
account.dropna(inplace=True)

# Importing dictionary of 'country_code':'country_name'
with open('data/country_names.json', 'r') as f:
    data = literal_eval(f.read())
account['country_name'] = [data[k] for k in account['country_code']]

# Merging data from account to iap_purchase using account_id key (equal to SQL Left (Outer) Join)
average_per_country = pd.merge(iap_purchase,
                               account,
                               on='account_id',
                               how='left')

# Deleting null values from the dataframe because they would conflict in the plot
average_per_country.dropna(inplace=True)

# Converting cents to euros
average_per_country['iap_price_usd_cents'] = average_per_country['iap_price_usd_cents'] / 100.

# Grouping data by country_name and averaging sales made in each country throughout the year
average_per_country = average_per_country.groupby('country_name')['iap_price_usd_cents'].mean()
average_per_country = average_per_country.reset_index()

# Plot with trend line using 'lowess' (data smoothing)
# locations - each country recorded in country_names column
# z - average revenue per user per country in euros
data = dict(type='choropleth',
            locations=average_per_country['country_name'],
            locationmode='country names',
            colorscale='Portland',
            text=['Country'],
            z=average_per_country['iap_price_usd_cents'],
            colorbar={'title': 'Average revenue per user in €'})

layout = dict(title='Average revenue per user per country in the year 2016',
              geo=dict(projection={'type': 'mercator'})
              )
users_map = go.Figure(data=[data], layout=layout)
users_map.show()
