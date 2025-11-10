from starlette.requests import Request
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.trace.status import Status, StatusCode

_already_instrumented = False


trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({SERVICE_NAME: "my-fastapi-service"}))
)
tracer = trace.get_tracer(__name__)

otlp_exporter = OTLPSpanExporter(endpoint="grpc://localhost:4317", insecure=True)

span_processor = BatchSpanProcessor(otlp_exporter)

trace.get_tracer_provider().add_span_processor(span_processor)


async def handle_tracing(request: Request, call_next):
    tracer = trace.get_tracer("request-tracer")

    with tracer.start_as_current_span(f"{request.method} {request.url.path}") as span:
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.url", str(request.url))
        span.set_attribute("client.ip", request.client.host if request.client else "unknown")

        try:
            response = await call_next(request)
            span.set_attribute("http.status_code", response.status_code)
            if response.status_code >= 400:
                span.set_status(Status(StatusCode.ERROR))
            return response
        except Exception as e:
            # Record exceptions inside the span
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            raise
