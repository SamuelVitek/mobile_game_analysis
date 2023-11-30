import sqlite3
from ast import literal_eval

import pandas as pd
import plotly.graph_objs as go

# Display options in order not to be constrained in some cases of printing
pd.set_option('display.max_columns', 15)
pd.set_option('display.max_rows', 120)
pd.set_option('display.width', None)

# Connecting to the data source, creating dataframes for each table
connection = sqlite3.connect("sample.sqlite")
account = pd.read_sql_query('select * from account', connection)

# Deleting null values from the dataset because they would conflict in the plot
account.dropna(inplace=True)

# Importing dictionary of 'country_code':'country_name'
with open('country_names.json', 'r') as f:
    data = literal_eval(f.read())

# Creating new column country_name and filling it based on country_code using 'data' dictionary
account['country_name'] = [data[k] for k in account['country_code']]

# Grouping data by country_name and counting how many account_ids (unique values) occurred in each country
users_by_country = account.groupby('country_name')['account_id'].count()
users_by_country = users_by_country.reset_index()

# Plot with trend line using 'lowess' (data smoothing)
# locations - each country recorded in country_names column
# z - total amounts of users in each country
data = dict(type='choropleth',
            locations=users_by_country['country_name'],
            locationmode='country names',
            colorscale='Portland',
            text=['Country'],
            z=users_by_country['account_id'],
            colorbar={'title': 'Amount of active users'})

layout = dict(title='Total amount of users in each country throughout the year 2016',
              geo=dict(projection={'type': 'mercator'})
              )
users_map = go.Figure(data=[data], layout=layout)
users_map.show()
