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
import varo
import re
import avatar

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
IMAGE_LOCATION = os.getenv('IMAGE_LOCATION')
if IMAGE_LOCATION == None:
    IMAGE_LOCATION = "/data"

random_sites = ""

# Templates available for user
templates = [
    'Standard',
    'Original',
    'No card around data',
    'No card around data (2)',
    'Blank',
    'Standard with donate footer'
    'No card with donate footer'
    ]

#Assets routes
@app.route('/assets/<path:path>')
def assets(path):
    return send_from_directory('templates/assets', path)

@app.route('/avatar/<path:path>')
def avatar_view(path):
    return send_from_directory(IMAGE_LOCATION, path)


def error(message):
    return render_template('error.html', message=message)

@app.route('/')
def index():
    global random_sites
    if random_sites == "":
        random_sites_names = db.get_random_sites()
        for site in random_sites_names:
            random_sites += "<a href='https://" + site + "." + CITY_DOMAIN + "' target='_blank'>" + site + "." +CITY_DOMAIN+ "</a><br>"
        
    


    if 'token' in request.cookies:
        token = request.cookies['token']
        # Verify token
        user = accounts.validate_token(token)
        if not user:
            # Remove cookie
            resp = make_response(redirect('/'))
            resp.set_cookie('token', '', expires=0)
            return resp
        return render_template('index.html',account=user['email'],account_link="account",account_link_name="Account",CITY_DOMAIN=CITY_DOMAIN,random_sites=random_sites)
    return render_template('index.html',account="Login",account_link="login",account_link_name="Login",CITY_DOMAIN=CITY_DOMAIN,random_sites=random_sites)

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email']
    domain = request.form['domain'].lower()
    password = request.form['password']

    # Verify domain
    if not re.match("^[a-z0-9]*$", domain):
        return error('Sorry domain can only contain lowercase letters and numbers')

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
    resp = make_response(redirect('/account'))
    resp.set_cookie('token', user['token'])
    return resp

@app.route('/edit')
def edit():
    if 'token' not in request.cookies:
        return redirect('/login')

    token = request.cookies['token']
    if not accounts.validate_token(token):
        return error('Sorry we had an issue verifying your account')
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
    hnschat = ""
    location = ""
    avatar = ""
    bg_colour = ""
    fg_colour = ""
    text_colour = ""
    email = ""
    hip2_display = False

    if 'data' in data:
        html = data['data'].encode('utf-8').decode('unicode-escape')
    if 'HNS' in data:
        hns = data['HNS']
    if 'BTC' in data:
        btc = data['BTC']
    if 'ETH' in data:
        eth = data['ETH']
    if 'hnschat' in data:
        hnschat = data['hnschat']
    if 'location' in data:
        location = data['location']
    if 'avatar' in data:
        avatar = data['avatar']
        if avatar != "":
            avatar = "<img class='rounded-circle' width='100px' height='100px' src='"+avatar+"' style='margin-right: 25px;' />"
        else:
            avatar = "<p style='margin-right: 25px;'>No avatar set</p>"

    if 'bg_colour' in data:
        bg_colour = data['bg_colour']
    if 'fg_colour' in data:
        fg_colour = data['fg_colour']
    else:
        fg_colour = "#ffffff"
    if 'text_colour' in data:
        text_colour = data['text_colour']
    if 'email' in data:
        email = data['email']

    if 'template' in data:
        selected_template = data['template']
    else:
        selected_template = templates[0]

    if 'hip2_display' in data:
        hip2_display = data['hip2_display']


    return render_template('edit.html',account=user['email'],account_link="account",account_link_name="Account",data=html,
                           hns=hns,btc=btc,eth=eth,hnschat=hnschat,email=email,location=location,avatar=avatar,
                           bg_colour=bg_colour,fg_colour=fg_colour,text_colour=text_colour,templates=templates,
                           selected_template=selected_template,CITY_DOMAIN=CITY_DOMAIN,domain=user['domain'],hip2_display=hip2_display)


