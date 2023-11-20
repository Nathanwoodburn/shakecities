from flask import Flask, redirect, render_template_string, request
from bs4 import BeautifulSoup
import os
import dotenv

main_domain = "shakecities.com"
if os.getenv('MAIN_DOMAIN') != None:
    main_domain = os.getenv('MAIN_DOMAIN')

FOOTER=""
if os.path.exists("parts/footer.html"):
    with open("parts/footer.html") as f:
        FOOTER = f.read()
elif os.path.exists("sites/parts/footer.html"):
    with open("sites/parts/footer.html") as f:
        FOOTER = f.read()

def render(data,db_object):
    if data == False:
        return redirect("https://" + main_domain + '/claim?domain=' + request.host.split('.')[0])
    elif data == "":
        return redirect("https://" + main_domain + '/empty_site?nodata')
    
    # Render as HTML
    html = ""
    ssl = "<script src='https://nathan.woodburn/https.js'></script>"
    if ("localhost" in request.host or "127.0.0.1" in request.host):
        ssl = ""

    try:
        soup = BeautifulSoup(data, 'html.parser')
        # Inject SSL
        soup.append(BeautifulSoup(ssl, 'html.parser'))

        html = str(soup)
    except Exception as e:
        return redirect("https://" + main_domain + '/empty_site?error='+str(e))
    
    try:
        avatar = db_object['avatar']
        hnschat = db_object['hnschat']
        location = db_object['location']
        email = db_object['email']
        hns = db_object['HNS']

        if 'hip2_display' in db_object:
            if db_object['hip2_display'] == True:
                hns = "@"+request.host

        btc = db_object['BTC']
        eth = db_object['ETH']
        bg_colour = db_object['bg_colour']
        fg_colour = db_object['fg_colour']
        text_colour = db_object['text_colour']
        if (rgb_to_hex(generate_foreground_color(text_colour)) == "#000000"):
            hns_icon = "assets/img/HNSW.png"
            btc_icon = "assets/img/BTCW.png"
            eth_icon = "assets/img/ETHW.png"
            hns_icon_invert = "assets/img/HNS.png"
            btc_icon_invert = "assets/img/BTC.png"
            eth_icon_invert = "assets/img/ETH.png"
            location_icon = "assets/img/mapw.png"
            email_icon = "assets/img/emailw.png"
        else:
            hns_icon = "assets/img/HNS.png"
            btc_icon = "assets/img/BTC.png"
            eth_icon = "assets/img/ETH.png"
            hns_icon_invert = "assets/img/HNSW.png"
            btc_icon_invert = "assets/img/BTCW.png"
            eth_icon_invert = "assets/img/ETHW.png"
            location_icon = "assets/img/map.png"
            email_icon = "assets/img/email.png"
        hns_address = hns
        btc_address = btc
        eth_address = eth
        if hns != "":
            hns = "<img src='" + hns_icon + "' width='20px' height='20px' style='margin-right: 5px;'>" + hns
        if btc != "":
            btc = "<img src='" + btc_icon + "' width='20px' height='25px' style='margin-right: 5px;'>" + btc
        if eth != "":
            eth = "<img src='" + eth_icon + "' width='20px' height='30px' style='margin-right: 5px;'>" + eth
        if hns != "":
            hns_invert = "<img src='" + hns_icon_invert + "' width='20px' height='20px' style='margin-right: 5px;'>" + hns_address
        if btc != "":
            btc_invert = "<img src='" + btc_icon_invert + "' width='20px' height='25px' style='margin-right: 5px;'>" + btc_address
        if eth != "":
            eth_invert = "<img src='" + eth_icon_invert + "' width='20px' height='30px' style='margin-right: 5px;'>" + eth_address

        hide_addresses = False
        if hns == "" and btc == "" and eth == "":
            hide_addresses = True
        
        if hnschat != "":
            hnschat = "<a href='https://hns.chat/#message:"+hnschat+"' target='_blank'><img src='"+hns_icon+"' width='20px' height='20px' style='margin-right: 5px;'>" + hnschat + "/</a>"
        if location != "":
            location = "<img src='"+location_icon+"' width='20px' height='30px' style='margin-right: 5px;'>" + location
        if email != "":
            email = "<a href='mailto:"+email+"'><img src='"+email_icon+"' width='30px' height='20px' style='margin-right: 5px;margin-left:-10px;'>" + email + "</a>"

        if avatar != "":
            avatar = "<img src='"+avatar+"' width='200vw' height='200vw' style='border-radius: 50%;margin-right: 5px;'>"
        else:
            avatar = "<h1 style='color:"+fg_colour+";'>" + request.host.split(':')[0] + "/</h1>"

        template = "Standard"

        if 'template' in db_object:
            if db_object['template'] != "":
                template = db_object['template']

        footer = render_template_string(FOOTER,main_domain=main_domain,fg_colour=fg_colour,hns_icon=hns_icon)
        return render_template_string(get_template(template,hide_addresses),bg_colour=bg_colour,text_colour=text_colour,
                fg_colour=fg_colour, avatar=avatar,main_domain=main_domain,
                hnschat=hnschat,email=email,location=location, hns_icon=hns_icon,
                hns=hns,btc=btc,eth=eth,hns_invert=hns_invert,btc_invert=btc_invert,
                eth_invert=eth_invert,hns_address=hns_address,btc_address=btc_address,eth_address=eth_address,
                hns_icon_invert=hns_icon_invert,btc_icon=btc_icon,btc_icon_invert=btc_icon_invert,
                eth_icon=eth_icon,eth_icon_invert=eth_icon_invert,
                data=html,footer=footer)
    except Exception as e:
        return redirect("https://" + main_domain + '/empty_site?error='+str(e))

def get_template(template,hide_addresses=False):
    file = "templates/" +get_template_file(template)
    with open(file) as f:
        data = f.read()

    # Read template
    soup = BeautifulSoup(data, 'html.parser')
    # Remove addresses div
    if hide_addresses:
        try:
            addresses = soup.find(id="addresses")
            addresses.decompose()
        except:
            pass    
    
    return str(soup)

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



def get_template_file(template):
    if template.endswith(".html"):
        return template


    template = template.lower()
    templates = {
        "standard": "city.html",
        "original": "city_old.html",
        "no card around data": "city_no_card.html",
        "no card around data (2)": "city_no_card_2.html",
        "blank": "city_blank.html"
    }

    if template in templates:
        return templates[template]
    
    
    return "city.html"