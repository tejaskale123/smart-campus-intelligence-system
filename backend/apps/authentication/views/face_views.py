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
from datetime import datetime
from apps.authentication.face_utils import recognize_faces

CAMERA_LOGS = db["camera_logs"]
SECURITY_LOGS = db["security_logs"]
FACE_COLLECTION = db["face_encodings"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
FACES_DIR = os.path.join(BASE_DIR, "media", "faces")
os.makedirs(FACES_DIR, exist_ok=True)

FACE_SAMPLE_SIZE = (96, 96)
FACE_MATCH_THRESHOLD = 0.62
FACE_DUPLICATE_THRESHOLD = 0.96
FACE_ENCODING_MIN_COUNT = 1


def _log_camera_event(camera_status, face_detected=False, student_name=None, **extra):
    try:
        log_data = {
            "camera_status": camera_status,
            "face_detected": face_detected,
            "created_at": datetime.now(),
        }
        if student_name:
            log_data["student_name"] = student_name
        log_data.update(extra)
        CAMERA_LOGS.insert_one(log_data)
    except Exception as error:
        print("Camera Log Error:", error)


def _log_security_event(request, event, **extra):
    try:
        log_data = {
            "event": event,
            "ip_address": request.META.get("REMOTE_ADDR"),
            "created_at": datetime.now(),
        }
        log_data.update(extra)
        SECURITY_LOGS.insert_one(log_data)
    except Exception as error:
        print("Security Log Error:", error)


def _save_face_documents(face_documents):
    try:
        if face_documents:
            FACE_COLLECTION.insert_many(face_documents)
    except Exception as error:
        print("Face Collection Save Error:", error)


def _decode_base64_image(image_data):
    if not image_data or ";base64," not in image_data:
        raise ValueError("Invalid camera image.")

    _, imgstr = image_data.split(";base64,", 1)
    image_bytes = base64.b64decode(imgstr)
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return np.array(image)


def _get_face_recognition():
    try:
        import face_recognition
        return face_recognition
    except ImportError:
        return None


def _extract_cv2_face_sample(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    gray = cv2.equalizeHist(gray)
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(cascade_path)
    faces = detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80)
    )

    if len(faces) > 0:
        x, y, width, height = max(faces, key=lambda item: item[2] * item[3])
        padding = int(width * 0.18)
        left = max(0, x - padding)
        top = max(0, y - padding)
        right = min(gray.shape[1], x + width + padding)
        bottom = min(gray.shape[0], y + height + padding)
        face = gray[top:bottom, left:right]
    else:
        height, width = gray.shape
        crop_size = min(height, width)
        left = (width - crop_size) // 2
        top = (height - crop_size) // 2
        face = gray[top:top + crop_size, left:left + crop_size]

    return cv2.resize(face, FACE_SAMPLE_SIZE)


