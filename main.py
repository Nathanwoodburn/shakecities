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
    'Standard with donate footer',
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
        
    tribes = db.get_tribes()
    tribesHTML = ""
    for tribe in tribes:
        tribesHTML += "<a href='/tribe/" + tribe + "'>" + tribe + "</a><br>"


    if 'token' in request.cookies:
        token = request.cookies['token']
        # Verify token
        user = accounts.validate_token(token)
        if not user:
            # Remove cookie
            resp = make_response(redirect('/'))
            resp.set_cookie('token', '', expires=0)
            return resp
        return render_template('index.html',account=user['email'],account_link="account",account_link_name="Account",CITY_DOMAIN=CITY_DOMAIN,random_sites=random_sites,tribes=tribesHTML)
    return render_template('index.html',account="Login",account_link="login",account_link_name="Login",CITY_DOMAIN=CITY_DOMAIN,random_sites=random_sites,tribes=tribesHTML)

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


@app.route('/tribe')
def tribe_list():
    tribes = db.get_tribes()
    tribesHTML = ""
    for tribe in tribes:
        tribesHTML += "<a href='/tribe/" + tribe + "'>" + tribe + "</a><br>"
    
    # Add create link if user is logged in
    if 'token' in request.cookies:
        token = request.cookies['token']
        # Verify token
        user = accounts.validate_token(token)
        if user:
            tribesHTML += "<br><br><a class='btn btn-primary' role='button' style='width: 100%;' href='/new_tribe'>Create a tribe</a>"
            return render_template('tribe.html',account="Account",account_link="account",account_link_name="Account",CITY_DOMAIN=CITY_DOMAIN,tribes=tribesHTML)
        
    return render_template('tribe.html',account="Login",account_link="login",account_link_name="Login",CITY_DOMAIN=CITY_DOMAIN,tribes=tribesHTML)

@app.route('/new_tribe')
def new_tribe():
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
    
    return render_template('new_tribe.html',account=user['email'],account_link="account",account_link_name="Account",CITY_DOMAIN=CITY_DOMAIN)

@app.route('/new_tribe', methods=['POST'])
def create_tribe():
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
    
    tribe = request.form['tribe'].strip().lower()
    if not re.match("^[a-z0-9]*$", tribe):
        return error('Sorry tribe can only contain lowercase letters and numbers')
    
    if len(tribe) < 3:
        return error('Sorry tribe must be at least 3 characters long')
    if len(tribe) > 255:
        return error('Sorry tribe must be less than 255 characters long')
    
    if db.create_tribe(tribe,user['domain']):
        return redirect('/tribe/' + tribe)
    else:
        return error('Sorry you already have a tribe')

@app.route('/tribe/<tribe>')
def tribe(tribe):
    tribe = tribe.lower()
    if not re.match("^[a-z0-9]*$", tribe):
        return error('Sorry we couldn\'t find that tribe')
    
    data = db.get_tribe_data_raw(tribe)
    if data == None:
        return error('Sorry we couldn\'t find that tribe')
    
    html = ""
    if 'data' in data:
        html = data['data'].encode('utf-8').decode('unicode-escape')
        html = html.replace("\n","<br>")
    
    tribe = tribe.capitalize()

    members_html = ""
    members = data['members']
    for member in members:
        members_html += "<a href='https://" + member + "." + CITY_DOMAIN + "' target='_blank'>" + member + "." +CITY_DOMAIN+ "</a><br>"

    edit = ""

    # Add edit link if user is logged in
    if 'token' in request.cookies:
        token = request.cookies['token']
        # Verify token
        user = accounts.validate_token(token)
        if user:
            if db.check_tribe_owner(tribe,user['domain']):
                edit = "<a class='btn btn-primary' role='button' style='width: 100%;' href='/edit_tribe'>Edit tribe</a>"
            elif user['domain'] not in members:
                edit = "<a class='btn btn-primary' role='button' style='width: 100%;' href='/join_tribe/" + tribe + "'>Join tribe</a>"
    
    return render_template('tribe_view.html',tribe=tribe,data=html,edit=edit,members=members_html)

@app.route('/join_tribe/<tribe>')
def join_tribe(tribe):
    tribe = tribe.lower()
    if not re.match("^[a-z0-9]*$", tribe):
        return error('Sorry we couldn\'t find that tribe')
    
    data = db.get_tribe_data_raw(tribe)
    if data == None:
        return error('Sorry we couldn\'t find that tribe')
    
    # Verify token
    token = request.cookies['token']
    if not accounts.validate_token(token):
        # Remove cookie
        resp = make_response(redirect('/login'))
        resp.set_cookie('token', '', expires=0)
        return resp
    user = accounts.validate_token(token)
    if not user:
        # Remove cookie
        resp = make_response(redirect('/login'))
        resp.set_cookie('token', '', expires=0)
        return resp
    
    members = data['members']
    if user['domain'] in members:
        return error('Sorry you are already a member of this tribe')
    
    members.append(user['domain'])
    data['members'] = members
    # Convert to json
    data = json.dumps(data)
    db.update_tribe_data_raw(tribe,data)
    return redirect('/tribe/' + tribe)


