import requests
import time
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.macrotrends.net/stocks/charts/TSLA/tesla/revenue"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

time.sleep(10)
response = requests.get(url, headers=headers)

if response:
    soup = BeautifulSoup(response.text, 'html')
    soup

tables = soup.find_all('table', class_="historical_data_table")

for i, table in enumerate(tables):
    if ('Tesla Quarterly Revenue' in str(table)):
        df_index = i

tesla_df = pd.DataFrame(columns=['date', 'revenue'])
for row in tables[df_index].tbody.find_all('tr'):
    col = row.find_all('td')
    if (col != []):
        date = col[0].text
        revenue = col[1].text.replace("$", "").replace(",", "")
        tesla_df = pd.concat([tesla_df, pd.DataFrame({'date': date, 'revenue': revenue}, index=[0])], ignore_index=True)

tesla_df=tesla_df[tesla_df['revenue'] != ""]

####SQLite3####
import sqlite3

#create connection
connection = sqlite3.connect("tesla.db")

#create table
connection.execute('''CREATE TABLE revenue
                   (date NUMERIC,
                   revenue NUMERIC)''')

#populate table
tesla_df.to_sql('revenue', connection, if_exists='replace', index=False)
query = 'SELECT * FROM revenue'
for row in connection.execute(query):
    print(row)

#commit changes
connection.commit()

####Plots####
import matplotlib.pyplot as plt
import seaborn as sns

#1 Line plot shows the evolution of revenue over the periods:

sns.lineplot(x='date', y='revenue', data=tesla_df, color='purple')
plt.title("Tesla's Revenue")
plt.xlabel('Date')
plt.ylabel('Revenue')
plt.tight_layout()
plt.show()

#2 Bar plot shows the revenue per year:

annual_revenue = tesla_df.groupby(tesla_df['date'].dt.year)['revenue'].sum()
annual_revenue.plot(kind='bar', colormap='cividis')
plt.title("Tesla's Revenue per Year")
plt.xlabel('Date')
plt.ylabel('Revenue')
plt.xticks(rotation=0, fontsize='small')
plt.yticks(fontsize='small')
plt.tight_layout()
plt.show()

#3 Bar plot with revenue per quarter stacked per year

df_stacked = tesla_df.copy()

df_stacked['year'] = df_stacked['date'].dt.year
df_stacked['month'] = df_stacked['date'].dt.month

df_stacked.head()
df_stacked['month'].replace(6, 'Q2', inplace=True)
df_stacked['month'].replace(3, 'Q1', inplace=True)
df_stacked['month'].replace(9, 'Q3', inplace=True)
df_stacked['month'].replace(12, 'Q4', inplace=True)

stacked = df_stacked.groupby(['year', 'month'])['revenue'].sum().unstack()

stacked.plot(kind='bar', stacked=True, colormap='cividis')
plt.title("Tesla's Revenue per Quarter Stacked per Year")
plt.xlabel('Year')
plt.ylabel('Revenue')
plt.legend(title='Quarter', bbox_to_anchor=(1, 1))
plt.xticks(rotation=0, fontsize='small')
plt.yticks(fontsize='small')
plt.tight_layout()
plt.show()
