from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os 

load_dotenv()
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
if not FIRECRAWL_API_KEY:
    raise ValueError("FIRECRAWL_API_KEY environment variable not set.")

firecrawl_client = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    
    
def get_article_content_from_url(url: str) -> str:
    """
    Fetches the main content of a given URL. 
    Use this to read an article from a link.
    Returns the clean text content of the page.
    """
    try:
        # 'scrape' gets the clean, LLM-ready markdown content
        scraped_data = firecrawl_client.scrape(url=url)
        return scraped_data
        # # Return just the text content
        # if 'content' in scraped_data:
        #     return scraped_data['content']
        # else:
        #     return "Error: Could not find 'content' in scrape result."
            
    except Exception as e:
        print(f"Error fetching article: {e}")
        return f"Error: Failed to fetch or process the URL. {e}"

