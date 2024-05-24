import argparse
import json
import os
from utils import hash_password
from main import create_user
from logger import log1

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
    create_user(username, password, "admin@gmail.com")
    print("Admin created successfully.")


def purge_data():
    try:
        os.remove("data/admin.json")
        print(f"Amin data deleted.")
        log1.info("purge admin data")

    except FileNotFoundError:
        print("Admin data not exist.")
    except Exception as e:
        print(e)

    try:
        os.remove("data/projects.json")
        print(f"projects data deleted.")
        log1.info("purge project data")

    except FileNotFoundError:
        print("project data not exist.")
    except Exception as e:
        print(e)
    try:
        os.remove("data/users.json")
        print(f"Users data deleted.")
        log1.info("purge users data")

    except FileNotFoundError:
        print("User data not exist.")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage the project management system.")
    # parser.add_argument('command', choices=['create-admin', 'purge-data'], help="Command to run.")
    parser.add_argument("--create-admin", action='store_true', help="Create an admin.")
    parser.add_argument("--purge-data", action='store_true', help="Purge all data.")
    parser.add_argument('--username', type=str, help="Admin username.")
    parser.add_argument('--password', type=str, help="Admin password.")

    args = parser.parse_args()
    if args.create_admin:
        create_admin(args.username, args.password)
    elif args.purge_data:
        choice = input("Are sure your decided?\n1. Yes\n2. No\n")
        if choice == '1':
            print("Removing all data...")
            purge_data()  # Not completed
        elif choice == "2":
            pass

# python manager.py --create-admin --username admin --password admin123456789
# python ./manager.py --purge-data
