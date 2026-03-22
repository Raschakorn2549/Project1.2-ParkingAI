from flask import Flask, Response, jsonify, render_template, request
from flask_cors import CORS
import cv2
import threading
import time
import requests
from vidgear.gears import CamGear
from parking import ParkingManagement
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)

# ====== LINE Config ======
load_dotenv()

LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_GROUP_ID     = os.getenv("LINE_GROUP_ID")

# ====== ค่าที่แชร์ระหว่าง thread ======
frame_lock = threading.Lock()
data_lock  = threading.Lock()

current_frame  = None
parking_data   = {"Occupancy": 0, "Available": 0}
last_occupancy = None
last_available = None

# ====== URL YouTube ======
YOUTUBE_URL = 'https://www.youtube.com/watch?v=4a-3iEM7bHk'  # เปลี่ยนเป็น URL ของคุณ

# ====== ฟังก์ชันส่ง LINE ======
def send_line(message):
    try:
        headers = {
            "Authorization": f"Bearer {LINE_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        body = {
            "to": LINE_GROUP_ID,
            "messages": [{"type": "text", "text": message}]
        }
        requests.post(
            "https://api.line.me/v2/bot/message/push",
            headers=headers,
            json=body,
            timeout=5
        )
        print("[LINE] ส่งสำเร็จ")
    except Exception as e:
        print(f"[LINE] error: {e}")

# ====== YOLO Thread ======
def yolo_thread():
    global current_frame, parking_data, last_occupancy, last_available

    stream = CamGear(
        source=YOUTUBE_URL,
        stream_mode=True,
        logging=False
    ).start()

    parking_manager = ParkingManagement(
        model="yolo11n.pt",
        classes=[2],
        json_file="bounding_boxes.json",
    )

    while True:
        im0 = stream.read()
        if im0 is None:
            print("Stream หลุด กำลัง retry...")
            time.sleep(2)
            continue

        im0 = cv2.resize(im0, (1280, 720))
        im0 = parking_manager.process_data(im0)

        occ   = parking_manager.pr_info.get("Occupancy", 0)
        avail = parking_manager.pr_info.get("Available", 0)

        with data_lock:
            parking_data["Occupancy"] = occ
            parking_data["Available"] = avail

        with frame_lock:
            current_frame = im0.copy()

        # ส่ง LINE เมื่อตัวเลขเปลี่ยน
        if occ != last_occupancy or avail != last_available:
            last_occupancy = occ
            last_available = avail
            total = occ + avail
            pct   = round((occ / total) * 100) if total > 0 else 0
            msg = (
                f"🅿️ อัปเดตที่จอดรถ\n"
                f"🚗 ถูกใช้: {occ} คัน\n"
                f"✅ ว่าง: {avail} คัน\n"
                f"📊 การใช้งาน: {pct}%"
            )
            threading.Thread(target=send_line, args=(msg,), daemon=True).start()

# ====== Video Stream Generator ======
def generate_frames():
    while True:
        with frame_lock:
            if current_frame is None:
                time.sleep(0.1)
                continue
            frame = current_frame.copy()

        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.033)

# ====== Routes ======
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/data')
def data():
    with data_lock:
        return jsonify(parking_data)

@app.route('/send_line', methods=['POST'])
def manual_send_line():
    with data_lock:
        occ   = parking_data["Occupancy"]
        avail = parking_data["Available"]
    total = occ + avail
    pct   = round((occ / total) * 100) if total > 0 else 0
    msg = (
        f"📢 รายงานสถานะที่จอดรถ\n"
        f"🚗 ถูกใช้: {occ} คัน\n"
        f"✅ ว่าง: {avail} คัน\n"
        f"📊 การใช้งาน: {pct}%"
    )
    threading.Thread(target=send_line, args=(msg,), daemon=True).start()
    return jsonify({"status": "ok"})

# ====== Main ======
if __name__ == '__main__':
    t = threading.Thread(target=yolo_thread, daemon=True)
    t.start()
    print("🚀 Flask API รันที่ http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)