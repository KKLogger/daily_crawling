import paramiko
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
from scp import SCPClient, SCPException
local_path = '/home/ec2-user/daily_crawling/'
remote_path = '/home/centos/result_from_servers/'


def get_page_url(page_num, user_code, maker_code):
    url = 'https://www.kbchachacha.com/public/search/list.empty?page=' + \
        str(page_num) + '&sort=-orderDate&useCode=' + \
        str(user_code) + '&makerCode=' + \
        str(maker_code)+'&_pageSize=3&pageSize=4'
    return url


def get_car_urls(user_code, num):

    car_url_list = list()
    maker_codes = ['101', '102', '103', '105',
                   '104', '189', '106', '107',
                   '108', '109', '112', '160',
                   '116', '122', '133', '115',
                   '110', '170', '153', '114',
                   '128', '123', '124', '117',
                   '136', '121', '137', '146',
                   '118', '142', '113', '138',
                   '130', '180', '166', '125',
                   '150', '148', '119', '156',
                   '129', '140', '111', '190',
                   '191', '132', '152', '161',
                   '157', '134', '181', '141',
                   '154', '126', '173', '139',
                   '169', '143', '167', '127']
    for maker_code in maker_codes:
        print(maker_code)
        page_num = 0
        while(True):
            page_num += 1
            url = get_page_url(page_num, user_code, maker_code)
            time.sleep(2)
            response = requests.get(url)
            soup = bs(response.text, "html.parser")
            #####종료 조건 ###############
            # if page_num == 3:
            #     break
            if soup.find('span', {'class': 'txt'}) is not None:
                print('종료')
                break
            if soup.find('h2') is None:
                print('종료, blocked')
                break
            car_list = soup.find_all('div', {'class': 'area'})

            for car in car_list:
                items = car.find_all('a')
                for item in items:
                    if 'detail.kbc?carSeq' in item['href']:
                        item_href = item['href']
                        price = car.find(
                            'strong', {'class', 'pay'}).text.strip()
                        if 'https://' in item_href:
                            car_url_list.append(item_href+"///" + price)
                        else:
                            car_url_list.append(
                                'https://www.kbchachacha.com' + item_href + "///" + price)
            num += 1
            print(num)

    return car_url_list


class SSHManager:
    """
    usage:
        >>> import SSHManager
        >>> ssh_manager = SSHManager()
        >>> ssh_manager.create_ssh_client(hostname, username, password)
        >>> ssh_manager.send_command("ls -al")
        >>> ssh_manager.send_file("/path/to/local_path", "/path/to/remote_path")
        >>> ssh_manager.get_file("/path/to/remote_path", "/path/to/local_path")
        ...
        >>> ssh_manager.close_ssh_client()
    """

    def __init__(self):
        self.ssh_client = None

    def create_ssh_client(self, hostname, username, password, key_filename):
        """Create SSH client session to remote server"""
        port = 22
        if self.ssh_client is None:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(
                paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                hostname, port=port, username=username, password=password, key_filename=key_filename)
        else:
            print("SSH client session exist.")

    def close_ssh_client(self):
        """Close SSH client session"""
        self.ssh_client.close()

    def send_file(self, local_path, remote_path):
        """Send a single file to remote path"""
        try:
            with SCPClient(self.ssh_client.get_transport()) as scp:
                scp.put(local_path, remote_path, preserve_times=True)
        except SCPException:
            raise SCPException.message

    def get_file(self, remote_path, local_path):
        """Get a single file from remote path"""
        try:
            with SCPClient(self.ssh_client.get_transport()) as scp:
                scp.get(remote_path, local_path)
        except SCPException:
            raise SCPException.message

    def send_command(self, command):
        """Send a single command"""
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        return stdout.readlines()


if __name__ == '__main__':
    s_time = time.time()
    car_url_list = list()
    num = 0
    df = pd.DataFrame(columns=['url'])
    for user_code in ['002001', '002012', '002013']:
        car_url_list = car_url_list + get_car_urls(user_code, num)
    car_url_list = list(set(car_url_list))
    print(len(car_url_list))
    df['url'] = car_url_list
    df.to_csv('/home/ec2-user/daily_crawling/filtered_url_1.csv')
    print("총 실행시간", time.time()-s_time)
    ssh_manager = SSHManager()
    ssh_manager.create_ssh_client(
        "133.186.150.193", "centos", "gozjRjwu~!", key_filename=local_path + 'shopify.pem')  # 세션생성
    ssh_manager.send_file('/home/ec2-user/daily_crawling/filtered_url_1.csv',
                          remote_path + 'filtered_url_1.csv')  # 파일전송
    ssh_manager.close_ssh_client()  # 세션종료
