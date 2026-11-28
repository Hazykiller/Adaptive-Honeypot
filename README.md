# Adaptive Honeypot

Run `python honeypot.py` with Python 3.10 or later, then visit http://127.0.0.1:8080 from the same computer. Stop it with Ctrl+C. Python's standard library provides the server and tests.

This HTTP decoy returns 404 for GET, HEAD and POST. When five handled requests arrive within 60 seconds across the listener, it returns 429. Each subsequent request reevaluates that window. JSON events on standard output contain the UTC time, method and response status. Paths, query strings, request headers and bodies are omitted.

Run `python -m unittest -v` to exercise requests over a local socket, including threshold expiry and event privacy.
