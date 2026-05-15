import cv2
import numpy as np
import time

from database.mongo import db
from datetime import datetime


# ==========================================
# DATABASE
# ==========================================

attendance_collection = db["attendance_logs"]

students_collection = db["students"]


# ==========================================
# LOAD STUDENTS
# ==========================================

known_faces = []
known_names = []

print("Loading students from MongoDB...")

students = students_collection.find()

for student in students:

    student_name = student.get("student_name", "").strip()

    face_encodings = student.get(
        "face_encodings",
        []
    )

    for encoding in face_encodings:

        known_faces.append(
            np.array(encoding)
        )

        known_names.append(
            student_name
        )

        print(f"Loaded: {student_name}")

print("Known Names:", known_names)


# ==========================================
# FACE ATTENDANCE
# ==========================================

def recognize_faces():

    try:
        import face_recognition
    except ImportError:
        print("face_recognition package not installed. Face attendance cannot start.")
        return

    # ==========================================
    # OPEN CAMERA
    # ==========================================

    video_capture = cv2.VideoCapture(
        0,
        cv2.CAP_DSHOW
    )

    if not video_capture.isOpened():

        print("Cannot Open Camera")

        return

    print("Camera Started")

    # ==========================================
    # CAMERA QUALITY
    # ==========================================

    video_capture.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        1280
    )

    video_capture.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        720
    )

    # ==========================================
    # PREVENT MULTIPLE ENTRIES
    # ==========================================

    last_detected_name = None
    last_detection_time = 0

    # ==========================================
    # AUTO CLOSE TIMER
    # ==========================================

    start_time = time.time()

    while True:

        ret, frame = video_capture.read()

        if not ret:

            print("Camera Error")

            break

        # ==========================================
        # SMALL FRAME FOR FAST PROCESSING
        # ==========================================

        small_frame = cv2.resize(
            frame,
            (0, 0),
            fx=0.25,
            fy=0.25
        )

        rgb_small_frame = cv2.cvtColor(
            small_frame,
            cv2.COLOR_BGR2RGB
        )

        # ==========================================
        # DETECT FACE
        # ==========================================

        face_locations = face_recognition.face_locations(
            rgb_small_frame,
            model="hog"
        )

        face_encodings = face_recognition.face_encodings(
            rgb_small_frame,
            face_locations
        )

        # ==========================================
        # PROCESS FACE
        # ==========================================

        for (
            top,
            right,
            bottom,
            left
        ), face_encoding in zip(
            face_locations,
            face_encodings
        ):

            matches = face_recognition.compare_faces(
                known_faces,
                face_encoding,
                tolerance=0.5
            )

            name = "Unknown"

            face_distances = face_recognition.face_distance(
                known_faces,
                face_encoding
            )

            if len(face_distances) > 0:

                best_match_index = np.argmin(
                    face_distances
                )

                if matches[best_match_index]:

                    name = known_names[
                        best_match_index
                    ]

                    current_time_seconds = time.time()

                    # ==========================================
                    # PREVENT REPEATED DETECTION
                    # ==========================================

                    if (
                        last_detected_name == name
                        and
                        current_time_seconds - last_detection_time < 10
                    ):

                        continue

                    last_detected_name = name
                    last_detection_time = current_time_seconds

                    today_date = datetime.now().strftime(
                        "%Y-%m-%d"
                    )

                    current_clock_time = datetime.now().strftime(
                        "%H:%M:%S"
                    )

                    # ==========================================
                    # CHECK IN
                    # ==========================================

                    check_in_record = attendance_collection.find_one({

                        "student_name": name,

                        "attendance_date": today_date,

                        "type": "IN"

                    })

                    # ==========================================
                    # CHECK OUT
                    # ==========================================

                    check_out_record = attendance_collection.find_one({

                        "student_name": name,

                        "attendance_date": today_date,

                        "type": "OUT"

                    })

                    # ==========================================
                    # FIRST ENTRY = IN
                    # ==========================================

                    if not check_in_record:

                        attendance_collection.insert_one({

                            "student_name": name,

                            "status": "Present",

                            "attendance_date": today_date,

                            "time": current_clock_time,

                            "type": "IN",

                            "method": "Face Recognition"

                        })

                        print(f"{name} CHECK-IN marked")

                    # ==========================================
                    # SECOND ENTRY = OUT
                    # ==========================================

                    elif not check_out_record:

                        attendance_collection.insert_one({

                            "student_name": name,

                            "status": "Present",

                            "attendance_date": today_date,

                            "time": current_clock_time,

                            "type": "OUT",

                            "method": "Face Recognition"

                        })

                        print(f"{name} CHECK-OUT marked")

                    # ==========================================
                    # ALREADY COMPLETED
                    # ==========================================

                    else:

                        print(
                            f"{name} attendance already completed today"
                        )

            # ==========================================
            # FACE BOX
            # ==========================================

            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            cv2.rectangle(
                frame,
                (left, top),
                (right, bottom),
                (0, 255, 0),
                3
            )

            cv2.putText(
                frame,
                name,
                (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

        # ==========================================
        # SHOW CAMERA
        # ==========================================

        cv2.imshow(
            "Smart Attendance System",
            frame
        )

        # ==========================================
        # AUTO CLOSE AFTER 15 SECONDS
        # ==========================================

        if time.time() - start_time > 15:

            print("Camera Auto Closed")

            break

        # ==========================================
        # PRESS Q TO EXIT
        # ==========================================

        if cv2.waitKey(1) & 0xFF == ord('q'):

            print("Camera Closed By User")

            break

    # ==========================================
    # RELEASE CAMERA
    # ==========================================

    video_capture.release()

    cv2.destroyAllWindows()