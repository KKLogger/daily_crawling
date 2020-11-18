import json
from ast import literal_eval
import pandas as pd
from data_processing import *
local_path = "C:/Users/jlee/Desktop/test/"


df1 = pd.read_csv(local_path + 'filtered_url_1.csv')
df2 = pd.read_csv(local_path + 'filtered_url_2.csv')
df3 = pd.read_csv(local_path + 'filtered_url_3.csv')
df4 = pd.read_csv(local_path + 'filtered_url_4.csv')
df5 = pd.read_csv(local_path + 'filtered_url_5.csv')
df6 = pd.read_csv(local_path + 'filtered_url_6.csv')
df = pd.read_csv(local_path + 'filtered_url.csv')


past =  list(df['url'])
current = list(df1['url'])+list(df2['url'])+list(df3['url'])+list(df4['url'])+list(df5['url'])+list(df6['url'])
print(len(past))
print(len(current))
n,s = compare_car(past,current)

print(len(n),len(s))

