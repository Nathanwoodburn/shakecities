from flask import Flask, send_from_directory
import sys
import sites.website as website
import json
import os

app = Flask(__name__)
template = "city"
data = "<h1>Test site</h1><p>This is a test site</p>"
# data = "<div style=\"text-align:center;\"><h1>Nathan.Woodburn/</h1><h2>This is fully customizable!</h2><p>You can even add custom css rules like below.<br>Try hovering over this image</p><style>img.background:hover {filter: blur(5px)}</style><div class=\"profile-container\" style=\"height: 300px;margin-bottom: 2em;\"><img class=\"profile background\" src=\"https://nathan.woodburn.au/assets/img/profile.jpg\" style=\"border-radius: 50%;width: 300px;position: absolute;left: 50%;margin-left: -150px;aspect-ratio: 1;padding-top: calc(var(--s)/5);transform: scale(1);transition: .5s;\" alt=\"My Profile\"><img class=\"profile foreground\" src=\"https://nathan.woodburn.au/assets/img/pfront.webp\" alt=\"\" style=\"border-radius: 50%;pointer-events: none;width: 300px;position: absolute;left: 50%;margin-left: -150px;aspect-ratio: 1;padding-top: calc(var(--s)/5);transform: scale(1);transition: .5s;\"></div>"

db_object = {
    'avatar': "https://woodburn.au/favicon.png",
    'hnschat':"nathan.woodburn",
    'location': "Australia",
    'email': "test@email",
    'HNS': "hs1qh7c98nexsrzwrmnh2avved6awe59jzpr3xx2xf",
    'BTC': "bc1qhs94zzcw64qnwq4hvk056rwxwvgrkd7tq7d4xw",
    'ETH' : "0x6cB4B39bEc23a921C9a20D061Bf17d4640B0d39e",
    'bg_colour': "#000000",
    # 'fg_colour': "#ffffff",
    # 'text_colour': "#152D45",
    'text_colour': "#ffffff",
    'fg_colour': "#8f00db",
    
}

@app.route('/')
def index():
    if os.path.exists("templates/"+template+".html"):
        with open("templates/"+template+".html") as f:
            filedata = f.read()
            filedata = filedata.replace('#f1ffff', '{{fg_colour}}')
            filedata = filedata.replace('#1fffff', '{{text_colour}}')
            filedata = filedata.replace('#000000', '{{bg_colour}}')
            # Save
            with open('templates/' + template+".tmp.html", 'w') as f:
                f.write(filedata)
    else:
        return "Template not found"
    
    db_object['template'] = template + ".tmp.html"
    render = website.render(data,db_object)
    
    # Delete tmp
    os.remove('templates/' + template+".tmp.html")
    return render

@app.route('/assets/<path:path>')
def send_assets(path):
    return send_from_directory('templates/assets', path)


@app.route('/.well-known/wallets/<path:path>')
def send_wallets(path):
    if path in db_object:
        return db_object[path]
    else:
        return "Not found"

if __name__ == "__main__":
    # Get second arg
    if len(sys.argv) > 1:
        template = sys.argv[1]
    else:
        print("Usage: python3 template.py <template>")
        sys.exit(0)


    
    app.run(host='0.0.0.0', port=5000, debug=True)
