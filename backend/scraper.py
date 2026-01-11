import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re

class WikipediaScraper:
    def __init__(self, url: str):
        self.url = url
        self.soup = None
        self.title = ""
        self.content = ""
        
    def validate_url(self) -> bool:
        """Validate if URL is a Wikipedia article"""
        pattern = r'https?://[a-z]{2,3}\.wikipedia\.org/wiki/.+'
        return bool(re.match(pattern, self.url))
    
    def fetch_page(self) -> bool:
        """Fetch the Wikipedia page"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.content, 'html.parser')
            return True
        except Exception as e:
            print(f"Error fetching page: {e}")
            return False
    
    def extract_title(self) -> str:
        """Extract article title"""
        try:
            title_tag = self.soup.find('h1', class_='firstHeading')
            if title_tag:
                self.title = title_tag.get_text().strip()
            return self.title
        except Exception as e:
            print(f"Error extracting title: {e}")
            return ""
    
    def extract_summary(self) -> str:
        """Extract first few paragraphs as summary"""
        try:
            content_div = self.soup.find('div', class_='mw-parser-output')
            if not content_div:
                return ""
            
            paragraphs = []
            for element in content_div.find_all(['p'], limit=5):
                text = element.get_text().strip()
                # Skip empty paragraphs or coordinate paragraphs
                if text and len(text) > 50 and not text.startswith('Coordinates:'):
                    paragraphs.append(text)
            
            summary = ' '.join(paragraphs[:2])  # First 2 substantial paragraphs
            return self._clean_text(summary)
        except Exception as e:
            print(f"Error extracting summary: {e}")
            return ""
    
    def extract_content(self) -> str:
        """Extract main article content"""
        try:
            content_div = self.soup.find('div', class_='mw-parser-output')
            if not content_div:
                return ""
            
            # Remove unwanted elements
            for element in content_div.find_all(['table', 'figure', 'style', 'script', 'sup']):
                element.decompose()
            
            paragraphs = []
            for p in content_div.find_all('p'):
                text = p.get_text().strip()
                if text and len(text) > 30:
                    paragraphs.append(text)
            
            self.content = ' '.join(paragraphs)
            return self._clean_text(self.content)
        except Exception as e:
            print(f"Error extracting content: {e}")
            return ""
    
    def extract_sections(self) -> List[str]:
        """Extract section headings"""
        try:
            sections = []
            for heading in self.soup.find_all(['h2', 'h3']):
                headline = heading.find('span', class_='mw-headline')
                if headline:
                    section_text = headline.get_text().strip()
                    # Skip common navigation sections
                    if section_text not in ['Contents', 'See also', 'References', 'External links', 'Notes', 'Bibliography']:
                        sections.append(section_text)
            return sections[:10]  # Limit to first 10 sections
        except Exception as e:
            print(f"Error extracting sections: {e}")
            return []
    
    def extract_entities(self) -> Dict[str, List[str]]:
        """Extract key entities (simple implementation)"""
        try:
            entities = {
                'people': [],
                'organizations': [],
                'locations': []
            }
            
            # Find all links in the content
            content_div = self.soup.find('div', class_='mw-parser-output')
            if content_div:
                links = content_div.find_all('a', href=True, limit=100)
                
                seen = set()
                
                for link in links:
                    href = link.get('href', '')
                    text = link.get_text().strip()
                    
                    # Simple heuristic: categorize based on common patterns
                    if '/wiki/' in href and text and len(text) > 2 and text not in seen:
                        # Skip file links, help pages, etc.
                        if not any(x in href for x in ['File:', 'Help:', 'Category:', 'Wikipedia:', 'Template:', 'Special:']):
                            seen.add(text)
                            
                            # Simple categorization (can be improved with NER)
                            if len(entities['people']) < 5:
                                entities['people'].append(text)
                            elif len(entities['organizations']) < 5:
                                entities['organizations'].append(text)
                            elif len(entities['locations']) < 5:
                                entities['locations'].append(text)
            
            return entities
        except Exception as e:
            print(f"Error extracting entities: {e}")
            return {'people': [], 'organizations': [], 'locations': []}
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove citation brackets like [1], [2], etc.
        text = re.sub(r'\[\d+\]', '', text)
        # Remove reference markers like [citation needed]
        text = re.sub(r'\[.*?\]', '', text)
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove newlines
        text = text.replace('\n', ' ')
        return text.strip()
    
    def scrape(self) -> Optional[Dict]:
        """Main scraping method"""
        if not self.validate_url():
            raise ValueError("Invalid Wikipedia URL")
        
        if not self.fetch_page():
            raise Exception("Failed to fetch Wikipedia page")
        
        return {
            'title': self.extract_title(),
            'summary': self.extract_summary(),
            'content': self.extract_content(),
            'sections': self.extract_sections(),
            'key_entities': self.extract_entities()
        }


# Test function
def test_scraper():
    """Test the scraper with a sample Wikipedia URL"""
    url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    scraper = WikipediaScraper(url)
    
    try:
        data = scraper.scrape()
        print("="*50)
        print("Title:", data['title'])
        print("\nSummary:", data['summary'][:300], "...")
        print("\nSections:", data['sections'])
        print("\nEntities:", data['key_entities'])
        print("\nContent length:", len(data['content']), "characters")
        print("="*50)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_scraper()