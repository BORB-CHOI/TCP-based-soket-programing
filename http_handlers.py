from db_manager import DBManager
import json

db = DBManager()


# HEAD 요청 처리
def handle_head_info():
    # 100 Continue 응답
    return 100, ""


# GET 요청 처리
def handle_get_users():
    # 전체 사용자 수 반환
    count = db.get_users_count()
    return 200, f"Users found: {count}"


def handle_get_users_1():
    """ID가 1인 사용자 조회"""
    user = db.get_user_by_id("1")
    if user:
        # MongoDB _id를 문자열로 변환해 JSON 직렬화
        user_data = {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
        }
        return 200, json.dumps(user_data)
    return 404, "User not found"


def handle_get_notfound():
    # 없는 리소스 요청 시 404 반환
    return 404, "Resource not found"


def handle_get_error():
    # 내부 서버 에러 응답
    return 500, "Internal server error occurred"


# POST 요청 처리
def handle_post_users(body):
    # 필수 필드 검증
    if not body or "name" not in body or "email" not in body:
        return 400, "Invalid user data"
    # ID 1로 사용자 생성
    user_id = db.create_user("1", body["name"], body["email"])
    if user_id is None:
        return 409, "User with id 1 already exists"
    return 201, f"User created: {user_id}"


def handle_post_invalid():
    # 잘못된 POST 요청
    return 400, "Invalid request data"


# PUT 요청 처리
def handle_put_users_1(body):
    # ID 1 사용자 정보 수정
    result = db.update_user("1", body or {})
    if result.modified_count > 0:
        return 200, "User updated"
    elif result.matched_count > 0:
        return 200, "No changes made"
    return 404, "User not found"


def handle_put_users_999():
    # 없는 사용자 수정 요청
    return 404, "User not found"


# DELETE 요청 처리
def handle_delete_users_1():
    # ID 1 사용자 삭제
    if db.delete_user("1"):
        return 200, "User deleted"
    return 404, "User not found"


def handle_delete_users_999():
    # 없는 사용자 삭제 요청
    return 404, "User not found"


# 지원하지 않는 메서드 처리
def handle_method_not_allowed():
    return 405, "Method not allowed"
