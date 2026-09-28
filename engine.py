import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_knowledge_card(query):
    """Récupère la fiche d'information Wikipédia (sans IA)"""
    try:
        url = f"https://fr.wikipedia.org/api/rest_v1/page/summary/{query}"
        res = requests.get(url, headers=HEADERS, timeout=4)
        if res.status_code == 200:
            data = res.json()
            if data.get('type') == 'standard':
                return {
                    'title': data.get('title'),
                    'description': data.get('description', ''),
                    'extract': data.get('extract'),
                    'thumbnail': data.get('thumbnail', {}).get('source'),
                    'link': data.get('content_urls', {}).get('desktop', {}).get('page')
                }
    except Exception as e:
        print(f"Erreur Knowledge Card : {e}")
    return None

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
    card = None
    results = []
    
    if query:
        card = get_knowledge_card(query)
        results = search_wikipedia(query)
    
    return render_template('index.html', query=query, card=card, results=results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
