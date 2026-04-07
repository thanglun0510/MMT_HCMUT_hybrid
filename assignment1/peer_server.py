import socket
import threading
import json

connections = []

def handle_peer(conn, addr):
    print(f"[P2P CONNECTED] {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            try:
                msg = json.loads(data.decode())
                print(f"[CHAT] {msg.get('from')}: {msg.get('message')}")
            except:
                print("[RAW]", data.decode())

    except Exception as e:
        print("[P2P ERROR]", e)

    finally:
        conn.close()
        if conn in connections:
            connections.remove(conn)
        print(f"[P2P DISCONNECTED] {addr}")


def start_peer_server(ip, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen()

    print(f"[P2P SERVER] {ip}:{port}")

    while True:
        conn, addr = server.accept()
        connections.append(conn)
        threading.Thread(target=handle_peer, args=(conn, addr), daemon=True).start()
