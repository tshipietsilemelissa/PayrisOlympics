import requests
import csv
import pandas as pd
import time
import random

csv_file = "web_logs.csv"

# Function to fetch data from the API
def fetch_raw_data_from_api(count=None):
    api_url = "http://127.0.0.1:5000/generate-logs"
    
    # If count is provided, append it to the URL as a query parameter
    if count is not None:
        api_url += f"?count={count}"
    
    print(f"Fetching data from API with count: {count}")  # Debugging print statement
    
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Received {len(data)} logs from the API")  # Debugging print statement
        return data
    else:
        print("Error: Failed to retrieve data from the API")
        return None

# Function to save data to a CSV file
def save_raw_to_csv(raw_data):
    if raw_data:
        with open(csv_file, "a", newline="") as csvfile: # appends new logs to the csv file
            writer = csv.writer(csvfile)
            for raw_log in raw_data:
                writer.writerow([raw_log])
        print(f"Raw data saved to CSV file: {csv_file}")
    else:
        print("No raw data to save.")

# Function to update CSV file periodically
def update_csv(iterations=1):
    for _ in range(iterations):
        # Simulating variable number of logs fetched
        new_logs_count = random.randint(300, 5000)  # Simulate between 300 to 5000 logs fetched
        
        # Fetch new data from the API with the specified count
        raw_data = fetch_raw_data_from_api(count=new_logs_count)
        
        if raw_data:
            # Convert fetched raw data to DataFrame
            new_data = pd.DataFrame(raw_data, columns=["log"])

            # Load existing data
            try:
                existing_data = pd.read_csv(csv_file, header=None, names=["log"])
            except FileNotFoundError:
                existing_data = pd.DataFrame(columns=["log"])

            # Append new data to existing data
            updated_data = pd.concat([existing_data, new_data])

            # Save updated data back to the CSV file
            updated_data.to_csv(csv_file, index=False, header=False)

            print(f"Updated CSV file with {len(new_data)} new entries.")

        # Wait for 60 seconds before fetching new data again
        time.sleep(60)

if __name__ == "__main__":
    # Start updating the CSV file
    while True:
        update_csv()
