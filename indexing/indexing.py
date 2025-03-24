from db.sqlite_db import storePage, getAllPages
from .ranking import calculate_rank

def build_index():
    pages = getAllPages()
    for page in pages:
        url = page['url']
        content = page['content']
        keyword = page.get('keyword', '')
        links = page.get('links', [])
        storePage(url, content, keyword, links)

def search(query):
    results = []
    try:
        docs = getAllPages()
        for doc in docs:
            content = doc.get('content', '')
            url = doc.get('url', '')
            links = doc.get('links', [])
            rank = calculate_rank(content, query, links)
            if rank > 0:
                results.append({
                    'url': url,
                    'content': content,
                    'rank': rank
                })
        results = sorted(results, key=lambda x: x['rank'], reverse=True)
    except Exception as e:
        print(f"Erreur lors de la recherche des pages : {e}")
    return results
