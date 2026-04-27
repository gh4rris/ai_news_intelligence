SELECT *
FROM {{ source('silver', 'sentiment') }}