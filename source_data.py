#%% Import Libraries 

import pandas as pd  # Import pandas for data manipulation
from fredapi import Fred  # Import Fred API to fetch economic data

# Set up FRED API with your unique key (Replace "YOUR_FRED_API_KEY" with your actual key)
FRED_API_KEY = "YOUR_FRED_API_KEY"
fred = Fred(api_key=FRED_API_KEY)

#%% FRED Data Pull 

# Specify the path to your CSV file
csv_file = r"Downloads/Data Sources.csv"  # Update the file path if needed

# Step 1: Read the CSV file into a DataFrame
df_sources = pd.read_csv(csv_file)

# Step 2: Filter out rows where the 'FRED Series ID' is missing or contains '--'
df_sources = df_sources[df_sources['FRED Series ID'].notna() & (df_sources['FRED Series ID'] != '--')]

# Step 3: Create a dictionary mapping the data source names to their corresponding FRED Series IDs
fred_series_dict = dict(zip(df_sources['Data Sources'], df_sources['FRED Series ID']))

# Function to fetch data from FRED
def fetch_fred_data(series_dict):
    """
    Fetches data from FRED for each indicator in the provided dictionary.

    :param series_dict: Dictionary where keys are indicator names and values are FRED Series IDs.
    :return: Dictionary with indicator names as keys and time series data as values.
    """
    data_dict = {}  # Initialize an empty dictionary to store fetched data
    
    for indicator, series_id in series_dict.items():
        try:
            print(f"Fetching {indicator} ({series_id})...")  # Print which series is being fetched
            data_dict[indicator] = fred.get_series(series_id)  # Fetch time-series data from FRED
        except Exception as e:
            print(f"Failed to fetch {indicator}: {e}")  # Print an error message if fetching fails
            
    return data_dict  # Return the collected data

# Function to convert fetched data into a DataFrame and resample to daily
def format_data_to_df(data_dict):
    """
    Converts the fetched FRED data dictionary into a pandas DataFrame and resamples to daily frequency.

    :param data_dict: Dictionary with indicator names as keys and time series data as values.
    :return: A pandas DataFrame with daily frequency and forward-filled missing values.
    """
    df = pd.DataFrame(data_dict)  # Convert dictionary to DataFrame
    df.index = pd.to_datetime(df.index)  # Ensure index is datetime

    # Define the full daily date range from the first to last available data point
    full_date_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')

    # Reindex the DataFrame to ensure all dates are present
    df = df.reindex(full_date_range)

    # Forward fill to propagate last known value, then backfill to fill the initial NaNs
    df.ffill(inplace=True)

    return df  # Return the daily frequency DataFrame

# Function to get metadata for each FRED series
def get_series_metadata(series_dict):
    """
    Fetches metadata for each FRED series, including first available date and frequency.

    :param series_dict: Dictionary of FRED series IDs.
    :return: A DataFrame with metadata including descriptions, first data date, and periodicity.
    """
    metadata_list = []
    
    for indicator, series_id in series_dict.items():
        try:
            # Fetch metadata from FRED
            info = fred.get_series_info(series_id)
            
            # Get first available date
            first_date = fred.get_series(series_id).dropna().index.min()
            
            # Store metadata
            metadata_list.append({
                "Indicator": indicator,
                "FRED Series ID": series_id,
                "Description": info.title if hasattr(info, 'title') else "N/A",
                "First Available Date": first_date,
                "Periodicity": info.frequency if hasattr(info, 'frequency') else "Unknown"
            })
        
        except Exception as e:
            print(f"Failed to fetch metadata for {indicator}: {e}")
    
    return pd.DataFrame(metadata_list)

# Function to analyze the dataset
def analyze_data(df):
    """
    Performs basic analysis on the dataset, including:
    - Descriptive statistics (mean, min, max)
    - Trends over time (last available value vs. historical mean)
    """
    analysis = {}
    
    for column in df.columns:
        series = df[column].dropna()  # Drop NaNs for calculations
        
        if not series.empty:
            analysis[column] = {
                "Mean": series.mean(),
                "Min": series.min(),
                "Max": series.max(),
                "Last Available Value": series.iloc[-1],
                "YoY Change (%)": ((series.iloc[-1] - series.iloc[-365]) / series.iloc[-365] * 100) if len(series) > 365 else "N/A"
            }
    
    return pd.DataFrame(analysis).T  # Transpose for better readability

