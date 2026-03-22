import cv2
import time
from vidgear.gears import CamGear

# นับจำนวนรูป
cpt = 0
maxFrames = 1  #5 = เซฟ 5 รูป

#URL 
url = 'https://www.youtube.com/watch?v=4a-3iEM7bHk'

# เปิด stream
stream = CamGear(source=url, stream_mode=True, logging=True).start()

time.sleep(2) 

while cpt < maxFrames:
    frame = stream.read()
    
    if frame is None:
        print("ไม่สามารถดึงภาพจาก stream ได้")
        break

    # resize
    frame = cv2.resize(frame, (1280, 720))

    # แสดงภาพ
    cv2.imshow("test window", frame)

    # เซฟรูป
    filename = f"img_{cpt}.jpg"
    cv2.imwrite(filename, frame)
    print(f"Saved: {filename}")

    cpt += 1

    # กด ESC เพื่อออก
    if cv2.waitKey(5) & 0xFF == 27:
        break

# ปิด stream
stream.stop()
cv2.destroyAllWindows()