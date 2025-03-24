from flask import Flask, request, jsonify, send_file
from indexing.indexing import search as getRankedPages
from db.sqlite_db import getAllPages, init_db
import os

app = Flask(__name__)

init_db()

@app.route('/')
def index():
    return send_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html'))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if query:
        results = getRankedPages(query)
        return jsonify(results)
    return jsonify({"error": "No query provided"}), 400

@app.route('/debug', methods=['GET'])
def debug():
    """Route de débogage pour vérifier les pages stockées en base de données"""
    try:
        pages = getAllPages()
        return jsonify({
            "total_pages": len(pages),
            "sample": pages[:5] if len(pages) > 0 else []
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/start-crawler', methods=['GET'])
def start_crawler():
    """Démarre le crawler avancé en arrière-plan"""
    url = request.args.get('url', 'https://stackoverflow.com/')
    max_pages = int(request.args.get('max_pages', 500))

    def run_crawler():
        start_crawling(url, max_pages)

    thread = threading.Thread(target=run_crawler)
    thread.daemon = True
    thread.start()

    return jsonify({
        "message": f"Advanced crawler started for {url} with max_pages={max_pages}",
        "status": "running"
    })

@app.route('/build-index', methods=['GET'])
def build_index_route():
    """Construit l'index à partir des pages en base de données"""
    from indexing.indexing import build_index
    try:
        build_index()
        return jsonify({"message": "Index built successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
