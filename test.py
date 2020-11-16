import os
import sys
from ast import literal_eval
import json
import requests
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import paramiko
import time
import random
from scp import SCPClient, SCPException

local_path = 'C:/Users/jlee/Desktop/test/'
remote_path = '/home/centos/result_from_servers/'


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


ssh_manager = SSHManager()
ssh_manager.create_ssh_client(
    "133.186.150.193", "centos", "gozjRjwu~!", key_filename=local_path + 'shopify.pem')  # 세션생성
ssh_manager.send_file(local_path+'asd.txt.txt', remote_path+"1.txt")  # 파일전송
ssh_manager.get_file(remote_path+"1.txt", local_path+'2.txt')  # 파일다운로드
ssh_manager.close_ssh_client()  # 세션종료
