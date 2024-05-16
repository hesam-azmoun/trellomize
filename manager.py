import argparse
import json
import os



def create_admin(username, password):

    with open('admin_info.json','r') as file:
        data = json.load(file)
        if not data:
            with open('admin_info.json', 'w') as f:
                json.dump({'username': username, 'password': password}, f, indent=4)
        else:
            print('error: System Manager Is Already Exists')





def main():
    parser = argparse.ArgumentParser(description='system administrator information')
    parser.add_argument('create-admin', help='create manager')
    parser.add_argument('--username', help='new userName', required=True)
    parser.add_argument('--password', help='new password', required=True)

    args = parser.parse_args()

    if 'create-admin' in args:
        create_admin(args.username, args.password)


if __name__ == '__main__':
    main()