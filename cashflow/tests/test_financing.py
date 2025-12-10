"""
Test script for automatic financing functionality
"""
import requests
import json

# API endpoint
url = "http://127.0.0.1:5000/calculate"

# Test data with typical property acquisition scenario
test_data = {
    # Project details
    "project_name": "Test Property Development",
    "start_date": "2025-01-01",
    "discount_rate": 10,

    # Program dates
    "acquisition_month": 0,
    "planning_start": 0,
    "planning_duration": 3,
    "construction_start_month": 3,
    "construction_duration": 12,
    "marketing_start": 12,
    "sale_month": 18,

    # Acquisition costs (Month 0)
    "purchase_price": 500000,
    "stamp_duty": 25000,
    "legal_fees": 5000,
    "survey_fees": 2000,
    "agent_fees": 10000,
    "other_acquisition": 0,

    # Development costs
    "demolition": 20000,
    "construction_cost": 600000,  # Spread over 12 months = 50k/month
    "professional_fees": 60000,
    "planning_fees": 5000,
    "building_control": 3000,
    "s106_cil": 15000,
    "utilities": 10000,
    "marketing": 5000,
    "contingency": 30000,
    "other_development": 0,

    # Revenue
    "gdv": 1500000,
    "sales_agent_pct": 1.5,
    "sales_legal": 3000,

    # Financing - NEW AUTOMATIC FUNDING STRUCTURE
    "equity_pct_funded": 30,  # 30% equity
    "loan_pct_funded": 70,    # 70% senior loan

    # Equity parameters
    "equity_opening": 0,
    "equity_interest_rate": 15,  # 15% annual

    # Senior Loan parameters
    "loan_opening": 0,
    "loan_establishment_fee_pct": 2,  # 2% of drawdowns
    "loan_line_fee_pct": 0.5,         # 0.5% annual
    "loan_interest_rate": 6           # 6% annual
}

print("=" * 80)
print("TESTING AUTOMATIC FINANCING FUNCTIONALITY")
print("=" * 80)
print()

# Send request
print("Sending calculation request...")
response = requests.post(url, json=test_data)

if response.status_code == 200:
    result = response.json()

    if result.get('success'):
        print("[OK] Calculation successful!")
        print()

        # Display metrics
        metrics = result.get('metrics', {})
        print("KEY METRICS:")
        print("-" * 80)
        print(f"Project IRR:      {metrics.get('project_irr', 0):.2f}%")
        print(f"Equity IRR:       {metrics.get('equity_irr', 0):.2f}%")
        print(f"NPV:              £{metrics.get('npv', 0):,.2f}")
        print(f"Profit:           £{metrics.get('profit', 0):,.2f}")
        print(f"Margin on GDV:    {metrics.get('margin_on_gdv', 0):.2f}%")
        print(f"Profit on Cost:   {metrics.get('profit_on_cost', 0):.2f}%")
        print(f"Peak Funding:     £{metrics.get('peak_funding', 0):,.2f}")
        print()

        # Display first few months of financing
        monthly_data = result.get('monthly_cashflows', [])

        if monthly_data:
            print("FINANCING DETAILS (First 5 months):")
            print("-" * 80)
            print(f"{'Month':<6} {'Net CF':<12} {'Eq Draw':<12} {'Loan Draw':<12} {'Eq Closing':<12} {'Loan Closing':<12}")
            print("-" * 80)

            for i, month in enumerate(monthly_data[:5]):
                print(f"{month['Month']:<6} "
                      f"£{month.get('Net_Cashflow', 0):>10,.0f}  "
                      f"£{month.get('Equity_Drawdown', 0):>10,.0f}  "
                      f"£{month.get('Loan_Drawdown', 0):>10,.0f}  "
                      f"£{month.get('Equity_Closing', 0):>10,.0f}  "
                      f"£{month.get('Loan_Closing', 0):>10,.0f}")

            print()

            # Display sale month
            print(f"SALE MONTH (Month {test_data['sale_month']}):")
            print("-" * 80)
            sale_data = monthly_data[test_data['sale_month']]
            print(f"Net Cashflow:        £{sale_data.get('Net_Cashflow', 0):>12,.0f}")
            print(f"Equity Drawdown:     £{sale_data.get('Equity_Drawdown', 0):>12,.0f}")
            print(f"Equity Repatriation: £{sale_data.get('Equity_Repatriation', 0):>12,.0f}")
            print(f"Loan Drawdown:       £{sale_data.get('Loan_Drawdown', 0):>12,.0f}")
            print(f"Loan Repatriation:   £{sale_data.get('Loan_Repatriation', 0):>12,.0f}")
            print(f"Equity Closing:      £{sale_data.get('Equity_Closing', 0):>12,.0f}")
            print(f"Loan Closing:        £{sale_data.get('Loan_Closing', 0):>12,.0f}")
            print()

            # Verify funding split
            print("FUNDING SPLIT VERIFICATION:")
            print("-" * 80)
            total_equity_drawn = sum(m.get('Equity_Drawdown', 0) for m in monthly_data)
            total_loan_drawn = sum(m.get('Loan_Drawdown', 0) for m in monthly_data)
            total_drawn = total_equity_drawn + total_loan_drawn

            if total_drawn > 0:
                actual_equity_pct = (total_equity_drawn / total_drawn) * 100
                actual_loan_pct = (total_loan_drawn / total_drawn) * 100

                print(f"Total Equity Drawdowns: £{total_equity_drawn:,.2f} ({actual_equity_pct:.1f}%)")
                print(f"Total Loan Drawdowns:   £{total_loan_drawn:,.2f} ({actual_loan_pct:.1f}%)")
                print(f"Expected Split:         30% Equity / 70% Loan")

                if abs(actual_equity_pct - 30) < 1 and abs(actual_loan_pct - 70) < 1:
                    print("[OK] Funding split matches expected percentages!")
                else:
                    print("[WARNING] Funding split differs from expected percentages")

            print()

        print("=" * 80)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)

    else:
        print(f"[ERROR] Calculation failed: {result.get('error', 'Unknown error')}")
else:
    print(f"[ERROR] HTTP Error {response.status_code}")
    print(response.text)
