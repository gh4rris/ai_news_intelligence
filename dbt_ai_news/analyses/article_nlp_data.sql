SELECT a.article_id, a.title, a.link, a.published, a.content, nlp.sentiment, nlp.sentiment_score, nlp.topics, nlp.entities
FROM {{ ref('articles') }} AS a
JOIN {{ source('silver', 'nlp_articles') }} AS nlp
ON a.article_id = nlp.article_id
