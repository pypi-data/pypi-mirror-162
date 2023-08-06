import logging
from datetime import datetime
from io import BytesIO
from spt_factory.exceptions import NotExistingBucket, ExistingKey, HTTPStatusCode

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class S3Manager:
    """
    This class you can use for managing bin-objects to AWS-S3 storage.
    Use upload_file to upload file to S3, function will convert object self.
    Use upload_binstr to upload already converted string to storage.
    Use download to download file from the storage.
    """
    def __init__(self, client):
        """
        Creating an instance creates a connection to the storage.
        """
        self.client = client

    def _check_existing_buckets(self, bucket_name):
        bucket_dict = self.client.list_buckets()
        for exist_bucket in bucket_dict['Buckets']:
            if exist_bucket['Name'] != bucket_name:
                return
        raise NotExistingBucket(bucket_name)

    def _check_existing_id(self, bucket_name, id):
        result = self.client.list_objects_v2(Bucket=bucket_name, Prefix=id)
        if 'Contents' in result:
            raise ExistingKey(id)

    def upload_file(self, bucket_name, id, filepath, author='default'):
        """
        Upload file to defined bucket, also you need to define id or name of file and author. Author and datetime will be
        received as metadata. File need to define regarding this folder.
        :param bucket_name: string
        :param id: string
        :param file: string
        :param author: string
        :return: id
        """

        self._check_existing_buckets(bucket_name)
        self._check_existing_id(bucket_name, id)

        now = datetime.now()
        meta_data = {
            "author": str(author),
            "date_of_creation": now.strftime("%d/%m/%Y %H:%M:%S")
        }

        self.client.upload_file(Filename=filepath, Bucket=bucket_name, Key=id, ExtraArgs={"Metadata": meta_data})
        logging.debug("File object uploaded successfully")

    def upload_bin(self, bucket_name, id, bin_str, author='default'):
        """
        You can upload binary-ready file, just pass to function as bin_str
        :param bucket_name: string
        :param id: string
        :param bin_str: string
        :param author: string
        :return:
        """

        self._check_existing_id(bucket_name, id)
        self._check_existing_buckets(bucket_name)

        now = datetime.now()
        meta_data = {
            "author": str(author),
            "date_of_creation": now.strftime("%d/%m/%Y %H:%M:%S")
        }

        response = self.client.put_object(Body=bin_str, Bucket=bucket_name, Key=id, Metadata=meta_data)
        res = response.get('ResponseMetadata')
        if res.get('HTTPStatusCode') != 200:
            raise HTTPStatusCode(res.get('HTTPStatusCode'))
        logging.debug("Binary object uploaded successfully")

    def download_file(self, bucket_name, id, filepath=None):
        """
        Download file from defined bucket, defining of file using id. Filepath is download file path at your computer
        regarding this folder
        :param bucket_name: string
        :param id: string
        :param filepath: string
        """
        self._check_existing_buckets(bucket_name)
        if filepath is None:
            filepath = id
        self.client.download_file(Bucket=bucket_name, Key=id, Filename=filepath)
        logging.debug("File downloaded successfully")

    def download_bin(self, bucket_name, id):
        """
        This method used to download binary files.
        :param bucket_name: string
        :param id: string
        :return: binary string
        """
        self._check_existing_buckets(bucket_name)
        with BytesIO() as data:
            self.client.download_fileobj(Bucket=bucket_name, Key=id, Fileobj=data)
            result = data.getvalue()
        logging.debug("File downloaded successfully")
        return result

    def delete_object(self, bucket_name, id):
        """
        This method allows you to remove file or binary object from bucket
        :param bucket_name: string
        :param id: string
        """
        self.client.delete_object(Bucket=bucket_name, Key=id)
        logging.debug('Object deleted successfully')
