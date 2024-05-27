import json
import os


class Storage:
    DATA_DIR = 'data'
    USERS_FILE = os.path.join(DATA_DIR, 'users.json')
    PROJECTS_FILE = os.path.join(DATA_DIR, 'projects.json')
    ADMIN_FILE = os.path.join(DATA_DIR, 'admin.json')

    @staticmethod
    def load_data(file_path: str) -> dict:
        """It reads the JSON file and returns it as a dictionary."""
        if not os.path.exists(file_path):
            return {}
        with open(file_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def save_data(file_path: str, data: dict) -> None:
        """It writes the JSON file and returns it as a dictionary."""
        with open(file_path, 'w') as file:
            json.dump(data, file, default=str)

    @staticmethod
    def load_users() -> dict:
        """It reads the JSON file and returns it as a dictionary."""
        return Storage.load_data(Storage.USERS_FILE)

    @staticmethod
    def save_users(users):
        """It writes the JSON file and returns it as a dictionary."""
        Storage.save_data(Storage.USERS_FILE, users)

    @staticmethod
    def load_projects():
        """It reads the JSON file and returns it as a dictionary."""
        return Storage.load_data(Storage.PROJECTS_FILE)

    @staticmethod
    def save_projects(projects):
        """It writes the JSON file and returns it as a dictionary."""
        Storage.save_data(Storage.PROJECTS_FILE, projects)

    @staticmethod
    def load_admin():
        """It reads the JSON file and returns it as a dictionary."""
        return Storage.load_data(Storage.ADMIN_FILE)
