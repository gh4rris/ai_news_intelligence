import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


# paths
ROOT_PATH = Path(__file__).parent.parent
DATA_PATH = ROOT_PATH / "data"
FEED_PATH = DATA_PATH / "feed"
CONTENT_PATH = DATA_PATH / "content"

# dbt
DBT_PATH = os.getenv("DBT_PATH")
DBT_IMAGE = "dbt_ai_news:latest"
DBT_WORK_DIR = "/dbt_ai_news"

# docker
DOCKER_URL = "unix://var/run/docker.sock"

# article scraper
RSS_FEED = {
    "TechCrunch": "https://techcrunch.com/category/artificial-intelligence/feed",
    "The Verge": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "Wired": "https://www.wired.com/feed/tag/ai/latest/rss",
    "VentureBeat":"https://venturebeat.com/category/ai/feed/"
}
MAX_CONCURRENT = 10
REQUEST_TIMEOUT = 10

# cloud
AWS_BUCKET = os.getenv("AWS_BUCKET")

# databricks
DATABRICKS_CATALOG = os.getenv("DATABRICKS_CATALOG")

# nlp
SENTIMENT_MODEL = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
ENTITY_EXTRACTOR_MODEL = "en_core_web_sm"
HF_TOKEN = os.getenv("HF_TOKEN")
TOPIC_KEYWORDS = {
    "Machine Learning": ["machine learning", "ml", "neural network", "deep learning", "training data", "model training", "supervised", "unsupervised", "classification", "regression"],
    "Generative AI": ["generative", "gpt", "llm", "llms", "chatgpt", "openai", "claude", "anthropic", "gemini"],
    "Robotics": ["robot", "robotics", "automation", "drone", "sensor", "physical ai", "embodied ai"],
    "Ethics & Safety": ["regulation", "government", "policy", "ethics", "safety", "transparency", "governance", "privacy", "legislature", "legislative"],
    "AI Research": ["research", "paper", "study", "experiment", "benchmark", "peer review"],
    "AI in Business": ["business", "enterprise", "startup", "funding", "venture", "revenue", "productivity", "automation", "ceo", "deal", "equity"],
    "Politics & Economy": ["economy", "economic", "economics", "gdp", "inflation", "tax", "investors", "government", "democrats", "republicans"],
    "Art & Design": ["art", "music", "instruments", "singing", "portrait", "painting"],
    "ecommerce": ["ecommerce", "online shopping", "online purchase", "shopping app", "amazon"],
    "Natural Language Processing": ["nlp", "natural language", "text processing", "sentiment", "tokenization", "embedding", "speech recognition"],
    "Computer Vision": ["computer vision", "image recognition", "object detection", "facial recognition", "image processing", "segmentation"],
    "Data Centers": ["data center", "data centers", "ai infrastructure", "data infrastructure", "cloud computing", "ai chips", "gpus"]
}
KEYWORD_THRESHOLD = 3
