# CloudWise — AWS FinOps & Cost Optimisation Tool

A serverless AWS cost-optimisation tool that scans multiple AWS accounts for idle and wasted resources, calculates estimated monthly savings in **INR**, generates an **AI-written executive summary**, raises a **GitHub Issue** for human approval, and publishes custom metrics to **CloudWatch dashboards**. The scanner runs as an **AWS Lambda function** on a weekly schedule via EventBridge, provisioned entirely with **Terraform**.

<img width="602" height="315" alt="Terminal_output" src="https://github.com/user-attachments/assets/1c856baf-1cc3-4652-8f9b-357fa0d83251" />

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

<img width="602" height="270" alt="lambda_console" src="https://github.com/user-attachments/assets/93d6b06c-6c81-495d-9839-4121017e2e38" />


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

  <img width="602" height="315" alt="terraform_output" src="https://github.com/user-attachments/assets/454c49b4-8899-47fd-a6b3-c163458fc3ec" />

## CI/CD (GitHub Actions)

<img width="602" height="304" alt="github_actions" src="https://github.com/user-attachments/assets/b148ae4d-b874-4a14-ba0b-71351730eebc" />


## Monitoring

<img width="602" height="110" alt="cloudwatch_dashboard" src="https://github.com/user-attachments/assets/30937a12-6bb9-44e4-abcb-982fd3108721" />


## Sample Output
CLOUDWISE COST OPTIMIZATION REPORT
Resource Type : stopped_ec2
Account       : personal
ID            : i-0abc123def456
Instance Type : t3.medium
Days Stopped  : 14 days
Monthly Cost  : INR 415
TOTAL MONTHLY WASTE : INR 1,245
TOTAL ANNUAL WASTE  : INR 14,940
☁️ CloudWise AI Analysis:
Your AWS environment has 3 idle resources wasting ₹1,245/month (₹14,940/year).
Immediate actions:

Terminate 1 stopped EC2 instance — biggest cost at ₹415/month with zero business value
Release 1 unassociated Elastic IP — charging ₹299/month for an unused IP address
Delete 1 unattached EBS volume — orphaned storage with no instance attached

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Fill in your AWS credentials and GitHub token

# Run the scanner locally
python lambda_handler.py
```

## Prerequisites

- AWS account(s) with appropriate IAM permissions
- Terraform >= 1.0
- Python 3.11
- GitHub Personal Access Token (for issue creation)
