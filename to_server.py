import os
import sys
from ast import literal_eval
import json
import requests
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import paramiko
from scp import SCPClient
import time
import random
from fake_useragent import UserAgent


def get_car_info(url, temp):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'www.kbchachacha.com',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = bs(response.text, 'html.parser')
    # if soup.find('h2') is None:
    #     raise Exception("blocked")
    Cookie = response.cookies.get('cha-cid')
    Cookie = "cha-cid=" + Cookie + ";"
    carSeq = url[url.index('?carSeq=')+len('?carSeq='):]
    json_url = 'https://www.kbchachacha.com/public/car/common/recent/car/list.json'
    json_headers = {
        'Accept': '*/*',
        'Accept-Encoding': "gzip, deflate, br",
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': "keep-alive",
        "Content-Length": "723",
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'www.kbchachacha.com',
        'Origin': 'https://www.kbchachacha.com',
        'Pragma': 'no-cache',
        'Referer': url,
        'Cookie': Cookie,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
        'X-AJAX': 'true',
    }
    json_data = {
        'gotoPage': '1',
        'pageSize': '1',
        'carSeqVal': carSeq
    }
    try:
        res_json = requests.post(
            json_url, headers=json_headers, data=json_data)
        car_dict = res_json.json()
        car_dict = car_dict['list'][0]
        temp['Manufacturer'] = car_dict['makerName']
        temp['Model'] = car_dict['carName']
        temp['Badge'] = car_dict['modelName']
        temp['Grade'] = car_dict['gradeName']
    except:
        temp['Manufacturer'] = 'null'
        temp['Model'] = 'null'
        temp['Badge'] = 'null'
        temp['Grade'] = 'null'
    car_price = soup.find(
        'div', {'class': 'car-buy-price'}).find('div').find('strong').text
    car_info1 = soup.find('dl', {'class': 'claerFix'}).find_all('dd')
    car_info1 = [x.text.strip().replace(' ', '') for x in car_info1]
    car_info2 = soup.find('div', {'class': 'detail-info02'}).find_all('dd')
    car_info2 = [x.text.strip().replace(' ', '') for x in car_info2]
    car_info = car_info1 + car_info2

    car_year = car_info[1]
    car_year = car_year[car_year.index('(')+1:car_year.index(')')]
    try:
        if soup.find('div', {'class': 'suc-price'}) is None:
            if soup.find_all('div', {'class': 'car-buy-debt-m'})[1].find('div').text == '리스 이용 금융상담문의':
                car_saletype = 'NORMAL_SALE'
                SeparationLease = "False"
            else:
                car_saletype = 'LEASE_SALE'
                SeparationLease = "True"
        else:
            car_saletype = 'LEASE_SALE'
            SeparationLease = "True"
    except:
        car_saletype = 'null'
        SeparationLease = "null"
    if soup.find('div', {'class': 'dealer-info-area'}).find('span', {'place-add'}).text == '개인판매자':
        SeparationDealer = 'False'
        SeparationIndividual = 'True'
    else:
        SeparationDealer = 'True'
        SeparationIndividual = 'False'
    service_list = [x.text for x in soup.find_all('div', {'class': 'line-ad'})]
    for service in service_list:
        if 'KB캐피탈 인증 중고차' in service:
            SeparationBrandCertified = 'True'
        else:
            SeparationBrandCertified = 'False'
        if '헛걸음보상서비스' in service:
            TrustCompensate = 'True'
        else:
            TrustCompensate = 'False'
    extend_service = soup.find(
        "div", {'class': 'service-list'}).find('a').get('class')
    if 'overlay' in extend_service:
        extend_service = 'False'
    else:
        extend_service = 'True'

    img_src = soup.find('ul', {'class': 'bxslider'}).find('img').get('src')
    try:
        t_date = requests.get(img_src).headers['Last-Modified'].split(' ')
        ModifiedDate = get_dateform(t_date)
    except:
        ModifiedDate = 'null'
    # 딜러 정보
    dealer_info = soup.find('div', {'class': 'dealer-cnt'})
    dealer_company = dealer_info.find('span', {'class', 'name'}).text.strip()
    dealer_location = dealer_info.find(
        'span', {'class', 'place-add'}).text.strip().split(' ')[0]
    dealer_phone = dealer_info.find(
        'div', {'class': 'dealer-tel-num'}).text.strip()

    dealerNo = soup.find('div', {'class': 'car-seller-info'}).find('img')
    find_txt = 'userImageError(this,'
    find_txt_len = len(find_txt)
    full_txt = dealerNo.get('onerror')
    if full_txt is None:
        dealerNo = 'null'
    else:
        dealerNo = full_txt[full_txt.index(
            find_txt)+find_txt_len: full_txt.index(')')].split(',')
        dealerNo = dealerNo[2].replace("'", '')
    # 값 입력

    if temp['Grade'] == '':
        temp['Grade'] = 'null'

    temp['Price'] = car_price.replace(',', '')
    temp['CarNumber'] = car_info[0]

    temp['Year'] = car_year
    # temp['Year'] = "20" + car_info[1].split('(')[0].split(' ')[0]
    temp['Mileage'] = car_info[2].replace(',', '')
    temp['FuelType'] = car_info[3]
    temp['Transmission'] = car_info[4]
    # temp['FuelEfficiency'] = car_info[5]
    temp['Category'] = car_info[6]
    temp['Displacement'] = car_info[7].replace(',', '')
    temp['Color'] = car_info[8]
    # temp['NoTax'] = car_info[9]
    if car_info[10] == "없음":
        temp['SeizingCount'] = "0건"
    else:
        temp['SeizingCount'] = car_info[10]
    if car_info[11] == "없음":
        temp['PledgeCount'] = "0건"
    else:
        temp['PledgeCount'] = car_info[11]

    temp['Id'] = car_info[12]
    temp['SeparationIndividual'] = SeparationIndividual
    temp['SeparationDealer'] = SeparationDealer
    temp['SeparationBrandCertified'] = SeparationBrandCertified
    temp['SeparationLease'] = SeparationLease
    temp['TrustEncarHomeservice'] = 'null'
    # temp['TrustKBHomeservice'] = HomeService
    temp['TrustEncarWarranty'] = 'null'
    # temp['TrustKBWarranty'] = Warranty
    temp['TrustEncarExtendWarranty'] = 'null'
    temp['TrustKBExtendWarranty'] = extend_service
    temp['TrustCompensate'] = TrustCompensate
    temp['TrustInspection'] = 'null'
    temp['ModifiedDate'] = ModifiedDate

    temp['CarSaleType'] = car_saletype
    # temp['전속이력'] = car_info[13]
    # temp['침수이력'] = car_info[14]
    # temp['useHis'] = car_info[15]
    # temp['소유자변경'] = car_info[16]
    temp['URL'] = url
    temp['SellerId'] = dealerNo

    temp['Location'] = dealer_location
    # FuelEfficiency
    # NoTax

    result = temp
    return result