def _detect_cv2_face_boxes(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    gray = cv2.equalizeHist(gray)
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(cascade_path)
    faces = detector.detectMultiScale(
        gray,
        scaleFactor=1.08,
        minNeighbors=4,
        minSize=(60, 60)
    )
    return sorted(faces, key=lambda item: item[2] * item[3], reverse=True)


def _cv2_box_to_face_location(frame, box):
    x, y, width, height = box
    padding = int(width * 0.22)
    top = max(0, y - padding)
    right = min(frame.shape[1], x + width + padding)
    bottom = min(frame.shape[0], y + height + padding)
    left = max(0, x - padding)
    return (top, right, bottom, left)


def _extract_face_encoding(face_recognition, frame):
    if not face_recognition:
        return None

    face_locations = face_recognition.face_locations(
        frame,
        number_of_times_to_upsample=2,
        model="hog"
    )
    encodings = face_recognition.face_encodings(frame, face_locations)
    if encodings:
        return encodings[0]

    for box in _detect_cv2_face_boxes(frame):
        face_location = _cv2_box_to_face_location(frame, box)
        encodings = face_recognition.face_encodings(frame, [face_location])
        if encodings:
            return encodings[0]

        top, right, bottom, left = face_location
        face_crop = frame[top:bottom, left:right]
        if face_crop.size == 0:
            continue

        crop_locations = face_recognition.face_locations(
            face_crop,
            number_of_times_to_upsample=2,
            model="hog"
        )
        encodings = face_recognition.face_encodings(face_crop, crop_locations)
        if encodings:
            return encodings[0]

    return None


def _encode_face_sample(sample):
    ok, buffer = cv2.imencode(".jpg", sample, [int(cv2.IMWRITE_JPEG_QUALITY), 82])
    if not ok:
        return ""
    return base64.b64encode(buffer).decode("utf-8")


def _decode_face_sample(sample_data):
    image_bytes = base64.b64decode(sample_data)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    sample = cv2.imdecode(image_array, cv2.IMREAD_GRAYSCALE)
    if sample is None:
        return None
    return cv2.resize(sample, FACE_SAMPLE_SIZE)


def _sample_similarity(first, second):
    first_vector = first.astype("float32").flatten() / 255.0
    second_vector = second.astype("float32").flatten() / 255.0
    denominator = np.linalg.norm(first_vector) * np.linalg.norm(second_vector)
    if denominator == 0:
        return 0

    cosine = float(np.dot(first_vector, second_vector) / denominator)
    mse = float(np.mean((first_vector - second_vector) ** 2))
    return (0.72 * cosine) + (0.28 * (1 - mse))


def _find_best_sample_match(captured_sample, students):
    best_student = None
    best_score = 0

    for student in students:
        for stored_sample in student.get("face_samples", []):
            sample = _decode_face_sample(stored_sample)
            if sample is None:
                continue

            score = _sample_similarity(captured_sample, sample)
            if score > best_score:
                best_score = score
                best_student = student

    return best_student, best_score


def _load_registered_students():
    students = []
    grouped_faces = {}

    for face in FACE_COLLECTION.find():
        student_name = (face.get("student_name") or "").strip()
        if not student_name:
            continue

        key = (
            student_name,
            face.get("roll_number", ""),
            face.get("course", ""),
        )
        grouped_faces.setdefault(key, {
            "student_name": student_name,
            "roll_number": face.get("roll_number", ""),
            "course": face.get("course", ""),
            "face_encodings": [],
            "face_samples": [],
        })

        encoding = face.get("encoding")
        if encoding:
            grouped_faces[key]["face_encodings"].append(np.array(encoding))

        sample = face.get("face_sample")
        if sample:
            grouped_faces[key]["face_samples"].append(sample)

    students.extend(grouped_faces.values())

    for student in db.students.find():
        encodings = [
            np.array(encoding)
            for encoding in student.get("face_encodings", [])
            if encoding
        ]
        face_samples = [
            sample
            for sample in student.get("face_samples", [])
            if sample
        ]
        if encodings or face_samples:
            students.append({
                "student_name": student.get("student_name", "").strip(),
                "roll_number": student.get("roll_number", ""),
                "course": student.get("course", ""),
                "face_encodings": encodings,
                "face_samples": face_samples,
            })
    return students


def _mark_face_attendance(student):
    today_date = datetime.now().strftime("%Y-%m-%d")
    current_clock_time = datetime.now().strftime("%H:%M:%S")
    student_name = student["student_name"]

    base_query = {
        "student_name": student_name,
        "attendance_date": today_date,
    }
    check_in_record = db.attendance_logs.find_one({
        **base_query,
        "type": "IN",
    })
    check_out_record = db.attendance_logs.find_one({
        **base_query,
        "type": "OUT",
    })

    if not check_in_record:
        attendance_type = "IN"
        message = f"{student_name} check-in marked successfully."
    elif not check_out_record:
        attendance_type = "OUT"
        message = f"{student_name} check-out marked successfully."
    else:
        return {
            "status": "already_marked",
            "attendance_type": "COMPLETED",
            "message": f"{student_name} attendance already completed today.",
            "time": current_clock_time,
        }

    db.attendance_logs.insert_one({
        "student_name": student_name,
        "roll_number": student.get("roll_number", ""),
        "student_course": student.get("course", ""),
        "status": "Present",
        "attendance_date": today_date,
        "time": current_clock_time,
        "type": attendance_type,
        "method": "Face Recognition",
    })

    return {
        "status": "marked",
        "attendance_type": attendance_type,
        "message": message,
        "time": current_clock_time,
    }


def start_face_attendance(request):
    try:
        camera_thread = threading.Thread(target=recognize_faces)
        camera_thread.daemon = True
        camera_thread.start()
        _log_camera_event("Started", face_detected=True)
        return JsonResponse({"status": "success", "message": "Camera Started"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})


def process_face_attendance(request):
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "POST request required."
        }, status=405)

    try:
        frame = _decode_base64_image(request.POST.get("image"))
    except ValueError as error:
        return JsonResponse({
            "status": "error",
            "message": str(error)
        }, status=400)

    students = _load_registered_students()
    if not students:
        _log_camera_event("Unknown Face", face_detected=False)
        return JsonResponse({
            "status": "error",
            "message": "No registered face data found."
        })

    best_student = None
    confidence = 0
    face_recognition = _get_face_recognition()

    if face_recognition:
        captured_encoding = _extract_face_encoding(face_recognition, frame)
        if captured_encoding is not None:
            best_distance = 1.0

            for student in students:
                if not student.get("face_encodings"):
                    continue

                distances = face_recognition.face_distance(
                    student["face_encodings"],
                    captured_encoding
                )
                if len(distances) == 0:
                    continue

                min_distance = float(np.min(distances))
                if min_distance < best_distance:
                    best_distance = min_distance
                    best_student = student

            if best_student and best_distance <= 0.5:
                confidence = max(0, min(100, round((1 - best_distance) * 100)))

    if not best_student:
        captured_sample = _extract_cv2_face_sample(frame)
        best_student, best_score = _find_best_sample_match(captured_sample, students)
        confidence = max(0, min(100, round(best_score * 100)))
        if not best_student or best_score < FACE_MATCH_THRESHOLD:
            best_student = None

    if not best_student:
        _log_camera_event(
            "Unknown Face",
            face_detected=False,
            confidence=confidence
        )
        _log_security_event(
            request,
            "Face Mismatch",
            confidence=confidence
        )
        return JsonResponse({
            "status": "unknown",
            "message": "Face not matched with registered students.",
            "confidence": confidence
        })

    attendance_result = _mark_face_attendance(best_student)
    _log_camera_event(
        "Face Detected",
        face_detected=True,
        student_name=best_student["student_name"],
        roll_number=best_student.get("roll_number", ""),
        course=best_student.get("course", ""),
        confidence=confidence,
        attendance_status=attendance_result.get("status"),
        attendance_type=attendance_result.get("attendance_type"),
    )

    return JsonResponse({
        **attendance_result,
        "student_name": best_student["student_name"],
        "roll_number": best_student.get("roll_number", ""),
        "course": best_student.get("course", ""),
        "confidence": confidence,
    })


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

        face_recognition = _get_face_recognition()
        encodings_list = []
        face_samples = []
        existing_students = list(db.students.find())
        duplicate_found = False

        for image_data in images:
            try:
                image_np = _decode_base64_image(image_data)
                sample = _extract_cv2_face_sample(image_np)
                face_samples.append(_encode_face_sample(sample))

                if not face_recognition:
                    continue

                encoding = _extract_face_encoding(face_recognition, image_np)
                if encoding is None:
                    continue

                for student in existing_students:
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

        if not face_samples:
            return JsonResponse({
                "status": "error",
                "message": "No clear face found. Capture again with better light."
            })

        if len(encodings_list) < FACE_ENCODING_MIN_COUNT:
            if not face_recognition:
                return JsonResponse({
                    "status": "error",
                    "message": "face_recognition package is not available. Install it before registering faces."
                })

            return JsonResponse({
                "status": "error",
                "message": "Face encoding failed. Keep face clear inside the box and capture again."
            })

        db.students.insert_one({
            "name": student_name,
            "student_name": student_name,
            "roll_number": roll_number,
            "course": course,
            "face_encodings": encodings_list,
            "face_samples": face_samples
        })

        face_documents = []
        for index, encoding in enumerate(encodings_list):
            face_documents.append({
                "student_name": student_name,
                "roll_number": roll_number,
                "course": course,
                "encoding": encoding,
                "face_sample": face_samples[index] if index < len(face_samples) else "",
                "created_at": datetime.now(),
            })

        _save_face_documents(face_documents)

        return JsonResponse({
            "status": "success",
            "message": f"{student_name} Registered Successfully",
            "engine": "face_recognition" if face_recognition else "opencv"
        })

    return render(request, "authentication/register_face.html")


def face_attendance_page(request):
    return render(request, "authentication/face_attendance.html")
