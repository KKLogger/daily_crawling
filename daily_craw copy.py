from crawl_info import *
from SSHManager import SSHManager


# local_path = '/home/ec2-user/daily_crawling/'
local_path = '/C:/Users/jlee/Desktop/test/'
remote_path = '/home/centos/result_from_servers/'


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
    '''
    >>> main
    '''
    # server_num = int(sys.argv[1])
    server_num = 30
    ssh_manager = SSHManager()
    ssh_manager.create_ssh_client(
        "133.186.150.193", "centos", "gozjRjwu~!", key_filename=local_path + 'shopify.pem')  # 세션생성
    '''
    >>> data load
    '''
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
    r_df_1 = pd.read_csv(local_path + 'filtered_url_1.csv')
    r_df_2 = pd.read_csv(local_path + 'filtered_url_2.csv')
    r_df_3 = pd.read_csv(local_path + 'filtered_url_3.csv')
    r_df_4 = pd.read_csv(local_path + 'filtered_url_4.csv')
    r_df_5 = pd.read_csv(local_path + 'filtered_url_5.csv')
    r_df_6 = pd.read_csv(local_path + 'filtered_url_6.csv')
    p_df = pd.read_csv(local_path + 'filtered_url.csv')
    r_car_urls = list(r_df_1['url']) + list(r_df_2['url']) + \
        list(r_df_3['url']) + list(r_df_4['url']) + \
        list(r_df_5['url']) + list(r_df_6['url'])
    p_car_urls = list(p_df['url'])
    os.remove(local_path + 'filtered_url_1.csv')
    os.remove(local_path + 'filtered_url_2.csv')
    os.remove(local_path + 'filtered_url_3.csv')
    os.remove(local_path + 'filtered_url_4.csv')
    os.remove(local_path + 'filtered_url_5.csv')
    os.remove(local_path + 'filtered_url_6.csv')
    '''
    >>> 새로운 데이터 갱신
    '''
    r_df = pd.DataFrame(data=r_car_urls, columns=['url'])
    r_df.to_csv(local_path + 'filtered_url.csv')
    '''
    >>>url,price 비교 후 신차,판완차 저장
    '''
    new_car, sold_car = compare_car(p_car_urls, r_car_urls)
    print(len(new_car))
    print(len(sold_car))
    input()
    new_url, new_price = split_car(new_car)
    sold_url, sold_price = split_car(sold_car)
    '''
    >>> 판매 완료된 차량 저장
    '''
    if server_num == 30:
        sold_dict = {
            "url": sold_url,
            "price": sold_price
        }
        s_df = pd.DataFrame(sold_dict)
        s_df.to_csv(local_path +
                    'sold_car.csv', encoding='euc-kr')
        ssh_manager.send_file(local_path + 'sold_car.csv',
                              remote_path + 'sold_car.csv')  # 파일전송
        os.remove(local_path + 'sold_car.csv')
    '''
    >>>신규 등록차량 차량 정보 수집 !!!서버에 분배 
    '''

    per_num = len(new_url)//29
    if server_num * per_num > len(new_url):
        new_url = new_url[per_num*(server_num-1):]
    else:
        new_url = new_url[per_num*(server_num-1):per_num*(server_num)]
    start(new_url, server_num)

    ssh_manager.send_file(local_path + 'result{server_num}_t.json'.format(server_num=server_num),
                          remote_path + 'result{server_num}_t.json'.format(server_num=server_num))  # 파일전송

    os.remove(
        local_path + 'result{server_num}_t.json'.format(server_num=server_num))

    ssh_manager.close_ssh_client()  # 세션종료
