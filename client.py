from socket import *
from dotenv import load_dotenv
import json, os

load_dotenv()

# 소켓 생성
sock = socket(AF_INET, SOCK_STREAM)
sock.connect((os.environ.get("HOST"), int(os.environ.get("PORT"))))

# 서버로 HTTP 요청을 보내는 함수
def send_http_request(method, path, body=None):
    # 요청 라인 및 헤더 작성
    request = f"{method} {path} HTTP/1.1\r\n"
    request += f"Host: {os.environ.get('HOST')}:{os.environ.get('PORT')}\r\n"

    # 바디가 있으면 JSON 변환 후 추가
    if body:
        body_str = json.dumps(body)
        request += "Content-Type: application/json\r\n"
        request += f"Content-Length: {len(body_str)}\r\n"
        request += "\r\n"
        request += body_str
    else:
        request += "Content-Length: 0"

    # 요청 송신
    sock.sendall(request.encode())

    # 서버 응답 수신 및 출력
    response = sock.recv(4096).decode()
    print("[Client 송신]")
    print(request)
    print("-" * 50)
    print("[Server 응답]")
    print(response)
    print("-" * 50)

    return response


# 다양한 HTTP 메서드/경로 테스트 케이스
test_cases = [
    ("HEAD", "/info", None),  # 100 Continue
    ("GET", "/users", None),  # 200 OK
    ("GET", "/notfound", None),  # 404 Not Found
    ("GET", "/error", None),  # 500 Internal Server Error
    ("POST", "/users", {"name": "Test User", "email": "test@test.com"}),  # 201 Created
    ("POST", "/invalid", {"invalid": "data"}),  # 400 Bad Request
    ("PUT", "/users/1", {"email": "edit@test.com"}),  # 200 OK
    ("PUT", "/users/999", {"email": "new@test.com"}),  # 404 Not Found
    ("GET", "/users/1", None),  # 200 OK
    ("DELETE", "/users/1", None),  # 200 OK
    ("DELETE", "/users/999", None),  # 404 Not Found
]

# 각 테스트 케이스 실행 및 상태 라인 출력
for i, (method, path, body) in enumerate(test_cases, 1):
    print("=" * 70)
    response = send_http_request(method, path, body)
    status_line = response.split("\r\n")[0]
    print(f"[{i:2d}] {method:6} {path:12} → {status_line}")
    print("=" * 70)

# 소켓 종료
sock.close()
