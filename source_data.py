#%% Import Libraries 

import pandas as pd  # Import pandas for data manipulation
from fredapi import Fred  # Import Fred API to fetch economic data

# Set up FRED API with your unique key (Replace "YOUR_FRED_API_KEY" with your actual key)
FRED_API_KEY = "YOUR_FRED_API_KEY"
fred = Fred(api_key=FRED_API_KEY)

#%% FRED Data Pull

# Specify the path to your CSV file
csv_file = "Data Sources.csv"  # Update the file path if needed

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
    
    for indicator, series_id in series_dict.items():  # Loop through each indicator and FRED Series ID
        try:
            print(f"Fetching {indicator} ({series_id})...")  # Print which series is being fetched
            data_dict[indicator] = fred.get_series(series_id)  # Fetch time-series data from FRED
        except Exception as e:  # Handle any errors
            print(f"Failed to fetch {indicator}: {e}")  # Print an error message if fetching fails
            
    return data_dict  # Return the collected data

# Function to convert fetched data into a DataFrame
def format_data_to_df(data_dict):
    """
    Converts the fetched FRED data dictionary into a pandas DataFrame.

    :param data_dict: Dictionary with indicator names as keys and time series data as values.
    :return: A pandas DataFrame where each column represents an economic indicator.
    """
    df = pd.DataFrame(data_dict)  # Convert dictionary to DataFrame
    df.index = pd.to_datetime(df.index)  # Ensure the index is in datetime format (for time series analysis)
    return df  # Return the formatted DataFrame

# Function to save the DataFrame to an Excel file
def save_to_excel(df, filename="economic_data_extended.xlsx"):
    """
    Saves the DataFrame to an Excel file.

    :param df: The DataFrame containing economic data.
    :param filename: The name of the output Excel file (default is 'economic_data_extended.xlsx').
    """
    df.to_excel(filename, engine='openpyxl')  # Save DataFrame to an Excel file
    print(f"Data saved to {filename}")  # Print confirmation message

# Main execution: Fetch data, convert it to a DataFrame, and save it
if __name__ == "__main__":
    """
    Main execution block:
    - Fetches FRED data based on the CSV file.
    - Converts it into a structured DataFrame.
    - Saves the data to an Excel file.
    """
    data = fetch_fred_data(fred_series_dict)  # Fetch data from FRED
    df = format_data_to_df(data)  # Convert to DataFrame
    save_to_excel(df)  # Save DataFrame to Excel


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