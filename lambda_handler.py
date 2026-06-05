import json
from multi_account import ACCOUNTS, get_session_for_account
from scanner.ec2_scanner import scan_stopped_instances
from scanner.ebs_scanner import scan_unattached_volumes
from scanner.eip_scanner import scan_idle_elastic_ips
from scanner.snapshot_scanner import scan_old_snapshots
from scanner.s3_scanner import scan_empty_buckets
from cost_explorer.real_costs import get_service_costs
from cloudwatch.metrics import publish_metrics
from notifications.github_issue import create_waste_issue
from ai_summary.summary import generate_ai_summary

def lambda_handler(event=None, context=None):
    print('CloudWise scan started')

    all_findings = []
    account_summaries = []

    # Scan each account
    for account in ACCOUNTS:
        print(f"Scanning account: {account['name']} ({account['id']})")

        try:
            session = get_session_for_account(account['id'], account['name'])
        except Exception as e:
            print(f"Could not get session for {account['name']}: {e}")
            continue

        # Run all scanners
        findings = []
        findings += scan_stopped_instances(session, account['name'])
        findings += scan_unattached_volumes(session, account['name'])
        findings += scan_idle_elastic_ips(session, account['name'])
        findings += scan_old_snapshots(session, account['name'])
        findings += scan_empty_buckets(session, account['name'])

        account_total = sum(f.get('estimated_monthly_inr', 0) for f in findings)
        # Get real costs from Cost Explorer
        print(f"  Getting real cost data for {account['name']}...")
        real_costs = get_service_costs(session, account['name'])
        print(f"  Real spend last 30 days: INR {real_costs['total_inr']}")

        account_summaries.append({
            'account': account['name'],
            'findings_count': len(findings),
            'monthly_waste_inr': account_total
        })

        all_findings.extend(findings)

    # Calculate totals
    total_monthly_inr = sum(f.get('estimated_monthly_inr', 0) for f in all_findings)

    # Print report
    print("\n" + "="*60)
    print("        CLOUDWISE COST OPTIMIZATION REPORT")
    print("="*60)

    for item in all_findings:
        print(f"\nResource Type : {item['resource_type']}")
        print(f"Account       : {item['account']}")
        print(f"ID            : {item['id']}")
        if 'name' in item:
            print(f"Name          : {item['name']}")
        if 'instance_type' in item:
            print(f"Instance Type : {item['instance_type']}")
        if 'size_gb' in item:
            print(f"Size          : {item['size_gb']} GB")
        if 'ip_address' in item:
            print(f"IP Address    : {item['ip_address']}")
        if 'days_stopped' in item:
            print(f"Days Stopped  : {item['days_stopped']} days")
        print(f"Monthly Cost  : INR {item.get('estimated_monthly_inr', 0)}")
        print("-" * 40)

    print(f"\nTOTAL MONTHLY WASTE : INR {total_monthly_inr}")
    print(f"TOTAL ANNUAL WASTE  : INR {total_monthly_inr * 12}")
    print("="*60)

    # Save findings to JSON for AI summary phase
    with open('findings.json', 'w') as f:
        json.dump({
            'findings': all_findings,
            'account_summaries': account_summaries,
            'total_monthly_inr': total_monthly_inr,
            'total_annual_inr': total_monthly_inr * 12
        }, f, indent=2, default=str)
        print("\nFindings saved to findings.json")

    # Generate AI summary
    if all_findings:
        print("\nGenerating AI summary...")
        summary = generate_ai_summary({
            'findings': all_findings,
            'total_monthly_inr': total_monthly_inr,
            'total_annual_inr': total_monthly_inr * 12
        })
        print("\n--- AI SUMMARY ---")
        print(summary)
        with open('ai_summary.txt', 'w', encoding='utf-8') as f:
            f.write(summary)
        print("\nSummary saved to ai_summary.txt")

    # Create GitHub Issue if waste found
    if all_findings:
        print("\nCreating GitHub Issue for approval...")
        create_waste_issue(all_findings, total_monthly_inr)

    # Publish to CloudWatch
    print("\nPublishing metrics to CloudWatch...")
    personal_session = get_session_for_account("515206814398", "personal")
    publish_metrics(personal_session, all_findings, total_monthly_inr)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'findings_count': len(all_findings),
            'total_monthly_waste_inr': total_monthly_inr,
            'accounts_scanned': len(ACCOUNTS)
        })
    }


# Run directly from terminal
if __name__ == '__main__':
    lambda_handler()
