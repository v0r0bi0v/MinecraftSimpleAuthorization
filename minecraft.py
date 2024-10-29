import json
import subprocess
import time
import os
import threading
from config import TIME_LOGIN_AVAILABILITY

class MinecraftServer:
    def __init__(self, server_path="../server.jar"):
        # Запускаем сервер
        self.server_process = subprocess.Popen(
            ["java", "-jar", server_path, "nogui"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("Minecraft server started.")
        self.active_players = set()  # Для хранения активных игроков
        threading.Thread(target=self.monitor_server_output, daemon=True).start()

    def monitor_server_output(self):
        """Поток для мониторинга вывода сервера и отслеживания отключений игроков."""
        while True:
            output = self.server_process.stdout.readline()
            if not output:
                break
            self.process_server_output(output.strip())

    def process_server_output(self, output):
        """Обрабатывает вывод сервера для отслеживания событий."""
        print(output)  # Печатаем вывод для отладки

        # Проверка на отключение игрока
        if "left the game" in output:
            # Извлекаем никнейм игрока
            nickname = output.split(" ")[0]
            self.remove_from_whitelist(nickname)

    def add_to_whitelist(self, nickname, duration=TIME_LOGIN_AVAILABILITY):
        """Добавляет игрока в whitelist на определенное время и затем проверяет, можно ли удалить его."""
        whitelist_path = "whitelist.json"
        
        # Создаем whitelist.json, если он отсутствует
        if not os.path.exists(whitelist_path):
            with open(whitelist_path, "w") as f:
                json.dump([], f)

        with open(whitelist_path, "r") as f:
            whitelist = json.load(f)

        # Проверяем, есть ли уже игрок в whitelist
        if any(entry["name"] == nickname for entry in whitelist):
            print(f"{nickname} уже в whitelist.")
            return

        # Добавляем нового игрока
        whitelist.append({"uuid": "отсутствует", "name": nickname})

        # Записываем обратно в whitelist.json
        with open(whitelist_path, "w") as f:
            json.dump(whitelist, f, indent=4)

        print(f"{nickname} добавлен в whitelist на {duration} секунд.")

        # Перезагружаем whitelist
        self.send_command("whitelist reload")

        # Запускаем таймер для проверки и удаления пользователя через указанное время
        threading.Timer(duration, self.check_player_login, [nickname]).start()

    def check_player_login(self, nickname):
        """Проверяет, находится ли игрок на сервере, и удаляет его из whitelist, если он вышел."""
        if nickname in self.active_players:
            print(f"{nickname} всё еще на сервере. Не удаляем из whitelist.")
        else:
            self.remove_from_whitelist(nickname)

    def get_active_players(self):
        """Получает список активных игроков на сервере."""
        self.send_command("list")  # Отправляем команду для получения списка игроков
        time.sleep(1)  # Небольшая задержка для обработки команды

        # Читаем вывод сервера, чтобы найти список игроков
        output = self.server_process.stdout.readline()
        while output:
            if " players online" in output:
                # Извлекаем список игроков
                player_list = output.split(": ")[1].strip().split(", ")
                self.active_players = set(player_list)  # Обновляем список активных игроков
                print("Активные игроки:", self.active_players)
                return player_list
            output = self.server_process.stdout.readline()

        return []

    def remove_from_whitelist(self, nickname):
        """Удаляет игрока из whitelist и обновляет список."""
        whitelist_path = "whitelist.json"
        
        # Загружаем текущий whitelist
        with open(whitelist_path, "r") as f:
            whitelist = json.load(f)

        # Удаляем игрока по имени
        new_whitelist = [entry for entry in whitelist if entry["name"] != nickname]

        # Обновляем файл whitelist.json
        with open(whitelist_path, "w") as f:
            json.dump(new_whitelist, f, indent=4)

        print(f"{nickname} удален из whitelist.")

        # Перезагружаем whitelist
        self.send_command("whitelist reload")

    def send_command(self, command):
        """Отправляет команду в консоль сервера."""
        self.server_process.stdin.write(command + "\n")
        self.server_process.stdin.flush()
        print(f"Команда '{command}' отправлена серверу.")

    def stop_server(self):
        """Останавливает сервер корректно."""
        self.send_command("stop")
        self.server_process.wait()
        print("Minecraft server stopped.")