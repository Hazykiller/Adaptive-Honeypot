"""Local HTTP decoy. Emit one JSON event per handled request."""
import json
import sys
from collections import deque
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from time import monotonic


class DecoyServer(HTTPServer):
    def __init__(self, port=8080, *, output=None, clock=monotonic):
        super().__init__(("127.0.0.1", port), Handler)
        self.output = output if output is not None else sys.stdout
        self.clock = clock
        self.recent = deque(maxlen=5)

    def get_request(self):
        connection, address = super().get_request()
        connection.settimeout(3)
        return connection, address


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # The default access log includes the raw request target.

    def respond(self):
        server = self.server
        now = server.clock()
        server.recent.append(now)
        busy = len(server.recent) == 5 and now - server.recent[0] < 60
        status = 429 if busy else 404
        event = {"time": datetime.now(timezone.utc).isoformat(),
                 "method": self.command, "status": status}
        print(json.dumps(event), file=server.output, flush=True)
        self.send_response(status)
        self.send_header("Content-Length", "0")
        self.end_headers()

    do_GET = do_HEAD = do_POST = respond


if __name__ == "__main__":
    with DecoyServer() as server:
        print("Listening on http://127.0.0.1:8080", file=sys.stderr)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
