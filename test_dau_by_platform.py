import sqlite3

import pandas as pd
import plotly.express as px

# Display options in order not to be constrained in some cases of printing
pd.set_option('display.max_columns', 15)
pd.set_option('display.max_rows', 120)
pd.set_option('display.width', None)

# Connecting to the data source, creating dataframes for each table
connection = sqlite3.connect("data/sample.sqlite")
account = pd.read_sql_query('select * from account', connection)
account_date_session = pd.read_sql_query('select * from account_date_session', connection)

# Analysing data to find how are they shaped and their quality (some of the check were made only using SQL)

merged = pd.merge(account_date_session,
                  account,
                  on='account_id',
                  how='left')

print(merged.head())

# Grouping data by date and counting how many account_ids (unique values) occurred in each day
dau_over_time_series = merged.groupby(['created_platform', 'date'])['account_id'].count()
dau_over_time = dau_over_time_series.reset_index()


print(dau_over_time.head())

# Plot with trend line using 'lowess' (data smoothing)
# x - days of the year 2016
# y - number of users logged each day
# trenline - local polynomial regression to create a readable relevant trend line
# trendline_options - fraction setting smoothing (the smaller the "less smooth" it will be)
dau = px.scatter(dau_over_time, x=pd.to_datetime(dau_over_time['date']), y='account_id',
                 color='created_platform',
                 title='Daily Active Users',
                 trendline="lowess",
                 trendline_options=dict(frac=0.1),
                 labels=dict(x="Days throughout year 2016",
                             y="Total users each day",
                             total_daily_users="Total Daily Active Users",
                             trendline="Trend"),
                 trendline_color_override='green')

dau.update_traces(mode='lines')
dau.show()
