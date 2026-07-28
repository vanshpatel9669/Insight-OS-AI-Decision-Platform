"""Prometheus metrics + OpenTelemetry tracing wiring for the FastAPI app.
Mirrors the TriageAI project's observability module for consistency across
this portfolio.
"""

from __future__ import annotations

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from prometheus_fastapi_instrumentator import Instrumentator


def build_tracer_provider(
    service_name: str, console_export: bool = False, otlp_endpoint: str | None = None
) -> TracerProvider:
    provider = TracerProvider(resource=Resource.create({SERVICE_NAME: service_name}))
    if otlp_endpoint:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint)))
    elif console_export:
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    return provider


def configure_tracing(
    service_name: str, console_export: bool = False, otlp_endpoint: str | None = None
) -> None:
    """No-ops if a TracerProvider is already registered globally in this
    process — the OTel SDK only allows setting it once.
    """
    if isinstance(trace.get_tracer_provider(), TracerProvider):
        return
    trace.set_tracer_provider(build_tracer_provider(service_name, console_export, otlp_endpoint))


def instrument_app(app: FastAPI) -> None:
    FastAPIInstrumentor.instrument_app(app)
    Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=True)
