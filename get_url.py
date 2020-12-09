import sys
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
from SSHManager import SSHManager
import os

# local_path = "/home/ec2-user/daily_crawling/"
local_path = "C:/Projects/crawlingCarInfo/to_server/"
remote_path = "/home/centos/result_from_servers/"


def get_page_url(page_num, user_code, maker_code, cityCode):
    """
    >>>input 페이지 번호, 차량종류번호, 브랜드번호, 중고차판매지역번호
    >>>output 쿼리로 필터링 적용된 url
    """
    url = (
        "https://www.kbchachacha.com/public/search/list.empty?page="
        + str(page_num)
        + "&sort=-orderDate&useCode="
        + str(user_code)
        + "&makerCode="
        + str(maker_code)
        + "&cityCode="
        + str(cityCode)
        + "&_pageSize=3&pageSize=4"
    )
    return url


def get_car_urls(user_code):
    # 3개 필터를 이용해 url 수집
    car_url_list = list()
    maker_codes = [
        "101",  # 현대
        "102",  # 기아
        "103",  # 한국GM
        "105",  # 르노삼성
        "104",  # 쌍용
        "189",  # 제네시스
        "106",  # 국산 기타
        "107",  # BMW
        "108",  # 벤츠
        "109",  # 아우디
        "112",  # 폭스바겐
        "160",  # 미니
        "116",  # 랜드로버
        "122",  # 포드
        "133",  # 렉서스
        "115",  # 재규어
        "170",  # 지프
        "110",  # 푸조
        "153",  # 인피니티
        "114",  # 포르쉐
        "128",  # 닛산
        "124",  # 도요타
        "123",  # 혼다
        "117",  # 볼보
        "136",  # 링컨
        "121",  # 크라이슬러
        "137",  # 마세라티
        "146",  # 캐딜락
        "118",  # 시트로엥
        "142",  # 쉐보레
        "113",  # 피아트
        "138",  # 벤틀리
        "130",  # 닷지
        "180",  # 중한자동차
        "166",  # 스마트트
        "125",  # 미쯔비시
        "150",  # 허머
        "148",  # 페라리
        "119",  # 롤스로이스
        "156",  # 애스터마틴
        "129",  # 다이하쓰
        "140",  # 스바루
        "111",  #
        "190",
        "191",
        "132",
        "152",
        "161",
        "157",
        "134",
        "181",
        "141",
        "154",
        "126",
        "173",
        "139",
        "169",
        "143",
        "167",
        "127",
        "192",
    ]
    cityCodes = [
        "021012",  # 인천
        "021009",  # 서울
        "021007",  # 대전
        "021006",  # 대구
        "021005",  # 광주
        "021008",  # 부산
        "021011",  # 울산
        "021010",  # 세종
        "021002",  # 경기
        "021001",  # 강원
        "021003",  # 경남
        "021004",  # 경북
        "021013",  # 전남
        "021014",  # 전북
        "021016",  # 충남
        "021017",  # 충북
        "021015",  # 제주
    ]
    # for maker_code in maker_codes:
    for maker_code in range(99, 201):
        for cityCode in cityCodes:
            print(maker_code, user_code, cityCode)
            page_num = 0
            while True:
                page_num += 1
                url = get_page_url(page_num, user_code, maker_code, cityCode)
                time.sleep(0.3)
                response = requests.get(url)
                soup = bs(response.text, "html.parser")
                ####종료 조건 ###############
                # if page_num == 3:
                #     break
                if soup.find("span", {"class": "txt"}) is not None:
                    print("종료")
                    break
                if soup.find("h2") is None:
                    print("종료, blocked")
                    break
                car_list = soup.find_all("div", {"class": "area"})
                for car in car_list:
                    items = car.find_all("a")
                    for item in items:
                        if "detail.kbc?carSeq" in item["href"]:
                            item_href = item["href"]
                            price = car.find("strong", {"class", "pay"}).text.strip()
                            if "https://" in item_href:
                                car_url_list.append(item_href + "///" + price)
                            else:
                                car_url_list.append(
                                    "https://www.kbchachacha.com"
                                    + item_href
                                    + "///"
                                    + price
                                )

    return car_url_list


if __name__ == "__main__":
    server_num = int(sys.argv[1])
    s_time = time.time()
    car_url_list = list()
    user_codes = [
        ["002001", "002007"],
        ["002005"],
        ["002004"],
        ["002003", "002006", "002010"],
        ["002008"],
        ["002002", "002009", "002011", "002012"],
    ]
    df = pd.DataFrame(columns=["url"])
    for user_code in user_codes[server_num - 1]:
        car_url_list = car_url_list + get_car_urls(user_code)
        print(len(car_url_list))
    car_url_list = list(set(car_url_list))
    print(len(car_url_list))
    df["url"] = car_url_list
    print("총 실행시간", time.time() - s_time)
    df.to_csv(
        local_path + "filtered_url_{server_num}.csv".format(server_num=server_num)
    )

    ssh_manager = SSHManager()
    for i in range(10):
        if i!= 0 :
            ssh_manager.close_ssh_client()
        try:
            ssh_manager.create_ssh_client(
                "133.186.150.193",
                "centos",
                "gozjRjwu~!",
                key_filename=local_path + "shopify.pem",
            )  # 세션생성
            ssh_manager.send_file(
                local_path + "filtered_url_{server_num}.csv".format(server_num=server_num),
                remote_path + "filtered_url_{server_num}.csv".format(server_num=server_num),
            )  # 파일전송
            os.remove(
                local_path + "filtered_url_{server_num}.csv".format(server_num=server_num)
            )
            break
        except Exception as e:
            print(f"error : {e}")
            time.sleep(10)
    ssh_manager.close_ssh_client()  # 세션종료
