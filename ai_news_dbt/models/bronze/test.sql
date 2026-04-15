SELECT 
    *
FROM read_files(
    's3://{{ env_var("AWS_BUCKET") }}/test/test_time.parquet',
    format => 'parquet'
)