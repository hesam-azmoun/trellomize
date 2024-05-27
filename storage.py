import json
import os

class Storage:
    DATA_DIR = 'data'
    USERS_FILE = os.path.join(DATA_DIR, 'users.json')
    PROJECTS_FILE = os.path.join(DATA_DIR, 'projects.json')
    ADMIN_FILE = os.path.join(DATA_DIR, 'admin.json')

    @staticmethod
    def load_data(file_path):
        if not os.path.exists(file_path):
            return {}
        with open(file_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def save_data(file_path, data):
        with open(file_path, 'w') as file:
            json.dump(data, file, default=str)

    @staticmethod
    def load_users():
        return Storage.load_data(Storage.USERS_FILE)

    @staticmethod
    def save_users(users):
        Storage.save_data(Storage.USERS_FILE, users)

    @staticmethod
    def load_projects():
        return Storage.load_data(Storage.PROJECTS_FILE)

    @staticmethod
    def save_projects(projects):
        Storage.save_data(Storage.PROJECTS_FILE, projects)

    @staticmethod
    def load_admin():
        return load_data(ADMIN_FILE)
