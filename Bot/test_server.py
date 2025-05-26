from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class TestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body)
            print(f"\nПолучен POST запрос к {self.path}")
            print(f"Данные: {data}")

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success'}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        # Сначала кодируем строку в UTF-8, затем в байты
        message = "Тестовый сервер работает!"
        self.wfile.write(message.encode('utf-8'))


def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, TestHandler)
    print('Тестовый сервер запущен на http://localhost:8000')
    print('Нажмите Ctrl+C для завершения')
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()