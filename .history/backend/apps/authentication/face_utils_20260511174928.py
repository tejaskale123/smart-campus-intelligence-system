import cv2
import face_recognition
import os
import numpy as np

from database.mongo import db
from datetime import datetime


# ==========================================
# DATABASE
# ==========================================

attendance_collection = db["attendance"]


# ==========================================
# KNOWN FACES DIRECTORY
# ==========================================

KNOWN_FACES_DIR = os.path.join(

    os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__)
        )
    ),

    "media",

    "faces"

)


# ==========================================
# STORAGE
# ==========================================

known_faces = []

known_names = []


print("Loading known faces...")


# ==========================================
# LOAD ALL FACES
# ==========================================

for person_name in os.listdir(KNOWN_FACES_DIR):

    person_folder = os.path.join(

        KNOWN_FACES_DIR,

        person_name

    )


    # SKIP NORMAL FILES
    if not os.path.isdir(person_folder):

        continue


    for image_name in os.listdir(person_folder):

        image_path = os.path.join(

            person_folder,

            image_name

        )

        try:

            image = face_recognition.load_image_file(

                image_path

            )

            encodings = face_recognition.face_encodings(

                image

            )

            if len(encodings) > 0:

                known_faces.append(

                    encodings[0]

                )

                known_names.append(

                    person_name

                )

                print(

                    f"Loaded: {person_name}"

                )

            else:

                print(

                    f"No face found in {image_name}"

                )

        except Exception as e:

            print(

                f"Error loading {image_name}: {e}"

            )


print("Known Names:", known_names)


# ==========================================
# FACE RECOGNITION
# ==========================================

def recognize_faces():

    video_capture = cv2.VideoCapture(0)


    # ==========================================
    # HD CAMERA
    # ==========================================

    video_capture.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        1280
    )

    video_capture.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        720
    )


    while True:

        ret, frame = video_capture.read()

        if not ret:

            print("Camera Error")

            break


        # ==========================================
        # SMALL FRAME FOR FAST SPEED
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
        # DETECT FACES
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
        # MATCH FACES
        # ==========================================

        for (top, right, bottom, left), face_encoding in zip(

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

                    name = known_names[best_match_index]


                    # ==========================================
                    # CHECK ATTENDANCE
                    # ==========================================

                    already_marked = attendance_collection.find_one({

                        "student_name": name,

                        "date": datetime.now().strftime(

                            "%Y-%m-%d"

                        )

                    })


                    # ==========================================
                    # MARK ATTENDANCE
                    # ==========================================

                    if not already_marked:

                        attendance_collection.insert_one({

                            "student_name": name,

                            "status": "Present",

                            "date": datetime.now().strftime(

                                "%Y-%m-%d"

                            ),

                            "time": datetime.now().strftime(

                                "%H:%M:%S"

                            ),

                            "method": "Face Recognition"

                        })


                        print(

                            f"{name} attendance marked"

                        )


            # ==========================================
            # RESIZE FACE BOX
            # ==========================================

            top *= 4
            right *= 4
            bottom *= 4
            left *= 4


            # ==========================================
            # FACE RECTANGLE
            # ==========================================

            cv2.rectangle(

                frame,

                (left, top),

                (right, bottom),

                (0, 255, 0),

                3

            )


            # ==========================================
            # NAME LABEL
            # ==========================================

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
        # WINDOW TITLE
        # ==========================================

        cv2.imshow(

            "Smart Campus AI Face Recognition",

            frame

        )


        # ==========================================
        # PRESS Q TO EXIT
        # ==========================================

        if cv2.waitKey(1) & 0xFF == ord("q"):

            break


    # ==========================================
    # RELEASE CAMERA
    # ==========================================

    video_capture.release()

    cv2.destroyAllWindows()