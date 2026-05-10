import cv2
import face_recognition
import os
import numpy as np
from database.mongo import db
from datetime import datetime
attendance_collection = db["attendance"]
KNOWN_FACES_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__)
        )
    ),
    "media",
    "faces"
)

known_faces = []
known_names = []

for filename in os.listdir(KNOWN_FACES_DIR):

    image_path = os.path.join(KNOWN_FACES_DIR, filename)

    image = face_recognition.load_image_file(image_path)

    face_encodings = face_recognition.face_encodings(image)

    if len(face_encodings) > 0:

        encoding = face_encodings[0]

        known_faces.append(encoding)

        known_names.append(os.path.splitext(filename)[0])

print("Loaded Faces:", known_names)


def recognize_faces():

    video_capture = cv2.VideoCapture(0)

    while True:

        ret, frame = video_capture.read()

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_frame)

        face_encodings = face_recognition.face_encodings(
            rgb_frame,
            face_locations
        )

        for (top, right, bottom, left), face_encoding in zip(
            face_locations,
            face_encodings
        ):

            matches = face_recognition.compare_faces(
                known_faces,
                face_encoding
            )

            name = "Unknown"

            face_distances = face_recognition.face_distance(
                known_faces,
                face_encoding
            )

            if len(face_distances) > 0:

                best_match_index = np.argmin(face_distances)

                if matches[best_match_index]:

                    name = known_names[best_match_index]
                    already_marked = attendance_collection.find_one({
    "student_name": name,
    "date": datetime.now().strftime("%Y-%m-%d")
})

if not already_marked:

    attendance_collection.insert_one({

        "student_name": name,
        "status": "Present",

        "date": datetime.now().strftime("%Y-%m-%d"),

        "time": datetime.now().strftime("%H:%M:%S"),

        "method": "Face Recognition"
    })

    print(f"{name} attendance marked")

             cv2.rectangle(
                frame,
                (left, top),
                (right, bottom),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                name,
                (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

        cv2.imshow("Smart Campus Face Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):

            break

    video_capture.release()

    cv2.destroyAllWindows()