SELECT
    a.article_id,
    a.title,
    a.link,
    a.author,
    a.published,
    a.source,
    EXPLODE(nlp.topics) AS topic,
    nlp.sentiment,
    nlp.sentiment_score
FROM {{ ref('articles') }} AS a
JOIN {{ source('silver', 'nlp_articles') }} AS nlp
ON a.article_id = nlp.article_id