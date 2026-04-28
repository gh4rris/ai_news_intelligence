SELECT
    a.title,
    a.link,
    a.author,
    a.published,
    a.source,
    entity.label AS entity_label,
    entity.text AS entity_text,
    nlp.sentiment,
    nlp.sentiment_score
FROM {{ ref('articles') }} AS a
JOIN {{ source('silver', 'nlp_articles') }} AS nlp
ON a.article_id = nlp.article_id
LATERAL VIEW EXPLODE(nlp.entities) AS entity
WHERE entity.label in ('ORG', 'PERSON', 'PRODUCT')
AND LENGTH(entity.text) > 2