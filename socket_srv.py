import socket
from pathlib import Path
from datetime import datetime
import logging
import urllib.parse
from dotenv import load_dotenv
import pymongo
from multiprocessing import Process

from connect_db import create_connect

# Configure logging
logging.basicConfig(filename="server.log", level=logging.ERROR,
                    format="%(asctime)s - %(levelname)s - %(message)s")
server_running = True


def save_message_to_db(username, message):
    """Save message details to MongoDB."""
    try:
        client = create_connect()
        db = client["db-messages"]
        collection = db["messages"]
        post = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "username": username,
            "message": message,
        }
        collection.insert_one(post)
        print("Message saved in MongoDB")
    except pymongo.errors.PyMongoError as e:
        logging.error(f"Database error: {e}")
    finally:
        client.close()


def handle_client(connection, address):
    """Handle incoming client connections and messages."""
    print(f"Connection from {address} established")
    try:
        while True:
            data = connection.recv(1024).decode("utf-8")
            if not data:
                break
            parsed_data = urllib.parse.parse_qs(data)
            username = parsed_data.get("username", [""])[0]
            message = parsed_data.get("message", [""])[
                0].strip().replace("\r\n", " ")
            print(f"Received data: username={username}, message={message}")

            save_message_to_db(username, message)
    except Exception as e:
        logging.error(f"Error processing data: {e}")
    finally:
        connection.close()


def socket_server(port):
    """Initialize and run the socket server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("", port))
        server.listen()
        print(f"Starting socket server on port {port}")
        global server_running
        try:
            while server_running:
                conn, addr = server.accept()
                p = Process(target=handle_client, args=(conn, addr))
                p.start()
        except KeyboardInterrupt:
            logging.error("Server stopping...")
        finally:
            server_running = False


if __name__ == "__main__":
    load_dotenv(Path(__file__).parent / ".env")
    PORT2 = int(os.getenv("SOCKET_SERVER_PORT", "9000"))
    socket_server(PORT2)
