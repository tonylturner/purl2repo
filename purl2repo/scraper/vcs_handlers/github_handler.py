import requests
from bs4 import BeautifulSoup

class GitHubHandler:
    @staticmethod
    def extract_vcs_links(url):
        """Scrapes a GitHub page for repository links."""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            links = []

            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href'].lower()
                if 'github.com' in href:
                    links.append(href)

            return links

        except requests.RequestException as e:
            print(f"Error scraping GitHub: {e}")
            return []
