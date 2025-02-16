import pandas as pd
from fredapi import Fred

# Set up FRED API
FRED_API_KEY = "YOUR_FRED_API_KEY"
fred = Fred(api_key=FRED_API_KEY)

MISSNG_SERIES = [Underemployment, Initial+Contiuining Jobless Claims, Layoff Announceements, Total Labor Force, Labor Force Partipation Rate, Productivity, Weekly Hours Worked, ADP Jobs, ISM Mfg Employment, ISM Svcs Employment, Challenger Hirings]

# Updated FRED Series Dictionary
FRED_SERIES_EXTENDED = {
    # Labor - Employment
    "Total Employment": "PAYEMS",
    "Temporary Employment": "TEMPHEL",
    "Non-Farm Payrolls": "PAYEMS",
    "Multiple Jobholders": "LNS12026620",

    # Labor - Unemployment
    "Unemployment Rate": "UNRATE",
    "Underemployment Rate": "U6RATE", 
    "Duration of Unemployment": "UEMPMEAN",
    "Initial Jobless Claims": "ICSA", 
    "Continuing Jobless Claims": "CCSA", 

    # Labor - Supply
    "Total Labor Force": "CLF16OV", 
    "Labor Force Participation Rate": "CIVPART", 
    "Productivity": "OPHNFB", 
    "Weekly Hours Worked": "AWHAETP", 

    # Labor - Demand
    "Total Job Openings": "JTSJOL", 
    "Quits Rate": "JTSQUR", 
    "Layoff Rate": "JTSLDL", 
    "Hires Rate": "JTSHIR", 
    "NFIB Job Openings": "NFIBJOBS",
    "Jobs Plentiful - Jobs Hard to Get": "CSCICP03USM665S",

    # Consumer - Spending
    "PCE": "PCE",
    "Retail Sales": "RSXFS", 
    "Durable Goods": "DGORDER",
    "Non-Durable Goods": "ANDPCE",
    "Services": "PCES",

    # Consumer - Confidence
    "UMich Sentiment": "UMCSENT",
    "Conf Brd Consumer Confidence": "CONCCONF",

    # Consumer - Financial Health
    "Total Consumer Credit Outstanding": "TOTALSL",
    "Revolving Credit": "REVOLSL",
    "Debt Service Ratio": "TDSP",
    "Credit Card Delinquency Rate": "DRCCLACBS",
    "Auto Loan Delinquency Rate": "DRALACBS",
    "Household Net Worth": "TNWBSHNO",
    
    # Businesses - Performance
    "Business Revenue & Sales": "TOTBUSAMT",
    "Corporate Profits": "CP",
    "NFIB Small Business Performance": "NFIBOPT",
    "Industrial Production": "INDPRO",
    "Capacity Utilization": "TCU",

    # Businesses - Investment
    "Private Fixed Investment": "FPI",
    "Business Spending": "PNFI",

    # Businesses - Financing
    "Corporate Debt Outstanding": "TCMDODNS",

    # Businesses - Confidence
    
    # Government
    "Total Tax Revenue": "FGRECPT",
    "Federal Budget Deficit": "FYFSD",
    "Federal Debt % GDP": "GFDEGDQ188S",
    "Total Federal Govt Debt Outstanding": "GFDEBTN",
}

# Fetch data from FRED
def fetch_fred_data(series_dict):
    data_dict = {}
    for indicator, series_id in series_dict.items():
        try:
            print(f"Fetching {indicator} ({series_id})...")
            data_dict[indicator] = fred.get_series(series_id)
        except Exception as e:
            print(f"Failed to fetch {indicator}: {e}")
    return data_dict

# Convert fetched data to DataFrame
def format_data_to_df(data_dict):
    df = pd.DataFrame(data_dict)
    df.index = pd.to_datetime(df.index)
    return df

# Save to Excel
def save_to_excel(df, filename="economic_data_extended.xlsx"):
    df.to_excel(filename, engine='openpyxl')
    print(f"Data saved to {filename}")

