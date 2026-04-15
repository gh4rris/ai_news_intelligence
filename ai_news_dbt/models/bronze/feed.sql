SELECT 
    *
FROM STREAM read_files(
    's3://{{ env_var("AWS_BUCKET") }}/feed',
    format => 'parquet'
)