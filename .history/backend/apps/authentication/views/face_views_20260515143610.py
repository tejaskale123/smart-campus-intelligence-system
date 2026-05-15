import os
import io
import cv2
import base64
import threading
import numpy as np
from PIL import Image
from django.http import JsonResponse
from django.shortcuts import render
from database.mongo import db
from .face_utils import recognize_faces

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
FACES_DIR = os.path.join(BASE_DIR, "media", "faces")
os.makedirs(FACES_DIR, exist_ok=True)


def start_face_attendance(request):
    try:
        camera_thread = threading.Thread(target=recognize_faces)
        camera_thread.daemon = True
        camera_thread.start()
        return JsonResponse({"status": "success", "message": "Camera Started"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})


def register_face(request):
    if request.method == "POST":
        student_name = request.POST.get("student_name")
        roll_number = request.POST.get("roll_number")
        course = request.POST.get("course")
        images = request.POST.getlist("images[]")

        if not student_name:
            return JsonResponse({"status": "error", "message": "Student Name Required"})

        if len(images) < 5:
            return JsonResponse({"status": "error", "message": "Capture 5 Images"})

        encodings_list = []
        all_students = db.students.find()
        duplicate_found = False

        for image_data in images:
            try:
                format, imgstr = image_data.split(";base64,")
                image_bytes = base64.b64decode(imgstr)
                image = Image.open(io.BytesIO(image_bytes))
                image_np = np.array(image)
                face_encodings = face_recognition.face_encodings(image_np)

                if len(face_encodings) > 0:
                    encoding = face_encodings[0]

                    for student in all_students:
                        stored_encodings = student.get("face_encodings", [])
                        for stored_encoding in stored_encodings:
                            matches = face_recognition.compare_faces(
                                [np.array(stored_encoding)],
                                encoding,
                                tolerance=0.45
                            )
                            if True in matches:
                                duplicate_found = True
                                break
                        if duplicate_found:
                            break

                    if duplicate_found:
                        return JsonResponse({"status": "error", "message": "Face Already Registered"})

                    encodings_list.append(encoding.tolist())
            except Exception as e:
                print("Encoding Error:", e)

        db.students.insert_one({
            "student_name": student_name,
            "roll_number": roll_number,
            "course": course,
            "face_encodings": encodings_list
        })

        return JsonResponse({
            "status": "success",
            "message": f"{student_name} Registered Successfully"
        })

    return render(request, "authentication/register_face.html")


def face_attendance_page(request):
    return render(request, "authentication/face_attendance.html")
