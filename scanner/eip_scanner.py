def scan_idle_elastic_ips(session, account_name):
    """Finds Elastic IPs not associated with a running instance."""
    ec2 = session.client('ec2')
    response = ec2.describe_addresses()

    results = []
    for addr in response['Addresses']:
        if 'AssociationId' not in addr:
            results.append({
                'resource_type': 'idle_eip',
                'account': account_name,
                'id': addr['AllocationId'],
                'ip_address': addr['PublicIp'],
                'estimated_monthly_inr': 299
            })
    return results
