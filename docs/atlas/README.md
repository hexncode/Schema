# Appraise.ai - Property Acquisition Cashflow Model

A Flask-based web application for modeling residential property acquisitions with monthly cashflow analysis.

## Features

- **Monthly Cashflow Modeling**: Track costs and revenues on a monthly basis
- **Key Metrics Calculation**:
  - Project IRR (Internal Rate of Return)
  - Profit
  - Margin on GDV (Gross Development Value)
  - Profit on Cost
  - NPV (Net Present Value)
  - Peak Funding Requirement

- **Interactive Visualizations**:
  - Monthly cashflow breakdown charts
  - Cumulative cashflow position
  - Cost vs profit analysis

- **Comprehensive Inputs**:
  - Acquisition costs (purchase price, stamp duty, legal fees, surveys)
  - Development costs (construction, professional fees, contingency)
  - Revenue modeling (GDV, sales costs)
  - Financing options (loans, interest rates)
  - Flexible timing controls

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python run.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

### Input Parameters

**Project Details:**
- Project Name
- Start Date
- Discount Rate (for NPV calculation)

**Acquisition Costs:**
- Purchase Price
- Stamp Duty
- Legal Fees
- Survey Fees

**Development Costs:**
- Construction Cost (spread monthly over duration)
- Professional Fees
- Contingency
- Construction Start Month
- Construction Duration (months)

**Revenue/Exit:**
- GDV (Gross Development Value/Sale Price)
- Sale Month
- Sales Costs (% of GDV)

**Financing (Optional):**
- Loan Amount
- Interest Rate (% p.a.)
- Arrangement Fee (%)

### Output Metrics

The model calculates and displays:

- **Project IRR**: Annual internal rate of return
- **Profit**: Total profit (Revenue - Costs)
- **Margin on GDV**: Profit as percentage of sale price
- **Profit on Cost**: Profit as percentage of total costs
- **Total Costs**: Sum of all acquisition, development, and finance costs
- **Peak Funding**: Maximum negative cashflow position
- **NPV**: Net present value at specified discount rate

### Visualizations

1. **Monthly Cashflow Breakdown**: Stacked bar chart showing costs, revenue, and financing by month
2. **Cumulative Cashflow**: Line chart showing cumulative cash position over time
3. **Cost vs Profit**: Pie chart showing total costs versus profit

## Project Structure

```
Appraise.ai/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── models/
│   │   └── cashflow.py       # Core cashflow calculation logic
│   ├── routes/
│   │   └── main.py           # Flask routes and API endpoints
│   ├── templates/
│   │   ├── base.html         # Base HTML template
│   │   └── index.html        # Main input form and results page
│   └── static/
│       ├── css/
│       └── js/
├── requirements.txt          # Python dependencies
├── run.py                   # Application entry point
└── README.md                # This file
```

## Technical Details

### Cashflow Calculation Engine

The `PropertyAcquisition` class in `app/models/cashflow.py` handles:

- **Cashflow Item Management**: Stores individual cashflow items with timing
- **Cost Spreading**: Distributes construction costs evenly over development period
- **Interest Calculation**: Computes monthly interest on loans
- **Metric Calculation**: Uses numpy-financial for IRR and NPV

### Monthly Cashflow Logic

- Acquisition costs occur in month 0 (or specified month)
- Construction costs spread evenly over construction duration
- Professional fees applied at construction start
- Contingency applied mid-construction
- Interest calculated monthly from loan drawdown to repayment
- Sale proceeds and costs occur in specified exit month

### IRR Calculation

- Monthly cashflows used to calculate monthly IRR
- Monthly IRR converted to annual equivalent: `(1 + monthly_irr)^12 - 1`
- Uses numpy-financial's `irr()` function

### NPV Calculation

- Discount rate converted from annual to monthly
- NPV calculated using monthly cashflows and monthly discount rate
- Uses numpy-financial's `npv()` function

## Example Scenario

**Default Values** (£500k acquisition, £300k construction, £1m GDV):

- Purchase Price: £500,000
- Stamp Duty: £25,000
- Legal & Survey: £7,000
- Construction: £300,000 (over 12 months)
- Professional Fees: £30,000
- Contingency: £15,000
- GDV: £1,000,000
- Exit: Month 18

**Expected Results:**
- Total Costs: ~£887,000
- Profit: ~£113,000
- Margin on GDV: ~11.3%
- Project IRR: Varies based on timing

## Future Enhancements

- [ ] Export to Excel/CSV
- [ ] Sensitivity analysis
- [ ] Multiple revenue streams (phased sales, rental income)
- [ ] Save/load project scenarios
- [ ] Comparison of multiple projects
- [ ] More detailed cost breakdowns
- [ ] Tax modeling (CGT, Corporation Tax)

## Requirements

- Python 3.8+
- Flask 3.0+
- pandas 2.1+
- numpy 1.26+
- numpy-financial 1.0+
- plotly 5.18+

## License

This project is for educational and professional use in property development appraisal.