@app.route('/edit_tribe')
def edit_tribe_view():
    token = request.cookies['token']
    if not accounts.validate_token(token):
        return error('Sorry we had an issue verifying your account')
    # Verify token
    user = accounts.validate_token(token)
    if not user:
        # Remove cookie
        resp = make_response(redirect('/'))
        resp.set_cookie('token', '', expires=0)
        return resp
    
    tribeData = db.get_user_owned_tribe(user['domain'])
    if len(tribeData) == 0:
        return error('Sorry you don\'t own a tribe')
    
    tribe = tribeData[0][1]
    data = tribeData[0][2]
    data = json.loads(data)
    html = data['data'].encode('utf-8').decode('unicode-escape')
    members = data['members']
    members_html = ""
    for member in members:
        members_html += "<a href='https://" + member + "." + CITY_DOMAIN + "' target='_blank'>" + member + "." +CITY_DOMAIN+ "</a> <a href='/remove_member?member=" + member + "'>(Remove)</a><br>"

    return render_template('edit_tribe.html',account=user['email'],account_link="account",account_link_name="Account",CITY_DOMAIN=CITY_DOMAIN,tribe=tribe,data=html,members=members_html)

@app.route('/edit_tribe', methods=['POST'])
def edit_tribe():
    token = request.cookies['token']
    if not accounts.validate_token(token):
        return error('Sorry we had an issue verifying your account')
    # Verify token
    user = accounts.validate_token(token)
    if not user:
        # Remove cookie
        resp = make_response(redirect('/'))
        resp.set_cookie('token', '', expires=0)
        return resp
    
    tribeData = db.get_user_owned_tribe(user['domain'])
    if len(tribeData) == 0:
        return error('Sorry you don\'t own a tribe')

    tribe = tribeData[0][1]
    data = tribeData[0][2]
    data = json.loads(data)
    data['data'] = request.form['data'].strip()
    
    # Convert to json
    data = json.dumps(data)
    db.update_tribe_data_raw(tribe,data)
    return redirect('/edit_tribe')

@app.route('/remove_member')
def remove_member():
    token = request.cookies['token']
    if not accounts.validate_token(token):
        return error('Sorry we had an issue verifying your account')

    member = request.args.get('member')
    # Verify token
    user = accounts.validate_token(token)
    if not user:
        # Remove cookie
        resp = make_response(redirect('/'))
        resp.set_cookie('token', '', expires=0)
        return resp
    
    tribeData = db.get_user_owned_tribe(user['domain'])
    if len(tribeData) == 0:
        return error('Sorry you don\'t own a tribe')
    
    # Verify member isn't owner
    if member == user['domain']:
        return error('Sorry you can\'t remove yourself from your own tribe')

    tribe = tribeData[0][1]
    data = tribeData[0][2]
    data = json.loads(data)
    members = data['members']
    if member in members:
        members.remove(member)
        data['members'] = members
        # Convert to json
        data = json.dumps(data)
        db.update_tribe_data_raw(tribe,data)
    return redirect('/edit_tribe')

@app.route('/<path:path>')
def catch_all(path):
    account = "Login"
    account_link = "login"
    account_link_name = "Login"
    site = "Null"
    domain = ""
    tribe_title = "Join a tribe"
    tribe_link = "tribe"

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
        # Check if user owns tribe
        tribeData = db.get_user_owned_tribe(user['domain'])
        if len(tribeData) > 0:
            tribe_title = "Edit your tribe"
            tribe_link = "edit_tribe"

    elif path != "signup" and path != "login" and path != "empty_site":
        return redirect('/')
    
    if path == "account":
        account_link = "logout"
        account_link_name = "Logout"

    # If file exists, load it
    if os.path.isfile('templates/' + path):
        return render_template(path,account=account,account_link=account_link,
                               account_link_name=account_link_name,site=site,
                               CITY_DOMAIN=CITY_DOMAIN,domain=domain,
                               tribe_title=tribe_title,tribe_link=tribe_link)
    
    # Try with .html
    if os.path.isfile('templates/' + path + '.html'):
        return render_template(path + '.html',account=account,account_link=account_link,
                               account_link_name=account_link_name,site=site,
                               CITY_DOMAIN=CITY_DOMAIN,domain=domain,
                               tribe_title=tribe_title,tribe_link=tribe_link)
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
    app.run(debug=True, port=5000, host='0.0.0.0')