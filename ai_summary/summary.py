# ai_summary/summary.py
import json

def generate_ai_summary(findings_data: dict) -> str:
    findings = findings_data.get('findings', [])
    total_monthly = findings_data.get('total_monthly_inr', 0)
    total_annual = findings_data.get('total_annual_inr', 0)

    # Count resource types
    stopped_ec2 = [f for f in findings if f['resource_type'] == 'stopped_ec2']
    unattached_ebs = [f for f in findings if f['resource_type'] == 'unattached_ebs']
    idle_eips = [f for f in findings if f['resource_type'] == 'idle_eip']

    summary = f"""☁️ CloudWise AI Analysis:

Your AWS environment has {len(findings)} idle resources wasting ₹{round(total_monthly, 2)}/month (₹{round(total_annual, 2)}/year).

Immediate actions:
- Terminate {len(stopped_ec2)} stopped EC2 instance(s) — these are your biggest cost at ₹415/month each with zero business value while stopped
- Release {len(idle_eips)} unassociated Elastic IP(s) — charging ₹299/month for an unused IP address
- Delete {len(unattached_ebs)} unattached EBS volume(s) — orphaned storage with no instance attached

Fixing all flagged resources will save approximately ₹{round(total_annual, 2)} annually."""

    return summary
