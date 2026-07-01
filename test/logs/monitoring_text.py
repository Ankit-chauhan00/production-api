import json
import logging
import time

from app.monitoring import (
    JsonFormatter,
    MetricsCollector,
    RequestTimer,
    get_logger,
)

"""uv run python -m test.logs.monitoring_text"""

print("=" * 60)
print("MONITORING TESTS")
print("=" * 60)

# -------------------------------------------------
# Test 1 : JSON Formatter
# -------------------------------------------------

print("\nTEST 1: JSON Formatter")
print("-" * 40)

logger = logging.getLogger("test")

record = logger.makeRecord(
    name="test",
    level=logging.INFO,
    fn="sample.py",
    lno=10,
    msg="Monitoring test",
    args=(),
    exc_info=None,
)

record.extra_data = {
    "request_id": "12345",
    "user": "ankit",
}

formatter = JsonFormatter()

output = formatter.format(record)

print(output)

data = json.loads(output)

assert data["level"] == "INFO"
assert data["message"] == "Monitoring test"
assert data["request_id"] == "12345"
assert data["user"] == "ankit"

print("JSON Formatter Passed")

# -------------------------------------------------
# Test 2 : Logger
# -------------------------------------------------

print("\nTEST 2: Structured Logger")
print("-" * 40)

logger = get_logger()

logger.info(
    "Application Started",
    extra={
        "extra_data": {
            "service": "production-api",
            "version": "1.0",
        }
    },
)

print("Logger Test Passed")

# -------------------------------------------------
# Test 3 : Metrics Collector
# -------------------------------------------------

print("\nTEST 3: Metrics Collector")
print("-" * 40)

metrics = MetricsCollector()

metrics.record_request(
    latency_ms=120,
    input_tokens=50,
    output_tokens=100,
    cache_hit=True,
)

metrics.record_request(
    latency_ms=220,
    input_tokens=40,
    output_tokens=80,
    cache_hit=False,
    error=True,
)

summary = metrics.summary

print(json.dumps(summary, indent=4))

assert summary["total_requests"] == 2
assert summary["total_errors"] == 1
assert summary["total_input_tokens"] == 90
assert summary["total_output_tokens"] == 180

print("Metrics Collector Passed")

# -------------------------------------------------
# Test 4 : Request Timer
# -------------------------------------------------

print("\nTEST 4: Request Timer")
print("-" * 40)

with RequestTimer() as timer:
    time.sleep(0.2)

print(f"Elapsed Time: {timer.elapsed_ms:.2f} ms")

assert timer.elapsed_ms >= 200

print("Request Timer Passed")

print("\nAll tests passed!")
