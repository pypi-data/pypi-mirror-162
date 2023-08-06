class S3Exception(Exception):
    pass


class NotExistingBucket(S3Exception):
    def __init__(self, bucket_name, message='Bucket was not found'):
        self.name = bucket_name
        self.message = message


class ExistingKey(S3Exception):
    def __init__(self, id, message='This id already exists'):
        self.id = id
        self.message = message


class HTTPStatusCode(S3Exception):
    def __init__(self, status, message='Status code is not ok'):
        self.status = status
        self.message = message