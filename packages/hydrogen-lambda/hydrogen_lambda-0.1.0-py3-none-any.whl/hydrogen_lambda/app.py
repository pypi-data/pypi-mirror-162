import functools
from typing import Callable, Optional

from pydantic import BaseModel

from hydrogen_lambda.content import get_content


class HydrogenLambda:
    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description

    def event_from(
        self,
        event_type: str,
        dlq: Optional[bool] = False,
        event_schema: Optional[BaseModel] = None,
        destination: Callable = None,
        destination_schema: Optional[BaseModel] = None,
    ):
        def decorator_event_from(lambda_handler):
            @functools.wraps(lambda_handler)
            def wrapper_event_from(*args, **kwargs):
                fallback = "sqs" if dlq else None
                records = get_content(
                    args[0],
                    event_type,
                    from_json=True,
                    raise_parsing_error=False,
                    fallback=fallback,
                )
                if event_schema:
                    records = [event_schema(**record) for record in records]

                result = lambda_handler(records)
                if destination and destination_schema:
                    result = destination(destination_schema(result))

                return result

            return wrapper_event_from

        return decorator_event_from

    def from_sns(
        self,
        dlq: Optional[bool] = False,
        event_schema: Optional[BaseModel] = None,
    ):
        return self.event_from("sns", dlq, event_schema)

    def from_sqs(
        self,
        dlq: Optional[bool] = False,
        event_schema: Optional[BaseModel] = None,
    ):
        return self.event_from("sqs", dlq, event_schema)

    def from_kinesis(
        self,
        dlq: Optional[bool] = False,
        event_schema: Optional[BaseModel] = None,
    ):
        return self.event_from("kinesis", dlq, event_schema)

    def handle_error(
        self, base_exception: Exception, error_handler: Callable = None, *options
    ):
        def decorator_handle_error(lambda_handler):
            @functools.wraps(lambda_handler)
            def wrapper_handle_error(*args, **kwargs):
                try:
                    return lambda_handler(args[0])
                except base_exception as exc:
                    return error_handler(args[0], exc, *options)

            return wrapper_handle_error

        return decorator_handle_error
