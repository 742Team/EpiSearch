import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from db.firebase import storePage

visited = set()

def crawl(url, max_pages=10):
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
            storePage(current_url, response.text)
            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(current_url, link['href'])
                if absolute_url not in visited:
                    to_visit.append(absolute_url)
        except Exception as e:
            pass
