import os
import hashlib

def genKey(password, salt):
    
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000)
    
    return str(key)

def checkKey(password, key_from_db, salt_from_db):
    if genKey(password, salt_from_db) == key_from_db:
        return True
    else:
        return False

def main():
    pass


if __name__ == "__main__":
    main()