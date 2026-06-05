from datetime import datetime, timezone, timedelta

def scan_old_snapshots(session, account_name, days_threshold=90):
    """Finds EBS snapshots older than threshold days."""
    ec2 = session.client('ec2')
    sts = session.client('sts')
    account_id = sts.get_caller_identity()['Account']

    response = ec2.describe_snapshots(OwnerIds=[account_id])
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_threshold)

    results = []
    for snap in response['Snapshots']:
        if snap['StartTime'] < cutoff:
            monthly_inr = round(snap['VolumeSize'] * 0.05 * 83, 2)
            results.append({
                'resource_type': 'old_snapshot',
                'account': account_name,
                'id': snap['SnapshotId'],
                'size_gb': snap['VolumeSize'],
                'age_days': (datetime.now(timezone.utc) - snap['StartTime']).days,
                'estimated_monthly_inr': monthly_inr
            })
    return results
