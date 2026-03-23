from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def _send_text(self, code, body):
        payload = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send_json(self, code, body):
        payload = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        print("\n--- GET request ---")
        print(f"path: {self.path}")
        self._send_text(200, "GET ok\n")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)

        print("\n--- POST request ---")
        print(f"path: {self.path}")
        print("headers:")
        for key, value in self.headers.items():
            print(f"{key}: {value}")
        print("body:")
        print(body.decode("utf-8", errors="replace"))

        self._send_json(200, '{"status":"ok"}\n')


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8080
    server = HTTPServer((host, port), Handler)
    print(f"Listening on http://{host}:{port}")
    server.serve_forever()
