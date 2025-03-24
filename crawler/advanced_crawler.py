import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import random
from db.sqlite_db import storePage, init_db
import re
from urllib.robotparser import RobotFileParser
from collections import deque
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='/Users/dalm1/Desktop/reroll/Progra/episearch/crawler.log'
)

# Cache for robots.txt
robots_cache = {}

class AdvancedCrawler:
    def __init__(self, respect_robots=True, delay=1.0, max_retries=3, timeout=10):
        self.visited = set()
        self.respect_robots = respect_robots
        self.delay = delay
        self.max_retries = max_retries
        self.timeout = timeout
        self.user_agent = 'EpiSearchBot/1.0'
        self.headers = {'User-Agent': self.user_agent}
        
        # Initialize database
        init_db()
    
    def get_robots_parser(self, url):
        """Get or create a robots.txt parser for the given URL"""
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        if base_url in robots_cache:
            return robots_cache[base_url]
        
        robots_url = f"{base_url}/robots.txt"
        parser = RobotFileParser(robots_url)
        
        try:
            parser.read()
            robots_cache[base_url] = parser
            return parser
        except Exception as e:
            logging.warning(f"Error reading robots.txt from {robots_url}: {e}")
            # Return a permissive parser if we can't read robots.txt
            empty_parser = RobotFileParser()
            empty_parser.allow_all = True
            robots_cache[base_url] = empty_parser
            return empty_parser
    
    def can_fetch(self, url):
        """Check if the URL can be fetched according to robots.txt"""
        if not self.respect_robots:
            return True
        
        parser = self.get_robots_parser(url)
        return parser.can_fetch(self.user_agent, url)
    
    def normalize_url(self, url):
        """Normalize URL to avoid crawling the same page with different URLs"""
        parsed = urlparse(url)
        # Remove fragments
        url = parsed._replace(fragment='').geturl()
        # Remove trailing slash if present
        if url.endswith('/'):
            url = url[:-1]
        return url
    
    def is_valid_url(self, url):
        """Check if URL is valid and should be crawled"""
        parsed = urlparse(url)
        
        # Check if URL has a scheme and netloc
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # Only crawl HTTP and HTTPS
        if parsed.scheme not in ['http', 'https']:
            return False
        
        # Avoid crawling common non-HTML resources
        extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip', '.tar', 
                     '.gz', '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.css', '.js']
        if any(parsed.path.lower().endswith(ext) for ext in extensions):
            return False
        
        return True
    
    def extract_links(self, soup, base_url):
        """Extract all links from the page"""
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            if not href:
                continue
                
            # Convert relative URL to absolute
            absolute_url = urljoin(base_url, href)
            
            # Normalize and validate URL
            absolute_url = self.normalize_url(absolute_url)
            if self.is_valid_url(absolute_url):
                links.append(absolute_url)
        
        return links
    
    def extract_text_content(self, soup):
        """Extract clean text content from the page"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        
        # Remove blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_keywords(self, soup, content):
        """Extract keywords from the page"""
        keywords = []
        
        # Try to get keywords from meta tags
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            keywords.extend([k.strip() for k in meta_keywords['content'].split(',')])
        
        # Extract title as a keyword
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            keywords.append(title_tag.string.strip())
        
        # Get h1 tags as keywords
        for h1 in soup.find_all('h1'):
            if h1.string:
                keywords.append(h1.string.strip())
        
        # If we still don't have keywords, extract most common words
        if not keywords:
            # Remove common words and punctuation
            words = re.findall(r'\b[a-zA-Z]{3,15}\b', content.lower())
            word_counts = {}
            for word in words:
                if word in word_counts:
                    word_counts[word] += 1
                else:
                    word_counts[word] = 1
            
            # Get top 5 words
            sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
            keywords.extend([word for word, count in sorted_words[:5]])
        
        return keywords
    
    def crawl(self, start_url, max_pages=100):
        """Main crawling method"""
        queue = deque([start_url])
        page_count = 0
        
        while queue and page_count < max_pages:
            url = queue.popleft()
            
            # Skip if already visited
            normalized_url = self.normalize_url(url)
            if normalized_url in self.visited:
                continue
            
            # Check robots.txt
            if not self.can_fetch(normalized_url):
                logging.info(f"Skipping {normalized_url} (disallowed by robots.txt)")
                continue
            
            # Mark as visited
            self.visited.add(normalized_url)
            
            # Respect crawl delay
            time.sleep(self.delay + random.uniform(0, 0.5))
            
            # Fetch the page with retries
            content = None
            html_content = None
            for attempt in range(self.max_retries):
                try:
                    logging.info(f"Crawling {normalized_url} (attempt {attempt+1})")
                    response = requests.get(
                        normalized_url, 
                        headers=self.headers,
                        timeout=self.timeout,
                        allow_redirects=True
                    )
                    
                    if response.status_code == 200:
                        html_content = response.text
                        break
                    elif response.status_code in [403, 404, 410, 500]:
                        # Don't retry for these status codes
                        logging.warning(f"Got status code {response.status_code} for {normalized_url}")
                        break
                    else:
                        # Wait before retrying
                        logging.warning(f"Got status code {response.status_code} for {normalized_url}, retrying...")
                        time.sleep(2 ** attempt)  # Exponential backoff
                except Exception as e:
                    logging.error(f"Error fetching {normalized_url}: {e}")
                    time.sleep(2 ** attempt)  # Exponential backoff
            
            if not html_content:
                continue
            
            # Parse the page
            try:
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract text content
                content = self.extract_text_content(soup)
                
                # Extract keywords
                keywords = self.extract_keywords(soup, content)
                keyword_str = ', '.join(keywords)
                
                # Extract links
                links = self.extract_links(soup, normalized_url)
                
                # Store the page
                storePage(normalized_url, content, keyword_str, links)
                
                # Add new links to the queue
                for link in links:
                    if link not in self.visited:
                        queue.append(link)
                
                page_count += 1
                logging.info(f"Successfully crawled {normalized_url} ({page_count}/{max_pages})")
                
            except Exception as e:
                logging.error(f"Error processing {normalized_url}: {e}")
        
        logging.info(f"Crawling complete. Visited {len(self.visited)} pages.")
        return self.visited

def start_crawling(start_url, max_pages=100):
    """Helper function to start the crawler"""
    crawler = AdvancedCrawler()
    return crawler.crawl(start_url, max_pages)

if __name__ == "__main__":
    # Example usage
    start_crawling("https://example.com", max_pages=50)