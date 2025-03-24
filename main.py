import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler.crawler import crawl
from indexing.indexing import build_index, search
from indexing.reverse_search import reverse_search
from db.firebase import getPageByContent

print(f'Running {__file__}')

def main():
    crawl('https://youtube.com', max_pages=200)
    build_index()
    query = input('Enter search query: ')
    search_results = getPageByContent(query)
    print('Search Results (sorted by rank):')
    for result in search_results:
        print(f"URL: {result['url']}, Rank: {result['rank']}")
    reverse_query = input('Enter content for reverse search: ')
    reverse_results = reverse_search(reverse_query)
    print('Reverse Search Results:', reverse_results)

if __name__ == "__main__":
    main()
