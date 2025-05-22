from flask import Flask, render_template, request
import requests
import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy import text

# Load .env file contents into environment variables
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

with app.app_context():
    try:
        db.session.execute(text("SELECT 1"))
        print("✅ Connected to database.")
    except Exception as e:
        print("❌ Failed to connect:", e)

@app.route('/', methods=['GET', 'POST'])
def splash():
    return render_template('splash.html')
    

API_KEY = os.getenv('API_KEY')
AUTH_ENDPOINT = "https://utslogin.nlm.nih.gov/cas/v1/api-key"
SEARCH_ENDPOINT = "https://uts-ws.nlm.nih.gov/rest/search/current"
DEFINITIONS_ENDPOINT = "https://uts-ws.nlm.nih.gov/rest/content/current/CUI"
def get_tgt(api_key):
    params = {'apikey': api_key}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(AUTH_ENDPOINT, data=params, headers=headers)
    if response.status_code == 201:
        tgt_url = response.headers['location']
        return tgt_url
    return None

def get_service_ticket(tgt_url):
    params = {'service': 'http://umlsks.nlm.nih.gov'}
    response = requests.post(tgt_url, data=params)
    print("service ticket", response.text)
    return response.text if response.status_code == 200 else None

def get_definitions(cui, st, language= "ENG"):
    rootsource_map = {
        "ENG": ["MSH", "HPO", "NCI"] # Common English sources
    }
    url = f"https://uts-ws.nlm.nih.gov/rest/content/2023AA/CUI/{cui}/definitions"
    params = {"ticket": st}
    response = requests.get(url, params)
    print("Reponse text", response.text)
    print("Response url", response.url)
    if response.status_code == 200:
        defs = response.json()['result']
        allowed_sources = rootsource_map.get(language.upper(), [])
        filtered_defs = [d.get("value") for d in defs if d.get("rootSource") in allowed_sources and d.get("value")]
        print("Filtered defs")
        return filtered_defs or ["No definitions available in this version."]
    print("not 200")
    return ["Definition lookup failed."]

@app.route('/search', methods=['GET', 'POST'])
def index():
    search_results = []
    error = None
    if request.method == 'POST':
        query = request.form['query']
        tgt = get_tgt(API_KEY)
        if tgt:
            st = get_service_ticket(tgt)
            if st:
                params = {
                    'string': query,
                    'ticket': st
                }
                response = requests.get(SEARCH_ENDPOINT, params=params)
                if response.status_code == 200:
                    search_items = response.json()['result']['results']
                    for item in search_items[:5]:  # limit to top 5 for speed
                        cui = item.get('ui')
                        name = item.get('name')
                        print("CUI", cui)
                        if cui and cui != 'NONE':
                            tgt = get_tgt(API_KEY)
                            st = get_service_ticket(tgt)
                            definitions = get_definitions(cui, st)
                            search_results.append({
                                'name': name,
                                'cui': cui,
                                'definitions': definitions
                            })
                else:
                    error = "Failed to fetch search results."
            else:
                error = "Failed to get service ticket."
        else:
            error = "Failed to get authentication ticket."

    return render_template('index.html', results=search_results, error=error)

if __name__ == '__main__':
    app.run(debug=True)