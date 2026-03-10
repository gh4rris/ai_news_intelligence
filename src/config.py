import os
from dotenv import load_dotenv

load_dotenv()

# database
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
DB_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres:5432/{POSTGRES_DB}"

# article scraper
RSS_FEED = {
    "TechCrunch": "https://techcrunch.com/category/artificial-intelligence/feed"
}
MAX_CONCURRENT = 10
REQUEST_TIMEOUT = 10