# CloudWise — AWS FinOps & Cost Optimisation Tool

A serverless AWS cost-optimisation tool that scans multiple AWS accounts for idle and wasted resources, calculates estimated monthly savings in **INR**, generates an **AI-written executive summary**, raises a **GitHub Issue** for human approval, and publishes custom metrics to **CloudWatch dashboards**. The scanner runs as an **AWS Lambda function** on a weekly schedule via EventBridge, provisioned entirely with **Terraform**.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11 |
| Compute | AWS Lambda |
| AWS SDK | Boto3 |
| Infrastructure | Terraform |
| Monitoring | AWS CloudWatch |
| Notifications | GitHub Issues API |

## What It Scans

| Scanner | Resource | Estimated Cost |
|---------|----------|---------------|
| ec2_scanner | Stopped EC2 instances | ~INR 415/month per instance |
| ebs_scanner | Unattached EBS volumes | Based on volume size |
| eip_scanner | Idle Elastic IPs | ~INR 299/month per EIP |
| snapshot_scanner | Old EBS snapshots | Based on snapshot size |
| s3_scanner | Empty S3 buckets | Flagged for hygiene |

## How It Works

1. **Multi-account scanning** — assumes IAM roles in each target account via STS for cross-account access
2. **Cost Explorer integration** — fetches real spend data from AWS Cost Explorer for the last 30 days
3. **AI Summary** — generates a human-readable executive summary highlighting top waste areas and recommended actions
4. **GitHub Issue creation** — posts findings as a GitHub Issue so a human can review and approve remediation
5. **CloudWatch metrics** — publishes custom metrics (`waste_count`, `total_waste_inr`) for dashboarding and alerting
6. **Automated scheduling** — EventBridge cron triggers Lambda every Monday at 9am UTC

## Project Structure
cloudwise-aws-finops/

├── lambda_handler.py           # Main Lambda entry point

├── multi_account.py            # Account list & STS session helper


├── scanner/

│   ├── ec2_scanner.py          # Stopped instance detection

│   ├── ebs_scanner.py          # Unattached volume detection

│   ├── eip_scanner.py          # Idle Elastic IP detection

│   ├── snapshot_scanner.py     # Old snapshot detection

│   └── s3_scanner.py           # Empty bucket detection

├── cost_explorer/

│   └── real_costs.py           # AWS Cost Explorer integration

├── ai_summary/

│   └── summary.py              # AI-generated cost report

├── notifications/

│   └── github_issue.py         # GitHub Issue creation

├── cloudwatch/

│   └── metrics.py              # CloudWatch custom metrics

├── terraform/

│   ├── lambda.tf               # Lambda + EventBridge schedule

│   ├── iam.tf                  # IAM roles & policies

│   ├── cloudwatch_dashboard.tf

│   ├── provider.tf

│   └── variables.tf

├── requirements.txt

└── .env                        # Local secrets (not committed)

## Deployment

```bash
cd terraform/
terraform init
terraform plan
terraform apply
```

- Terraform packages the Lambda ZIP automatically using the `archive_file` data source
- Lambda timeout is set to 300 seconds to accommodate multi-account scans
- IAM role includes permissions for EC2, EBS, EIP, S3, Cost Explorer, CloudWatch, and STS

## Sample Output
