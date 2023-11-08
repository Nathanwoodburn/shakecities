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


#Assets routes
@app.route('/assets/<path:path>')
def assets(path):
    return send_from_directory('templates/assets', path)

#! TODO make prettier
def error(message):
    return jsonify({'success': False, 'message': message}), 400

@app.route('/')
def index():
    host = request.host
    if len(host.split('.')) != 2:
        return error('Invalid domain')
    host = host.split('.')[0]
    
    # Get website data
    data = db.get_website_data(host)
    # Render as HTML
    return website.render(data)


@app.route('/<path:path>')
def catch_all(path):
    return redirect('/') # 404 catch all

# 404 catch all
@app.errorhandler(404)
def not_found(e):
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')