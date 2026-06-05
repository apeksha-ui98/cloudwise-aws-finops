# cloudwatch/metrics.py
import boto3
from datetime import datetime

def publish_metrics(session, findings, total_monthly_inr):
    """
    Publishes scan results as custom metrics to CloudWatch.
    """
    cw = session.client('cloudwatch', region_name='ap-south-1')

    # Count by resource type
    stopped_ec2 = len([f for f in findings if f['resource_type'] == 'stopped_ec2'])
    unattached_ebs = len([f for f in findings if f['resource_type'] == 'unattached_ebs'])
    idle_eips = len([f for f in findings if f['resource_type'] == 'idle_eip'])
    old_snapshots = len([f for f in findings if f['resource_type'] == 'old_snapshot'])

    metrics = [
        {'MetricName': 'IdleEC2Count',         'Value': stopped_ec2},
        {'MetricName': 'UnattachedEBSCount',   'Value': unattached_ebs},
        {'MetricName': 'IdleEIPCount',         'Value': idle_eips},
        {'MetricName': 'OldSnapshotCount',     'Value': old_snapshots},
        {'MetricName': 'TotalFindingsCount',   'Value': len(findings)},
        {'MetricName': 'TotalMonthlyWasteINR', 'Value': total_monthly_inr},
    ]

    try:
        cw.put_metric_data(
            Namespace='CloudWise/CostOptimization',
            MetricData=[
                {
                    'MetricName': m['MetricName'],
                    'Value': m['Value'],
                    'Unit': 'Count' if 'INR' not in m['MetricName'] else 'None',
                    'Timestamp': datetime.utcnow()
                }
                for m in metrics
            ]
        )
        print("  CloudWatch metrics published successfully")
    except Exception as e:
        print(f"  Could not publish CloudWatch metrics: {e}")
