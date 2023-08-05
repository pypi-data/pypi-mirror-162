"""
Input File
"""

import ftplib
from contextlib import closing
import os
from urllib.parse import urlparse
import zipfile
import requests
import boto3
from config import EXTENSION_LIST
from config import S3_BUCKET_NAME
from config import INPUT_FILE_FOLDER

SESSION = boto3.Session()
S3 = SESSION.resource('s3')


def upload_file_to_s3(local_file_path):
    """
    Upload File to s3
    """
    try:
        # saving file to s3
        S3.meta.client.upload_file(
            local_file_path, S3_BUCKET_NAME, INPUT_FILE_FOLDER + os.path.basename(local_file_path))
        return INPUT_FILE_FOLDER + os.path.basename(local_file_path)
    except Exception as error:
        return error


class InputAdaptor:
    """
    Input Adaptor class
    """

    def __init__(self):
        pass

    def file_upload(self, local_file_path, cloud_name):
        """
        File Input Funtion
        """
        try:
            extension = os.path.splitext(local_file_path)[-1].lower()
            if extension in EXTENSION_LIST:
                # check file extension is valid from specified extension list
                if cloud_name.lower() == 'aws':
                    # checking cloud name
                    # calling function to save data to s3
                    upload_file_to_s3(local_file_path)
                    return INPUT_FILE_FOLDER+local_file_path
                else:
                    raise Exception("Sorry, invalid cloud")
        except FileNotFoundError:
            return "file not found"

    def zip_upload(self, zip_file, cloud_name):
        '''
        zip file upload Function
        '''
        try:
            if zipfile.is_zipfile(zip_file):
                # checking given file is zip
                with zipfile.ZipFile(zip_file, "r") as zip_file_name:
                    # reading zip file
                    for file_name in zip_file_name.namelist():
                        # extracting files from zip
                        extension = os.path.splitext(file_name)[-1].lower()
                        if extension not in EXTENSION_LIST:
                            # checking if any invalid extension file in present in zip file
                            raise Exception("Sorry, invalid zip file")

                if cloud_name.lower() == 'aws':
                    # checking cloud name
                    upload_file_to_s3(zip_file)
                    return INPUT_FILE_FOLDER+zip_file

                else:
                    return "Sorry, invalid cloud"
            else:
                return "Sorry, given File is not a zip file"
        except FileNotFoundError:
            return "file not found"

    def url_upload(self, link, colud_name):
        """
        url file upload Function
        """
        try:
            # saving file in object from url
            url_object = requests.get(link, stream=True).raw
            file_name = os.path.basename(urlparse(link).path)
            # extracting file extension
            extension = os.path.splitext(file_name)[-1].lower()
            if extension in EXTENSION_LIST:
                # check file extension is valid from specified extension list
                if colud_name.lower() == 'aws':  # checking cloud name
                    # saving data to s3
                    S3.meta.client.upload_fileobj(
                        url_object, S3_BUCKET_NAME, INPUT_FILE_FOLDER + file_name)
                    return INPUT_FILE_FOLDER+file_name
                else:
                    return 'invalid cloud option'
            else:
                return "invalid url"
        except IOError:
            return "url not found"

    def ftp_upload(self, ftp_host, username, password, ftp_folder_path, cloud_name):
        """
        ftp file upload function
        """
        try:
            with closing(ftplib.FTP()) as ftp:
                # connect to the FTP server
                ftp.connect(ftp_host, 21, 30*5)  # 5 mins timeout
                ftp.login(username, password)
                ftp.set_pasv(True)

                # get filenames within the directory
                filenames = ftp.nlst(ftp_folder_path)
                lst = []
                for filename in filenames:
                    # extrating particular filename from filenames
                    tmp_path = os.path.join('/tmp', os.path.basename(filename))
                    extension = os.path.splitext(tmp_path)[-1].lower()
                    if extension in EXTENSION_LIST:
                        # check file extension is valid from specified extension list
                        if not os.path.exists(tmp_path):
                            # check if file already exist in tmp folder
                            with open(tmp_path, 'wb') as f:
                                # writing file at /tmp folder
                                ftp.retrbinary('RETR %s' %
                                               filename, f.write)
                                if cloud_name.lower() == 'aws':
                                    # checking cloud name
                                    # calling function to save data to s3
                                    s3_file = upload_file_to_s3(tmp_path)
                                    # appending s3's response to list
                                    lst.append(s3_file)
                                else:
                                    raise Exception("Sorry, invalid cloud ")
                        else:
                            return "file already exist in tmp folder"
                    else:
                        return "Sorry, file format"
            return lst
        except Exception as error:
            return error
