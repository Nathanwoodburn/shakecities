from flask import Flask, make_response, redirect, request, jsonify, render_template, send_from_directory
import os
import dotenv
import requests
import json
import schedule
import time
from email_validator import validate_email, EmailNotValidError
import accounts
import db

app = Flask(__name__)
dotenv.load_dotenv()

# Database connection
dbargs = {
    'host':os.getenv('DB_HOST'),
    'user':os.getenv('DB_USER'),
    'password':os.getenv('DB_PASSWORD'),
    'database':os.getenv('DB_NAME')
}

CITY_DOMAIN = os.getenv('CITY_DOMAIN')
if CITY_DOMAIN == None:
    CITY_DOMAIN = "exampledomainnathan1"

#Assets routes
@app.route('/assets/<path:path>')
def assets(path):
    return send_from_directory('templates/assets', path)


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
        return render_template('index.html',account=user['email'],account_link="account",account_link_name="Account",CITY_DOMAIN=CITY_DOMAIN)
    return render_template('index.html',account="Login",account_link="login",account_link_name="Login",CITY_DOMAIN=CITY_DOMAIN)

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email']
    domain = request.form['domain']
    password = request.form['password']
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
    
@app.route('/login', methods=['POST'])
def login():
    email=request.form['email']
    password=request.form['password']
    user = accounts.login(email,password)
    if not user['success']:
        return error(user['message'])
    # Redirect to dashboard with cookie
    resp = make_response(redirect('/edit'))
    resp.set_cookie('token', user['token'])
    return resp

@app.route('/edit')
def edit():
    if 'token' not in request.cookies:
        return redirect('/login')

    token = request.cookies['token']
    if not accounts.validate_token(token):
        return error('Invalid token')
    # Verify token
    user = accounts.validate_token(token)
    if not user:
        # Remove cookie
        resp = make_response(redirect('/login'))
        resp.set_cookie('token', '', expires=0)
        return resp
    
    data = db.get_website_data_raw(user['domain'])
    html = ""
    hns = ""
    btc = ""
    eth = ""

    if 'data' in data:
        html = data['data'].encode('utf-8').decode('unicode-escape')
    if 'HNS' in data:
        hns = data['HNS']
    if 'BTC' in data:
        btc = data['BTC']
    if 'ETH' in data:
        eth = data['ETH']

    return render_template('edit.html',account=user['email'],account_link="account",account_link_name="Account",data=html,hns=hns,btc=btc,eth=eth)


@app.route('/edit', methods=['POST'])
def send_edit():
    token = request.cookies['token']
    if not accounts.validate_token(token):
        return error('Invalid token')
    # Verify token
    user = accounts.validate_token(token)
    if not user:
        # Remove cookie
        resp = make_response(redirect('/login'))
        resp.set_cookie('token', '', expires=0)
        return resp
    
    # Json data
    data = {}
    data['data'] = request.form['data']
    data['HNS'] = request.form['hns']
    data['BTC'] = request.form['btc']
    data['ETH'] = request.form['eth']

    # Convert to json
    data = json.dumps(data)
    db.update_website_data_raw(user['domain'],data)
    return redirect('/edit')



@app.route('/logout')
def logout():
    token = request.cookies['token']
    if not accounts.logout(token)['success']:
        return error('Invalid token')
    
    # Remove cookie
    resp = make_response(redirect('/'))
    resp.set_cookie('token', '', expires=0)
    return resp

@app.route('/claim')
def claim():
    # Find domain
    domain = request.args.get('domain')
    return redirect('/signup?domain=' + domain)



@app.route('/<path:path>')
def catch_all(path):
    account = "Login"
    account_link = "login"
    account_link_name = "Login"
    site = "Null"
    domain = ""
    if 'domain' in request.args:
        domain = request.args.get('domain')
    if 'token' in request.cookies:
        token = request.cookies['token']
        # Verify token
        user = accounts.validate_token(token)
        if not user:
            # Remove cookie
            resp = make_response(redirect('/'))
            resp.set_cookie('token', '', expires=0)
            return resp
        account = user['email']
        account_link = "account"
        account_link_name = "Account"
        site = user['domain'] + "." + CITY_DOMAIN
    elif path != "signup" and path != "login":
        return redirect('/')

    # If file exists, load it
    if os.path.isfile('templates/' + path):
        return render_template(path,account=account,account_link=account_link,account_link_name=account_link_name,site=site,CITY_DOMAIN=CITY_DOMAIN,domain=domain)
    
    # Try with .html
    if os.path.isfile('templates/' + path + '.html'):
        return render_template(path + '.html',account=account,account_link=account_link,account_link_name=account_link_name,site=site,CITY_DOMAIN=CITY_DOMAIN,domain=domain)
    return redirect('/') # 404 catch all

# 404 catch all
@app.errorhandler(404)
def not_found(e):
    return redirect('/')



if __name__ == '__main__':
    db.check_tables()
    app.run(debug=False, port=5000, host='0.0.0.0')