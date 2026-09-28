import os
from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Headers simulant un vrai navigateur Chrome pour éviter les blocs 429 et timeout
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'
}

def search_wikipedia(query):
    try:
        url = f"https://fr.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json"
        res = requests.get(url, headers=HEADERS, timeout=8)
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

def search_duckduckgo(query):
    try:
        url = f"https://html.duckduckgo.com/html/?q={query}"
        res = requests.get(url, headers=HEADERS, timeout=8)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            results = []
            for a in soup.find_all('a', class_='result__url', limit=5):
                results.append({
                    'title': a.text.strip(),
                    'snippet': '',
                    'link': a['href']
                })
            return results
    except Exception as e:
        print(f"Erreur DuckDuckGo : {e}")
    return []

@app.route('/')
def index():
    query = request.args.get('q', '')
    results = []
    if query:
        results = search_wikipedia(query) + search_duckduckgo(query)
    
    if os.path.exists('templates/index.html'):
        return render_template('index.html', query=query, results=results)
    
    items_html = "".join([f"<li><a href='{r['link']}' target='_blank'><b>{r['title']}</b></a><p>{r['snippet']}</p></li>" for r in results])
    return f"<h1>Télécompagnie</h1><form><input name='q' value='{query}'><button>Chercher</button></form><ul>{items_html}</ul>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