# Function to save the DataFrame and metadata to an Excel file
def save_to_excel(df, metadata_df, analysis_df, filename="economic_data_extended.xlsx"):
    """
    Saves the DataFrame, metadata, and analysis to an Excel file.

    :param df: The DataFrame containing economic data.
    :param metadata_df: The DataFrame containing metadata for each series.
    :param analysis_df: The DataFrame containing statistical analysis.
    :param filename: The name of the output Excel file.
    """
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="FRED Data")  # Save main data
        metadata_df.to_excel(writer, sheet_name="Metadata")  # Save metadata
        analysis_df.to_excel(writer, sheet_name="Analysis")  # Save analysis
    
    print(f"Data saved to {filename}")  # Print confirmation message

# Main execution: Fetch data, convert it to a DataFrame, analyze, and save
if __name__ == "__main__":
    """
    Main execution block:
    - Fetches FRED data based on the CSV file.
    - Converts it into a structured DataFrame with daily frequency.
    - Collects metadata for each series.
    - Performs basic analysis on the data.
    - Saves the data, metadata, and analysis to an Excel file.
    """
    data = fetch_fred_data(fred_series_dict)  # Fetch data from FRED
    df = format_data_to_df(data)  # Convert to daily DataFrame with forward fill
    metadata_df = get_series_metadata(fred_series_dict)  # Fetch metadata
    analysis_df = analyze_data(df)  # Perform analysis
    save_to_excel(df, metadata_df, analysis_df)  # Save everything to Excel

#%% ADP Data Pull
'''
import requests  # To send HTTP requests and fetch web pages
from bs4 import BeautifulSoup  # To parse HTML content
import pandas as pd  # To structure and save data into Excel

# Define the URL for ADP Employment Report
ADP_URL = "https://adpemploymentreport.com/"  # ADP publishes job reports here

# Function to scrape ADP job report
def scrape_adp_jobs():
    """
    Scrapes the ADP employment report website and extracts job data.
    Returns a dictionary with key job metrics.
    """
    try:
        # Send an HTTP GET request to fetch the webpage content
        response = requests.get(ADP_URL)
        response.raise_for_status()  # Raises an error if the request fails (e.g., website is down)

        # Parse the webpage content using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Locate the section containing employment data
        # This class name may change, so update it based on the actual HTML structure
        data_section = soup.find("div", class_="employment_numbers")  # Example class (Update if needed)

        # Dictionary to store extracted job data
        job_data = {}

        # If the employment numbers section is found, extract data
        if data_section:
            # Find all metric titles (e.g., 'Total Nonfarm Employment', 'Private Payroll')
            job_titles = data_section.find_all("h2")  # ADP may use <h2> for job titles

            # Find all corresponding values (e.g., '+140,000 jobs added')
            job_values = data_section.find_all("p")  # ADP may use <p> for values

            # Loop through the extracted data and store it in the dictionary
            for title, value in zip(job_titles, job_values):
                job_data[title.text.strip()] = value.text.strip()  # Clean and store data
            
        return job_data  # Return dictionary with extracted job numbers

    except requests.RequestException as e:
        # If there's a problem fetching the webpage, print an error message
        print(f"Error fetching ADP Jobs data: {e}")
        return None  # Return None to indicate failure

# Function to save job data to an Excel file
def save_adp_to_excel(job_data, filename="adp_jobs_data.xlsx"):
    """
    Converts ADP job data to a pandas DataFrame and saves it to an Excel file.

    :param job_data: Dictionary containing job metrics and their values.
    :param filename: Name of the Excel file to save data.
    """
    if job_data:
        # Convert the dictionary to a DataFrame
        df = pd.DataFrame(job_data.items(), columns=["Metric", "Value"])

        # Save the DataFrame to an Excel file using 'openpyxl' engine
        df.to_excel(filename, index=False, engine='openpyxl')

        # Print a success message
        print(f"ADP Jobs data saved to {filename}")
    else:
        # Print a message if no data was fetched
        print("No data to save.")

# Main execution block - Fetches and saves ADP job data
if __name__ == "__main__":
    """
    - Fetches job report from ADP's website.
    - Converts it into a structured DataFrame.
    - Saves the data to an Excel file for analysis.
    """
    adp_jobs = scrape_adp_jobs()  # Scrape ADP jobs data
    if adp_jobs:  # If data is successfully fetched
        save_adp_to_excel(adp_jobs)  # Save data to Excel
'''

