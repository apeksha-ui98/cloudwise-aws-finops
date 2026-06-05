def scan_empty_buckets(session, account_name):
    """Finds S3 buckets with zero objects."""
    s3 = session.client('s3')
    buckets = s3.list_buckets()['Buckets']

    results = []
    for bucket in buckets:
        try:
            obj = s3.list_objects_v2(Bucket=bucket['Name'], MaxKeys=1)
            if obj['KeyCount'] == 0:
                results.append({
                    'resource_type': 'empty_s3_bucket',
                    'account': account_name,
                    'id': bucket['Name'],
                    'name': bucket['Name'],
                    'estimated_monthly_inr': 0
                })
        except Exception:
            pass
    return results
