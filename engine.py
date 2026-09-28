import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def search_wikipedia(query):
    try:
        url = f"https://fr.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json"
        res = requests.get(url, headers=HEADERS, timeout=5)
        if res.status_code == 200:
            data = res.json()
            return [
                {
                    'title': item['title'],
                    'snippet': BeautifulSoup(item['snippet'], 'html.parser').text,
                    'link': f"https://fr.wikipedia.org/wiki/{item['title'].replace(' ', '_')}"
                }
                for item in data.get('query', {}).get('search', [])
            ]
    except Exception as e:
        print(f"Erreur Wiki: {e}")
    return []

@app.route('/')
def index():
    query = request.args.get('q', '')
    results = search_wikipedia(query) if query else []
    
    if os.path.exists('templates/index.html'):
        return render_template('index.html', query=query, results=results)
    
    html = f"<h1>Télécompagnie</h1><form><input name='q' value='{query}'><button>Chercher</button></form><ul>"
    for r in results:
        html += f"<li><a href='{r['link']}' target='_blank'><b>{r['title']}</b></a><p>{r['snippet']}</p></li>"
    html += "</ul>"
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
