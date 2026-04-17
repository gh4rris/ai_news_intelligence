WITH feed as
(
    SELECT article_id, title, link, author, published_parsed, summary, source, ingested_at
    FROM {{ ref('feed') }}
),
content as
(
    SELECT article_id, content, ingested_at
    FROM {{ ref('content') }}
),
articles as
(
    SELECT
        feed.article_id,
        feed.title,
        feed.link,
        feed.author,
        feed.published_parsed AS published,
        feed.summary,
        feed.source,
        feed.ingested_at AS feed_ingestion,
        content.content,
        content.ingested_at AS content_ingestion
    FROM feed
    JOIN content
    ON feed.article_id = content.article_id
)

SELECT *
FROM articles