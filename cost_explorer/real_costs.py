# cost_explorer/real_costs.py
from datetime import datetime, timedelta

def get_service_costs(session, account_name):
    """
    Pulls actual AWS spend for the last 30 days, broken down by service.
    """
    ce = session.client('ce', region_name='us-east-1')  # Cost Explorer is always us-east-1

    # Date range: last 30 days
    end = datetime.today().strftime('%Y-%m-%d')
    start = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')

    try:
        response = ce.get_cost_and_usage(
            TimePeriod={'Start': start, 'End': end},
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
        )

        costs = {}
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                service = group['Keys'][0]
                amount_usd = float(group['Metrics']['UnblendedCost']['Amount'])
                if amount_usd > 0:  # Only show services with actual cost
                    costs[service] = round(amount_usd * 83, 2)

        return {
            'account': account_name,
            'period': f'{start} to {end}',
            'costs_inr': costs,
            'total_inr': round(sum(costs.values()), 2)
        }

    except Exception as e:
        print(f"  Could not get Cost Explorer data for {account_name}: {e}")
        return {
            'account': account_name,
            'period': f'{start} to {end}',
            'costs_inr': {},
            'total_inr': 0
        }
