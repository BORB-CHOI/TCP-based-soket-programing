from pymongo import MongoClient, errors
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URI = f"mongodb+srv://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_CLUSTER')}?retryWrites=true&w=majority&appName=CS"

class DBManager:
    """MongoDB 관련 DB 관리 기능"""

    def __init__(self):
        # MongoDB 클라이언트 및 users 컬렉션 초기화
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client.test
        self.users = self.db.users

    def get_users_count(self):
        # 전체 사용자 수 반환
        return self.users.count_documents({})

    def get_user_by_id(self, user_id):
        # ID로 사용자 조회
        user = self.users.find_one({"_id": user_id})
        return user

    def create_user(self, user_id, name, email):
        # 새 사용자 생성 (중복 ID 예외 처리)
        try:
            result = self.users.insert_one(
                {"_id": user_id, "name": name, "email": email}
            )
            return str(result.inserted_id)
        except errors.DuplicateKeyError:
            return None

    def update_user(self, user_id, update_data):
        # 사용자 정보 수정
        result = self.users.update_one({"_id": user_id}, {"$set": update_data})
        return result.modified_count > 0

    def delete_user(self, user_id):
        # 사용자 삭제
        result = self.users.delete_one({"_id": user_id})
        return result.deleted_count > 0
