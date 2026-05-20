SELECT *
FROM {{ source('silver', 'nlp_articles') }}