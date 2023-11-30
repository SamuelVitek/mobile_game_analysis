import sqlite3

import pandas as pd
import plotly.express as px

# Display options in order not to be constrained in some cases of printing
pd.set_option('display.max_columns', 15)
pd.set_option('display.max_rows', 120)
pd.set_option('display.width', None)

# Connecting to the data source, creating dataframes for each table
connection = sqlite3.connect("sample.sqlite")
account = pd.read_sql_query('select * from account', connection)
account_date_session = pd.read_sql_query('select * from account_date_session', connection)
iap_purchase = pd.read_sql_query('select * from iap_purchase', connection)

# Analysing data to find how are they shaped and their quality (some of the check were made only using SQL)
print('Headers, to see how the data look')
print(account.head(), '\n')
print(account_date_session.head(), '\n')
print(iap_purchase.head(), '\n')

print('\n', 'Counts to find empty values')
print(account.count(), '\n')
print(account_date_session.count(), '\n')
print(iap_purchase.count(), '\n')

# Grouping data by date and counting how many account_ids (unique values) occurred in each day
dau_over_time_series = account_date_session.groupby('date')['account_id'].count()
dau_over_time = dau_over_time_series.reset_index()

# Plot with trend line using 'lowess' (data smoothing)
# x-axis - days of the year 2016
# y-axis - number of users logged each day
dau = px.scatter(dau_over_time_series, x=pd.to_datetime(dau_over_time['date']).unique(), y='account_id',
                 title='Daily Active Users',
                 trendline="lowess",
                 trendline_options=dict(frac=0.1),
                 labels=dict(x="Days throughout year 2016", total_daily_users="Total Daily Active Users",
                             trendline="Trend"),
                 trendline_color_override='orangered')

dau.update_traces(mode='lines')
dau.show()
