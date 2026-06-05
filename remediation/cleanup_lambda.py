# remediation/cleanup_lambda.py
import boto3
import json

def cleanup_approved_resources(findings):
    """
    Deletes resources that were approved via GitHub Issue label.
    Only call this after human approval is confirmed.
    """
    ec2 = boto3.client('ec2', region_name='ap-south-1')
    deleted = []
    errors = []

    for resource in findings:
        resource_type = resource['resource_type']
        resource_id = resource['id']

        try:
            if resource_type == 'stopped_ec2':
                ec2.terminate_instances(InstanceIds=[resource_id])
                deleted.append(f"Terminated EC2: {resource_id}")
                print(f"  ✅ Terminated EC2 instance: {resource_id}")

            elif resource_type == 'unattached_ebs':
                ec2.delete_volume(VolumeId=resource_id)
                deleted.append(f"Deleted EBS: {resource_id}")
                print(f"  ✅ Deleted EBS volume: {resource_id}")

            elif resource_type == 'idle_eip':
                ec2.release_address(AllocationId=resource_id)
                deleted.append(f"Released EIP: {resource_id}")
                print(f"  ✅ Released Elastic IP: {resource_id}")

            elif resource_type == 'old_snapshot':
                ec2.delete_snapshot(SnapshotId=resource_id)
                deleted.append(f"Deleted Snapshot: {resource_id}")
                print(f"  ✅ Deleted snapshot: {resource_id}")

        except Exception as e:
            error_msg = f"Failed to delete {resource_type} {resource_id}: {e}"
            errors.append(error_msg)
            print(f"  ❌ {error_msg}")

    return {
        'deleted': deleted,
        'errors': errors,
        'total_deleted': len(deleted),
        'total_errors': len(errors)
    }


def lambda_handler(event=None, context=None):
    """
    Entry point when triggered by GitHub webhook after approval label is added.
    Reads findings.json and cleans up all listed resources.
    """
    print("CloudWise Cleanup Lambda started")

    try:
        with open('findings.json', 'r') as f:
            data = json.load(f)
        findings = data.get('findings', [])
    except FileNotFoundError:
        print("findings.json not found — run scanner first")
        return {'statusCode': 404, 'body': 'No findings file'}

    if not findings:
        print("No findings to clean up")
        return {'statusCode': 200, 'body': 'Nothing to clean up'}

    print(f"Found {len(findings)} resources to clean up...")
    result = cleanup_approved_resources(findings)

    print(f"\nCleanup complete:")
    print(f"  Deleted: {result['total_deleted']} resources")
    print(f"  Errors:  {result['total_errors']} resources")

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
