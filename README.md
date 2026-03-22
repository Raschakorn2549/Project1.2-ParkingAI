# 🅿️ Real-time Parking Lot Detection System

ระบบตรวจสอบที่จอดรถแบบ Real-time ด้วย YOLO11 และ Flask + React Dashboard

## 📌 Features
- ตรวจจับรถจาก YouTube Live Stream ด้วย YOLO11
- แสดงจำนวนช่องจอดที่ว่างและถูกใช้งานแบบ Real-time
- Dashboard สวยงามด้วย React + Tailwind CSS
- แจ้งเตือนผ่าน LINE Messaging API อัตโนมัติเมื่อสถานะเปลี่ยน
- มีปุ่มกดส่งสถานะไปยัง LINE ได้ทันที

## 🛠️ Tech Stack
- **AI/CV**: YOLO11, OpenCV
- **Backend**: Python, Flask
- **Frontend**: React, Tailwind CSS, Vite
- **Notification**: LINE Messaging API
- **Stream**: vidgear, yt-dlp

## 📁 Project Structure
```
├── server.py              # Flask API + YOLO thread
├── NewMain.py             # รันดู YOLO ผลลัพธ์เฉยๆ ไม่มี web
├── parking.py             # Parking zone detection logic
├── bounding_boxes.json    # Parking zone coordinates
├── img.py                 # Stream test utility
├── se.py                  # Parking zone selector
├── .env                   # API keys (ไม่อัป GitHub)
├── requirements.txt       # Python dependencies
└── parking-frontend/      # React + Tailwind frontend
    └── src/
        └── App.jsx
```

## ⚙️ Installation

### Backend
```bash
pip install -r requirements.txt
```

### Frontend
```bash
cd parking-frontend
npm install
```

## 🚀 How to Run

### แบบมี Web Dashboard
**Terminal 1 — Flask Backend:**
```bash
py server.py
```

**Terminal 2 — React Frontend:**
```bash
cd parking-frontend
npm run dev
```

เปิด browser ที่ `http://localhost:5173`

### แบบไม่มี Web (ดูผลลัพธ์ใน window เฉยๆ)
```bash
py NewMain.py
```

## 🔐 Environment Variables
สร้างไฟล์ `.env` แล้วใส่:
```
LINE_ACCESS_TOKEN=your_token_here
LINE_GROUP_ID=your_group_id_here
```