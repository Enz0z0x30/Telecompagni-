import os
from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

HEADERS = {
    'User-Agent': 'TelecompagnieSearch/1.0 (contact@telecompagnie.fr)'
}

def search_wikipedia(query):
    try:
        url = f"https://fr.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json"
        res = requests.get(url, headers=HEADERS, timeout=5)
        if res.status_code == 200:
            data = res.json()
            results = []
            for item in data.get('query', {}).get('search', []):
                results.append({
                    'title': item['title'],
                    'snippet': BeautifulSoup(item['snippet'], 'html.parser').text,
                    'link': f"https://fr.wikipedia.org/wiki/{item['title'].replace(' ', '_')}"
                })
            return results
    except Exception as e:
        print(f"Erreur Wikipedia : {e}")
    return []

@app.route('/')
def index():
    query = request.args.get('q', '')
    results = []
    if query:
        results = search_wikipedia(query)
    return render_template('index.html', query=query, results=results) if os.path.exists('templates/index.html') else f"<h1>Télécompagnie</h1><form><input name='q' value='{query}'><button>Chercher</button></form><ul>" + "".join([f"<li><a href='{r['link']}'>{r['title']}</a>: {r['snippet']}</li>" for r in results]) + "</ul>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
