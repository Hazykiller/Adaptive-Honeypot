import io
import json
import threading
import unittest
from http.client import HTTPConnection
from honeypot import DecoyServer


class DecoyTests(unittest.TestCase):
    def test_repeated_requests_and_recovery(self):
        output = io.StringIO()
        now = [0]
        with DecoyServer(0, output=output, clock=lambda: now[0]) as server:
            worker = threading.Thread(target=server.serve_forever)
            worker.start()
            try:
                for method, expected in zip(["GET", "HEAD", "POST", "GET", "GET", "GET"],
                                            [404, 404, 404, 404, 429, 404]):
                    conn = HTTPConnection(*server.server_address, timeout=3)
                    try:
                        conn.request(method, "/test?secret=private", headers={"Cookie": "private"})
                        reply = conn.getresponse()
                        self.assertEqual(reply.status, expected)
                        self.assertEqual(reply.read(), b"")
                    finally:
                        conn.close()
                    if expected == 429:
                        now[0] = 60
            finally:
                server.shutdown()
                worker.join()
        events = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(len(events), 6)
        self.assertTrue(all(set(event) == {"method", "status", "time"} for event in events))
        self.assertNotIn("private", output.getvalue())
