import hashlib
import re

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    # regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    # if re.search(regex, email):
    #     return True
    # return False
    return True
