from models.raw_data import RawData

import feedparser as fp


RSS_FEED = {"TechCrunch": "https://techcrunch.com/category/artificial-intelligence/feed"}

def fetch_articles():
    articles = []

    for source_name, url in RSS_FEED.items():
        feed = fp.parse(url)

        for entry in feed["entries"]:
            article_url = entry.get("url")
            if article_url:
                article = RawData(
                    article_id=article_url,
                    title=entry.get("title"),
                    url=article_url,
                    source_name=source_name,
                    author=entry.get("author"),
                    summary=entry.get("summary"),
                    published_at=entry.get("published_parsed"),
                    content=entry.get("summary")
                )
            articles.append(article)

    return articles

def deduplicate_articles():
    print("Deduplicating articles...")


fetch_articles()