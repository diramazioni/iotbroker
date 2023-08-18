import asyncio
from dotenv import load_dotenv
import os
import logging

from ftplib import FTP, all_errors
import shutil


class AsyncFtpClient:
    def __init__(self, host, port, user, password, timeout=10):
        self.logger = logging.getLogger(__name__)
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.timeout = timeout
        self.ftp = None

    async def connect(self):
        try:
            client_ftp = FTP()
            client_ftp.debugging = 5
            client_ftp.connect(host=self.host, port=self.port)
            client_ftp.login(user=self.user, passwd=self.password)
            self.ftp = client_ftp
        except all_errors as e:
            logging.error(f"Error in Ftp -> {self.host} \n{e}")

    async def disconnect(self):
        self.ftp.close()

    async def sendFile(self, remotePath, localFile):
        try:
            fileName = os.path.basename(localFile)
            logging.info("sending:" + localFile)
            if os.path.exists(localFile):
                with open(localFile, "rb") as file:
                    # file = open(localFile, 'rb')
                    self.ftp.cwd(remotePath)
                    self.ftp.storbinary("STOR " + fileName, file)
                    file.close()
            else:
                logging.error("ftp sendFile: file not found")
        except all_errors as e:
            logging.error(f"Error in sendFile -> {self.host} \n{e}")

    async def retrieveFile(self, remotePath, localFile):
        try:
            fileName = os.path.basename(localFile)
            logging.info("retrieving:" + localFile)
            if os.path.exists(localFile):
                with open(localFile, "wb") as file:
                    self.ftp.cwd(remotePath)
                    self.ftp.retrbinary("RETR " + fileName, file.write, 1024)
                    file.close()
            else:
                logging.error("ftp retrieveFile: file not found")
        except all_errors as e:
            logging.error(f"Error in retrieveFile -> {self.host} \n{e}")
