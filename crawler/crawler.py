import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from db.sqlite_db import storePage

visited = set()

def crawl(url, max_pages=500000):
    to_visit = [url]
    while to_visit and len(visited) < max_pages:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue
        try:
            response = requests.get(current_url)
            if response.status_code != 200:
                continue
            visited.add(current_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraire les liens
            links = []
            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(current_url, link['href'])
                links.append(absolute_url)
                if absolute_url not in visited:
                    to_visit.append(absolute_url)
            
            # Stocker la page avec ses liens
            storePage(current_url, response.text, '', links)
            print(f"Crawled: {current_url}")
        except Exception as e:
            print(f"Error crawling {current_url}: {e}")
