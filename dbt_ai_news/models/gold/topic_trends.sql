WITH sentiment_counts AS
(
    SELECT
        CAST(published AS DATE) AS published_date,
        topic,
        sentiment,
        COUNT(*) AS sentiment_count
    FROM {{ ref('int_articles_topics') }}
    GROUP BY CAST(published AS DATE), topic, sentiment
),
sentiment_rank AS
(
    SELECT
        published_date,
        topic,
        sentiment,
        ROW_NUMBER() OVER (PARTITION BY published_date, topic ORDER BY sentiment_count DESC, topic ASC) AS sentiment_row
    FROM sentiment_counts
)

SELECT
    CAST(t.published AS DATE) AS published_date,
    t.topic,
    COUNT(*) AS article_count,
    MAX(sr.sentiment) AS dominant_sentiment
FROM {{ ref('int_articles_topics') }} AS t
LEFT JOIN sentiment_rank AS sr
    ON CAST(t.published AS DATE) = sr.published_date AND t.topic = sr.topic AND sr.sentiment_row = 1
GROUP BY CAST(t.published AS DATE), t.topic
ORDER BY published_date, t.topic