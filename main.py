import sqlite3
import pandas as pd

pd.set_option('display.max_columns', 15)
pd.set_option('display.width', None)

connection = sqlite3.connect("sample.sqlite")
account = pd.read_sql_query('select * from account', connection)
account_date_session = pd.read_sql_query('select * from account_date_session', connection)
iap_purchase = pd.read_sql_query('select * from iap_purchase', connection)

print(account.head(), '\n')
print(account_date_session.head(), '\n')
print(iap_purchase.head(), '\n')
