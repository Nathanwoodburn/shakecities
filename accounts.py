import os
import dotenv
from passlib.hash import argon2
import json

dotenv.load_dotenv()
local = os.getenv('LOCAL')

def hash_password(password):
    return argon2.using(rounds=16).hash(password)

# Verify a password against a hashed password
def verify_password(password, hashed_password):
    return argon2.verify(password, hashed_password)

def generate_cookie():
    token = os.urandom(24).hex()
    # Verify token doesn't already exist
    with open('users.json', 'r') as f:
        users = json.load(f)
    for user in users:
        if token in user['tokens']:
            print('Token already exists, generating new one')
            return generate_cookie()
        
    return token

# Create a new user
def create_user(email, domain, password):
    # Hash password
    hashed_password = hash_password(password)
    # Create user
    user = {
        'email': email,
        'domain': domain,
        'password': hashed_password
    }

    # Create a cookie
    token = generate_cookie()
    user['tokens'] = [token]

    # If file doesn't exist, create it
    if not os.path.isfile('users.json'):
        with open('users.json', 'w') as f:
            json.dump([], f)



    # Write to file
    with open('users.json', 'r') as f:
        users = json.load(f)

    for u in users:
        if u['email'] == email:
            return {'success': False, 'message': 'Email already exists'}

    users.append(user)
    with open('users.json', 'w') as f:
        json.dump(users, f)
    return {'success': True, 'message': 'User created', 'token': token}

def validate_token(token):
    with open('users.json', 'r') as f:
        users = json.load(f)
    for user in users:
        if token in user['tokens']:
            return user
    return False