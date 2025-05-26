import requests
import os


def send_files_to_server():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(current_dir, '../appTelega/telegram_logs')

    if not os.path.exists(logs_dir):
        print(f"Ошибка: директория {logs_dir} не найдена")
        return

    for folder in os.listdir(logs_dir):
        folder_path = os.path.join(logs_dir, folder)
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(folder_path, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        response = requests.post("http://localhost:8000/", json={'content': content})
                        print(response.text)
                    except Exception as e:
                        print(f"Ошибка: {str(e)}")


print("Начинаю отправку файлов...")
send_files_to_server()
print("\nВыполнение завершено")