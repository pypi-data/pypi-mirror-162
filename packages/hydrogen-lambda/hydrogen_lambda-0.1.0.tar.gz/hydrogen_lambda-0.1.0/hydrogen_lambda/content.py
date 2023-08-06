import json
from base64 import b64decode
from typing import Optional

from hydrogen_lambda.errors import EventParsingException


def get_content_from_sns(event: dict) -> list:
    return [record["Sns"]["Message"] for record in event["Records"]]


def get_content_from_sqs(event: dict) -> list:
    return [record["body"] for record in event["Records"]]


def get_content_from_kinesis(event: dict) -> list:
    return [b64decode(record["kinesis"]["data"]) for record in event["Records"]]


EVENTS = {
    "sns": get_content_from_sns,
    "sqs": get_content_from_sqs,
    "kinesis": get_content_from_kinesis,
}


def get_content(
    event: dict,
    event_type: str,
    from_json=True,
    raise_parsing_error=False,
    fallback: str = None,
) -> Optional[list]:
    if fn := EVENTS.get(event_type):

        try:
            records = fn(event)
        except KeyError as exc:
            if fallback:
                return get_content(event, fallback, from_json, raise_parsing_error)
            if raise_parsing_error:
                raise EventParsingException(f"Error while parsing the message : {exc}")
            return None

        if from_json and records:
            return [json.loads(record) for record in records]

        return records