# Run the script
if __name__ == "__main__":
    data = fetch_fred_data(FRED_SERIES_EXTENDED)
    df = format_data_to_df(data)
    save_to_excel(df)

"""
Economic Activity:
  Real Economic Activity:
    Labor:
      Employment: 
        - ADP Jobs Added
        - ISM Mfg. Employment
        - ISM Svcs. Employment
        - Challenger Hiring Announcements
      Unemployment: 
        - Challenger Layoff Announcements
      Labor Demand: 
        - NFIB Avg Change in Employment 
        - NFIB Actual Employment Changes
        - NFIB Hirings Plans
        - NFIB Jobs Openings
        - NFIB % Positions Not Able to Fill
        - More Jobs - Fewer Jobs (6 months hence)
        - Probability of Finding Job if Fired
    Consumer: 
      Confidence: 
        Current Conditions: 
          - UMich Current Economic Conditions 
        Expected Conditions: 
          - UMich Expectations
          - Conf Brd Expectations
          - NY Fed Consumer Expectations
      Financial Health: 
        Income: 
          - Real Personal Income
          - Real Disposable Personal Income
        Savings:
          - Personal Savings Rate 
        Credit Availability and Debt Burden: 
          - Total Consumer Credit Outstanding
          - Revolving Credit
          - Non-Revolving Credit
          - Debt Service Ratio
          - Household Debt to GDP
        Delinquencies: 
          - Credit Cards Delinquency Rate
          - Auto Loan Delinquency Rate
          - Mortgage Delinquency Rate
        Wealth: 
          - Household Net Worth
          - Household Real Estate Assets 
          - Retirement Assets
    Businesses: 
      Performance: 
        - Business Revenue & Sales
        - Corporate Profits
        - NFIB Small Business Performance
        - Industrial Production 
        - Capacity Utilization 
      Investment: 
        - Private Fixed Investment
        - Business Spending
        - New Orders for Capital Goods
        - Non-resedential Construction Spending
      Financing: 
        - Corporate Debt Outstanding
        - Corporate Bond Yields & Spreads
        - Bank Lending to Businesses 
        - Commerical Loan Delinquency Rate
      Confidence:
        Current Conditions: 
          - ISM Manufacturing PMI
          - ISM Services PMI
          - NFIB Small Business Optimism
          - CEO Confidence
          - Business Conditions Survey (Richmond, Dallas, Philly) 
        Expected Conditions: 
          - ISM Mfg New Orders
          - ISM Svcs New Orders 
          - NFIB Business Outlook 
          - Conf Brd LEI
    Government: 
      Revenue: 
        - Total Tax Revenue
        - Corporate Tax Receipts
        - Personal Income Tax Receipts
        - Customs Duties & Tariffs Collected
        - State & Local Government Tax Revenue
      Spending:  
        - Total Federal Spending
        - Defense Spending
        - Social Security & Medicare Expenditures 
        - Infrastructure & Public Works Spending
        - State & Local Government Spending
      Deficit: 
        - Federal Budget Deficit
        - Federal Debt % GDP 
        - Total Federal Govt Debt Outstanding
        - State and Local Govt Debt Outstanding
      Monetary & Fiscal Policy: 
        - Fed Funds Rate 
        - Money Supply
        - Fed Balance Sheet
        - US 10Yr Yld
        - US 10Yr - 2Yr Spread
      Investment:  
        - Government Investment in Infrastructure
        - Federal R&D Spending 
        - State & Local Capital Investment in Public Services 
  Prices:
    Realized Prices:
      Consumers: 
        - CPI
        - Core CPI 
        - PCE 
        - Core PCE
        - CPI Housing Component
      Businessses: 
        - PPI 
        - Core PPI 
        - Labor Costs (Wages)
        - Commodoties (BCOM)
    Price Expectations:
      Survey-Based:
        - UMich 1Yr Inflation Expectations
        - UMICH 5Yr Inflation Expectations
        - NY Fed Inflation Expectations
      Market-Based:
        - 5Yr Breakeven 
        - 10Yr Breakeven
        - 5Yr5Yr Forward Breakeven

"""