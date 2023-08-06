import boto3

from hydrogen_lambda.aws.base import AWSClient


class SNSClient(AWSClient):
    service_name = "sns"

    def send(self, message, topic_arn: str = None, message_attributes: dict = None):
        self.client.publish(
            TopicArn=topic_arn, Message=message, MessageAttributes=message_attributes
        )
