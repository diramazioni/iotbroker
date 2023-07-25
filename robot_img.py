'''
WELASER - by GV June 2023
Capture messages from  Ardesia MQTT (insecure)
and publish them to WeLASER MQTTS (over TLS)
then parse MQTT message, extract FTP file name and copy
the files from  Ardesia to Local and to WeLASER
Further on capture messages from MQTTS and
append them to device.txt
Finally publish a TEST message on MQTTS 
'''
import os
#import ast # to convert string into dictionary
import ssl
from ftplib import FTP, all_errors
import time
from time import strftime, localtime
#from datetime import datetime  # datetime data type

from dotenv import load_dotenv # legge codici di accesso
import shutil


#  ==========================================
#          LOADS ENVIROMENT VARIABLES
load_dotenv()
# FTPs
HOST_TO = os.getenv('HOST_TO')
PORT_TO = int(os.getenv('PORT_TO'))
USER_TO = os.getenv('USER_TO')
PASS_TO = os.getenv('PASS_TO')

'''
HOST_FROM = os.getenv('HOST_FROM')
PORT_FROM = int(os.getenv('PORT_FROM'))
USER_FROM = os.getenv('USER_FROM')
PASS_FROM = os.getenv('PASS_FROM')
'''

PATH_LOCAL = os.getenv('PATH_LOCAL')

PATH_ROBOT = "/robot_images"
PATH_FIELD = "/field_images"

PATH_DATA = os.path.join(PATH_LOCAL, "dash", "data")

# ==========================================================
#                     FTP
# -------------------------------------------------
def retrieveFile(ftp, remotePath, fileName):
    localFile = os.path.join(PATH_LOCAL,  fileName)
    print("retrieving:" + localFile)
    with open(localFile, 'wb') as file:
        ftp.cwd(remotePath)
        ftp.retrbinary('RETR ' + fileName, file.write, 1024)
        file.close()
# -------------------------------------------------
def sendFile(ftp, remotePath, fileName):
    localFile = os.path.join(PATH_LOCAL,  fileName)
    print("sending:" + localFile)
    if os.path.exists(localFile):
        with open(localFile, 'rb') as file:
        #file = open(localFile, 'rb')
            ftp.cwd(remotePath)
            ftp.storbinary('STOR '+ fileName , file)
            file.close()
    else:
        print("ftp file not found")

# -------------------------------------------------
def ftp_connect(host,port,user,password):
    try:
        client_ftp = FTP()
        client_ftp.debugging = 5
        client_ftp.connect(host=host, port=port)
        client_ftp.login(user=user, passwd=password)
        return  client_ftp
    except all_errors as e:
        print(f"Error in Ftp -> {host} \n{e}")

def read_images(directory):
    image_list = []
    for filename in os.listdir(directory):
        if filename.lower().endswith('.jpg'):
            image_list.append(os.path.abspath(filename))
    return image_list

def ftp_copy(src,dst):
    image_list = read_images(src)            
    try:
        client_to = ftp_connect(HOST_TO, PORT_TO, USER_TO, PASS_TO)
        print("connected ftp")
        for picture in image_list:
            sendFile(client_to, dst, picture)
        print("ftp done")
    except all_errors as e:
        print(f'Error in Ftp -> {e}')
    finally:
        client_to.close
        sendFile(client_to, dst, picture)
        print("ftp done")

    for picture in image_list:
        newFile = os.path.join(dst, picture)
        if os.path.exists(picture):
            shutil.move(picture, newFile) # local copy
        else:
            print(f"{picture} DOES NOT EXIST")
    

def main():
    ftp_copy("/robot_images", "/remote/robot_images")
    print("ftp done")

if __name__ == '__main__':
    main()