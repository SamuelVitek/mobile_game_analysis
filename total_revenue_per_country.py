import sqlite3
from ast import literal_eval

import pandas as pd
import plotly.graph_objects as go
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
    countries_data = literal_eval(f.read())
account['country_name'] = [countries_data[k] for k in account['country_code']]

# Merging data from account to iap_purchase using account_id key (equal to SQL Left (Outer) Join)
revenue_per_country = pd.merge(iap_purchase,
                               account,
                               on='account_id',
                               how='left')

# Deleting null values from the dataframe because they would conflict in the plot
revenue_per_country.dropna(inplace=True)

# Converting cents to euros
revenue_per_country['iap_price_usd_cents'] = revenue_per_country['iap_price_usd_cents'] / 100.

# Grouping data by country_name and summing sales made in each country throughout the year
revenue_per_country = revenue_per_country.groupby('country_name')['iap_price_usd_cents'].sum()
revenue_per_country = revenue_per_country.reset_index()
revenue_per_country = revenue_per_country.sort_values(by='iap_price_usd_cents', ascending=False)

# Plot with trend line using 'lowess' (data smoothing)
# locations - each country recorded in country_names column
# z - total revenue generated by users in each country in euros
map_data = go.Figure(go.Choropleth(
    locations=revenue_per_country['country_name'],
    locationmode='country names',
    colorscale='Portland',
    text=['Country'],
    z=revenue_per_country['iap_price_usd_cents'],
    colorbar={'title': 'Total revenue in $'}
))

bar_chart_data = go.Figure(go.Bar(
    x=revenue_per_country['iap_price_usd_cents'].nlargest(n=10),
    y=revenue_per_country['country_name'],
    hovertemplate='Total revenue: %{x}$, Country: %{y} <extra></extra>',
    marker=dict(color=revenue_per_country['iap_price_usd_cents'],
                colorscale='Portland'),
    orientation='h'))

# Create Subplot with two columns and one row
subplot = make_subplots(rows=1, cols=2,
                        specs=[[{'type': 'choropleth'}, {'type': 'xy'}]])

# Add traces from figures to subplot
for trace in map_data.data:
    subplot.add_trace(trace, row=1, col=1)

for trace in bar_chart_data.data:
    subplot.add_trace(trace, row=1, col=2)

# Update and show layout of the Subplot
subplot.update_layout(title_text="Total revenue generated by each country in the year 2016",
                      yaxis={'categoryorder': 'total ascending'},
                      margin=dict(l=60, r=60, t=50, b=50))
subplot.show()