#%% ISM Employment Components Data Pull 
'''
import requests  # For making HTTP requests
from bs4 import BeautifulSoup  # For parsing HTML content
import pandas as pd  # For structuring and saving data

# Define ISM URLs for Manufacturing and Services Reports
ISM_MANUFACTURING_URL = "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/pmi/"
ISM_SERVICES_URL = "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/services/"

# Function to scrape ISM Employment Component from a given URL
def scrape_ism_employment(url, sector):
    """
    Scrapes the ISM Employment Index data from the given ISM sector page.

    :param url: The URL of the ISM report page (Manufacturing or Services)
    :param sector: Name of the sector ("Manufacturing" or "Services")
    :return: A dictionary containing ISM Employment Index data.
    """
    try:
        # Send a GET request to the ISM page
        response = requests.get(url)
        response.raise_for_status()  # Raise an error if request fails

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Locate the Employment Index section (Modify based on HTML structure)
        employment_section = soup.find("div", class_="section")  # Example class (may need to be updated)

        # Dictionary to store ISM Employment Index data
        ism_data = {"Sector": sector, "Employment Index": "N/A"}

        if employment_section:
            # Extract the Employment Index value (Update selector if needed)
            employment_text = employment_section.get_text(strip=True)
            
            # Look for numerical value in the text
            for word in employment_text.split():
                if word.replace(".", "").isdigit():  # Identify a number (e.g., 51.3)
                    ism_data["Employment Index"] = float(word)  # Convert to float
                    break

        return ism_data

    except requests.RequestException as e:
        print(f"Error fetching ISM {sector} Employment data: {e}")
        return None

# Function to save ISM Employment Data to an Excel file
def save_ism_to_excel(ism_data_list, filename="ism_employment_data.xlsx"):
    """
    Saves ISM Employment data to an Excel file.

    :param ism_data_list: List of dictionaries containing ISM Employment Index data.
    :param filename: Name of the output Excel file.
    """
    if ism_data_list:
        df = pd.DataFrame(ism_data_list)  # Convert list of dicts to DataFrame
        df.to_excel(filename, index=False, engine='openpyxl')  # Save to Excel
        print(f"ISM Employment data saved to {filename}")
    else:
        print("No data to save.")

# Main execution block
if __name__ == "__main__":
    """
    - Scrapes ISM Employment Index for Manufacturing & Services.
    - Saves the extracted data into an Excel file.
    """
    ism_employment_data = []

    # Scrape data for both Manufacturing and Services
    ism_manufacturing = scrape_ism_employment(ISM_MANUFACTURING_URL, "Manufacturing")
    ism_services = scrape_ism_employment(ISM_SERVICES_URL, "Services")

    # Append to the list if data was successfully fetched
    if ism_manufacturing:
        ism_employment_data.append(ism_manufacturing)
    if ism_services:
        ism_employment_data.append(ism_services)

    # Save the data to an Excel file
    save_ism_to_excel(ism_employment_data)

'''

