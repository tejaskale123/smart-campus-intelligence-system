from database.mongo import db


# ==============================
# ADD STUDENT SERVICE
# ==============================

def create_student(data):

    return db["students"].insert_one(data)


# ==============================
# GET ALL STUDENTS
# ==============================

def get_all_students():

    return db["students"].find()


# ==============================
# GET SINGLE STUDENT
# ==============================

def get_student(student_id):

    from bson import ObjectId

    return db["students"].find_one({

        "_id": ObjectId(student_id)

    })