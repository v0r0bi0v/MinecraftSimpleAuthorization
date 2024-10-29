import subprocess
import threading

class MinecraftServer:
    def __init__(self, server_path="../server.jar"):
        # Start the server
        self.server_process = subprocess.Popen(
            ["java", "-jar", server_path, "nogui"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("Minecraft server started.")
        self.whitelist = set()  # For storing the whitelist
        threading.Thread(target=self._monitor_server_output, daemon=True).start()  # Start a thread to monitor logs

    def add_to_whitelist(self, nickname):
        """Adds a player to the custom whitelist and starts a timer for removal."""
        self.whitelist.add(nickname)
        print(f"{nickname} added to the whitelist.")

        # Start a timer to remove the player after 2 minutes
        threading.Timer(120, self._remove_from_whitelist, [nickname]).start()

    def _monitor_server_output(self):
        """Thread to monitor the server output and track player logins."""
        while True:
            output = self.server_process.stdout.readline()
            if not output:
                break
            self._process_server_output(output.strip())

    def _process_server_output(self, output):
        """Processes the server output to track player login events."""
        print(output)  # Print output for debugging

        # Check for player login
        if "joined the game" in output:
            # Extract the player's nickname
            nickname = output.split(" ")[0]
            if nickname not in self.whitelist:
                self._kick_player(nickname)  # Kick the player if they're not in the whitelist

    def _kick_player(self, nickname):
        """Kicks a player from the server."""
        self._send_command(f"kick {nickname} You are not whitelisted.")  # Send a kick command to the player

    def _remove_from_whitelist(self, nickname):
        """Removes a player from the whitelist."""
        self.whitelist.discard(nickname)
        print(f"{nickname} removed from the whitelist.")

    def _send_command(self, command):
        """Sends a command to the server console."""
        self.server_process.stdin.write(command + "\n")
        self.server_process.stdin.flush()
        print(f"Command '{command}' sent to the server.")

    def _stop_server(self):
        """Stops the server gracefully."""
        self._send_command("stop")
        self.server_process.wait()
        print("Minecraft server stopped.")
