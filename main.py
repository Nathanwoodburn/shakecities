from flask import Flask, make_response, redirect, request, jsonify, render_template, send_from_directory
import os
import dotenv
import requests
import json
import schedule
import time
from email_validator import validate_email, EmailNotValidError
import accounts

app = Flask(__name__)
dotenv.load_dotenv()


#Assets routes
@app.route('/assets/<path:path>')
def assets(path):
    return send_from_directory('templates/assets', path)

#! TODO make prettier
def error(message):
    return jsonify({'success': False, 'message': message}), 400

@app.route('/')
def index():
    if 'token' in request.cookies:
        token = request.cookies['token']
        # Verify token
        user = accounts.validate_token(token)
        if not user:
            # Remove cookie
            resp = make_response(redirect('/'))
            resp.set_cookie('token', '', expires=0)
            return resp
        return render_template('index.html',account=user['email'],account_link="account")
    return render_template('index.html',account="Login",account_link="login")

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email']
    domain = request.form['domain']
    password = request.form['password']
    print("New signup for " + email + " | " + domain)
    try:
        valid = validate_email(email)
        email = valid.email
        user = accounts.create_user(email, domain, password)
        if not user['success']:
            return error(user['message'])

        # Redirect to dashboard with cookie
        resp = make_response(redirect('/edit'))
        resp.set_cookie('token', user['token'])
        return resp

    except EmailNotValidError as e:
        return jsonify({'success': False, 'message': 'Invalid email'}), 400

@app.route('/<path:path>')
def catch_all(path):
    # If file exists, load it
    if os.path.isfile('templates/' + path):
        return render_template(path)
    
    # Try with .html
    if os.path.isfile('templates/' + path + '.html'):
        return render_template(path + '.html')
    return redirect('/') # 404 catch all

# 404 catch all
@app.errorhandler(404)
def not_found(e):
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')