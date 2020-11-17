import json
from ast import literal_eval
import os
from datetime import datetime
local_path = "/home/centos/result_from_servers/"
result = list()
for server_num in range(1, 31):
    with open(local_path + 'result{server_num}_t.json'.format(server_num=server_num), encoding='utf-8-sig', errors='ignore') as f:
        str_data = f.read()
    str_data = str(str_data)
    str_data = str_data[:]
    str_data = str_data.replace('{}', "")
    str_data = str_data.replace('}{', "}///{")
    str_datas = str_data.split('///')
    str_datas = [x.replace("'", '"') for x in str_datas]
    num = 0

    for str_data in str_datas:
        num += 1
        try:
            dict_data = literal_eval(str_data)
            json_data = json.loads(str_data)
            result.append(dict_data)
        except:
            print("Fail", num)
    print("총 json에 차량 개수 ", len(result))
    # os.remove(local_path+'result_t.json')
with open(local_path+'result_{date}_{len}건.json'.format(date=datetime.today(), len=len(result)), 'w', encoding='utf-8-sig') as ff:
    json.dump(result, ff, indent=4, ensure_ascii=False, sort_keys=True)
