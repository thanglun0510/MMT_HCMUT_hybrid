import socket
import threading
import json
from channel import add_message

# 1. Khai báo danh sách lưu tin nhắn
chat_history = [] 
connections = []

# 2. Hợp nhất thành MỘT hàm handle_peer duy nhất và chuẩn lề
def handle_peer(conn, addr):
    print(f"[P2P CONNECTED] {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            try:
                # Đọc gói tin JSON gửi tới
                msg = json.loads(data.decode())
                
                # Trích xuất người gửi và nội dung
                sender_id = msg.get('from', 'Unknown')
                msg_text = msg.get('message', '')
                channel_name = msg.get("channel", "general")
                
                # IN RA TERMINAL
                print(f"[CHAT] {sender_id}: {msg_text}")
                
                # LƯU VÀO LỊCH SỬ ĐỂ GIAO DIỆN WEB ĐỌC ĐƯỢC
                chat_history.append(f"{sender_id}: {msg_text}")
                
                # Lưu vào logic channel của thầy (nếu có)
                add_message(channel_name, msg)

            except Exception as json_err:
                # Nếu không phải JSON chuẩn thì in dạng thô
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