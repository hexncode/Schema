"""
Test script for waterfall financing functionality
"""
import requests
import json

# API endpoint
url = "http://127.0.0.1:5000/calculate"

# Test data with waterfall financing limits
test_data = {
    # Project details
    "project_name": "Waterfall Financing Test",
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
    "construction_cost": 600000,  # Spread over 12 months
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

    # WATERFALL FINANCING STRUCTURE
    # Equity parameters
    "equity_opening": 0,
    "equity_max_limit": 200000,  # Max equity available
    "equity_interest_rate": 15,  # 15% annual

    # Senior Loan parameters
    "loan_opening": 0,
    "loan_max_limit": 600000,  # Max senior loan available
    "loan_establishment_fee_pct": 2,  # 2% of drawdowns
    "loan_line_fee_pct": 0.5,         # 0.5% annual
    "loan_interest_rate": 6,           # 6% annual

    # Mezzanine Loan (Overdraft) parameters
    "mezz_opening": 0,
    "mezz_max_limit": 100000,  # Max mezzanine available (only as overdraft)
    "mezz_establishment_fee_pct": 3,  # 3% of drawdowns
    "mezz_line_fee_pct": 1,           # 1% annual
    "mezz_interest_rate": 12          # 12% annual
}

print("=" * 80)
print("TESTING WATERFALL FINANCING STRUCTURE")
print("=" * 80)
print()
print("Waterfall Priority:")
print("1. Equity (up to $200,000)")
print("2. Senior Loan (up to $600,000)")
print("3. Mezzanine (up to $100,000 - overdraft only)")
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
        print(f"NPV:              ${metrics.get('npv', 0):,.2f}")
        print(f"Profit:           ${metrics.get('profit', 0):,.2f}")
        print(f"Margin on GDV:    {metrics.get('margin_on_gdv', 0):.2f}%")
        print(f"Profit on Cost:   {metrics.get('profit_on_cost', 0):.2f}%")
        print(f"Peak Funding:     ${metrics.get('peak_funding', 0):,.2f}")
        print()

        # Display financing usage by source
        monthly_data = result.get('monthly_cashflows', [])

        if monthly_data:
            # Calculate total drawdowns and max balances
            total_equity_drawn = sum(m.get('Equity_Drawdown', 0) for m in monthly_data)
            total_loan_drawn = sum(m.get('Loan_Drawdown', 0) for m in monthly_data)
            total_mezz_drawn = sum(m.get('Mezz_Drawdown', 0) for m in monthly_data)

            max_equity_balance = max(m.get('Equity_Closing', 0) for m in monthly_data)
            max_loan_balance = max(m.get('Loan_Closing', 0) for m in monthly_data)
            max_mezz_balance = max(m.get('Mezz_Closing', 0) for m in monthly_data)

            print("FINANCING USAGE SUMMARY:")
            print("-" * 80)
            print(f"Equity:")
            print(f"  Total Drawdowns:   ${total_equity_drawn:,.2f}")
            print(f"  Max Balance:       ${max_equity_balance:,.2f} (Limit: $200,000)")
            print(f"  Utilization:       {(max_equity_balance / 200000 * 100):.1f}%")
            print()
            print(f"Senior Loan:")
            print(f"  Total Drawdowns:   ${total_loan_drawn:,.2f}")
            print(f"  Max Balance:       ${max_loan_balance:,.2f} (Limit: $600,000)")
            print(f"  Utilization:       {(max_loan_balance / 600000 * 100):.1f}%")
            print()
            print(f"Mezzanine (Overdraft):")
            print(f"  Total Drawdowns:   ${total_mezz_drawn:,.2f}")
            print(f"  Max Balance:       ${max_mezz_balance:,.2f} (Limit: $100,000)")
            print(f"  Utilization:       {(max_mezz_balance / 100000 * 100) if max_mezz_balance > 0 else 0:.1f}%")
            print()

            # Show first few months to see waterfall in action
            print("WATERFALL IN ACTION (First 6 months):")
            print("-" * 80)
            print(f"{'Month':<6} {'Net CF':>12} {'Eq Draw':>12} {'Loan Draw':>12} {'Mezz Draw':>12} | {'Eq Bal':>12} {'Loan Bal':>12} {'Mezz Bal':>12}")
            print("-" * 80)

            for i, month in enumerate(monthly_data[:6]):
                print(f"{month['Month']:<6} "
                      f"${month.get('Net_Cashflow', 0):>11,.0f} "
                      f"${month.get('Equity_Drawdown', 0):>11,.0f} "
                      f"${month.get('Loan_Drawdown', 0):>11,.0f} "
                      f"${month.get('Mezz_Drawdown', 0):>11,.0f} | "
                      f"${month.get('Equity_Closing', 0):>11,.0f} "
                      f"${month.get('Loan_Closing', 0):>11,.0f} "
                      f"${month.get('Mezz_Closing', 0):>11,.0f}")

            print()

            # Display sale month
            print(f"SALE MONTH (Month {test_data['sale_month']}):")
            print("-" * 80)
            sale_data = monthly_data[test_data['sale_month']]
            print(f"Net Cashflow:         ${sale_data.get('Net_Cashflow', 0):>12,.0f}")
            print(f"Equity Repatriation:  ${sale_data.get('Equity_Repatriation', 0):>12,.0f}")
            print(f"Loan Repatriation:    ${sale_data.get('Loan_Repatriation', 0):>12,.0f}")
            print(f"Mezz Repatriation:    ${sale_data.get('Mezz_Repatriation', 0):>12,.0f}")
            print(f"Final Equity Balance: ${sale_data.get('Equity_Closing', 0):>12,.0f}")
            print(f"Final Loan Balance:   ${sale_data.get('Loan_Closing', 0):>12,.0f}")
            print(f"Final Mezz Balance:   ${sale_data.get('Mezz_Closing', 0):>12,.0f}")
            print()

        print("=" * 80)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)

    else:
        print(f"[ERROR] Calculation failed: {result.get('error', 'Unknown error')}")
else:
    print(f"[ERROR] HTTP Error {response.status_code}")
    print(response.text)
