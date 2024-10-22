from crawler.crawler import crawl
from indexing.index import build_index, search
from indexing.reverse_search import reverse_search

def main():
    crawl('https://github.com/', max_pages=20000)
    build_index()
    query = input('Enter search query: ')
    search_results = search(query)
    print('Search Results:', search_results)
    reverse_query = input('Enter content for reverse search: ')
    reverse_results = reverse_search(reverse_query)
    print('Reverse Search Results:', reverse_results)

if __name__ == "__main__":
    main()
