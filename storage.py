import json
import os

DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
PROJECTS_FILE = os.path.join(DATA_DIR, 'projects.json')
ADMIN_FILE = os.path.join(DATA_DIR, 'admin.json')


def load_data(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r') as file:
        return json.load(file)


def save_data(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file)


def load_users():
    return load_data(USERS_FILE)


def save_users(users):
    save_data(USERS_FILE, users)


def load_projects():
    return load_data(PROJECTS_FILE)


def save_projects(projects):
    save_data(PROJECTS_FILE, projects)


def load_admin():
    return load_data(ADMIN_FILE)
