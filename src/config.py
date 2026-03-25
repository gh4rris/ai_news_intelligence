import os
import sys
from dotenv import load_dotenv

load_dotenv()


# paths
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PATH = os.path.join(ROOT_PATH, "src")

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# database
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
APP_DB = os.getenv("APP_DB")
DB_URL = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{APP_DB}"

# article scraper
RSS_FEED = {
    "TechCrunch": "https://techcrunch.com/category/artificial-intelligence/feed"
}
MAX_CONCURRENT = 10
REQUEST_TIMEOUT = 10

# nlp
SENTIMENT_MODEL = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
ENTITY_EXTRACTOR_MODEL = "en_core_web_sm"
TOPIC_KEYWORDS = {
    "LLMs": ["gpt", "llm", "chatgpt", "openai"],
    "Robotics": ["robot", "automation"],
    "AI Policy": ["regulation", "government", "policy"],
    "Startups": ["startup", "funding", "venture"]
}