def get_options(url):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Length': '42',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'www.kbchachacha.com',
        'Origin': 'https://www.kbchachacha.com',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'iframe',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }
    jump = len('?carSeq=')
    result = dict()
    index = url.index('?carSeq=') + jump
    carSeq = url[index:]
    data = {
        'layerId': 'layerCarOptionView',
        'carSeq': carSeq
    }
    res = requests.post(
        'https://www.kbchachacha.com/public/layer/car/option/list.kbc', headers=headers, data=data)
    soup = bs(res.text, 'html.parser')
    option_codes = soup.find('input', {'id': 'carOption'})[
        'value'].split(',')
    res = requests.post(
        'https://www.kbchachacha.com/public/car/option/code/list.json')
    json_datas = json.loads(res.text)
    json_datas = json_datas['optionList']
    all_option_codes = list()
    for json_data in json_datas:
        all_option_codes.append(json_data['optionCode'])
    temp = list()
    for code in all_option_codes:
        if code in option_codes:
            temp.append('포함')
        else:
            temp.append('미포함')
    columns = ['sun_roof', '제논라이트(HID)', 'aluminium_wheel', 'electrically_folded_side_mirror',
               '주간주행등(DLR)', '파노라마썬루프', 'loop_rack', 'LED리어램프', '하이빔 어시스트', 'ghost_door_closing', '자동슬라이딩도어', '전동사이드스탭',
               'head_lamp', 'heated_sheet_(front)', 'ventilation_sheet_(left)', 'power_steering_wheel', 'steering_wheel_remote_control', 'leather_seat', 'electric_sheet_(left)', 'electric_sheet_(right)', 'electric_seat_(back_seat)', 'memory_sheets_(left)', 'massage_sheet', '슈퍼비전계기판', 'paddle_shift', 'high_pass',
               'memory_sheets_(right)', 'heated_sheet_(rear)', '엠비언트라이트', '워크인시트', '전동햇빛가리개', 'ventilation_sheet_(right)', 'ventilation_seat_(back_seat)', 'rear_side_alert_system', '사이드&커튼에어백', 'airbag_(left)', 'airbag_(right)', 'rear_camera',
               '360_degree_around_view', '블랙박스', 'anti_lock_brake_(ABS)', 'electronic_control_suspension_(ECS)', 'anti_slipping_(TCS)', 'body_position_control_(ESC)', 'lane_departure_alarm_system_(LDWS)', '도난경보기', 'tire_pressure_sensor_(TPMS)', '무릎에어백', 'parking_detection_sensor', '전방카메라', '자동긴급제동(AEB)', 'smart_key', 'power_window', 'power_door_lock', 'automatic_air_conditioning', 'auto_wright', '자동주차시스템',
               'electric_parking_brake_(EPB)', 'head_up_display (HUD)', 'ECM_Roommirror', 'cruise_control', 'power_powered_trunk', 'heated_steering_wheel', 'radio_door_lock', 'rain_rensor', '스탑앤고', '무선충전', 'navigation', 'CD_player', 'CD체인저', 'front_seat_AV_monitor', 'MP3', 'AUX_terminal', 'USB_terminal', '핸즈프리', 'iPod 단자', 'rear_seat_AV_monitor', '스마트폰미러링', '내비게이션 (비순정)', 'bluetooth']
    # 추가 curtain/blind , motor_controlled_steering_wheel
    # 나누기 airbag (Side), airbag (curtain)
    df = pd.DataFrame([temp], columns=columns)
    result = df_to_dict(df)
    del(result['제논라이트(HID)'])
    del(result['주간주행등(DLR)'])
    del(result['파노라마썬루프'])
    del(result['LED리어램프'])
    del(result['하이빔 어시스트'])
    del(result['자동슬라이딩도어'])
    del(result['전동사이드스탭'])
    del(result['슈퍼비전계기판'])
    del(result['엠비언트라이트'])
    del(result['워크인시트'])
    del(result['전동햇빛가리개'])
    del(result['블랙박스'])
    del(result['도난경보기'])
    del(result['무릎에어백'])
    del(result['전방카메라'])
    del(result['자동긴급제동(AEB)'])
    del(result['자동주차시스템'])
    del(result['스탑앤고'])
    del(result['무선충전'])
    del(result['CD체인저'])
    del(result['MP3'])
    del(result['핸즈프리'])
    del(result['iPod 단자'])
    del(result['스마트폰미러링'])
    del(result['내비게이션 (비순정)'])
    t_value = result['사이드&커튼에어백']
    result['airbag_(side)'] = t_value
    result['airbag_(curtain)'] = t_value
    del(result['사이드&커튼에어백'])
    result['curtain/blind'] = 'null'
    result['motor_controlled_steering_wheel'] = 'null'
    return result


