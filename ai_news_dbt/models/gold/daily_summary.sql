WITH source_counts AS
(
    SELECT
        CAST(published AS DATE) AS published_date,
        source,
        COUNT(*) AS source_count
    FROM {{ ref('articles') }}
    GROUP BY published_date, source
),
topic_counts AS
(
    SELECT
        CAST(published AS DATE) AS published_date,
        topic,
        COUNT(*) AS topic_count
    FROM {{ ref('int_articles_topics') }}
    GROUP BY published_date, topic
),
entity_counts AS
(
    SELECT
        CAST(published AS DATE) AS published_date,
        entity_label,
        entity_text,
        COUNT(*) AS entity_count
    FROM {{ ref('int_articles_entities') }}
    GROUP BY published_date, entity_label, entity_text
),
source_rank AS
(
    SELECT
        published_date,
        source,
        ROW_NUMBER() OVER (PARTITION BY published_date ORDER BY source_count DESC, source ASC) AS source_row
    FROM source_counts
),
topic_rank AS(
    SELECT
        published_date,
        topic,
        ROW_NUMBER() OVER (PARTITION BY published_date ORDER BY topic_count DESC, topic ASC) AS topic_row
    FROM topic_counts
),
entity_rank AS
(
    SELECT
        published_date,
        entity_label,
        entity_text,
        ROW_NUMBER() OVER (PARTITION BY published_date ORDER BY entity_count DESC, entity_text ASC) AS entity_row
    FROM entity_counts
)

SELECT
    CAST(t.published AS DATE) AS published_date,
    COUNT(DISTINCT t.article_id) AS total_articles,
    ROUND(SUM(CASE WHEN t.sentiment = 'POSITIVE' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS pct_positive,
    ROUND(SUM(CASE WHEN t.sentiment = 'NEGATIVE' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS pct_negative,
    MAX(sr.source) AS most_active_source,
    MAX(tr.topic) AS top_topic,
    MAX(er.entity_label) AS top_entity_label,
    MAX(er.entity_text) AS top_entity_text
FROM {{ ref('int_articles_topics') }} AS t
LEFT JOIN source_rank AS sr
    ON CAST(t.published AS DATE) = sr.published_date AND sr.source_row = 1
LEFT JOIN topic_rank AS tr
    ON CAST(t.published AS DATE) = tr.published_date AND tr.topic_row = 1
LEFT JOIN entity_rank AS er
    ON CAST(t.published AS DATE) = er.published_date AND er.entity_row = 1
GROUP BY CAST(t.published AS DATE)