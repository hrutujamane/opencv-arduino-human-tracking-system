import cv2
import serial
import time

# -------------------------
# Arduino connection
# -------------------------

arduino = serial.Serial("COM6", 9600)

time.sleep(2)

# -------------------------
# Camera
# -------------------------

camera = cv2.VideoCapture(0)

# -------------------------
# Face detector
# -------------------------

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

while True:

    ret, frame = camera.read()

    if not ret:
        print("Camera error")
        break

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)
    )

    frame_width = frame.shape[1]

    # Default = no face
    command = "N"

    if len(faces) > 0:

        # Take first detected face
        x, y, w, h = faces[0]

        # Draw rectangle
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        # Face center
        face_center = x + w // 2

        screen_center = frame_width // 2

        # -----------------------
        # Decide direction
        # -----------------------

        if face_center < screen_center - 80:

            command = "L"

            cv2.putText(
                frame,
                "LEFT",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255),
                2
            )

        elif face_center > screen_center + 80:

            command = "R"

            cv2.putText(
                frame,
                "RIGHT",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255),
                2
            )

        else:

            command = "C"

            cv2.putText(
                frame,
                "CENTER",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

        cv2.putText(
            frame,
            "FACE DETECTED",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

    # Send command to Arduino
    arduino.write(command.encode())

    # Draw center line
    cv2.line(
        frame,
        (frame_width // 2, 0),
        (frame_width // 2, frame.shape[0]),
        (255, 0, 0),
        2
    )

    cv2.imshow(
        "AI Tracking Robot",
        frame
    )

    # Q to stop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()

arduino.close()

cv2.destroyAllWindows()