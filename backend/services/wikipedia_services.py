import requests
from typing import Optional, Dict

class WikipediaService:
    BASE_URL = "https://en.wikipedia.org/wiki/"
    API_URL = "https://en.wikipedia.org/w/api.php"
    
    # Wikipedia requires a User-Agent header
    HEADERS = {
        "User-Agent": "WikiQuizApp/1.0 (Educational Project; Python/requests)"
    }
    
    @staticmethod
    def search_topic(topic: str) -> Optional[str]:
        """Search for a Wikipedia topic and return the best match"""
        params = {
            "action": "opensearch",
            "search": topic,
            "limit": 1,
            "format": "json"
        }
        
        try:
            print(f"Searching Wikipedia for: {topic}")
            response = requests.get(
                WikipediaService.API_URL, 
                params=params, 
                headers=WikipediaService.HEADERS,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            print(f"Search results: {data}")
            
            if data and len(data) > 1 and data[1]:
                found = data[1][0]
                print(f"Found: {found}")
                return found
            
            print("No search results")
            return None
            
        except Exception as e:
            print(f"Error searching Wikipedia: {e}")
            return None
    
    @staticmethod
    def fetch_article_content(topic: str) -> Optional[Dict[str, str]]:
        """Fetch Wikipedia article content"""
        
        # First try to search for the topic
        exact_topic = WikipediaService.search_topic(topic)
        
        # If search fails, use original topic
        if not exact_topic:
            exact_topic = topic
            print(f"Using original topic: {exact_topic}")
        
        params = {
            "action": "query",
            "titles": exact_topic,
            "prop": "extracts",
            "explaintext": True,
            "format": "json",
            "redirects": 1
        }
        
        try:
            print(f"Fetching content for: {exact_topic}")
            response = requests.get(
                WikipediaService.API_URL, 
                params=params, 
                headers=WikipediaService.HEADERS,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            pages = data.get("query", {}).get("pages", {})
            
            if not pages:
                print("No pages in response")
                return None
            
            page_id = list(pages.keys())[0]
            
            if page_id == "-1":
                print(f"Article not found (page_id = -1)")
                return None
            
            page = pages[page_id]
            content = page.get("extract", "")
            title = page.get("title", exact_topic)
            
            if not content or len(content) < 100:
                print(f"Content too short: {len(content)} chars")
                return None
            
            # Limit content to 3000 chars
            if len(content) > 3000:
                content = content[:3000] + "..."
            
            print(f"Successfully fetched: {title} ({len(content)} chars)")
            
            return {
                "title": title,
                "content": content,
                "url": f"{WikipediaService.BASE_URL}{title.replace(' ', '_')}"
            }
            
        except Exception as e:
            print(f"Error fetching content: {e}")
            return None