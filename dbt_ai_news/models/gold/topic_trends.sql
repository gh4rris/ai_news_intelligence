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
),
topic_counts AS
(
	SELECT
		CAST(t.published AS DATE) AS published_date,
		t.topic,
		COUNT(*) AS article_count,
		MAX(sr.sentiment) AS dominant_sentiment
	FROM {{ ref('int_articles_topics') }} AS t
	LEFT JOIN sentiment_rank AS sr
	ON CAST(t.published AS DATE) = sr.published_date AND t.topic = sr.topic AND sr.sentiment_row = 1
	GROUP BY CAST(t.published AS DATE), t.topic
),
week_avg AS
(
	SELECT
		tc.published_date,
		tc.topic,
		tc.article_count,
		SUM(tc.article_count) OVER (PARTITION BY tc.topic ORDER BY tc.published_date ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING) / 7 AS prev_7d_avg_articles,
		tc.dominant_sentiment
	FROM topic_counts AS tc
)

SELECT
	wa.published_date,
	wa.topic,
	wa.article_count,
	CASE WHEN CAST(wa.published_date AS DATE) < DATEADD(DAY, 1, MIN(wa.published_date) OVER ()) THEN NULL
	ELSE ROUND(wa.prev_7d_avg_articles, 2) END AS prev_7d_avg_articles,
	CASE WHEN CAST(wa.published_date AS DATE) < DATEADD(DAY, 1, MIN(wa.published_date) OVER ()) THEN NULL
	ELSE ROUND((wa.article_count - wa.prev_7d_avg_articles) / NULLIF(wa.prev_7d_avg_articles, 0), 2) END AS momentum,
	wa.dominant_sentiment
FROM  week_avg AS wa
ORDER BY wa.published_date, wa.topic