@app.route('/edit', methods=['POST'])
def send_edit():
    token = request.cookies['token']
    if not accounts.validate_token(token):
        return error('Sorry we had an issue verifying your account')
    # Verify token
    user = accounts.validate_token(token)
    if not user:
        # Remove cookie
        resp = make_response(redirect('/login'))
        resp.set_cookie('token', '', expires=0)
        return resp
    
    # Json data
    data = db.get_website_data_raw(user['domain'])
    data['data'] = request.form['data'].strip()
    data['HNS'] = request.form['hns'].strip()
    data['BTC'] = request.form['btc'].strip()
    data['ETH'] = request.form['eth'].strip()
    data['hnschat'] = request.form['hnschat'].strip()

    data['hnschat'] = data['hnschat'].replace("/","").strip()

    data['location'] = request.form['location'].strip()
    data['bg_colour'] = request.form['bg_colour'].strip()
    data['fg_colour'] = request.form['fg_colour'].strip()
    data['text_colour'] = request.form['text_colour'].strip()
    data['email'] = request.form['email'].strip()
    data['template'] = request.form['template'].strip()

    if 'hip2_display' in request.form:
        data['hip2_display'] = True
    else:
        data['hip2_display'] = False

    # Convert to json
    data = json.dumps(data)
    db.update_website_data_raw(user['domain'],data)
    return redirect('/edit')



@app.route('/logout')
def logout():
    token = request.cookies['token']
    if not accounts.logout(token)['success']:
        return error('Sorry we had an issue verifying your account')
    
    # Remove cookie
    resp = make_response(redirect('/'))
    resp.set_cookie('token', '', expires=0)
    return resp

@app.route('/claim')
def claim():
    # Find domain
    domain = request.args.get('domain')
    return redirect('/signup?domain=' + domain)

@app.route('/hnschat')
def hnschat():
    token = request.cookies['token']
    if not accounts.validate_token(token):
        return error('Sorry we had an issue verifying your account')
    # Verify token
    user = accounts.validate_token(token)
    if not user:
        # Remove cookie
        resp = make_response(redirect('/login'))
        resp.set_cookie('token', '', expires=0)
        return resp
    record = varo.get_auth(user['domain'])
    return render_template('hnschat.html',account=user['email'],account_link="account",account_link_name="Account",CITY_DOMAIN=CITY_DOMAIN,domain=user['domain'],hnschat=record)

@app.route('/hnschat', methods=['POST'])
def save_hnschat():
    token = request.cookies['token']
    if not accounts.validate_token(token):
        return error('Sorry we had an issue verifying your account')
    # Verify token
    user = accounts.validate_token(token)
    if not user:
        # Remove cookie
        resp = make_response(redirect('/login'))
        resp.set_cookie('token', '', expires=0)
        return resp
    
    record = request.form['hnschat']
    varo.update_auth(record,user['domain'])    
    
    return redirect('/hnschat')

@app.route('/upload', methods=['POST'])
def upload_avatar():
    token = request.cookies['token']
    if not accounts.validate_token(token):
        return error('Sorry we had an issue verifying your account')
    # Verify token
    user = accounts.validate_token(token)
    if not user:
        # Remove cookie
        resp = make_response(redirect('/login'))
        resp.set_cookie('token', '', expires=0)
        return resp

    if 'file' not in request.files:
        return error('We couldn\'t find a file in your request')
    file = request.files['file']

    if file.filename == '':
        return error('We couldn\'t find a file in your request')

    if file and avatar.allowed_file(file.filename):
        # Save the file to the upload folder
        avatar.save_avatar(file,user['domain'])
        return redirect('/edit')
        

    return error('Sorry we couldn\'t upload your file')

@app.route('/avatar/clear')
def avatar_clear():
    token = request.cookies['token']
    if not accounts.validate_token(token):
        return error('Sorry we had an issue verifying your account')
    # Verify token
    user = accounts.validate_token(token)
    if not user:
        # Remove cookie
        resp = make_response(redirect('/login'))
        resp.set_cookie('token', '', expires=0)
        return resp

    avatar.clear(user['domain'])
    return redirect('/edit')


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
    
    if path == "account":
        account_link = "logout"
        account_link_name = "Logout"

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

def update_random_sites():
    global random_sites
    random_sites_names = db.get_random_sites()
    random_sites = ""
    for site in random_sites_names:
        random_sites += "<a href='https://" + site + "." + CITY_DOMAIN + "' target='_blank'>" + site + "." +CITY_DOMAIN+ "</a><br>"

if __name__ == '__main__':
    db.check_tables()
    app.run(debug=False, port=5000, host='0.0.0.0')