def df_to_dict(df):
    result = df.to_dict()
    for key, value in result.items():
        result[key] = list(value.values())[0]
    return result


def get_history(url, temp):

    response = requests.get(url)
    soup = bs(response.text, 'html.parser')
    soup = str(soup)
    str_len = len('carHistorySeq = "')
    carHistorySeq = soup[soup.index(
        'carHistorySeq = "')+str_len:soup.index('"', soup.index('carHistorySeq = "')+str_len)]

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Length': '50',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'www.kbchachacha.com',
        'Origin': 'https://www.kbchachacha.com',
        'Referer': url,
        'Sec-Fetch-Dest': 'iframe',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }
    datas = {
        'layerId': 'layerCarHistoryInfo',
        'carHistorySeq': carHistorySeq
    }
    response = requests.post(
        'https://www.kbchachacha.com/public/layer/car/history/info.kbc', headers=headers, data=datas)
    soup = bs(response.text, 'html.parser')

    registeredDate = soup.find('div', {'class': 'b-right'}).find_all('tr')
    registeredDate = registeredDate[3].find('td').text.strip()
    try:
        y = registeredDate.split('-')[0] + "년"
        m = registeredDate.split('-')[1] + "월"
        d = registeredDate.split('-')[2] + "일"
        registeredDate = y+m+d
    except:
        registeredDate = 'null'
    noRegisterPeriod = soup.find('div', {'class', 'box-line'})
    if noRegisterPeriod.find('div', {'class', 'date'}) is None:
        noRegisterPeriod = "none"
    else:
        noRegisterPeriod = noRegisterPeriod.find_all('div', {'class', 'date'})
        noRegisterPeriod = [x.text for x in noRegisterPeriod]

    historys = soup.find_all(
        'div', {'class': 'cmm-table table-l02 ct-line td-ptb-15'})
    HistDamage = dict()

    class dateform(object):
        def __init__(self, date):
            self.num = int(date.split(
                '-')[0] + date.split('-')[1] + date.split('-')[2])
            y = date.split('-')[0] + "년"
            m = date.split('-')[1] + "월"
            d = date.split('-')[2] + "일"
            date = y+m+d
            self.date = date

        def __str__(self):
            return self.date

        def __repr__(self):
            return "'"+self.date+"'"

        def __lt__(self, other):
            return self.num < other.num
    for num, history in enumerate(historys):
        # 내차 피해
        if history.find('tbody').find('tr').find_all('td')[1].text.strip() == '-':
            date = history.find('th').text.strip()
            y = date.split('-')[0] + "년"
            m = date.split('-')[1] + "월"
            d = date.split('-')[2] + "일"
            # date = y+m+d
            date = str(num) + ") : " + y+m+d
            price = history.find('span', {'class': 'cor-blue'}).text.strip()
            HistDamage[date] = price.replace(',', '')
    else:  # 상대차 피해
        pass

    try:
        hide_list = soup.find('ul', {'class': 'hide-list'}
                              ).find_all('span', {'class': 'txt'})
        a = hide_list[0].text.strip()
        b = hide_list[1].text.strip()
        c = hide_list[2].text.strip()
        if a == '없음':
            a = '0'
        if b == '없음':
            b = '0'
        if c == '없음':
            c = '0'

        temp['AccidentHistory'] = "전손: {a}, 도난 : {b}, 침수(전손/분손) : {c}".format(
            a=a, b=b, c=c)

        temp['UseHistory'] = hide_list[3].text.strip()
        temp['MyDamage'] = hide_list[4].text.strip().replace(',', '')
        temp['OtherDamage'] = hide_list[5].text.strip().replace(',', '')
        temp['NumberOwnerCount'] = "{a}/{b}".format(
            a=hide_list[7].text.strip(), b=hide_list[6].text.strip())
    except:
        temp['AccidentHistory'] = 'null'
        temp['UseHistory'] = 'null'
        temp['MyDamage'] = 'null'
        temp['OtherDamage'] = 'null'
        temp['NumberOwnerCount'] = 'null'

    temp['FirstRegister'] = registeredDate

    if noRegisterPeriod == 'None':
        temp['noRegisterPeriod'] = 'null'
    else:
        temp['noRegisterPeriod'] = noRegisterPeriod
    if bool(HistDamage):
        temp['HistDamage'] = HistDamage
    else:
        temp['HistDamage'] = 'null'
    temp['HistOwner'] = 'null'
    return temp


