import argparse
import json
import os
from utils import hash_password

DATA_DIR = 'data'
ADMIN_FILE = os.path.join(DATA_DIR, 'admin.json')

def create_admin(username, password):
    if os.path.exists(ADMIN_FILE):
        print("Admin already exists.")
        return
    admin = {
        'username': username,
        'password': hash_password(password)
    }
    with open(ADMIN_FILE, 'w') as f:
        json.dump(admin, f)
    print("Admin created successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage the project management system.")
    parser.add_argument('command', choices=['create-admin'], help="Command to run.")
    parser.add_argument('--username', required=True, help="Admin username.")
    parser.add_argument('--password', required=True, help="Admin password.")

    args = parser.parse_args()
    if args.command == 'create-admin':
        create_admin(args.username, args.password)
