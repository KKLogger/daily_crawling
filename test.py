import pandas as pd
from crawl_info import *
from data_processing import *
from SSHManager import SSHManager
import time
import random
import json
import sys
import os
import datetime
import random

# local_path = "/home/ec2-user/daily_crawling/"
# remote_path = "/home/centos/result_from_servers/"
local_path = 'D:/desktop/아름드리/0101/'
day = datetime.datetime.today().strftime("%Y%m%d")
random_int = random.randint(25,40)

def start(urls, server_num, option_codes):
    num = 0

    for url in urls:

        temp = dict()
        temp, carHistorySeq, chk_tag_url = get_car_info(url, temp)
        temp.update(get_history(url, temp, carHistorySeq))
        temp["Options"] = get_options(url, option_codes)
        temp = get_checkdata(url, temp, chk_tag_url)
        # try:
        #     temp, carHistorySeq, chk_tag_url = get_car_info(url, temp)
        # except Exception as e:
        #     print(f"error in get_car_info : {e}")
        # try:
        #     temp.update(get_history(url, temp, carHistorySeq))
        # except Exception as e:
        #     print(f"error in get_history : {e}")
        # try:
        #     temp["Options"] = get_options(url, option_codes)
        # except Exception as e:
        #     print(f"error in get_options : {e}")
        # try:
        #     temp = get_checkdata(url, temp, chk_tag_url)
        #     num += 1
        # except Exception as e:
        #     print(f"error in get_checkdata : {e}")
        print("현재 : ", num)
        try:
            if bool(temp):
                with open(
                    local_path
                    + "{day}.result{server_num}_t.json".format(
                        server_num=server_num, day=day
                    ),
                    "a",
                    encoding="utf-8-sig",
                ) as outfile:
                    json.dump(
                        temp, outfile, indent=4, ensure_ascii=False, sort_keys=True
                    )
        except Exception as e:
            print(f"error in dump : {e}")

if __name__ == "__main__":

    server_num = 15

    r_df_1 = pd.read_csv(local_path + "filtered_url_1.csv")
    r_df_2 = pd.read_csv(local_path + "filtered_url_2.csv")
    r_df_3 = pd.read_csv(local_path + "filtered_url_3.csv")
    r_df_4 = pd.read_csv(local_path + "filtered_url_4.csv")
    r_df_5 = pd.read_csv(local_path + "filtered_url_5.csv")
    r_df_6 = pd.read_csv(local_path + "filtered_url_6.csv")

    car_urls = (
        list(r_df_1["url"])
        + list(r_df_2["url"])
        + list(r_df_3["url"])
        + list(r_df_4["url"])
        + list(r_df_5["url"])
        + list(r_df_6["url"])
    )

    car_urls, temp = split_car(car_urls)
    num_per_url = len(car_urls) // 29

    server_num = int(server_num)
    start_idx = 0
    if server_num * num_per_url > len(car_urls):
        car_urls = car_urls[start_idx + num_per_url * (server_num - 1) :]
    else:
        car_urls = car_urls[
            start_idx + num_per_url * (server_num - 1) : num_per_url * (server_num)
        ]
    while True:
        idx = 0
        try:
            option_codes = get_optioncodes(car_urls[idx])
            break
        except:
            print("option_codes error")
            idx += 1
            if idx > len(car_urls):
                break

    start(car_urls, server_num, option_codes)