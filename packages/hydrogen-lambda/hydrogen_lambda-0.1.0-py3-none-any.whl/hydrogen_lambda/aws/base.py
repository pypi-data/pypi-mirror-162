import boto3


class AWSClient:
    def __init__(self):
        self.client = boto3.client(service_name)

    def send(self, message):
        raise NotImplemented()
