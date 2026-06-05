def scan_unattached_volumes(session, account_name):
    """Finds EBS volumes not attached to any instance."""
    ec2 = session.client('ec2')
    response = ec2.describe_volumes(
        Filters=[{'Name': 'status', 'Values': ['available']}]
    )

    results = []
    for vol in response['Volumes']:
        name = next(
            (t['Value'] for t in vol.get('Tags', []) if t['Key'] == 'Name'), 'unnamed'
        )
        monthly_inr = round(vol['Size'] * 0.08 * 83, 2)

        results.append({
            'resource_type': 'unattached_ebs',
            'account': account_name,
            'id': vol['VolumeId'],
            'name': name,
            'size_gb': vol['Size'],
            'volume_type': vol['VolumeType'],
            'estimated_monthly_inr': monthly_inr
        })
    return results
