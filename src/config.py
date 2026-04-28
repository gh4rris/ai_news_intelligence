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

# databricks
DATABRICKS_CATALOG = os.getenv("DATABRICKS_CATALOG")

# nlp
SENTIMENT_MODEL = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
ENTITY_EXTRACTOR_MODEL = "en_core_web_sm"
TOPIC_KEYWORDS = {
    "Machine Learning": ["machine learning", "ml", "neural network", "deep learning", "training data", "model training", "supervised", "unsupervised", "classification", "regression"],
    "Generative AI": ["generative", "gpt", "llm", "chatgpt", "openai", "claude", "anthropic", "gemini"],
    "Robotics": ["robot", "robotics", "automation", "drone", "sensor", "physical ai", "embodied ai"],
    "AI Ethics & Safety": ["regulation", "government", "policy", "ethics", "safety", "transparency", "governance", "privacy", "legislature", "legislative"],
    "AI Research": ["research", "paper", "study", "experiment", "benchmark", "peer review"],
    "AI in Business": ["business", "enterprise", "startup", "funding", "venture", "revenue", "productivity", "automation", "ceo", "deal", "equity"],
    "Natural Language Processing": ["nlp", "natural language", "text processing", "sentiment", "tokenization", "embedding", "speech recognition"],
    "Computer Vision": ["computer vision", "image recognition", "object detection", "facial recognition", "image processing", "segmentation", "recognition"]
}
KEYWORD_THRESHOLD = 3