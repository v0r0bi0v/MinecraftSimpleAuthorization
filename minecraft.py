import subprocess
import time
import threading

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
        self.whitelist = set()  # Для хранения вайтлиста
        threading.Thread(target=self.monitor_server_output, daemon=True).start()  # Запускаем поток для мониторинга логов

    def monitor_server_output(self):
        """Поток для мониторинга вывода сервера и отслеживания логинов игроков."""
        while True:
            output = self.server_process.stdout.readline()
            if not output:
                break
            self.process_server_output(output.strip())

    def process_server_output(self, output):
        """Обрабатывает вывод сервера для отслеживания событий входа игроков."""
        print(output)  # Печатаем вывод для отладки

        # Проверка на вход игрока
        if "joined the game" in output:
            # Извлекаем никнейм игрока
            nickname = output.split(" ")[0]
            if nickname not in self.whitelist:
                self.kick_player(nickname)  # Кикаем игрока, если его нет в вайтлисте

    def add_to_whitelist(self, nickname):
        """Добавляет игрока в собственный вайтлист и запускает таймер на удаление."""
        self.whitelist.add(nickname)
        print(f"{nickname} добавлен в вайтлист.")

        # Запускаем таймер для удаления игрока через 2 минуты
        threading.Timer(120, self.remove_from_whitelist, [nickname]).start()

    def kick_player(self, nickname):
        """Кикает игрока с сервера."""
        self.send_command(f"kick {nickname} You are not whitelisted.")  # Отправляем команду кика игрока

    def remove_from_whitelist(self, nickname):
        """Удаляет игрока из вайтлиста."""
        self.whitelist.discard(nickname)
        print(f"{nickname} удален из вайтлиста.")

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
