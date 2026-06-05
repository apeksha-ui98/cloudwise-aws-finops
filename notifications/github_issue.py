# notifications/github_issue.py
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def create_waste_issue(findings, total_monthly_inr):
    """
    Opens a GitHub Issue listing all waste resources.
    Issue must be labeled 'cloudwise-approved' to trigger cleanup.
    """
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPO")  # format: username/repo-name

    if not token or not repo:
        print("  GitHub token or repo not set in .env, skipping issue creation")
        return None

    # Build issue body
    rows = ""
    for f in findings:
        rows += f"| {f['resource_type']} | {f['account']} | {f['id']} | ₹{f.get('estimated_monthly_inr', 0)}/month |\n"

    body = f"""## 🔍 CloudWise Cost Optimization Report

**Total Monthly Waste: ₹{total_monthly_inr}**
**Total Annual Waste: ₹{total_monthly_inr * 12}**

### Idle Resources Found

| Resource Type | Account | Resource ID | Monthly Cost |
|---------------|---------|-------------|--------------|
{rows}

---
### ✅ To approve cleanup:
Add the label `cloudwise-approved` to this issue.
The cleanup Lambda will automatically delete all resources listed above.

> ⚠️ **Warning:** This will permanently delete the listed resources. Review carefully before approving.
"""

    payload = {
        "title": f"☁️ CloudWise: ₹{round(total_monthly_inr, 2)}/month waste detected",
        "body": body,
        "labels": ["cloudwise-scan"]
    }

    response = requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        },
        json=payload
    )

    if response.status_code == 201:
        issue_url = response.json()["html_url"]
        print(f"  GitHub Issue created: {issue_url}")
        return issue_url
    else:
        print(f"  Failed to create issue: {response.status_code} {response.text}")
        return None
