SELECT
    *
FROM read_files(
    '{{ env_var("AWS_BUCKET") }}/feed',
    format => 'parquet'
    )