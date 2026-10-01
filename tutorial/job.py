"""A small CI workload: child spans, a counter, a histogram, and correlated stdout."""
import json
import os
import time

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

# Job IDs are useful on traces/logs. Keep metric dimensions small and bounded.
resource_attributes = {"service.name": "buildkite-job-lab"}
for variable, attribute in (
    ("BUILDKITE_JOB_ID", "buildkite.job.id"),
    ("BUILDKITE_BUILD_NUMBER", "buildkite.build.number"),
    ("BUILDKITE_PIPELINE_SLUG", "buildkite.pipeline.slug"),
    ("K8S_POD_UID", "k8s.pod.uid"),
):
    if os.getenv(variable):
        resource_attributes[attribute] = os.environ[variable]
traces = TracerProvider(resource=Resource.create(resource_attributes))
traces.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(traces)
meters = MeterProvider(
    resource=Resource.create({"service.name": "buildkite-job-lab"}),
    metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter())],
)
metrics.set_meter_provider(meters)
tracer = trace.get_tracer("otel-buildkite-tutorial")
meter = metrics.get_meter("otel-buildkite-tutorial")
completed = meter.create_counter("lab.ci.runs", unit="{run}")
duration = meter.create_histogram("lab.ci.duration", unit="s")

# Python's HTTP carrier getter expects lowercase keys. The agent uses uppercase env names.
carrier = {k.lower(): os.environ[k] for k in ("TRACEPARENT", "TRACESTATE") if k in os.environ}
parent = TraceContextTextMapPropagator().extract(carrier)
started = time.monotonic()
outcome = "success"
try:
    with tracer.start_as_current_span("ci.exercise", context=parent):
        for phase in ("prepare", "test", "package"):
            with tracer.start_as_current_span(phase) as span:
                context = span.get_span_context()
                print(json.dumps({
                    "message": f"running {phase}",
                    "trace_id": f"{context.trace_id:032x}",
                    "span_id": f"{context.span_id:016x}",
                    "buildkite.job.id": os.getenv("BUILDKITE_JOB_ID", "local"),
                }), flush=True)
                time.sleep(float(os.getenv("LAB_PHASE_SECONDS", "1")))
                if phase == "test" and os.getenv("LAB_FAIL") == "1":
                    raise RuntimeError("intentional tutorial failure")
except Exception:
    outcome = "failure"
    raise
finally:
    labels = {"outcome": outcome}
    completed.add(1, labels)
    duration.record(time.monotonic() - started, labels)
    # CI processes can exit before the periodic exporter runs. Flush while still alive.
    traces.force_flush()
    meters.force_flush()
    traces.shutdown()
    meters.shutdown()
