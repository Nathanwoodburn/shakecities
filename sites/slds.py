from flask import Flask, make_response, redirect, render_template_string, request, jsonify, render_template, send_from_directory
import os
import dotenv
import requests
import json
import schedule
import time
import db
import website


app = Flask(__name__)
dotenv.load_dotenv()

main_domain = "cities.hnshosting.au"
if os.getenv('MAIN_DOMAIN') != None:
    main_domain = os.getenv('MAIN_DOMAIN')

#Assets routes
@app.route('/assets/<path:path>')
def assets(path):
    return send_from_directory('templates/assets', path)

@app.route('/')
def index():
    host = request.host
    if len(host.split('.')) != 2:
        return redirect('https://'+main_domain)
    host = host.split('.')[0]
    
    # Get website data
    data = db.get_website_data(host)
    db_object = db.get_website_data_raw(host)
    # Render as HTML
    return website.render(data,db_object)


@app.route('/.well-known/wallets/<token>')
def wallet(token):
    address = db.get_website_wallet(request.host.split('.')[0],token)
    if address == "":
        return redirect('/')
    # Plain text
    response = make_response(address)
    response.mimetype = "text/plain"
    return response

@app.route('/<path:path>')
def catch_all(path):
    return redirect('/') # 404 catch all

# 404 catch all
@app.errorhandler(404)
def not_found(e):
    return redirect('/')

def clean_template():
    # Clean template
    with open('templates/city.html') as f:
        data = f.read()
    
    data = data.replace('#f1ffff', '{{fg_colour}}')
    data = data.replace('#1fffff', '{{text_colour}}')
    data = data.replace('#000000', '{{bg_colour}}')
    # Save
    with open('templates/city.html', 'w') as f:
        f.write(data)
    print("Cleaned template", flush=True)

if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')