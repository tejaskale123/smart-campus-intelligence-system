import cv2
import face_recognition
import numpy as np

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

    student_name = student.get("student_name")

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

    video_capture = cv2.VideoCapture(
        0,
        cv2.CAP_DSHOW
    )

    if not video_capture.isOpened():

        print("Cannot Open Camera")

        return

    # ==========================================
    # CAMERA SIZE
    # ==========================================

    video_capture.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        1280
    )

    video_capture.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        720
    )

    attendance_done = False
    last_detected_name = None
    while True:
       
        ret, frame = video_capture.read()

        if not ret:

            print("Camera Error")

            break

        # ==========================================
        # RESIZE FRAME
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
        # FACE DETECTION
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
        # FACE MATCHING
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

            name = "Unknown"

            matches = face_recognition.compare_faces(
                known_faces,
                face_encoding,
                tolerance=0.5
            )

            face_distances = face_recognition.face_distance(
                known_faces,
                face_encoding
            )

            if len(face_distances) > 0:

                best_match_index = np.argmin(
                    face_distances
                )

  if matches[best_match_index]:

            if last_detected_name == known_names[best_match_index]:

                continue

            last_detected_name = known_names[best_match_index]

            name = known_names[
                best_match_index
            ] if matches[best_match_index]:

                    name = known_names[
                        best_match_index
                    ]

                    today_date = datetime.now().strftime(
                        "%Y-%m-%d"
                    )

                    current_time = datetime.now().strftime(
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

                            "time": current_time,

                            "type": "IN",

                            "method": "Face Recognition"

                        })

                        print(f"{name} CHECK-IN marked")

                        cv2.waitKey(3000)

                    # ==========================================
                    # SECOND ENTRY = OUT
                    # ==========================================

                    elif not check_out_record:

                        attendance_collection.insert_one({

                            "student_name": name,

                            "status": "Present",

                            "attendance_date": today_date,

                            "time": current_time,

                            "type": "OUT",

                            "method": "Face Recognition"

                        })

                        print(f"{name} CHECK-OUT marked")

                        cv2.waitKey(3000)

                    # ==========================================
                    # BOTH DONE
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

            cv2.rectangle(
                frame,
                (left, bottom - 35),
                (right, bottom),
                (0, 255, 0),
                cv2.FILLED
            )

            cv2.putText(
                frame,
                name,
                (left + 6, bottom - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 0),
                2
            )

        # ==========================================
        # SHOW CAMERA
        # ==========================================

       

        # ==========================================
        # AUTO CLOSE AFTER SUCCESS
        # ==========================================

        

        # ==========================================
        # PRESS Q TO EXIT
        # ==========================================

        

    # ==========================================
    # RELEASE CAMERA
    # ==========================================

    video_capture.release()

    