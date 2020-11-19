import json
import os
from ast import literal_eval
import pandas as pd


def df_to_dict(df):
    '''
    >>>데이터 프레임
    >>>dict로 변환하여 반환
    '''
    result = df.to_dict()
    for key, value in result.items():
        result[key] = list(value.values())[0]
    return result


def split_car(url_price):
    '''
    input : url///price 으로 된 str list
    ouput : url 과 price를 split ,price list 와 url list로  반환
    '''
    price = list()
    url = list()
    for item in url_price:
        try:
            price.append(item.split('///')[1])
        except:
            pass
        url.append(item.split('///')[0])
    return url, price


def get_dateform(date):
    '''
    날짜 데이터 형식 변환
    '''
    y = date[3]
    m = date[2]
    d = date[1]
    time = date[4]
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for i, month in enumerate(months):
        if month == m:
            m = i+1
            break
    result = str(y) + "년" + str(m) + "월" + str(d) + "일 " + str(time)
    return result


def compare_car(p_car_urls, r_car_urls):
    '''
    input : url///price list 어제 수집한 데이터 와 오늘 수집한 데이터
    output : 두 list 를 비교하여 신규등록 차량 리스트와 판매완료 차량 리스트 반환
    '''
    chage_car_urls = (set(r_car_urls) - set(p_car_urls)
                      ) & (set(r_car_urls) - set(p_car_urls))
    new_car_urls = set(r_car_urls) - set(p_car_urls)
    sold_car_urls = set(p_car_urls) - set(r_car_urls)
    return new_car_urls, sold_car_urls


def split_car(url_price):
    '''
    input : url///price 으로 된 str list
    ouput : url 과 price를 split ,price list 와 url list로  반환
    '''
    price = list()
    url = list()
    for item in url_price:
        try:
            price.append(item.split('///')[1])
        except:
            pass
        url.append(item.split('///')[0])
    return url, price
