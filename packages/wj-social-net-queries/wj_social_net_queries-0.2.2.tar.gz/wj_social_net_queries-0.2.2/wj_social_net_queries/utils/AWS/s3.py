import os
import traceback
from urllib.parse import urlparse

import boto3
import requests

from wj_social_net_queries.utils.utils import get_file_extension


class AwsS3:
    def __init__(self, bucket:str, aws_access_key_id:str, aws_secret_access_key:str):
        self.client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.bucket = bucket

    def upload_file(self, local_file, s3_filename, directory):
        try:
            if isinstance(local_file, str):
                key = directory + "/" + s3_filename
                self.client.upload_file(local_file, self.bucket, key)
            else:
                self.client.upload_fileobj(local_file, self.bucket, s3_filename)
            os.remove(s3_filename)
            return True
        except Exception:
            traceback.print_exc()
            return False

    def delete_file(self, s3_filename):
        try:
            self.client.delete_object(Bucket=self.bucket, Key=s3_filename)
            return True
        except Exception:
            traceback.print_exc()
            return False

    def copy_delete_file(self, s3_original_path, s3_dest_path):
        try:
            copy_source = {'Bucket': self.bucket, 'Key': s3_original_path}
            self.client.copy_object(Bucket=self.bucket, CopySource=copy_source, Key=s3_dest_path)
            self.client.delete_object(Bucket=self.bucket, Key=s3_original_path)
            return True
        except Exception:
            traceback.print_exc()
            return False
    
    def empty_bucket(self):
        try:
            client = boto3.resource(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
            )
            client.Bucket(self.bucket).objects.all().delete()
            return True
        except Exception:
            traceback.print_exc()
            return False

    def files_in_folder(self, folder=None, search_term=None):
        try:
            if folder is None:
                result = self.client.list_objects(Bucket=self.bucket, Delimiter="/")
            else:
                result = self.client.list_objects(Bucket=self.bucket, Prefix=f"{folder}/", Delimiter="/")
            if search_term is None:
                return [key["Key"] for key in result["Contents"] if key["Key"] != f"{folder}/"]
            else:
                return [key["Key"] for key in result["Contents"] if search_term in key["Key"]]
        except Exception:
            traceback.print_exc()
            return []

    def read_file(self, s3_filename):
        data = self.client.get_object(Bucket=self.bucket, Key=s3_filename)
        return data['Body'].read()
    

    def upload_file_from_url_to_aws_s3(self, url:str, directory:str, file_name:str):
        # get the connection of AWS S3 Bucket
        s3 = boto3.resource(
            's3',
            aws_access_key_id = self.aws_access_key_id,
            aws_secret_access_key = self.aws_secret_access_key
        )
        
        response = requests.get(url)
        if response.status_code==200:
            raw_data = response.content
            url_parser = urlparse(url)
            extension= get_file_extension(file_name=os.path.basename(url_parser.path))
            file_name = file_name + '.' + extension
            key = directory + "/" + file_name
            try:
                # Write the raw data as byte in new file_name in the server
                
                with open(file_name, 'wb') as new_file:
                    new_file.write(raw_data)
        
                # Open the server file as read mode and upload in AWS S3 Bucket.
                data = open(file_name, 'rb')
                s3.Bucket(self.bucket).put_object(Key=key, Body=data)
                data.close()
                os.remove(file_name)

            except Exception as e:
                print("Error in file upload %s." % (str(e)))
            
        else:
            print("Cannot parse url")
