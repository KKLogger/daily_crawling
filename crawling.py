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

local_path = '/home/ec2-user/daily_crawling/'
remote_path = '/home/centos/result_from_servers/'
day = datetime.datetime.today().strftime('%Y%m%d')


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
                with open(local_path + '{day}.result{server_num}_t.json'.format(server_num=server_num,day=day), 'a', encoding='utf-8-sig') as outfile:
                    json.dump(temp, outfile, indent=4,
                              ensure_ascii=False, sort_keys=True)
        except Exception as e:
            print(f"error : {e}")



#########################main#################################
if __name__ == '__main__':

    server_num = sys.argv[1]
    ssh_manager = SSHManager()
    ssh_manager.create_ssh_client(
        "133.186.150.193", "centos", "gozjRjwu~!", key_filename=local_path + 'shopify.pem')  # 세션생성
    for idx in range(20):
        try:
            ssh_manager.get_file(remote_path + 'filtered_url_1.csv',
                                local_path + 'filtered_url_1.csv')  # 파일다운로드
            ssh_manager.get_file(remote_path + 'filtered_url_2.csv',
                                local_path + 'filtered_url_2.csv')  # 파일다운로드
            ssh_manager.get_file(remote_path + 'filtered_url_3.csv',
                                local_path + 'filtered_url_3.csv')  # 파일다운로드
            ssh_manager.get_file(remote_path + 'filtered_url_4.csv',
                                local_path + 'filtered_url_4.csv')  # 파일다운로드
            ssh_manager.get_file(remote_path + 'filtered_url_5.csv',
                                local_path + 'filtered_url_5.csv')  # 파일다운로드
            ssh_manager.get_file(remote_path + 'filtered_url_6.csv',
                                local_path + 'filtered_url_6.csv')  # 파일다운로드
            break
        except :
            time.sleep(300)
    r_df_1 = pd.read_csv(local_path + 'filtered_url_1.csv')
    r_df_2 = pd.read_csv(local_path + 'filtered_url_2.csv')
    r_df_3 = pd.read_csv(local_path + 'filtered_url_3.csv')
    r_df_4 = pd.read_csv(local_path + 'filtered_url_4.csv')
    r_df_5 = pd.read_csv(local_path + 'filtered_url_5.csv')
    r_df_6 = pd.read_csv(local_path + 'filtered_url_6.csv')

    car_urls = list(r_df_1['url']) + list(r_df_2['url']) + \
        list(r_df_3['url']) + list(r_df_4['url']) + \
        list(r_df_5['url']) + list(r_df_6['url'])
    os.remove(local_path + 'filtered_url_1.csv')
    os.remove(local_path + 'filtered_url_2.csv')
    os.remove(local_path + 'filtered_url_3.csv')
    os.remove(local_path + 'filtered_url_4.csv')
    os.remove(local_path + 'filtered_url_5.csv')
    os.remove(local_path + 'filtered_url_6.csv')

    car_urls, temp = split_car(car_urls)
    num_per_url = len(car_urls)//29

    server_num = int(server_num)
    start_idx = 0
    if server_num * num_per_url > len(car_urls):
        car_urls = car_urls[start_idx + num_per_url*(server_num-1):]
    else:
        car_urls = car_urls[start_idx + num_per_url *
                            (server_num-1):num_per_url*(server_num)]
    print(len(car_urls))
    while True:
        idx = 0
        try:
            option_codes = get_optioncodes(car_urls[idx])
            break
        except:
            print('option_codes error')
            idx += 1

    start(car_urls, server_num, option_codes)
    for i  in range(20):
        try:
            ssh_manager.send_file(local_path + '{day}.result{server_num}_t.json'.format(server_num=server_num,day=day),
                            remote_path + '{day}.result{server_num}_t.json'.format(server_num=server_num,day=day))  # 파일전송=
            os.remove(
                local_path + '{day}.result{server_num}_t.json'.format(server_num=server_num,day=day))
            break
        except :
            pass

    ssh_manager.close_ssh_client()  # 세션종료