def start(urls, server_num):
    num = 0
    time.sleep(random.randint(1, 3))
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
            temp = get_car_info(url, temp)
            temp.update(get_history(url, temp))
            temp['Options'] = get_options(url)
            temp = get_checkdata(url, temp)
            num += 1

            print("현재 : ", num)
            if bool(temp):
                with open('result{server_num}_t.json'.format(server_num=server_num), 'a', encoding='utf-8-sig') as outfile:
                    json.dump(temp, outfile, indent=4,
                              ensure_ascii=False, sort_keys=True)
        except Exception as e:
            print(f"error : {e}")


def crawl_iframe(url, temp):

    carSeq = url[url.index('?carSeq=') + len('?carSeq='):]
    data = {
        'layerId': 'layerCarCheckInfo',
        'carSeq': carSeq
    }
    res = requests.post(
        'https://www.kbchachacha.com/public/layer/car/check/info.kbc', data=data)
    soup = bs(res.text, 'html.parser')

    table = soup.find_all('table')
    temp['RegistrationID'] = table[0].find_all('tr')[5].find('td').text
    if temp['RegistrationID'] == '':
        temp['RegistrationID'] = 'null'
    # temp['변속기종류'] = table[0].find_all(
    #     'tr')[6].find('div').get('value')
    # temp['사용연료'] = table[0].find_all('tr')[7].find('div').get('value')
    temp['MotorType'] = table[0].find_all('tr')[8].find('td').text
    if temp['MotorType'] == '':
        temp['MotorType'] = 'null'
    temp['WarrantyType'] = table[0].find_all(
        'tr')[9].find('div').get('value')
    if temp['WarrantyType'] == '':
        temp['WarrantyType'] = 'null'
    # result['가격잔정 기준가격'] = table[0].find_all('tr')[10].find('td').text.strip()
    check_inner = dict()
    check_outer = dict()

    # result['주행거리 계기상태'] = table[1].find('tbody').find_all(
    #     'tr')[0].find('div', {'class': 'option-ch'}).get('value')
    # result['주행거리 상태'] = table[1].find('tbody').find_all(
    #     'tr')[1].find('div', {'class': 'option-ch'}).get('value')
    # result['현재 주행거리'] = table[1].find('tbody').find_all(
    #     'tr')[0].find('td', {'rowspan': '2'}).text
    check_inner['BrakeMasterCylinderOilLeakage'] = table[4].find('tbody').find_all(
        'tr')[29].find('div', {'class': 'option-ch'}).get('value')
    check_inner['BrakeOilLeakage'] = table[4].find('tbody').find_all(
        'tr')[30].find('div', {'class': 'option-ch'}).get('value')
    check_inner['BrakeSystemStatus'] = table[4].find('tbody').find_all(
        'tr')[31].find('div', {'class': 'option-ch'}).get('value')
    check_inner['ElectricGeneratorOutput'] = table[4].find('tbody').find_all(
        'tr')[32].find('div', {'class': 'option-ch'}).get('value')
    check_inner['ElectricIndoorBlowerMotor'] = table[4].find('tbody').find_all(
        'tr')[35].find('div', {'class': 'option-ch'}).get('value')
    check_inner['ElectricRadiatorFanMotor'] = table[4].find('tbody').find_all(
        'tr')[36].find('div', {'class': 'option-ch'}).get('value')
    check_inner['ElectricStarterMotor'] = table[4].find('tbody').find_all(
        'tr')[33].find('div', {'class': 'option-ch'}).get('value')
    check_inner['ElectricWindowMotor'] = table[4].find('tbody').find_all(
        'tr')[37].find('div', {'class': 'option-ch'}).get('value')
    check_inner['ElectricWiperMotorFunction'] = table[4].find('tbody').find_all(
        'tr')[34].find('div', {'class': 'option-ch'}).get('value')

    # result['차대번호 표기'] = table[1].find('tbody').find_all(
    #     'tr')[2].find('div', {'class': 'option-ch'}).get('value')
    # result['배출가스'] = table[1].find('tbody').find_all(
    #     'tr')[3].find('div', {'class': 'option-ch'}).get('value')
    # result['튜닝'] = table[1].find('tbody').find_all(
    #     'tr')[4].find('div', {'class': 'option-ch'}).get('value')
    # result['사고이력'] = table[2].find('tbody').find_all('tr')[0].find_all(
    #     'div', {'class': 'option-ch'})[0].get('value')
    # result['단순수리이력'] = table[2].find('tbody').find_all(
    #     'tr')[0].find_all('div', {'class': 'option-ch'})[1].get('value')
    # result['외판부위 1랭크 이상여부'] = table[2].find('tbody').find_all(
    #     'tr')[1].find('div', {'class': 'option-ch'}).get('value')
    # result['외판부위 2랭크 이상여부'] = table[2].find('tbody').find_all(
    #     'tr')[2].find('div', {'class': 'option-ch'}).get('value')
    # result['주요골격 이상여부'] = table[2].find('tbody').find_all(
    #     'tr')[3].find('div', {'class': 'option-ch'}).get('value')
    check_inner['SelfCheckMotor'] = table[4].find('tbody').find_all(
        'tr')[0].find('div', {'class': 'option-ch'}).get('value')
    check_inner['SelfCheckTransmission'] = table[4].find('tbody').find_all(
        'tr')[1].find('div', {'class': 'option-ch'}).get('value')
    check_inner['MotorOperationStatus'] = table[4].find('tbody').find_all(
        'tr')[2].find('div', {'class': 'option-ch'}).get('value')
    check_inner['MotorOilLeakLockerArmCover'] = table[4].find('tbody').find_all(
        'tr')[3].find('div', {'class': 'option-ch'}).get('value')
    check_inner['MotorOilLeakCylinderHeaderGasket'] = table[4].find('tbody').find_all(
        'tr')[4].find('div', {'class': 'option-ch'}).get('value')
    check_inner['MotorOilLeakOilFan'] = table[4].find('tbody').find_all(
        'tr')[5].find('div', {'class': 'option-ch'}).get('value')
    check_inner['MotorOilFlowRate'] = table[4].find('tbody').find_all(
        'tr')[6].find('div', {'class': 'option-ch'}).get('value')
    check_inner['MotorWaterLeakCylinderHeaderGasket'] = table[4].find('tbody').find_all(
        'tr')[7].find('div', {'class': 'option-ch'}).get('value')
    check_inner['MotorWaterLeakPump'] = table[4].find('tbody').find_all(
        'tr')[8].find('div', {'class': 'option-ch'}).get('value')
    check_inner['MotorWaterLeakRadiato'] = table[4].find('tbody').find_all(
        'tr')[9].find('div', {'class': 'option-ch'}).get('value')
    check_inner['MotorWaterLeakCoolingRate'] = table[4].find('tbody').find_all(
        'tr')[10].find('div', {'class': 'option-ch'}).get('value')
    check_inner['MotorHighPressurePump'] = table[4].find('tbody').find_all(
        'tr')[11].find('div', {'class': 'option-ch'}).get('value')
    check_inner['TransAutoOilLeakage'] = table[4].find('tbody').find_all(
        'tr')[12].find('div', {'class': 'option-ch'}).get('value')
    check_inner['TransAutoOilFlowAndCondition'] = table[4].find('tbody').find_all(
        'tr')[13].find('div', {'class': 'option-ch'}).get('value')
    check_inner['TransAutoStatus'] = table[4].find('tbody').find_all(
        'tr')[14].find('div', {'class': 'option-ch'}).get('value')
    check_inner['TransManualOilLeakage'] = table[4].find('tbody').find_all(
        'tr')[15].find('div', {'class': 'option-ch'}).get('value')
    check_inner['TransManualGearShifting'] = table[4].find('tbody').find_all(
        'tr')[16].find('div', {'class': 'option-ch'}).get('value')
    check_inner['TransManualFluidFlowAndCondition'] = table[4].find('tbody').find_all(
        'tr')[17].find('div', {'class': 'option-ch'}).get('value')
    check_inner['TransManualStatus'] = table[4].find('tbody').find_all(
        'tr')[18].find('div', {'class': 'option-ch'}).get('value')
    check_inner['PowerClutchAssembly'] = table[4].find('tbody').find_all(
        'tr')[19].find('div', {'class': 'option-ch'}).get('value')
    check_inner['PowerConstantVelocityJoint'] = table[4].find('tbody').find_all(
        'tr')[20].find('div', {'class': 'option-ch'}).get('value')
    check_inner['PowerWeightedShaftAndBearing'] = table[4].find('tbody').find_all(
        'tr')[21].find('div', {'class': 'option-ch'}).get('value')
    # result['동력전달 디퍼렌셜기어'] = table[4].find('tbody').find_all(
    #     'tr')[22].find('div', {'class': 'option-ch'}).get('value')
    check_inner['SteeringPowerOilLeakage'] = table[4].find('tbody').find_all(
        'tr')[23].find('div', {'class': 'option-ch'}).get('value')
    check_inner['SteeringPump'] = table[4].find('tbody').find_all(
        'tr')[24].find('div', {'class': 'option-ch'}).get('value')
    check_inner['SteeringGear'] = table[4].find('tbody').find_all(
        'tr')[25].find('div', {'class': 'option-ch'}).get('value')
    # result['조향 작동상태 스티어링조인트'] = table[4].find('tbody').find_all(
    #     'tr')[26].find('div', {'class': 'option-ch'}).get('value')
    # result['조향 작동상태 파워고압호스'] = table[4].find('tbody').find_all(
    #     'tr')[27].find('div', {'class': 'option-ch'}).get('value')
    check_inner['SteeringTieRodEndAndBallJoint'] = table[4].find('tbody').find_all(
        'tr')[28].find('div', {'class': 'option-ch'}).get('value')

    # result['고전원전기장치 충전구절연상태'] = table[4].find('tbody').find_all(
    #     'tr')[38].find('div', {'class': 'option-ch'}).get('value')
    # result['고전원전기장치 구동축전지격리상태'] = table[4].find('tbody').find_all(
    #     'tr')[39].find('div', {'class': 'option-ch'}).get('value')
    # result['고전원전기장치 고전원전기배선상태'] = table[4].find('tbody').find_all(
    #     'tr')[40].find('div', {'class': 'option-ch'}).get('value')
    # check_inner['OtherFuelLeaks'] = table[4].find('tbody').find_all(
    #     'tr')[41].find('div', {'class': 'option-ch'}).get('value')
    # result['수리필요 외장'] = table[5].find('tbody').find_all(
    #     'tr')[0].find('div', {'class': 'option-ch'}).get('value')
    # result['수리필요 광택'] = table[5].find('tbody').find_all(
    #     'tr')[1].find('div', {'class': 'option-ch'}).get('value')
    # result['수리필요 내장'] = table[5].find('tbody').find_all(
    #     'tr')[2].find('div', {'class': 'option-ch'}).get('value')
    # result['수리필요 룸크리닝'] = table[5].find('tbody').find_all(
    #     'tr')[3].find('div', {'class': 'option-ch'}).get('value')
    # result['수리필요 휠'] = table[5].find('tbody').find_all(
    #     'tr')[4].find('div', {'class': 'option-ch'}).get('value')
    # result['수리필요 타이어'] = table[5].find('tbody').find_all(
    #     'tr')[5].find('div', {'class': 'option-ch'}).get('value')
    # result['수리필요 유리'] = table[5].find('tbody').find_all(
    #     'tr')[6].find('div', {'class': 'option-ch'}).get('value')
    # result['기본품목 보유상태'] = table[5].find('tbody').find_all(
    #     'tr')[7].find('div', {'class': 'option-ch'}).get('value')
    check_outer['CrossMember'] = 'null'
    check_outer['DashPanel'] = 'null'
    check_outer['FloorPanel'] = 'null'
    check_outer['FrontDoorLeft'] = 'null'
    check_outer['FrontDoorRight'] = 'null'
    check_outer['FrontFenderLeft'] = 'null'
    check_outer['FrontFenderRight'] = 'null'
    check_outer['FrontPanel'] = 'null'
    check_outer['FrontSideMemberLeft'] = 'null'
    check_outer['FrontSideMemberRight'] = 'null'
    check_outer['FrontWheelHouseLeft'] = 'null'
    check_outer['FrontWheelHouseRight'] = 'null'
    check_outer['Hood'] = 'null'
    check_outer['InsidePanelLeft'] = 'null'
    check_outer['InsidePanelRight'] = 'null'
    check_outer['PackageTray'] = 'null'
    check_outer['PillarPanelFrontLeft'] = 'null'
    check_outer['PillarPanelFrontRight'] = "null"
    check_outer['PillarPanelMiddleLeft'] = "null"
    check_outer['PillarPanelMiddleRight'] = "null"
    check_outer['PillarPanelRearLeft'] = "null"
    check_outer['PillarPanelRearRight'] = "null"
    check_outer['QuarterPanelLeft'] = "null"
    check_outer['QuarterPanelRight'] = "null"
    check_outer['RadiatorSupport'] = "null"
    check_outer['RearDoorLeft'] = "null"
    check_outer['RearDoorRight'] = "null"
    check_outer['RearPanel'] = "null"
    check_outer['RearSideMemberLeft'] = "null"
    check_outer['RearSideMemberRight'] = "null"
    check_outer['RearWheelHouseLeft'] = "null"
    check_outer['RearWheelHouseRight'] = "null"
    check_outer['RoofPanel'] = "null"
    check_outer['SideSillPanelLeft'] = "null"
    check_outer['SideSillPanelRight'] = "null"
    check_outer['TrunkFloor'] = "null"
    check_outer['TrunkLead'] = "null"
    repair_items = ['Hood', 'FrontFenderLeft', 'FrontFenderRight', 'FrontDoorLeft', 'FrontDoorRight', 'RearDoorLeft', 'RearDoorRight', 'TrunkLead', 'RadiatorSupport', 'QuarterPanelLeft', 'QuarterPanelRight', 'RoofPanel', 'SideSillPanelLeft', 'SideSillPanelRight', 'FrontPanel', 'CrossMember', 'InsidePanelLeft', 'InsidePanelRight', 'RearSideMemberLeft',
                    'RearSideMemberRight', 'FrontSideMemberLeft', 'FrontSideMemberRight', 'FrontWheelHouseLeft', 'FrontWheelHouseRight', 'RearWheelHouseLeft', 'RearWheelHouseRight',
                    'PillarPanelFrontLeft', 'PillarPanelFrontRight', 'PillarPanelMiddleLeft', 'PillarPanelMiddleRight', 'PillarPanelRearLeft', 'PillarPanelRearRight', 'DashPanel',
                    'noitem1', 'FloorPanel', 'noitem2', 'TrunkFloor', 'RearPanel', 'PackageTray']  # 1~39

    items_index = soup.find('input', {'id': 'carCheck'}).get('value')

    for i, item in enumerate(items_index):
        if repair_items[i] == 'noitem1' or repair_items[i] == 'noitem2':
            continue
        if item == 'X' or item == 'C' or item == 'W' or item == 'A' or item == 'U' or item == 'T':
            check_outer[repair_items[i]] = item
        elif item == ' ' and check_inner['MotorOperationStatus'] != 'null' and check_inner['SelfCheckMotor'] != 'null':
            check_outer[repair_items[i]] = 'none'
        else:
            pass
    for key, value in check_inner.items():
        if value == '':
            check_inner[key] = 'null'
    for key, value in check_outer.items():
        if value == '':
            check_outer[key] = 'null'

    temp['IssueDt'] = soup.find('div', {'class': 'date'}).text.replace(' ', '')
    if temp['IssueDt'] == '':
        temp['IssueDt'] = 'null'
    temp['CHECK_INNER'] = check_inner
    temp['CHECK_OUTER'] = check_outer
    return temp


