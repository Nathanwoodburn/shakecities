from flask import Flask, make_response, redirect, render_template_string, request, jsonify, render_template, send_from_directory
from bs4 import BeautifulSoup
import os
import dotenv

main_domain = "cities.hnshosting.au"
if os.getenv('MAIN_DOMAIN') != None:
    main_domain = os.getenv('MAIN_DOMAIN')

def render(data,db_object):
    if data == "":
        return redirect("https://" + main_domain + '/claim?domain=' + request.host.split('.')[0])
    
    # Render as HTML
    html = ""
    try:
        soup = BeautifulSoup(data, 'html.parser')
        for script in soup.find_all('script'):
            script.extract()

        html = str(soup)
    except Exception as e:
        return "<h1>Invalid HTML</h1><br>" + str(e)
    
    try:
        avatar = db_object['avatar']
        hnschat = db_object['hnschat']
        location = db_object['location']
        hns = db_object['HNS']
        btc = db_object['BTC']
        eth = db_object['ETH']
        if hns != "":
            hns = "HNS: " + hns
        if btc != "":
            btc = "BTC: " + btc
        if eth != "":
            eth = "ETH: " + eth

        bg_colour = db_object['bg_colour']
        fg_colour = db_object['fg_colour']
        text_colour = db_object['text_colour']
        if (rgb_to_hex(generate_foreground_color(fg_colour)) == ""):
            hns_icon = "assets/img/HNSW.png"
        else:
            hns_icon = "assets/img/HNS.png"

    except Exception as e:
        return "<h1>Invalid data</h1><br><h2>Please contact support</h2><br><p>This can often be fixed by saving your site again in the editor</p><br>" + "<script>console.log('" + str(e) + "');</script>"


    return render_template('city.html',html=html,bg_colour=bg_colour,text_colour=text_colour,
                            fg_colour=fg_colour, avatar=avatar,main_domain=main_domain,
                           hnschat=hnschat,location=location, hns_icon=hns_icon,
                           hns=hns,btc=btc,eth=eth, data=html)
    


def calculate_contrast_ratio(color1, color2):
    def calculate_luminance(color):
        def adjust_color_value(value):
            value /= 255.0
            if value <= 0.03928:
                return value / 12.92
            return ((value + 0.055) / 1.055) ** 2.4

        r, g, b = color
        r = adjust_color_value(r)
        g = adjust_color_value(g)
        b = adjust_color_value(b)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    luminance1 = calculate_luminance(color1)
    luminance2 = calculate_luminance(color2)

    brighter = max(luminance1, luminance2)
    darker = min(luminance1, luminance2)

    contrast_ratio = (brighter + 0.05) / (darker + 0.05)
    return contrast_ratio

def generate_foreground_color(background_color):
    # Convert to RGB tuple
    background_color=background_color.lstrip('#')
    background_color = tuple(int(background_color[i:i+2], 16) for i in (0, 2, 4))

    contrast_color = (255, 255, 255)  # White
    ratio = calculate_contrast_ratio(background_color, contrast_color)

    if ratio < 4.5:
        return (0, 0, 0)  # Black
    else:
        return contrast_color
    
def rgb_to_hex(rgb_color):
    return "#{:02x}{:02x}{:02x}".format(*rgb_color)
