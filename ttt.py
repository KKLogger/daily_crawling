import json
from ast import literal_eval

local_path = "C:/Users/jlee/Desktop/"

if __name__ == '__main__':
    for server_num in range(63, 67):
        with open(local_path + 'result{server_num}_t.json'.format(server_num=server_num), encoding='utf-8-sig', errors='ignore') as f:
            str_data = f.read()
        str_data = str(str_data)
        str_data = str_data[1:-1].strip()
        str_data = str_data.replace('"{', '{')
        str_data = str_data.replace('}"', '}')
        str_data = str_data.replace('\\"', '"')
        str_data = str_data.replace('\\n', "")
        str_data = str_data.replace('\n', "")
        str_data = str_data.replace(']},', "]}///")
        str_data = str_data.replace(
            '"noRegisterPeriod": "none"},', '"noRegisterPeriod": "none"}///')
        str_datas = str_data.split('///')
        str_datas = [x.replace("'", '"').strip() for x in str_datas]
        num = 0
        print(len(str_datas))
        # print(str_datas[3])
        # input()
        for str_data in str_datas:
            num += 1
            try:
                dict_data = literal_eval(str_data)
                json_data = json.loads(str_data)
                with open(local_path+'result28_t.json', 'a', encoding='utf-8-sig') as ff:
                    json.dump(dict_data, ff, indent=4,
                              ensure_ascii=False, sort_keys=True)
            except:

                print("Fail", num)
