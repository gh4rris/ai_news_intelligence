import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


# paths
ROOT_PATH = Path(__file__).parent.parent
DATA_PATH = ROOT_PATH / "data"
FEED_PATH = DATA_PATH / "feed"
CONTENT_PATH = DATA_PATH / "content"

# article scraper
RSS_FEED = {
    "TechCrunch": "https://techcrunch.com/category/artificial-intelligence/feed"
}
MAX_CONCURRENT = 10
REQUEST_TIMEOUT = 10

# cloud
AWS_BUCKET = os.getenv("AWS_BUCKET")

# nlp
SENTIMENT_MODEL = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
ENTITY_EXTRACTOR_MODEL = "en_core_web_sm"
TOPIC_KEYWORDS = {
    "LLMs": ["gpt", "llm", "chatgpt", "openai"],
    "Robotics": ["robot", "automation"],
    "AI Policy": ["regulation", "government", "policy"],
    "Startups": ["startup", "funding", "venture"]
}