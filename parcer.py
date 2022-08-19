#!/bin/bash
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import pandas as pd

print('Start. Please wait 3-5 min.')

url1 = 'http://eis0.clevo.com.tw/RMA_Schedule/Login.asp?company=G'
payload = {'UserID': 'test', 'Password': 'test'}

with requests.Session() as s:
    post = s.post(url1, data=payload)

    page = 1
    url2 = f'http://eis0.clevo.com.tw/RMA_Schedule/RMA_SCHEDULE_List.asp?n={page}&A_Status=A&rmano='
    get = s.get(url2)
    soup = BeautifulSoup(get.content, 'lxml')
    a = soup.find_all('a', href=True, text=True)
    print(f'Pages: {int(a[-1].text)}')
    last_page = int(a[-1].text) * 10 + 10
    first_time = 1

    res = []

    while page != last_page:
        url2 = f'http://eis0.clevo.com.tw/RMA_Schedule/RMA_SCHEDULE_List.asp?n={page}&A_Status=A&rmano='
        get = s.get(url2)
        soup = BeautifulSoup(get.content, 'lxml')
        table = soup.find('table')
        table_rows = table.find_all('tr')[5::2]
        table_comments = table.find_all('tr')[6::2]

        for tr, tr_comment in zip(table_rows, table_comments):
            td = tr.find_all('td')
            row = [tr.text for tr in td if tr.text]
            com_td = tr_comment.find_all('td')
            row_comment = [tr_comment.text.strip() for tr_comment in com_td if tr_comment.text.strip()]
            add_com = row_comment[1]
            add_com_str = add_com[15:].strip()

            row.append(add_com_str)
            res.append(row)

        if first_time == 1:
            page += 9
            first_time = 0
        else:
            page += 10


df = pd.DataFrame(res, columns=["RMA  No.", "RMA Status", "Issue Date", "Received Date", "Repair Date", "Charge Date", "Charge Status", "Ship Date", "Invoice Date", "S", "M", "I", "P", "Notes"])
df_obj = df.select_dtypes(['object'])
df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())
df.to_csv (r'./RMA_Schedule.csv', index=False, header=True)
print('Create file RMA_Schedule.csv in /Home')
print('End.')
