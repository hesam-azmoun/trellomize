import hashlib
import re


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def validate_email(email):
    # regex = r'^[a-zA-Z0-9]+[\._]?[a-zA-Z0-9]+[@]\w+[.]\w+$'
    # if re.search(regex, email):
    #     return True
    # return False
    return True


def validate_username(username):
    # regex = r'^[A-Z]+[a-z]+[0-9._]+$'
    # if re.search(regex, username):
    #     return True
    # return False
    return True

