from crawler.advanced_crawler import start_crawling
import argparse

def main():
    parser = argparse.ArgumentParser(description='Run the EpiSearch advanced crawler')
    parser.add_argument('--url', type=str, default='https://example.com',
                        help='Starting URL for the crawler')
    parser.add_argument('--max-pages', type=int, default=100,
                        help='Maximum number of pages to crawl')
    
    args = parser.parse_args()
    
    print(f"Starting crawler at {args.url} with max_pages={args.max_pages}")
    start_crawling(args.url, args.max_pages)
    print("Crawling complete!")

if __name__ == "__main__":
    main()