#%% Challenger Hiring Announcements
'''
import requests  # For making HTTP requests
from bs4 import BeautifulSoup  # For parsing HTML
import pandas as pd  # For structuring and saving data

# Define the URL for Challenger Reports
CHALLENGER_URL = "https://www.challengergray.com/reports/"

# Function to scrape Challenger hiring announcements
def scrape_challenger_hiring():
    """
    Scrapes Challenger Hiring Announcements from the latest report page.
    
    :return: A list of dictionaries containing hiring announcement data.
    """
    try:
        # Send a GET request to the Challenger Reports page
        response = requests.get(CHALLENGER_URL)
        response.raise_for_status()  # Raise an error for failed requests
        
        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Locate the latest hiring announcement section (Update selector if needed)
        hiring_section = soup.find("section", class_="reports-list")  # Example selector

        # List to store extracted hiring announcements
        hiring_data = []

        if hiring_section:
            # Find all report items within the section
            reports = hiring_section.find_all("article")

            # Loop through reports and extract hiring data
            for report in reports:
                title = report.find("h2").text.strip() if report.find("h2") else "N/A"  # Report title
                date = report.find("time").text.strip() if report.find("time") else "N/A"  # Report date
                link = report.find("a")["href"] if report.find("a") else "N/A"  # Report link

                # Store extracted data
                hiring_data.append({"Date": date, "Title": title, "Report Link": link})

        return hiring_data  # Return extracted hiring announcements

    except requests.RequestException as e:
        print(f"Error fetching Challenger Hiring Announcements: {e}")
        return None

# Function to save hiring data to an Excel file
def save_hiring_to_excel(hiring_data, filename="challenger_hiring_announcements.xlsx"):
    """
    Saves Challenger Hiring Announcements data to an Excel file.

    :param hiring_data: List of dictionaries containing hiring data.
    :param filename: Name of the output Excel file.
    """
    if hiring_data:
        df = pd.DataFrame(hiring_data)  # Convert list of dicts to DataFrame
        df.to_excel(filename, index=False, engine='openpyxl')  # Save to Excel
        print(f"Challenger Hiring Announcements saved to {filename}")
    else:
        print("No data to save.")

# Main execution block
if __name__ == "__main__":
    """
    - Scrapes the latest Challenger Hiring Announcements.
    - Saves the extracted data into an Excel file.
    """
    hiring_announcements = scrape_challenger_hiring()

    if hiring_announcements:  # If data is successfully fetched
        save_hiring_to_excel(hiring_announcements)

'''
#%% Challenger Layoff Announcements Data Pull
'''
import requests  # For making HTTP requests
from bs4 import BeautifulSoup  # For parsing HTML content
import pandas as pd  # For structuring and saving data

# Define the URL for Challenger Reports
CHALLENGER_URL = "https://www.challengergray.com/reports/"

# Function to scrape Challenger Layoff Announcements
def scrape_challenger_layoffs():
    """
    Scrapes Challenger Layoff Announcements from the latest report page.
    
    :return: A list of dictionaries containing layoff announcement data.
    """
    try:
        # Send a GET request to the Challenger Reports page
        response = requests.get(CHALLENGER_URL)
        response.raise_for_status()  # Raise an error for failed requests
        
        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Locate the latest layoff announcement section (Update selector if needed)
        layoff_section = soup.find("section", class_="reports-list")  # Example selector

        # List to store extracted layoff announcements
        layoff_data = []

        if layoff_section:
            # Find all report items within the section
            reports = layoff_section.find_all("article")

            # Loop through reports and extract layoff data
            for report in reports:
                title = report.find("h2").text.strip() if report.find("h2") else "N/A"  # Report title
                date = report.find("time").text.strip() if report.find("time") else "N/A"  # Report date
                link = report.find("a")["href"] if report.find("a") else "N/A"  # Report link

                # Store extracted data
                if "layoff" in title.lower() or "job cuts" in title.lower():  # Filter layoff-related reports
                    layoff_data.append({"Date": date, "Title": title, "Report Link": link})

        return layoff_data  # Return extracted layoff announcements

    except requests.RequestException as e:
        print(f"Error fetching Challenger Layoff Announcements: {e}")
        return None

# Function to save layoff data to an Excel file
def save_layoffs_to_excel(layoff_data, filename="challenger_layoff_announcements.xlsx"):
    """
    Saves Challenger Layoff Announcements data to an Excel file.

    :param layoff_data: List of dictionaries containing layoff data.
    :param filename: Name of the output Excel file.
    """
    if layoff_data:
        df = pd.DataFrame(layoff_data)  # Convert list of dicts to DataFrame
        df.to_excel(filename, index=False, engine='openpyxl')  # Save to Excel
        print(f"Challenger Layoff Announcements saved to {filename}")
    else:
        print("No data to save.")

# Main execution block
if __name__ == "__main__":
    """
    - Scrapes the latest Challenger Layoff Announcements.
    - Saves the extracted data into an Excel file.
    """
    layoff_announcements = scrape_challenger_layoffs()

    if layoff_announcements:  # If data is successfully fetched
        save_layoffs_to_excel(layoff_announcements)
'''

