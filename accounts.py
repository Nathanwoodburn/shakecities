import os
import dotenv
from passlib.hash import argon2
import json
import db

dotenv.load_dotenv()
local = os.getenv('LOCAL')

def hash_password(password):
    return argon2.using(rounds=16).hash(password)

def convert_db_users(db_entry):
    return {
        'id': db_entry[0],
        'email': db_entry[1],
        'domain': db_entry[2],
        'password': db_entry[3],
        'tokens': db_entry[4].split(',')
    }

# Verify a password against a hashed password
def verify_password(password, hashed_password):
    return argon2.verify(password, hashed_password)

def generate_cookie():
    token = os.urandom(24).hex()
    # Verify token doesn't already exist
    while db.search_users_token(token) != []:
        token = os.urandom(24).hex()
        
    return token

# Create a new user
def create_user(email, domain, password):
    if len(email) < 4 or len(domain) < 4 or len(password) < 4:
        return {'success': False, 'message': 'Invalid email, domain, or password'}


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

    # Check if user exists
    if db.search_users(email) != []:
        return {'success': False, 'message': 'User already exists'}
    
    if db.search_users_domain(domain) != []:
        return {'success': False, 'message': 'Domain already exists'}

    db.add_user(email, domain, hashed_password, token)
    return {'success': True, 'message': 'User created', 'token': token}

def validate_token(token):
    search = db.search_users_token(token)
    if search == []:
        return False
    else:
        return convert_db_users(search[0])
    
def logout(token):
    # Remove token from user
    user = validate_token(token)
    if not user:
        return {'success': False, 'message': 'Invalid token'}
    user['tokens'].remove(token)
    # Update user
    db.update_tokens(user['id'], user['tokens'])


    return {'success': True, 'message': 'Logged out'}

def login(email,password):
    # Verify email
    search = db.search_users(email)
    if search == []:
        return {'success': False, 'message': 'Invalid email'}
    user = convert_db_users(search[0])
    # Verify password
    if not verify_password(password, user['password']):
        return {'success': False, 'message': 'Invalid password'}
    
    # Create a cookie
    token = generate_cookie()
    user['tokens'].append(token)
    # Get the newest 2 tokens
    user['tokens'] = user['tokens'][-2:]

    # Update user
    db.update_tokens(user['id'], user['tokens'])
    return {'success': True, 'message': 'Logged in', 'token': token}