from SSHManager import SSHManager
import time
import os

remote_path = '/home/centos/result_from_servers/'
local_path = 'C:/Users/jlee/Crawling-Car-Info/Crawling/to_server/'


ssh_manager = SSHManager()

for _ in range(10):
    try:
        ssh_manager.create_ssh_client(
            "133.186.150.193", "centos", "gozjRjwu~!", key_filename=local_path + 'shopify.pem')  # 세션생성
        break
    except Exception as e:
        print(f"error : {e}")
        time.sleep(10)

for i  in range(20):
    try:
        if bool(ssh_manager.ssh_client):
            ssh_manager.send_file(local_path + 'ttt.txt',
                            remote_path + 'ttt.txt')  # 파일전송=
            os.remove(
                local_path + 'ttt.txt')
            break
    except Exception as e:
        print(f"error : {e}")
        time.sleep(10)
        pass

