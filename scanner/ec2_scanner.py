import boto3
from datetime import datetime, timezone

def scan_stopped_instances(session, account_name):
    """Finds EC2 instances that are stopped but not terminated."""
    ec2 = session.client('ec2')
    response = ec2.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}]
    )

    results = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            name = next(
                (tag['Value'] for tag in instance.get('Tags', [])
                 if tag['Key'] == 'Name'), 'unnamed'
            )
            days_stopped = (datetime.now(timezone.utc) - instance['LaunchTime']).days

            results.append({
                'resource_type': 'stopped_ec2',
                'account': account_name,
                'id': instance['InstanceId'],
                'name': name,
                'instance_type': instance['InstanceType'],
                'days_stopped': days_stopped,
                'estimated_monthly_inr': 415
            })
    return results
