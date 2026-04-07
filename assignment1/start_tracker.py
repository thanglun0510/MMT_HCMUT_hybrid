import json
import sys
import os

# Đảm bảo Python tìm thấy package daemon trong thư mục hiện tại
sys.path.append(os.getcwd())

from daemon import AsynapRous

# 1. Khởi tạo ứng dụng Tracker sử dụng class AsynapRous
app = AsynapRous()

# 2. Database tạm thời để lưu trữ danh sách Peer (Tracking list)
# Cấu trúc lưu trữ: { "ID_Peer": {"ip": "192.168.x.x", "port": 8881} }
active_peers = {}

@app.route('/submit-info', methods=['POST'])
def register(headers, body):
    """
    Xử lý giai đoạn Peer Registration.
    Nhận thông tin định danh, IP và Port từ các Peer gửi lên.
    """
    try:
        # Giải mã dữ liệu JSON từ body bản tin HTTP
        data = json.loads(body)
        peer_id = data.get("id")
        
        # Cập nhật danh sách các peer đang hoạt động
        active_peers[peer_id] = {
            "ip": data.get("ip"),
            "port": data.get("port")
        }
        
        print(f"[Tracker] Đã đăng ký thành công Peer: {peer_id} tại {data.get('ip')}")
        
        # Trả về phản hồi JSON
        return json.dumps({"status": "success", "total": len(active_peers)}).encode("utf-8")
    except Exception as e:
        print(f"[Tracker] Lỗi: {e}")
        return json.dumps({"status": "error"}).encode("utf-8")

@app.route('/get-list', methods=['GET'])
def get_list(headers, body):
    """
    Xử lý giai đoạn Peer Discovery.
    Trả về danh sách toàn bộ các Peer đang online.
    """
    print(f"[Tracker] Đang gửi danh sách cho {len(active_peers)} peers.")
    return json.dumps(active_peers).encode("utf-8")

if __name__ == "__main__":
    # 3. Chuẩn bị địa chỉ và chạy Server
    # '0.0.0.0' để máy bạn cùng nhóm có thể kết nối vào qua Wi-Fi
    app.prepare_address('0.0.0.0', 9000)
    
    print("=== ASYNAPROUS TRACKER SERVER IS RUNNING ===")
    print("Mô hình: Client-Server (Tracker) | Port: 9000")
    
    # Kích hoạt backend không chặn (non-blocking)
    app.run()