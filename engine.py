import urllib.parse
import urllib.request
import re
import json
from flask import Flask, request, render_template_string

app = Flask(__name__)

def search_ddg_lite(query):
    """Effectue une recherche Web directe sur la version HTML ultra-légère de DuckDuckGo."""
    results = []
    try:
        data = urllib.parse.urlencode({'q': query}).encode('utf-8')
        req = urllib.request.Request(
            'https://html.duckduckgo.com/html/',
            data=data,
            headers={
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
                'Referer': 'https://html.duckduckgo.com/'
            }
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            # Extraction par regex des blocs de résultats HTML
            snippets = re.findall(r'<a class="result__snippet[^"]*"[^>]*>(.*?)</a>', html, re.DOTALL)
            links = re.findall(r'<a class="result__url"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
            titles = re.findall(r'<a class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL)
            
            for i in range(min(len(titles), 12)):
                title_clean = re.sub(r'<[^>]+>', '', titles[i]).strip()
                raw_url = links[i][0] if i < len(links) else ""
                
                # Décodage de la redirection DuckDuckGo
                match_url = re.search(r'uddg=(https?://[^&]+)', raw_url)
                direct_url = urllib.parse.unquote(match_url.group(1)) if match_url else raw_url
                
                snippet_clean = re.sub(r'<[^>]+>', '', snippets[i]).strip() if i < len(snippets) else ""
                
                if direct_url.startswith('http'):
                    results.append({
                        "title": title_clean,
                        "url": direct_url,
                        "snippet": snippet_clean or "Lien Web direct."
                    })
    except Exception as e:
        print(f"[!] Erreur DuckDuckGo Lite : {e}")
    return results

def search_wikipedia_fallback(query):
    """Source de secours Wikipedia API."""
    results = []
    try:
        url = f"https://fr.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json&utf8=1"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode('utf-8'))
            for item in data.get('query', {}).get('search', [])[:8]:
                title = item.get('title', '')
                snippet = re.sub(r'<[^>]+>', '', item.get('snippet', ''))
                page_url = f"https://fr.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
                results.append({
                    "title": title,
                    "url": page_url,
                    "snippet": snippet + "..."
                })
    except Exception as e:
        print(f"[!] Erreur Wikipedia : {e}")
    return results

def get_web_results(query):
    if not query.strip():
        return []
    
    # Tentative 1 : DuckDuckGo HTML Lite
    results = search_ddg_lite(query)
    
    # Tentative 2 (Fallback) : Wikipedia si DuckDuckGo ne renvoie rien
    if not results:
        results = search_wikipedia_fallback(query)
        
    return results

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Télécompagnie — Moteur Web</title>
    <style>
        :root {
            --bg-color: #0b0d17;
            --card-bg: #151828;
            --gradient-accent: linear-gradient(135deg, #00f2fe 0%, #4facfe 35%, #ff0844 70%, #ffb199 100%);
            --text-glow: 0 0 20px rgba(0, 242, 254, 0.4);
            --btn-glow: 0 0 15px rgba(255, 8, 68, 0.5);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: #ffffff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 30px 15px;
        }

        .header { text-align: center; margin-bottom: 30px; }

        .brand-title {
            font-size: 2.4rem;
            font-weight: 900;
            background: var(--gradient-accent);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: var(--text-glow);
            letter-spacing: -0.5px;
        }

        .tagline {
            font-size: 0.95rem;
            color: #a0a5c0;
            margin-top: 8px;
            font-style: italic;
        }

        .tagline span { color: #ff416c; font-weight: 600; }

        form {
            display: flex;
            width: 100%;
            max-width: 600px;
            gap: 10px;
            background: rgba(255, 255, 255, 0.03);
            padding: 8px;
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(10px);
        }

        input[type="text"] {
            flex: 1;
            padding: 14px 18px;
            border-radius: 10px;
            border: none;
            background: var(--card-bg);
            color: #fff;
            font-size: 1rem;
            outline: none;
            border: 1px solid transparent;
            transition: all 0.3s ease;
        }

        input[type="text"]:focus {
            border-color: #00f2fe;
            box-shadow: 0 0 10px rgba(0, 242, 254, 0.2);
        }

        button {
            padding: 14px 24px;
            border-radius: 10px;
            border: none;
            background: linear-gradient(135deg, #00f2fe, #ff0844);
            color: #ffffff;
            font-weight: 700;
            font-size: 0.95rem;
            cursor: pointer;
            box-shadow: var(--btn-glow);
            transition: transform 0.2s ease;
        }

        button:active { transform: scale(0.97); }

        .results { width: 100%; max-width: 600px; margin-top: 30px; }

        .results-count {
            color: #7b809a;
            font-size: 0.85rem;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .card {
            background: var(--card-bg);
            padding: 18px;
            border-radius: 12px;
            margin-bottom: 14px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            position: relative;
            overflow: hidden;
        }

        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: var(--gradient-accent);
        }

        .title {
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 6px;
        }

        .title a {
            color: #00f2fe;
            text-decoration: none;
        }

        .title a:hover {
            text-decoration: underline;
            color: #ff416c;
        }

        .url-link {
            font-size: 0.75rem;
            color: #4facfe;
            word-break: break-all;
            margin-bottom: 10px;
            display: block;
        }

        .snippet { font-size: 0.9rem; line-height: 1.4; color: #a0a5c0; }

        .footer { margin-top: auto; padding-top: 30px; font-size: 0.75rem; color: #52566d; }
    </style>
</head>
<body>
    <div class="header">
        <h1 class="brand-title">Télécompagnie</h1>
        <p class="tagline">Le moteur P2P qui vous garde en <span>bonne compagnie</span>.</p>
    </div>

    <form action="/" method="GET">
        <input type="text" name="q" placeholder="Tapez une recherche (ex: Youtube, Linux, Python)..." value="{{ query }}">
        <button type="submit">Chercher</button>
    </form>

    <div class="results">
        {% if query %}
            <div class="results-count">{{ results|length }} résultat(s) trouvé(s) pour "{{ query }}"</div>
            {% for r in results %}
                <div class="card">
                    <div class="title"><a href="{{ r.url }}" target="_blank">{{ r.title }}</a></div>
                    <span class="url-link">{{ r.url }}</span>
                    <div class="snippet">{{ r.snippet }}</div>
                </div>
            {% else %}
                <p style="color: #a0a5c0; text-align: center; margin-top: 20px;">Aucun résultat trouvé pour cette recherche.</p>
            {% endfor %}
        {% else %}
            <p style="color: #52566d; text-align: center; margin-top: 20px;">Entrez un terme pour lancer la recherche Web.</p>
        {% endif %}
    </div>

    <div class="footer">
        Powered by Termux Engine • Télécompagnie Web
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def home():
    q = request.args.get('q', '')
    results = get_web_results(q) if q else []
    return render_template_string(HTML_TEMPLATE, query=q, results=results)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050, debug=False)
