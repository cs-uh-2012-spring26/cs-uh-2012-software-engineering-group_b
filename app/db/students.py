from app.db.utils import serialize_item, serialize_items
from app.db import DB

# Student Collection Name
STUDENT_COLLECTION = "students"

# Student fields
NAME = "name"
EMAIL = "email"
SENIORITY = "seniority"


class StudentResource:

    def __init__(self):
        self.collection = DB.get_collection(STUDENT_COLLECTION)

    def get_students(self, name: str | None = None, seniority: str | None = None):
        query = {}
        if name is not None:
            query[NAME] = {"$regex": name}
        if seniority is not None:
            query[SENIORITY] = seniority

        students = self.collection.find(query)
        return serialize_items(list(students))

    def create_student(self, name: str, email: str, seniority: str):
        student = {NAME: name, EMAIL: email, SENIORITY: seniority}
        result = self.collection.insert_one(student)
        return result.inserted_id

    def update_student(self, lookupemail: str, name: str, email: str, seniority: str):
        student_record = self.get_student_by_email(lookupemail)

        if student_record is None:
            return None

        new_data = {NAME: name, EMAIL: email, SENIORITY: seniority}
        result = self.collection.update_one({EMAIL: lookupemail}, {"$set": new_data})

        return result

    def get_student_by_email(self, email: str):
        student = self.collection.find_one({EMAIL: email})
        return serialize_item(student)

    def delete_all_students(self):
        self.collection.delete_many({})

    def add_multiple_students(self, students: list[dict]):
        if not students:
            return

        self.collection.insert_many(students)
