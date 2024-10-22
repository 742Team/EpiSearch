import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler.crawler import crawl
from indexing.indexing import build_index, search
from indexing.reverse_serach import reverse_search

def main():
    crawl('https://github.com', max_pages=20)
    build_index()
    query = input('Enter search query: ')
    search_results = search(query)
    print('Search Results:', search_results)
    reverse_query = input('Enter content for reverse search: ')
    reverse_results = reverse_search(reverse_query)
    print('Reverse Search Results:', reverse_results)

if __name__ == "__main__":
    main()
