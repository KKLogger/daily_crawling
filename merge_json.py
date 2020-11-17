import json
from ast import literal_eval
import os
from datetime import datetime
import sys


if __name__ == '__main__':
    local_path = "/home/centos/result_from_servers/"

    # local_path = "C:/Users/jlee/Desktop/"
    result = list()

    options = sys.argv[1]
    if options == '1':
        str_list = list()
        for server_num in range(1, 64):
            with open(local_path + 'result{server_num}_t.json'.format(server_num=server_num), encoding='utf-8-sig', errors='ignore') as f:
                str_data = f.read()
            str_data = str(str_data)
            str_data = str_data[:]
            str_data = str_data.replace('{}', "")
            str_data = str_data.replace('}{', "}///{")
            str_datas = str_data.split('///')
            str_datas = [x.replace("'", '"') for x in str_datas]
            str_list = str_list + str_datas
        str_list = list(set(str_list))
        num = 0
        for str_data in str_list:
            num += 1
            try:
                dict_data = literal_eval(str_data)
                json_data = json.loads(str_data)
                result.append(dict_data)
            except:
                print("Fail", num)

            # os.remove(local_path+'result_t.json')
        print("총 json에 차량 개수 ", len(result))
        with open(local_path+'result.json', 'w', encoding='utf-8-sig') as ff:
            json.dump(result, ff, indent=4,
                      ensure_ascii=False, sort_keys=True)
    else:
        for server_num in range(34, 35):
            with open(local_path + 'result{server_num}_t.json'.format(server_num=server_num), encoding='utf-8-sig', errors='ignore') as f:
                str_data = f.read()
            str_data = str(str_data)
            str_data = str_data[:]
            str_data = str_data.replace('{}', "")
            str_data = str_data.replace('}{', "}///{")
            str_datas = str_data.split('///')
            str_datas = [x.replace("'", '"') for x in str_datas]
            num = 0
            print(len(str_datas))
            for str_data in str_datas:
                try:
                    dict_data = literal_eval(str_data)
                    json_data = json.loads(str_data)
                    with open(local_path+'result{options}_t.json'.format(options=options), 'w', encoding='utf-8-sig') as ff:
                        json.dump(dict_data, ff, indent=4,
                                  ensure_ascii=False, sort_keys=True)
                except:
                    print("Fail", num)

            # os.remove(
            #     local_path + 'result{server_num}_t.json'.format(server_num=server_num))
