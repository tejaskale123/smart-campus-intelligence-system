import face_recognition
import cv2
import os


# ====================================
# SAVE STUDENT FACE
# ====================================

def save_student_face(image_path, student_name):

    image = face_recognition.load_image_file(
        image_path
    )

    encodings = face_recognition.face_encodings(
        image
    )

    if len(encodings) == 0:

        return False

    save_path = f"media/faces/{student_name}.jpg"

    cv2.imwrite(
        save_path,
        cv2.imread(image_path)
    )

    return True


# ====================================
# FACE RECOGNITION
# ====================================

def recognize_faces():

    known_faces = []

    known_names = []

    faces_dir = "media/faces"

    # LOAD ALL FACES

    for file in os.listdir(faces_dir):

        image_path = os.path.join(
            faces_dir,
            file
        )

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
                file.split(".")[0]
            )

    # CAMERA START

    video = cv2.VideoCapture(0)

    while True:

        ret, frame = video.read()

        if not ret:
            break

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        locations = face_recognition.face_locations(
            rgb
        )

        encodings = face_recognition.face_encodings(
            rgb,
            locations
        )

        for face_encoding, face_location in zip(
            encodings,
            locations
        ):

            matches = face_recognition.compare_faces(
                known_faces,
                face_encoding
            )

            name = "Unknown"

            if True in matches:

                match_index = matches.index(True)

                name = known_names[match_index]

            top, right, bottom, left = face_location

            # FACE BOX

            cv2.rectangle(
                frame,
                (left, top),
                (right, bottom),
                (0, 255, 0),
                2
            )

            # NAME TEXT

            cv2.putText(
                frame,
                name,
                (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

        cv2.imshow(
            "Smart Campus Face Recognition",
            frame
        )

        # ENTER PRESS = EXIT

        if cv2.waitKey(1) == 13:
            break

    video.release()

    cv2.destroyAllWindows()