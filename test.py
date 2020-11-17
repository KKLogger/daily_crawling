import pandas as pd
from crawl_info import *
from data_processing import *
from SSHManager import SSHManager
import time
import random
import json

local_path = 'C:/Users/jlee/Desktop/test/'

def start(urls, server_num, option_codes):
    num = 0

    for url in urls:

        temp = dict()
        # try:
        #     temp = get_car_info(
        #         url, temp)
        # except:
        #     print("error in car info")
        # try:
        #     temp.update(get_history(
        #         url, temp))
        # except:
        #     print("error in car history")
        # try:
        #     temp['Options'] = get_options(
        #         url)
        # except:
        #     print("error in car options")
        # try:
        #     temp = get_checkdata(url, temp)
        # except:
        #     print("error in car checkdata")
        try:
            temp, carHistorySeq, chk_tag_url = get_car_info(url, temp)
            temp.update(get_history(url, temp, carHistorySeq))
            temp['Options'] = get_options(url, option_codes)
            temp = get_checkdata(url, temp, chk_tag_url)
            num += 1

            print("현재 : ", num)
            if bool(temp):
                with open(local_path + 'result{server_num}_t.json'.format(server_num=server_num), 'a', encoding='utf-8-sig') as outfile:
                    json.dump(temp, outfile, indent=4,
                              ensure_ascii=False, sort_keys=True)
        except Exception as e:
            print(f"error : {e}")


if __name__ == '__main__':
    df = pd.read_csv(local_path+'filtered_url.csv')
    urls = df['url']
    urls, _ = split_car(urls)
    option_codes = get_optioncodes(urls[0])
    print(len(urls))
    start(urls,1,option_codes)