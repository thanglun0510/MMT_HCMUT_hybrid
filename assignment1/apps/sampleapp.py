import sys
import os
import json
import threading
import argparse

# PHẢI đặt 2 dòng này lên trên cùng, trước khi import daemon
sys.path.append(os.getcwd()) 

from daemon import AsynapRous
# Import các logic P2P và Tracker từ các file bạn đã gửi
from tracker_client import register_peer, get_peer_list
from peer_server import start_peer_server
from peer_client import connect_to_peer, broadcast, connections
from protocol import create_message

app = AsynapRous()
MY_ID = "Guest"
MY_IP = "127.0.0.1"
MY_PORT = 2026

# --- CÁC ROUTE ĐIỀU KHIỂN PEER QUA HTTP ---

@app.route('/login', methods=['POST'])
def login(headers, body):
    """Xác nhận đăng nhập trên máy Peer"""
    print(f"[App] Peer {MY_ID} logging in...")
    data = {"message": f"Welcome {MY_ID} to the P2P Network"}
    return json.dumps(data).encode("utf-8")

@app.route('/connect-all', methods=['GET'])
def connect_all_peers(headers, body):
    """
    Tự động hỏi Tracker (máy Thắng) để lấy danh sách 
    và kết nối tới tất cả các Peer khác.
    """
    print("[App] Fetching peer list from Tracker...")
    try:
        peer_list = get_peer_list() # Gọi tới máy Thắng
        count = 0
        for p_id, info in peer_list.items():
            if p_id != MY_ID: # Không tự kết nối chính mình
                success = connect_to_peer(info['ip'], info['port'])
                if success: count += 1
        
        return json.dumps({"status": "connected", "new_peers": count}).encode("utf-8")
    except Exception as e:
        return json.dumps({"error": str(e)}).encode("utf-8")

@app.route('/broadcast-peer', methods=['POST'])
def broadcast_to_network(headers, body):
    """Gửi tin nhắn tới tất cả Peer đã kết nối P2P"""
    try:
        data = json.loads(body)
        msg_text = data.get("message", "Hello everyone!")
        
        # Tạo gói tin theo đúng giao thức protocol.py
        msg = create_message(MY_ID, msg_text)
        broadcast(msg)
        
        return json.dumps({"status": "sent", "to_active_connections": len(connections)}).encode("utf-8")
    except Exception as e:
        return json.dumps({"error": str(e)}).encode("utf-8")
@app.route('/hello', methods=['PUT'])
async def hello(headers, body):
    """
    Test khả năng xử lý bất đồng bộ (async) của Framework với lệnh PUT
    """
    print(f"[SampleApp] ['PUT'] **ASYNC** Hello in {headers} to {body}")
    data =  {"id": 1, "name": "Alice", "email": "alice@example.com"}
    return json.dumps(data).encode("utf-8")
# --- HÀM KHỞI CHẠY HỆ THỐNG ---

def create_sampleapp(ip, port, peer_id):
    global MY_ID, MY_IP, MY_PORT
    MY_ID = peer_id
    MY_IP = ip
    MY_PORT = port
    
    # 1. Khởi chạy P2P Server ngầm (để nhận tin nhắn từ bạn bè)
    # Thường Port P2P sẽ khác Port HTTP để tránh xung đột
    p2p_port = port + 1000 
    threading.Thread(target=start_peer_server, args=(ip, p2p_port), daemon=True).start()
    print(f"[App] P2P Server listening on {ip}:{p2p_port}")

    # 2. Tự động đăng ký báo danh lên máy Thắng (Tracker)
    print(f"[App] Registering {peer_id} to Tracker...")
    register_peer(peer_id, ip, p2p_port) 

    # 3. Chạy HTTP Server để nhận lệnh điều khiển (connect-all, broadcast...)
    app.prepare_address(ip, port)
    print(f"[App] HTTP Control API running on {ip}:{port}")
    app.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', default='127.0.0.1') # Sửa thành IP máy người chạy
    parser.add_argument('--port', type=int, default=2026)
    parser.add_argument('--id', default='Peer_A')
    
    args = parser.parse_args()
    create_sampleapp(args.ip, args.port, args.id)