import sqlite3
from ast import literal_eval

import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

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

# Converting cents to USD
average_per_country['iap_price_usd'] = average_per_country['iap_price_usd_cents'] / 100.

# Grouping data by country_name and averaging sales made in each country throughout the year
average_per_country = average_per_country.groupby('country_name').agg(sum_sales=('iap_price_usd', 'sum'), count_dist=('account_id', 'nunique'))
# Creating new column with calculated average by distinct user + putting back to DataFrame and sorting
average_per_country['avg_per_user_per_country'] = average_per_country['sum_sales'] / average_per_country['count_dist']
average_per_country = average_per_country.reset_index()
average_per_country = average_per_country.sort_values(by='avg_per_user_per_country', ascending=False)

# Plot with geographical split by average sales by user in countries
# locations - each country recorded in country_names column
# z - average sales by user
map_data_one = go.Figure(go.Choropleth(
    locations=average_per_country['country_name'],
    locationmode='country names',
    colorscale='Portland',
    text=['Country'],
    z=average_per_country['avg_per_user_per_country'],
    colorbar={'title': 'Average revenue per user in $'}
))

# Horizontal bar chart showing top 10 countries by average sales per user
# x - top 10 averages by user
# y - their countries
bar_chart_data_one = go.Figure(go.Bar(
    x=average_per_country['avg_per_user_per_country'].nlargest(n=10),
    y=average_per_country['country_name'],
    hovertemplate='Total revenue: %{x}$, Country: %{y} <extra></extra>',
    marker=dict(color=average_per_country['avg_per_user_per_country'],
                colorscale='Portland'),
    orientation='h'))

# Preparing subplot grid and what types it will contain
subplot = make_subplots(rows=1, cols=2,
                        specs=[[{'type': 'choropleth'}, {'type': 'xy'}]])

# Add traces from figures to subplot
for trace in map_data_one.data:
    subplot.add_trace(trace, row=1, col=1)

for trace in bar_chart_data_one.data:
    subplot.add_trace(trace, row=1, col=2)

# Update and show layout of the Subplot
subplot.update_layout(title_text="Average revenue per user per country in the year 2016",
                      yaxis={'categoryorder': 'total ascending'},
                      margin=dict(l=60, r=60, t=50, b=50))
subplot.show()

# Filtering dataset only for countries with more than one user making purchases
average_per_country = average_per_country[average_per_country['count_dist'] > 1]

# Plot with geographical split by average sales by user in countries (more than one buyer)
# locations - each country recorded in country_names column
# z - average sales by user
map_data_more = go.Figure(go.Choropleth(
    locations=average_per_country['country_name'],
    locationmode='country names',
    colorscale='Portland',
    text=['Country'],
    z=average_per_country['avg_per_user_per_country'],
    colorbar={'title': 'Average revenue per user in $'}
))

# Horizontal bar chart showing top 10 countries by average sales per user (more than one buyer)
# x - top 10 averages by user
# y - their countries
bar_chart_data_more = go.Figure(go.Bar(
    x=average_per_country['avg_per_user_per_country'].nlargest(n=10),
    y=average_per_country['country_name'],
    hovertemplate='Total revenue: %{x}$, Country: %{y} <extra></extra>',
    marker=dict(color=average_per_country['avg_per_user_per_country'],
                colorscale='Portland'),
    orientation='h'))

# Preparing subplot grid and what types it will contain
subplot = make_subplots(rows=1, cols=2,
                        specs=[[{'type': 'choropleth'}, {'type': 'xy'}]])

# Add traces from figures to subplot
for trace in map_data_more.data:
    subplot.add_trace(trace, row=1, col=1)

for trace in bar_chart_data_more.data:
    subplot.add_trace(trace, row=1, col=2)

# Update and show layout of the Subplot
subplot.update_layout(title_text="Average revenue per user per country in the year 2016 with more than 1 purchasing account",
                      yaxis={'categoryorder': 'total ascending'},
                      margin=dict(l=60, r=60, t=50, b=50))
subplot.show()
