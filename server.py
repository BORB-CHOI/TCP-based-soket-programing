from socket import *
from http_handlers import *
import json, os
from dotenv import load_dotenv
from email.utils import formatdate

load_dotenv()

# HTTP 응답 함수
def http_response(status_code, body="", content_type="text/plain"):
    status_texts = {
        100: "Continue",
        200: "OK",
        201: "Created",
        400: "Bad Request",
        404: "Not Found",
        405: "Method Not Allowed",
        409: "Conflict",
        500: "Internal Server Error",
    }
    status_text = status_texts.get(status_code, "Unknown")

    # 상태 라인 및 헤더 작성
    response = f"HTTP/1.1 {status_code} {status_text}\r\n"
    response += f"Date: {formatdate(timeval=None, localtime=True, usegmt=True)}\r\n"
    response += f"Content-Type: {content_type}; charset=UTF-8\r\n"
    response += f"Content-Length: {len(body)}"

    # 바디가 있으면 추가
    if body:
        response += f"\r\n\r\n{body}"

    return response.encode()


# (메서드, 경로)별 핸들러 매핑
ROUTES = {
    ("HEAD", "/info"): lambda _: handle_head_info(),
    ("GET", "/users"): lambda _: handle_get_users(),
    ("GET", "/error"): lambda _: handle_get_error(),
    ("POST", "/users"): lambda body: handle_post_users(body),
    ("POST", "/invalid"): lambda _: handle_post_invalid(),
    ("PUT", "/users/1"): lambda body: handle_put_users_1(body),
    ("PUT", "/users/999"): lambda _: handle_put_users_999(),
    ("GET", "/users/1"): lambda _: handle_get_users_1(),
    ("DELETE", "/users/1"): lambda _: handle_delete_users_1(),
    ("DELETE", "/users/999"): lambda _: handle_delete_users_999(),
}


# HTTP 요청 처리 함수
def handle_request(request):
    # 요청 라인 파싱
    lines = request.split("\r\n")
    method, path = lines[0].split()[:2]
    body = None

    # POST/PUT이면 바디 JSON 파싱 시도
    if method in ["POST", "PUT"] and len(lines) > 1:
        try:
            body = json.loads(lines[-1])
        except:
            pass

    # 유효한 경로인지 확인
    available_paths = set(route[1] for route in ROUTES.keys())
    if path not in available_paths:
        return http_response(404, "Not Found")

    # 핸들러 호출
    handler = ROUTES.get((method, path))
    if handler:
        status, body_content = handler(body)
        content_type = (
            "application/json" if body and method in ["POST", "PUT"] else "text/plain"
        )
        return http_response(status, body_content, content_type)
    else:
        # 허용되지 않은 메서드
        return http_response(405, "Method Not Allowed")


# 서버 소켓 생성 및 바인딩
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind((os.environ.get('HOST'), int(os.environ.get('PORT'))))
server_socket.listen(1)
print(f"서버 시작: {os.environ.get('HOST')}:{os.environ.get('PORT')}")

# 클라이언트 연결 대기 및 처리 루프
while True:
    conn, addr = server_socket.accept()
    while True:
        request = conn.recv(4096).decode()
        if not request:
            break  # 클라이언트가 연결을 끊으면 루프 탈출
        response = handle_request(request)
        conn.sendall(response)
    conn.close()
