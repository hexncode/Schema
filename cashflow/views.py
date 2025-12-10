from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime
import json
import plotly.graph_objs as go
import plotly
import numpy as np
import numpy_financial as npf
import math
from dateutil.relativedelta import relativedelta


def cashflow_index(request):
    """Cashflow page"""
    return render(request, 'cashflow/index.html')


@require_http_methods(["POST"])
def calculate(request):
    """Calculate cashflow model"""
    try:
        data = json.loads(request.body)

        # Extract parameters
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        discount_rate = float(data.get('discount_rate', 10)) / 100

        # Program timing
        acquisition_month = int(data.get('acquisition_month', 0))
        construction_start = int(data.get('construction_start_month', 4))
        construction_duration = int(data.get('construction_duration', 12))
        sale_month = int(data.get('sale_month', 18))

        # Build cashflows
        cashflows = []

        # Acquisition costs
        for name, key in [
            ('Purchase Price', 'purchase_price'),
            ('Stamp Duty', 'stamp_duty'),
            ('Legal Fees', 'legal_fees')
        ]:
            amt = float(data.get(key, 0))
            if amt > 0:
                cashflows.append({
                    'month': acquisition_month,
                    'category': 'Acquisition',
                    'amount': -amt
                })

        # Construction (spread monthly)
        construction_cost = float(data.get('construction_cost', 0))
        if construction_cost > 0:
            monthly = construction_cost / construction_duration
            for i in range(construction_duration):
                cashflows.append({
                    'month': construction_start + i,
                    'category': 'Development',
                    'amount': -monthly
                })

        # Revenue
        gdv = float(data.get('gdv', 0))
        if gdv > 0:
            cashflows.append({
                'month': sale_month,
                'category': 'Revenue',
                'amount': gdv
            })

        # Financing params
        financing = {
            'equity': {
                'opening': float(data.get('equity_opening', 0)),
                'max_limit': float(data.get('equity_max_limit', 200000)),
                'interest_rate': float(data.get('equity_interest_rate', 0)) / 100
            },
            'loan': {
                'opening': float(data.get('loan_opening', 0)),
                'max_limit': float(data.get('loan_max_limit', 600000)),
                'interest_rate': float(data.get('loan_interest_rate', 6)) / 100,
                'establishment_fee': float(data.get('loan_establishment_fee_pct', 2)) / 100
            }
        }

        # Calculate
        max_month = max(cf['month'] for cf in cashflows) if cashflows else sale_month
        monthly_data = build_monthly_cashflows(cashflows, start_date, max_month, financing)
        metrics = calculate_metrics(monthly_data, discount_rate)
        charts = create_charts(monthly_data)

        return JsonResponse({
            'success': True,
            'metrics': metrics,
            'monthly_cashflows': monthly_data,
            'charts': charts
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def build_monthly_cashflows(cashflows, start_date, max_month, financing):
    """Build monthly cashflow table with waterfall financing"""
    months_data = []
    equity = financing['equity']
    loan = financing['loan']

    for month_num in range(max_month + 1):
        date = start_date + relativedelta(months=month_num)

        # Get cashflows for this month
        month_cfs = [cf for cf in cashflows if cf['month'] == month_num]
        acquisition = sum(cf['amount'] for cf in month_cfs if cf['category'] == 'Acquisition')
        development = sum(cf['amount'] for cf in month_cfs if cf['category'] == 'Development')
        revenue = sum(cf['amount'] for cf in month_cfs if cf['category'] == 'Revenue')
        net_project_cf = acquisition + development + revenue

        # Opening balances
        if month_num == 0:
            equity_bal = equity['opening']
            loan_bal = loan['opening']
        else:
            equity_bal = months_data[-1]['Equity_Closing']
            loan_bal = months_data[-1]['Loan_Closing']

        # Interest
        equity_interest = equity_bal * (equity['interest_rate'] / 12)
        loan_interest = loan_bal * (loan['interest_rate'] / 12)

        net_after_fees = net_project_cf - equity_interest - loan_interest

        # Waterfall: Equity first, then loan
        if net_after_fees < 0:
            # Need funding
            need = abs(net_after_fees)
            equity_draw = min(need, equity['max_limit'] - equity_bal)
            need -= equity_draw

            loan_draw = min(need, loan['max_limit'] - loan_bal) if need > 0 else 0
            loan_fee = loan_draw * loan['establishment_fee']

            equity_repay = 0
            loan_repay = 0
        else:
            # Surplus - repay loan first, then equity
            surplus = net_after_fees
            equity_draw = 0
            loan_draw = 0
            loan_fee = 0

            loan_repay = min(surplus, loan_bal)
            surplus -= loan_repay

            equity_repay = min(surplus, equity_bal) if surplus > 0 else 0

        # Closing balances
        equity_close = equity_bal + equity_draw - equity_interest - equity_repay
        loan_close = loan_bal + loan_draw - loan_fee - loan_interest - loan_repay

        total_cf = net_project_cf + equity_draw - equity_interest - equity_repay + loan_draw - loan_fee - loan_interest - loan_repay
        cumulative = total_cf if month_num == 0 else months_data[-1]['Cumulative_Cashflow'] + total_cf

        months_data.append({
            'Month': month_num,
            'Date': date.isoformat(),
            'Acquisition': acquisition,
            'Development': development,
            'Revenue': revenue,
            'Net_Cashflow': net_project_cf,
            'Equity_Opening': equity_bal,
            'Equity_Drawdown': -equity_draw,
            'Equity_Interest': -equity_interest,
            'Equity_Repatriation': equity_repay,
            'Equity_Closing': equity_close,
            'Loan_Opening': loan_bal,
            'Loan_Drawdown': -loan_draw,
            'Loan_Fee': -loan_fee,
            'Loan_Interest': -loan_interest,
            'Loan_Repatriation': loan_repay,
            'Loan_Closing': loan_close,
            'Total_Net_Cashflow': total_cf,
            'Cumulative_Cashflow': cumulative
        })

    return months_data


def calculate_metrics(monthly_data, discount_rate):
    """Calculate financial metrics"""
    cashflows = [m['Net_Cashflow'] for m in monthly_data]

    # IRR
    try:
        monthly_irr = npf.irr(cashflows)
        annual_irr = ((1 + monthly_irr) ** 12 - 1) * 100 if np.isfinite(monthly_irr) else 0
    except:
        annual_irr = 0

    # NPV
    monthly_discount = (1 + discount_rate) ** (1/12) - 1
    try:
        npv = npf.npv(monthly_discount, cashflows)
        npv = npv if math.isfinite(npv) else 0
    except:
        npv = 0

    # Totals
    total_acq = abs(sum(m['Acquisition'] for m in monthly_data))
    total_dev = abs(sum(m['Development'] for m in monthly_data))
    total_rev = sum(m['Revenue'] for m in monthly_data)
    total_costs = total_acq + total_dev
    profit = total_rev - total_costs
    peak_funding = abs(min(m['Cumulative_Cashflow'] for m in monthly_data))

    return {
        'project_irr': round(annual_irr, 2),
        'npv': round(npv, 2),
        'profit': round(profit, 2),
        'margin_on_gdv': round((profit / total_rev * 100) if total_rev > 0 else 0, 2),
        'profit_on_cost': round((profit / total_costs * 100) if total_costs > 0 else 0, 2),
        'total_costs': round(total_costs, 2),
        'total_revenue': round(total_rev, 2),
        'peak_funding': round(peak_funding, 2)
    }


def create_charts(monthly_data):
    """Create Plotly charts"""
    months = [m['Month'] for m in monthly_data]
    cumulative = [m['Cumulative_Cashflow'] for m in monthly_data]

    chart = go.Figure()
    chart.add_trace(go.Scatter(
        x=months,
        y=cumulative,
        mode='lines+markers',
        name='Cumulative Cashflow',
        line=dict(color='royalblue', width=3),
        fill='tozeroy'
    ))

    chart.update_layout(
        title='Cumulative Cashflow',
        xaxis_title='Month',
        yaxis_title='Amount',
        height=400
    )

    chart.add_hline(y=0, line_dash="dash", line_color="gray")

    return {'cumulative': json.loads(plotly.io.to_json(chart))}


@require_http_methods(["POST"])
def export(request):
    """Export cashflow"""
    return JsonResponse({'message': 'Export coming soon'})
