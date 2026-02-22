import json
import statistics
from http.server import BaseHTTPRequestHandler

# Load telemetry data
with open("telemetry.json") as f:
    DATA = json.load(f)

class handler(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        request = json.loads(body)

        regions = request.get("regions", [])
        threshold = request.get("threshold_ms", 0)

        result = {}

        for region in regions:
            records = [r for r in DATA if r["region"] == region]

            latencies = [r["latency_ms"] for r in records]
            uptimes = [r["uptime_pct"] for r in records]

            if not latencies:
                continue

            avg_latency = statistics.mean(latencies)
            p95_latency = statistics.quantiles(latencies, n=100)[94]
            avg_uptime = statistics.mean(uptimes)
            breaches = sum(1 for l in latencies if l > threshold)

            result[region] = {
                "avg_latency": avg_latency,
                "p95_latency": p95_latency,
                "avg_uptime": avg_uptime,
                "breaches": breaches
            }

        self._set_headers()
        self.wfile.write(json.dumps(result).encode())
