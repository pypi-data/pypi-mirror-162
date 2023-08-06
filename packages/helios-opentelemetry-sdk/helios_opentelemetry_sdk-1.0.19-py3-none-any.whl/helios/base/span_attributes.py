from opentelemetry.semconv.trace import SpanAttributes as OpenTelemetrySpanAttributes


class SpanAttributes(OpenTelemetrySpanAttributes):
    DB_QUERY_RESULT = 'db.query_result'
    HTTP_REQUEST_BODY = 'http.request.body'
    HTTP_RESPONSE_BODY = 'http.response.body'
    RPC_REQUEST_BODY = 'rpc.request.body'
    RPC_RESPONSE_BODY = 'rpc.response.body'
    MESSAGING_PAYLOAD = 'messaging.payload'
