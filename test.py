from SSHManager import SSHManager
import time
import os

remote_path = "/home/centos/result_from_servers/"
local_path = os.getcwd()



ssh_manager = SSHManager()
while True:
    for i in range(100):
        time.sleep(1)
        if i != 0:
            ssh_manager.close_ssh_client()
            print('close')
        try:
            ssh_manager.create_ssh_client(
                "133.186.150.193",
                "centos",
                "gozjRjwu~!",
                key_filename=local_path + "\\shopify.pem",
            )  # 세션생성
            print(bool(ssh_manager.ssh_client))
            ssh_manager.get_file(
                            remote_path + "ttt.txt", local_path + "\\ttt.txt"
                        )
            break
        except Exception as e:
            print(f"{i} 번째 error : {e}")
            try:
                ssh_manager.close_ssh_client()
            except :
                pass
            time.sleep(10)
#
# for i in range(20):
#     try:
#         if bool(ssh_manager.ssh_client):
#             ssh_manager.send_file(
#                 local_path + "ttt.txt", remote_path + "ttt.txt"
#             )  # 파일전송=
#             os.remove(local_path + "ttt.txt")
#             break
#     except Exception as e:
#         print(f"error : {e}")
#         time.sleep(10)
#         pass
