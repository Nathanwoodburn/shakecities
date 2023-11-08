from flask import Flask, make_response, redirect, render_template_string, request, jsonify, render_template, send_from_directory
from bs4 import BeautifulSoup

def render(data):
    if data == "":
        return "No data found for this domain"
    
    try:
        soup = BeautifulSoup(data, 'html.parser')
        for script in soup.find_all('script'):
            script.extract()
        modified_data = str(soup)
        return render_template_string(modified_data)


    except Exception as e:
        return "<h1>Invalid HTML</h1><br>" + str(e)