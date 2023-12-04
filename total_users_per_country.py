import sqlite3
from ast import literal_eval

import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Connecting to the data source, creating dataframes for account table
connection = sqlite3.connect("data/sample.sqlite")
account = pd.read_sql_query('select * from account', connection)

# Deleting null values from the dataframe because they would conflict when mapping the country names
account.dropna(inplace=True)

# Importing dictionary of 'country_code':'country_name'
with open('data/country_names.json', 'r') as f:
    data = literal_eval(f.read())

# Creating new column country_name and filling it based on country_code using 'data' dictionary
account['country_name'] = [data[k] for k in account['country_code']]

# Grouping data by country_name and counting how many account_ids (unique values) occurred in each country + sorting
users_by_country = account.groupby('country_name')['account_id'].count()
users_by_country = users_by_country.reset_index()
users_by_country = users_by_country.sort_values(by='account_id', ascending=False)

# Plot with geographical split of total amount of users
# locations - each country recorded in country_names column
# z - total amounts of users in each country
map_data = go.Figure(go.Choropleth(
    locations=users_by_country['country_name'],
    locationmode='country names',
    colorscale='Portland',
    text=['Country'],
    z=users_by_country['account_id'],
    colorbar={'title': 'Total users'}
))

# Horizontal bar chart showing top 10 countries by total users
# x - top 10 amounts of users
# y - their countries
bar_chart_data = go.Figure(go.Bar(
    x=users_by_country['account_id'].nlargest(n=10),
    y=users_by_country['country_name'],
    hovertemplate='Total users: %{x}, Country: %{y} <extra></extra>',
    marker=dict(color=users_by_country['account_id'],
                colorscale='Portland'),
    orientation='h'))

# Preparing subplot grid and what types it will contain
subplot = make_subplots(rows=1, cols=2,
                        specs=[[{'type': 'choropleth'}, {'type': 'xy'}]])

# Add traces from figures to subplot
for trace in map_data.data:
    subplot.add_trace(trace, row=1, col=1)

for trace in bar_chart_data.data:
    subplot.add_trace(trace, row=1, col=2)

# Update and show layout of the Subplot
subplot.update_layout(title_text="Total amount of users in each country throughout the year 2016",
                      yaxis={'categoryorder': 'total ascending'},
                      margin=dict(l=60, r=60, t=50, b=50))
subplot.show()
