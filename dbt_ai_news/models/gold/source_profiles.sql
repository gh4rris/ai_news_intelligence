WITH word_count AS
(
    SELECT 
        article_id, 
        LENGTH(content) - LENGTH(REPLACE(content, ' ', '')) + 1 AS word_count
    FROM {{ ref('articles') }}
),
sentiment_counts AS
(
    SELECT 
        CAST(a.published AS DATE) AS published_date,
        a.source,
        nlp.sentiment,
        COUNT(*) AS sentiment_count
    FROM {{ ref('articles') }} AS a
    INNER JOIN {{ source('silver', 'nlp_articles') }} AS nlp
    ON a.article_id = nlp.article_id
    GROUP BY CAST(a.published AS DATE), a.source, nlp.sentiment
),
source_rank AS
(
    SELECT
        published_date,
        source,
        sentiment,
        ROW_NUMBER() OVER (PARTITION BY published_date, source ORDER BY sentiment_count DESC, source ASC) AS sentiment_row
    FROM sentiment_counts
)

SELECT 
    CAST(a.published AS DATE) AS published_date,
    a.source,
    COUNT(*) AS article_count,
    ROUND(SUM(wc.word_count) / COUNT(*), 2) AS avg_word_count,
    MAX(sr.sentiment) AS dominant_sentiment
FROM {{ ref('articles') }} AS a
INNER JOIN word_count AS wc
ON  a.article_id = wc.article_id
LEFT JOIN source_rank AS sr
ON CAST(a.published AS DATE) = sr.published_date AND a.source = sr.source AND sr.sentiment_row = 1
GROUP BY CAST(a.published AS DATE), a.source