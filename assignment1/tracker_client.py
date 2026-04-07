import json
import http.client

TRACKER_HOST = "localhost"
TRACKER_PORT = 9000

def register_peer(peer_id, ip, port):
    conn = http.client.HTTPConnection(TRACKER_HOST, TRACKER_PORT)

    data = json.dumps({
        "id": peer_id,
        "ip": ip,
        "port": port
    })

    conn.request("POST", "/submit-info", data)
    res = conn.getresponse()
    print("[REGISTER]", res.read().decode())


def get_peer_list():
    conn = http.client.HTTPConnection(TRACKER_HOST, TRACKER_PORT)
    conn.request("GET", "/get-list")

    res = conn.getresponse()
    data = res.read().decode()

    return json.loads(data)