#%% NFIB Data Pull
'''
import requests  # For making HTTP requests
from bs4 import BeautifulSoup  # For parsing HTML content
import pandas as pd  # For structuring and saving data

# Define the NFIB survey URL
NFIB_URL = "https://www.nfib.com/surveys/small-business-economic-trends/"

# Function to scrape NFIB employment and business sentiment data
def scrape_nfib_data():
    """
    Scrapes NFIB employment and business sentiment indicators from the latest report.

    :return: A dictionary containing NFIB key indicators.
    """
    try:
        # Send a GET request to the NFIB page
        response = requests.get(NFIB_URL)
        response.raise_for_status()  # Raise an error for failed requests
        
        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Locate the latest report section (Modify selector based on actual page structure)
        report_section = soup.find("div", class_="article-listing")  # Example class (update if needed)

        # Dictionary to store NFIB employment and business sentiment data
        nfib_data = {
            "Report Date": "N/A",
            "Avg Change in Employment": "N/A",
            "Actual Employment Changes": "N/A",
            "Hiring Plans": "N/A",
            "Job Openings": "N/A",
            "% Positions Not Able to Fill": "N/A",
            "NFIB Small Business Optimism": "N/A",
            "Small Business Outlook": "N/A",
            "Report Link": "N/A"
        }

        if report_section:
            # Find the latest report title and link
            latest_report = report_section.find("a")  # Find first report link
            if latest_report:
                nfib_data["Report Link"] = latest_report["href"]  # Extract the report link
                nfib_data["Report Date"] = latest_report.text.strip()  # Extract report title (date)

            # Extract employment and sentiment-related data
            employment_section = soup.find("div", class_="employment-section")  # Example class (update as needed)
            sentiment_section = soup.find("div", class_="sentiment-section")  # Example class (update as needed)

            if employment_section:
                text_content = employment_section.get_text(strip=True)

                # Extract specific employment data (Modify based on actual report structure)
                if "Average Change in Employment" in text_content:
                    nfib_data["Avg Change in Employment"] = text_content.split("Average Change in Employment:")[1].split()[0]

                if "Actual Employment Changes" in text_content:
                    nfib_data["Actual Employment Changes"] = text_content.split("Actual Employment Changes:")[1].split()[0]

                if "Hiring Plans" in text_content:
                    nfib_data["Hiring Plans"] = text_content.split("Hiring Plans:")[1].split()[0]

                if "Job Openings" in text_content:
                    nfib_data["Job Openings"] = text_content.split("Job Openings:")[1].split()[0]

                if "% Positions Not Able to Fill" in text_content:
                    nfib_data["% Positions Not Able to Fill"] = text_content.split("% Positions Not Able to Fill:")[1].split()[0]

            if sentiment_section:
                sentiment_text = sentiment_section.get_text(strip=True)

                # Extract business sentiment data
                if "NFIB Small Business Optimism" in sentiment_text:
                    nfib_data["NFIB Small Business Optimism"] = sentiment_text.split("NFIB Small Business Optimism:")[1].split()[0]

                if "Small Business Outlook" in sentiment_text:
                    nfib_data["Small Business Outlook"] = sentiment_text.split("Small Business Outlook:")[1].split()[0]

        return nfib_data  # Return extracted NFIB data

    except requests.RequestException as e:
        print(f"Error fetching NFIB data: {e}")
        return None

# Function to save NFIB data to an Excel file
def save_nfib_to_excel(nfib_data, filename="nfib_employment_data.xlsx"):
    """
    Saves NFIB Employment & Business Sentiment data to an Excel file.

    :param nfib_data: Dictionary containing NFIB data.
    :param filename: Name of the output Excel file.
    """
    if nfib_data:
        df = pd.DataFrame([nfib_data])  # Convert dict to DataFrame
        df.to_excel(filename, index=False, engine='openpyxl')  # Save to Excel
        print(f"NFIB Employment & Business Sentiment data saved to {filename}")
    else:
        print("No data to save.")

# Main execution block
if __name__ == "__main__":
    """
    - Scrapes NFIB Employment and Business Sentiment data.
    - Saves the extracted data into an Excel file.
    """
    nfib_data = scrape_nfib_data()

    if nfib_data:  # If data is successfully fetched
        save_nfib_to_excel(nfib_data)
'''