def get_checkdata(url, temp):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'www.kbchachacha.com',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }
    res = requests.get(
        url, headers=headers)

    soup = bs(res.text, 'html.parser')
    chk_tag_url = soup.find('li', {'class': 'used01'}).find('a')[
        'data-link-url']
    if 'http' in chk_tag_url:  # 다른 페이지로 이동
        # call domain by scraper
        temp['CHECK_INNER'] = "null"
        temp['CHECK_OUTER'] = "null"
    else:
        carSeq = url[url.index('?carSeq=')+len('?carSeq='):]
        data = {
            'layerId': 'layerCarCheckInfo',
            'carSeq': carSeq
        }
        res = requests.post(
            'https://www.kbchachacha.com/public/layer/car/check/info.kbc', data=data)

        soup = bs(res.text, 'html.parser')

        img_check = soup.find('div', {'class': 'ch-car-txt'})
        if img_check == None:
            if soup.find('div', {'class': 'ch-car-name'}) == None:
                temp['CHECK_INNER'] = "null"
                temp['CHECK_OUTER'] = "null"
                temp['RegistrationID'] = "null"
                temp['MotorType'] = 'null'
                temp['WarrantyType'] = 'null'
                temp['IssueDt'] = 'null'
            else:
                # call iframe scraper
                temp = crawl_iframe(url, temp)

        else:
            temp['CHECK_INNER'] = "null"
            temp['CHECK_OUTER'] = "null"
            temp['RegistrationID'] = "null"
            temp['MotorType'] = 'null'
            temp['WarrantyType'] = 'null'
            temp['IssueDt'] = 'null'

    return temp


