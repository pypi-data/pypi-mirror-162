from ddtrace import Span
from ddtrace.context import Context

from hydrogen_lambda.datadog.utils import (
    MESSAGE_ATTRIBUTE_PARENT_ID,
    MESSAGE_ATTRIBUTE_TRACE_ID,
)


class SNSPropagator:
    """
    Datadog trace propagation through SNS message attributes
    """

    @staticmethod
    def inject(span_context: Span, message_attributes: dict):
        """
        Inject datadogTraceId and datadogSpanId into the SNS message attributes
        """
        message_attributes.update(
            {
                MESSAGE_ATTRIBUTE_TRACE_ID: {
                    "DataType": "String",
                    "StringValue": str(span_context.trace_id),
                },
                MESSAGE_ATTRIBUTE_PARENT_ID: {
                    "DataType": "String",
                    "StringValue": str(span_context.span_id),
                },
            }
        )

    @staticmethod
    def extract(message_attributes: dict) -> Context:
        """
        Extract datadogTraceId and datadogSpanId from the SNS message attributes
        """
        trace_id = message_attributes.get(MESSAGE_ATTRIBUTE_TRACE_ID, 0)
        parent_span_id = message_attributes.get(MESSAGE_ATTRIBUTE_PARENT_ID, 0)

        if trace_id and parent_span_id:
            trace_id = trace_id.get("StringValue", 0)
            parent_span_id = parent_span_id.get("StringValue", 0)

        return Context(
            trace_id=int(trace_id) or None,
            span_id=int(parent_span_id) or None,
        )

    @staticmethod
    def activate(event: dict):
        try:
            message_attributes = event["Records"][0]["Sns"]["MessageAttributes"]
        except KeyError:
            print("No MessageAttributes found on Sns message")
        else:
            ctx = SNSPropagator.extract(message_attributes)
            tracer.context_provider.activate(ctx)
