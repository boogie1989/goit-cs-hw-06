from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from pathlib import Path
import signal
import socket
import logging
from dotenv import load_dotenv
from socket_srv import socket_server
from multiprocessing import Process

WEB_DIR = "./front-init"
server_running = True

logging.basicConfig(
    filename="server.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        file_map = {
            "/": "index.html",
            "/message.html": "message.html",
            "/logo.png": "logo.png",
            "/style.css": "style.css"
        }
        file_type = {
            ".html": "text/html",
            ".png": "image/png",
            ".css": "text/css"
        }

        file_path = file_map.get(self.path, "error.html")
        content_type = file_type.get(Path(file_path).suffix, "text/html")

        self.send_response(200 if file_path != "error.html" else 404)
        self.send_header("Content-type", content_type)
        self.end_headers()

        with open(os.path.join(WEB_DIR, file_path), "rb") as file:
            self.wfile.write(file.read())

    def do_POST(self):
        if self.path == "/message":
            content_length = int(self.headers["Content-Length"])
            data = self.rfile.read(content_length)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(("localhost", self.server.server_port))
                sock.sendall(data)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Data sent to socket server")


def run_server(port):
    server_address = ("", port)
    httpd = HTTPServer(server_address, RequestHandler)
    try:
        print(f"Starting server on port {port}...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.error("Server stopping...")
        httpd.shutdown()


def stop_servers(signum, frame):
    global server_running
    print("Stopping servers...")
    server_running = False


signal.signal(signal.SIGINT, stop_servers)

if __name__ == "__main__":
    load_dotenv(Path(__file__).parent / ".env")
    http_port = int(os.getenv("HTTP_SERVER_PORT", "8080"))
    socket_port = int(os.getenv("SOCKET_SERVER_PORT", "9000"))

    web_process = Process(target=run_server, args=(http_port,))
    web_process.daemon = True
    web_process.start()

    socket_server(socket_port)
