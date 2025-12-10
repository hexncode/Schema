# Quick Start Guide

## Installation & Setup

1. **Install dependencies:**
```bash
python -m pip install -r requirements.txt
```

2. **Run the application:**
```bash
python run.py
```

3. **Open in browser:**
```
http://localhost:5000
```

## Test the Model

Run the test script to see example calculations:
```bash
python test_model.py
```

## Example Scenario

The default form values demonstrate a typical residential development:

**Acquisition (Month 0):**
- Purchase Price: £500,000
- Stamp Duty: £25,000
- Legal & Survey: £7,000

**Development (Months 1-12):**
- Construction: £300,000 (£25k/month over 12 months)
- Professional Fees: £30,000
- Contingency: £15,000

**Exit (Month 18):**
- Sale Price (GDV): £1,000,000
- Sales Costs: 2% = £20,000

**Optional Financing:**
- Loan: £600,000 @ 6% p.a.
- Arrangement Fee: 2% = £12,000
- Monthly Interest: ~£3,000/month

### Expected Results:
- **Project IRR:** ~12.45%
- **Profit:** £37,000
- **Margin on GDV:** 3.7%
- **Peak Funding:** £340,000

## Key Features

### Input Categories
1. **Project Details** - Name, start date, discount rate
2. **Acquisition Costs** - Purchase, stamp duty, legal, survey
3. **Development Costs** - Construction, fees, contingency, timing
4. **Revenue/Exit** - GDV, exit month, sales costs
5. **Financing** - Loans, interest rates, fees (optional)

### Output Metrics
- **Project IRR** - Annual internal rate of return
- **Profit** - Total profit on the project
- **Margin on GDV** - Profit as % of sale price
- **Profit on Cost** - Profit as % of total costs
- **Peak Funding** - Maximum cash requirement
- **NPV** - Net present value at discount rate

### Visualizations
1. **Monthly Cashflow Chart** - Breakdown of costs/revenue/financing
2. **Cumulative Cashflow** - Running cash position over time
3. **Cost vs Profit** - Pie chart of total costs vs profit

## Tips

- **Monthly Timing:** All periods are in months from start date
- **Costs:** Enter as positive numbers (automatically treated as outflows)
- **Interest:** Calculated monthly from loan drawdown to repayment
- **Construction:** Costs spread evenly over construction period
- **Financing:** Optional - leave loan amount at 0 if equity-only

## Customization

Edit the input values to model your specific project:

- Change construction duration for different build times
- Adjust interest rates for current market conditions
- Modify sales costs % for different property types
- Add contingency as a % buffer on construction costs
- Set different exit months for various hold strategies

## Next Steps

After testing the basic model, you can:

1. Save your project scenarios (export feature coming soon)
2. Run sensitivity analysis on key variables
3. Compare multiple development options
4. Model phased developments with multiple revenue streams

---

**Application Structure:**
```
app/
├── models/cashflow.py     # Core calculation engine
├── routes/main.py         # Flask routes & API
└── templates/index.html   # Web interface
```

For more details, see [README.md](README.md)
