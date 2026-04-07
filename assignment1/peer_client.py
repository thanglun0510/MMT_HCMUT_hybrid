import socket
import threading
import json
from peer_server import connections, handle_peer

def connect_to_peer(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))

        connections.append(s)

        threading.Thread(target=handle_peer, args=(s, (ip, port)), daemon=True).start()

        print(f"[CONNECTED TO PEER] {ip}:{port}")
        return True
    except Exception as e:
        print("[CONNECT ERROR]", e)
        return False


def send_message(conn, msg):
    try:
        conn.send(json.dumps(msg).encode())
    except:
        pass


def broadcast(msg):
    for conn in connections:
        send_message(conn, msg)
