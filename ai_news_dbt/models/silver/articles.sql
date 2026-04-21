WITH feed as
(
    SELECT f1.article_id, f1.title, f1.link, f1.author, f1.published_parsed, f1.summary, f1.source, f1.ingested_at
    FROM {{ ref('feed') }} AS f1
    JOIN (
        SELECT article_id, MAX(ingested_at) AS max_ingested
        FROM {{ ref('feed') }}
        GROUP BY article_id
    ) AS f2
    ON f1.article_id = f2.article_id AND f1.ingested_at = f2.max_ingested
),
content as
(
    SELECT c1.article_id, c1.content, c1.ingested_at
    FROM {{ ref('content') }} AS c1
    JOIN (
        SELECT article_id, MAX(ingested_at) AS max_ingested
        FROM {{ ref('content') }}
        GROUP BY article_id
    ) AS c2
    ON c1.article_id = c2.article_id AND c1.ingested_at = c2.max_ingested
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
    INNER JOIN content
    ON feed.article_id = content.article_id
)

SELECT *
FROM articles