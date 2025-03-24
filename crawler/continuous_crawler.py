import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
from db.firebase import storePage

visited_urls = set()

def crawl(url, max_depth=3):
    if url in visited_urls or max_depth == 0:
        return
    try:
        response = requests.get(url)
        if response.status_code == 200:
            visited_urls.add(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.get_text()
            storePage(url, content)
            print(f"Exploring {url}, depth {max_depth}")

            for link in soup.find_all('a', href=True):
                absolute_link = urljoin(url, link['href'])
                crawl(absolute_link, max_depth - 1)
        else:
            print(f"Failed to fetch {url}")
    except Exception as e:
        print(f"Error crawling {url}: {e}")

def continuous_crawl(start_url, delay=60):
    while True:
        crawl(start_url)
        print(f"Sleeping for {delay} seconds before next crawl...")
        time.sleep(delay)
