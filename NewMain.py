import cv2
import requests
from vidgear.gears import CamGear
from parking import ParkingManagement

# ====== LINE / WEBHOOK ======
LINE_ACCESS_TOKEN = "cMsPyQTfhVOuZ+Ejlz3DrELCSoZfUarin2VlZ7/PuZRhO/rPSCT4WJcTkV5UrusZlUMGuNrsm4Hws2UuVSj0O/Dfa9Rxv2zbJu+PvSjOLdF0R7npDgf5ij+HKR4bSGDib31Z/nTZ/tA+XAwEdF5LuQdB04t89/1O/w1cDnyilFU="
LINE_GROUP_ID = "C32bc81974bec31c0288844171d430bd6"
WEBHOOK_URL = "https://webhook.site/06c33b30-36dd-43b0-a80f-a5abba9128d2"

# ====== VIDEO SOURCE ======
stream = CamGear(
    source='https://www.youtube.com/watch?v=4a-3iEM7bHk',  # ใช้ตัวที่ใช้ได้
    stream_mode=True,
    logging=True
).start()

# ====== YOLO PARKING ====== 
parking_manager = ParkingManagement(
    model="yolo11n.pt",
    classes=[2],
    json_file="bounding_boxes.json",
)

# ====== เก็บค่าก่อนหน้า ======
last_occupancy = None
last_available = None

while True:
    im0 = stream.read()

    # 🔥 กันพัง (สำคัญมาก)
    if im0 is None:
        print("ดึงภาพไม่ได้")
        break

    im0 = cv2.resize(im0, (1280, 720))

    # process YOLO
    im0 = parking_manager.process_data(im0)

    # อ่านค่า
    occupancy = parking_manager.pr_info.get('Occupancy', 0)
    available = parking_manager.pr_info.get('Available', 0)

    # ถ้ามีการเปลี่ยนแปลง
    if occupancy != last_occupancy or available != last_available:
        message = f"🚗 ที่จอดรถอัปเดต:\n🅿️ ถูกใช้: {occupancy} คัน\n✅ ว่าง: {available} คัน"

        print(message)  # 🔥 แสดงใน console ด้วย

        # ====== ส่ง Webhook ======
        if WEBHOOK_URL:
            try:
                requests.post(WEBHOOK_URL, json={
                    "Occupancy": occupancy,
                    "Available": available
                })
            except:
                print("❌ Webhook error")

        # ====== ส่ง LINE ======
        if LINE_ACCESS_TOKEN and LINE_GROUP_ID:
            try:
                headers = {
                    "Authorization": f"Bearer {LINE_ACCESS_TOKEN}",
                    "Content-Type": "application/json"
                }
                data = {
                    "to": LINE_GROUP_ID,
                    "messages": [{"type": "text", "text": message}]
                }
                requests.post(
                    "https://api.line.me/v2/bot/message/push",
                    headers=headers,
                    json=data
                )
            except:
                print("❌ LINE error")

        # อัปเดตค่า
        last_occupancy = occupancy
        last_available = available

    # แสดงผล
    cv2.imshow("Parking Detection", im0)

    if cv2.waitKey(1) & 0xFF == 27:
        break

# ปิด
stream.stop()
cv2.destroyAllWindows()