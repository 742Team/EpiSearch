from collections import defaultdict
from db.firebase import getAllPages

index = defaultdict(list)

def build_index():
    pages = getAllPages()
    for page in pages:
        words = page['content'].split()
        for word in words:
            index[word].append(page['url'])

def search(query):
    results = index.get(query, [])
    return results