def get_dateform(date):
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


def process_json(server_num):

    result = list()
    with open('result{server_num}_t.json'.format(server_num=server_num), encoding='utf-8-sig', errors='ignore') as f:
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
    os.remove('result{server_num}_t.json'.format(server_num=server_num))
    with open('result{server_num}.json'.format(server_num=server_num), 'w', encoding='utf-8-sig') as ff:
        json.dump(result, ff, indent=4, ensure_ascii=False, sort_keys=True)


class Uploader:

    def __init__(self, resultFileName):
        self.localPath = '/home/centos/'
        self.resultFileName = resultFileName
        self.remotePath = '/home/centos/result_from_servers/'
        self.main()

    def main(self):
        ssh = self.createSSHClient()
        scp = SCPClient(ssh.get_transport())
        scp.put(self.localPath+self.resultFileName,
                self.remotePath+self.resultFileName)

    def createSSHClient(self):
        host = '133.186.211.78'  # IP
        username = 'centos'  # username
        password = 'gozjRjwu~!'  # password (root)
        port = 22
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, port, username, password,
                       key_filename='/home/centos/shopify.pem')  # public-key
        return client


#########################main#################################
# with open('argu.txt', 'r') as f:
#     server_num = f.read()
server_num = sys.argv[1]

num_per_url = 2700

df = pd.read_csv('filtered_url.csv')
car_urls = list(df['url'].values)
server_num = int(server_num)
car_urls = car_urls[num_per_url*(server_num-1):num_per_url*server_num]

print(len(car_urls))
start(car_urls, server_num)
Uploader(
    '/home/centos/daily_crawling/result{server_num}_t.json'.format(server_num=server_num))
# process_json(server_num)
