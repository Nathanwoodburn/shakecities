from flask import Flask, make_response, redirect, render_template_string, request, jsonify, render_template, send_from_directory
from bs4 import BeautifulSoup
import os
import dotenv

main_domain = "cities.hnshosting.au"
if os.getenv('MAIN_DOMAIN') != None:
    main_domain = os.getenv('MAIN_DOMAIN')

def render(data):
    if data == "":
        return redirect("https://" + main_domain + '/claim?domain=' + request.host.split('.')[0])
    
    try:
        soup = BeautifulSoup(data, 'html.parser')
        for script in soup.find_all('script'):
            script.extract()

        modified = str(soup)
        return render_template_string(modified)


    except Exception as e:
        return "<h1>Invalid HTML</h1><br>" + str(e)