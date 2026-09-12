import cv2

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Camera not found")
    exit()

while True:
    ret, frame = camera.read()

    if not ret:
        print("Failed to capture image")
        break

    cv2.imshow("OpenCV Camera Test", frame)

    # Press Q to close
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()