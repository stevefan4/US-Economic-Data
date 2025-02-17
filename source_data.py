import pandas as pd
from fredapi import Fred

# Set up FRED API
FRED_API_KEY = "YOUR_FRED_API_KEY"
fred = Fred(api_key=FRED_API_KEY)

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
