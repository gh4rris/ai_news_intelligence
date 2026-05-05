WITH sentiment_counts AS
(
    SELECT
        CAST(published AS DATE) AS published_date,
        entity_label,
        entity_text,
        sentiment,
        COUNT(*) AS sentiment_count
    FROM {{ ref('int_articles_entities') }}
    GROUP BY CAST(published AS DATE), entity_label, entity_text, sentiment
),
sentiment_rank
(
    SELECT
        published_date,
        entity_label,
        entity_text,
        sentiment,
        ROW_NUMBER() OVER (PARTITION BY published_date, entity_label, entity_text ORDER BY sentiment_count DESC, entity_text ASC) AS sentiment_row
    FROM sentiment_counts
)

SELECT
    CAST(e.published AS DATE) AS published_date,
    e.entity_label,
    e.entity_text,
    COUNT(*) AS article_count,
    MAX(sr.sentiment) AS dominant_sentiment
FROM {{ ref('int_articles_entities') }} AS e
LEFT JOIN sentiment_rank AS sr
    ON CAST(e.published AS DATE) = sr.published_date AND e.entity_label = sr.entity_label AND e.entity_text = sr.entity_text
GROUP BY CAST(e.published AS DATE), e.entity_label, e.entity_text
ORDER BY published_date, e.entity_label, e.entity_text