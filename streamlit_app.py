import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pycountry
import time
import calendar
from datetime import datetime
import humanize
import re


csv_file= "web_logs.csv"

@st.cache(ttl=60)
def load_data():
    # Load data from CSV file
    return pd.read_csv("web_logs.csv")
        
def load_and_clean_data(csv_file):
    # Load raw data from CSV
    raw_data = pd.read_csv(csv_file, header=None)

    # Extract information from raw data
    cleaned_data = raw_data[0].str.extract(r'(\d+\.\d+\.\d+\.\d+) - - \[(.*?)\] - \[(.*?)\]\"(.+?)\" (\d+) (\d+) \"(.+?)\" \"(\w+)\" \"(.+?)\"')

    # Rename the columns
    cleaned_data.columns = ['IP Address', 'Timestamp Start', 'Timestamp End', 'Request', 'Status Code', 'Response Size', 'User Agent', 'Country Code', 'Traffic Source']

    # Convert timestamps to datetime format
    cleaned_data['Timestamp Start'] = pd.to_datetime(cleaned_data['Timestamp Start'], format='%d/%b/%Y:%H:%M:%S')
    cleaned_data['Timestamp End'] = pd.to_datetime(cleaned_data['Timestamp End'], format='%d/%b/%Y:%H:%M:%S')

    return cleaned_data

# Function to download the cleaned data
def download_cleaned_data(cleaned_data):
    csv = cleaned_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name='cleaned_data.csv',
        mime='text/csv',
    )

# Function for dashboard
def dashboard_page(cleaned_data):
    st.title('FUN OLYMPICS DASHBOARD')

    # Create a dropdown menu to select columns
    selected_columns = st.multiselect("Select columns to display", ["Display all columns"] + cleaned_data.columns.tolist())

    # If no columns are selected, display a warning message
    if not selected_columns:
        st.warning("Click to view CSV.")

    # If "Display all columns" option is chosen, display the first 5 records of the entire DataFrame
    elif "Display all columns" in selected_columns:
        st.write(cleaned_data.head())

    # If columns are selected, display the first 5 records with selected columns
    else:
        st.write(cleaned_data[selected_columns].head())
    
    
    download_cleaned_data(cleaned_data)

    # Date filters
    st.subheader('Select Date Range')
    
    col1, col2 = st.columns(2)

    # Define the range for generating logs
    generation_start_date = pd.Timestamp(2024, 5, 30)
    generation_end_date = pd.Timestamp(2024, 8, 30)

    # Set the default value for the date input fields
    default_start_date = generation_start_date
    default_end_date = generation_end_date

    with col1:
        start_date = st.date_input('Start Date', value=default_start_date, min_value=generation_start_date, max_value=generation_end_date)
    with col2:
        end_date = st.date_input('End Date', value=default_end_date, min_value=generation_start_date, max_value=generation_end_date)

    if start_date > end_date:
        st.warning("Start date must be before end date.")
        return

    # Filter data based on the selected date range
    filtered_data = cleaned_data[
        (pd.to_datetime(cleaned_data['Timestamp Start']) >= pd.to_datetime(start_date)) & 
        (pd.to_datetime(cleaned_data['Timestamp Start']) <= pd.to_datetime(end_date))
    ]

    # Calculate total visits
    total_visits = filtered_data.shape[0]

    # Calculate number of live sessions from Olympic Channel
    live_sessions_olympic_channel = filtered_data['Request'].str.contains('/olympic-channel/live-stream').sum()

    # Total live sessions
    total_live_sessions = live_sessions_olympic_channel

    # Calculate total page views
    total_page_views = filtered_data['Request'].nunique()
    
    # Calculate average session duration
    filtered_data['Session Duration'] = (filtered_data['Timestamp End'] - filtered_data['Timestamp Start']).dt.total_seconds()
    average_session_duration = filtered_data['Session Duration'].mean()

    # Format the numbers for presentation
    formatted_total_visits = humanize.intcomma(total_visits)
    formatted_total_page_views = humanize.intcomma(total_page_views)
    formatted_total_live_streams = humanize.intcomma(total_live_sessions)
    formatted_average_session_duration = humanize.naturaldelta(average_session_duration)

    # Display metrics using st.metric() function
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Log Entries", formatted_total_visits)

    with col2:
        st.metric("Page Views", formatted_total_page_views)

    with col3:
        st.metric("Live Streams", formatted_total_live_streams)

    with col4:
        st.metric("Avg. Session Duration (m)", formatted_average_session_duration)

    st.subheader("Traffic Analysis")

    analysis_option = st.selectbox("Select analysis option", ["Traffic Per Hour", "Traffic Per Day", "Traffic Per Week", "Traffic Per Month"])

    if analysis_option == "Traffic Per Hour":
        analyze_traffic_per_hour(filtered_data)
    elif analysis_option == "Traffic Per Day":
        analyze_traffic_per_day(filtered_data)
    elif analysis_option == "Traffic Per Week":
        analyze_traffic_per_week(filtered_data)
    elif analysis_option == "Traffic Per Month":
        analyze_traffic_per_month(filtered_data)


    #  Extract relevant information from User Agent strings
    if 'User Agent' in filtered_data.columns:
        filtered_data['Browser'] = filtered_data['User Agent'].str.extract(r'(?P<Browser>Chrome|Firefox|Edge|Safari)')
        filtered_data['Device'] = filtered_data['User Agent'].str.extract(r'(?P<Device>\bAndroid\b|\biPad\b|\biPhone\b|\bWindows\b|\bMacintosh\b|\bLinux\b)')

    # Ensure 'Browser' and 'Device' columns exist
    if 'Browser' in filtered_data.columns:
        browser_counts = filtered_data['Browser'].value_counts()
    else:
        browser_counts = pd.Series([], name='Browser')

    if 'Device' in filtered_data.columns:
        device_counts = filtered_data['Device'].value_counts()
    else:
        device_counts = pd.Series([], name='Device')
    
    #traffic analysis
    traffic_sources = filtered_data['Traffic Source'].value_counts().reset_index()
    traffic_sources.columns = ['Traffic Source', 'Count']

    # Assuming cleaned_data contains the relevant column for status codes
    error_data = filtered_data['Status Code'].value_counts().reset_index()
    error_data.columns = ['Status Code', 'Count']
    
    #Response Size distribution
    response_size_data = filtered_data['Response Size'].describe().reset_index()
    response_size_data.columns = ['Metric', 'Value']

    # most requested page 
    # Extract page path from request URLs
    filtered_data['page'] = filtered_data['Request'].apply(lambda x: x.split()[1])

    # Most accessed pages
    most_accessed_pages = filtered_data['page'].value_counts().reset_index()
    most_accessed_pages.columns = ['Page', 'Count']

    top_n = 10  # Change this number to the desired number of top pages
    top_pages = most_accessed_pages.head(top_n)

    # Live stream interaction
    # Extract interactions
    chats = filtered_data[filtered_data['Request'].str.contains('/olympic-channel/live-stream/.*/chat')]
    polls = filtered_data[filtered_data['Request'].str.contains('/olympic-channel/live-stream/.*/poll')]
    share_reactions = filtered_data[filtered_data['Request'].str.contains('/olympic-channel/live-stream/.*/share-reaction')]

    # Count interactions
    interaction_counts = pd.DataFrame({
        'Interaction Type': ['Chat', 'Poll', 'Share Reaction'],
        'Count': [len(chats), len(polls), len(share_reactions)]
    })
    
    # Extract the sports event and interaction type from the 'Request' column
    filtered_data[['Sports Event', 'Interaction']] = filtered_data['Request'].str.extract(r'/olympic-channel/live-stream/(\w+)/(.*?)\b')
    
    # Count the number of interactions for each sports event
    top_sports = filtered_data.groupby('Sports Event').size().reset_index(name='Interactions').sort_values(by='Interactions', ascending=False)
    
    # Filter top 10 sports
    top_sports = top_sports.head(10)

    # Create two columns for displaying visuals side by side
    col1, col2 = st.columns(2)

    # Add browser distribution visualization to the first column
    with col1:
        st.plotly_chart(px.bar(browser_counts, x=browser_counts.index, y=browser_counts.values, labels={'x': 'Browser', 'y': 'Count'}, title='Browser Distribution', height=350, width=300))

    # Add device distribution visualization to the second column
    with col2:
        st.plotly_chart(px.bar(device_counts, x=device_counts.index, y=device_counts.values, labels={'x': 'Device', 'y': 'Count'}, title='Device Distribution', height=350, width=300))
    
    col1, col2 = st.columns(2)
    # Add traffic source analysis visualization (Pie chart) to the first column
    with col1:
        st.plotly_chart(px.pie(traffic_sources, names='Traffic Source', values='Count', title='Traffic Sources Distribution', height=400, width= 350))

    # Add error analysis visualization (Bar graph) to the second column
    with col2:
        st.plotly_chart(px.pie(error_data,
        names='Status Code',
        values='Count',
        title='Error Analysis', height=400, width= 350))
    
    col1, col2 = st.columns(2)   
    # Distribution of response sizes (Histogram)
    with col1:
        st.plotly_chart(px.histogram(filtered_data, x='Response Size', nbins=50, title='Distribution of Response Sizes', height=400, width= 300))
    
    with col2:
        fig = go.Figure(data=[go.Table(
            header=dict(values=['Page', 'Count'],
                        fill_color='light blue',
                        align='left'),
            cells=dict(values=[top_pages.Page, top_pages.Count],
                        fill_color='light gray',
                        align='left'))
        ])
        fig.update_layout(
            title='Top Accessed Pages',  
            height=400,  # Adjust height to fit within the column
            margin=dict(l=0, r=0, b=0, t=100)  # Adjust margins as needed
        )
        st.plotly_chart(fig, use_container_width=True)

    # Create two columns for displaying visuals side by side
    col1, col2 = st.columns(2)

    # Add Donut Chart to the first column
    with col1:
        fig_donut_chart = px.pie(interaction_counts, 
                             values='Count', 
                             names='Interaction Type', 
                             title='Viewership Interactions',
                             hole=0.4)
        fig_donut_chart.update_layout(width=300, height=350)
        st.plotly_chart(fig_donut_chart)

    with col2:
        # Create a vertical bar chart for the top sports
        fig_top_sports = px.bar(top_sports, 
                                x='Sports Event', 
                                y='Interactions', 
                                title='Top 10 Viewed Sports Based on Interactions', 
                                labels={'Sports Event': 'Sport', 'Interactions': 'Interaction Count'},
                                color='Interactions')
        fig_top_sports.update_layout(width=400, height=400)
        # Display the bar chart in Streamlit
        st.plotly_chart(fig_top_sports)

    st.subheader("Number Of Visit Analysis")
    # Create a multi-select menu for country analysis columns
    country_analysis_columns = st.multiselect("Select columns for analysis", ["Country Code", "Timestamp Start"])

    # Show the appropriate visualization based on the selected columns
    country_names = {c.alpha_2: c.name for c in pycountry.countries}
    if "Country Code" in country_analysis_columns and "Timestamp Start" in country_analysis_columns:
        # Compare time of visit with number of visits by country
        filtered_data['hour'] = pd.to_datetime(filtered_data['Timestamp Start']).dt.hour
        time_country_visits = filtered_data.groupby(['Country Code', 'hour']).size().reset_index(name='Number of Visits')
        time_country_visits['Country Name'] = time_country_visits['Country Code'].map(country_names)
        fig = px.line(time_country_visits, x='hour', y='Number of Visits', color='Country Name', title='Number of Visits by Time and Country', height=600, width=600)
        fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(24)),
                ticktext=[f'{hour:02}:00' for hour in range(24)]
            )
        )
        st.plotly_chart(fig)

    elif "Country Code" in country_analysis_columns:
        # Number of visits by country visualization
        visits_by_country = filtered_data['Country Code'].value_counts().reset_index()
        visits_by_country.columns = ['Country Code', 'Number of Visits']
        st.plotly_chart(px.bar(visits_by_country, x='Country Code', y='Number of Visits', title='Number of Visits by Country'))
    

# Function to analyze traffic per hour
def analyze_traffic_per_hour(df):
    # Assuming df contains Timestamp Start column
    df['hour'] = pd.to_datetime(df['Timestamp Start']).dt.hour

    # Grouping data by hour and counting the number of requests
    traffic_per_hour = df.groupby('hour').size().reset_index(name='count')

    # Plotting traffic per hour
    fig = px.line(traffic_per_hour, x='hour', y='count', title='Traffic Per Hour')
    
    # Customize x-axis labels to display actual hours
    fig.update_layout(
        xaxis=dict(
            title='Hour of the Day',
            tickmode='array',
            tickvals=list(range(24)),  # Hourly values from 0 to 23
            ticktext=[f'{hour:02}:00' for hour in range(24)]  # Format labels as 'hour:00'
        ),
        yaxis=dict(title='Traffic Count')
    )

    st.plotly_chart(fig)

def analyze_traffic_per_day(df):
    # Assuming df contains Timestamp Start column
    df['day'] = pd.to_datetime(df['Timestamp Start']).dt.date

    # Grouping data by day and counting the number of requests
    traffic_per_day = df.groupby('day').size().reset_index(name='count')

    # Plotting traffic per day
    fig = px.line(traffic_per_day, x='day', y='count', title='Traffic Per Day')

    # Customize x-axis labels
    fig.update_layout(
        xaxis=dict(title='Day'),
        yaxis=dict(title='Traffic Count')
    )

    st.plotly_chart(fig)

# Function to analyze traffic per week
def analyze_traffic_per_week(df):
    # Assuming df contains timestamp_start column
    df['week'] = pd.to_datetime(df['Timestamp Start']).dt.isocalendar().week

    # Grouping data by week and counting the number of requests
    traffic_per_week = df.groupby('week').size().reset_index(name='count')

    # Plotting traffic per week
    fig = px.bar(traffic_per_week, x='week', y='count', title='Traffic Per Week')
    st.plotly_chart(fig)

# Function to analyze traffic per month
def analyze_traffic_per_month(df):
    # Assuming df contains Timestamp Start column
    df['month'] = pd.to_datetime(df['Timestamp Start']).dt.month

    # Grouping data by month and counting the number of requests
    traffic_per_month = df.groupby('month').size().reset_index(name='count')
    
    # Get month names
    traffic_per_month['month'] = traffic_per_month['month'].apply(lambda x: calendar.month_name[x])

    # Plotting traffic per month
    fig = px.bar(traffic_per_month, x='month', y='count', title='Traffic Per Month')
    st.plotly_chart(fig)

# Function for Exploratory Data Analysis
def perform_eda(df):

    # Interactive widgets for exploratory data analysis
    st.title("Exploratory Data Analysis")

    # Display basic statistics
    st.subheader("OLYMPICS BASIC STATISTICS ")
    st.write(df.describe())

    # Country of Origin Analysis
    country_names = {c.alpha_2: c.name for c in pycountry.countries}
    st.subheader("COUNTRY OF ORIGIN ANALYSIS")
    country_visits = df['Country Code'].value_counts().rename(index=country_names)
    st.write(country_visits)

    # Total number of visits from all countries
    total_visits = country_visits.sum()
    
    # Display the total number of visits
    st.write("Total Visits:", total_visits)
    
    # Top countries with the highest number of visits
    top_countries = country_visits.head(5)  # Change 5 to the desired number of top countries
    st.write("Top 5 Countries with the Highest Number of Visits:")
    st.write(top_countries)

    #Time Visit Analysis
    st.subheader("TIME OF VISIT ANALYSIS")
    # Extract hour and day from the timestamp
    df['Hour'] = df['Timestamp Start'].dt.hour
    df['Date'] = df['Timestamp Start'].dt.date
    df['week'] = df['Timestamp Start'].dt.isocalendar().week
    df['month']= df['Timestamp Start'].dt.month
    # Group visits by hour
    visits_by_hour = df.groupby(df['Timestamp Start'].dt.strftime('%H:00')).size()
    
    # Display the results
    st.write("Visits by Hour:")
    st.write(visits_by_hour)

    # Find the hour with the highest number of visits
    peak_hour = visits_by_hour.idxmax()

    # Get the number of visits during the peak hour
    peak_hour_visits = visits_by_hour.max()

    # Display the peak hour and the number of visits during that hour
    st.write(f"The peak period is at {peak_hour} with {peak_hour_visits} visits.")
    
    # Group visits by day
    visits_by_day = df.groupby('Date').size()
     
    st.write("\nVisits by Day:")
    st.write(visits_by_day)

    # Find the day with the highest number of visits
    peak_day = visits_by_day.idxmax()
    peak_day_visits = visits_by_day.max()

    st.write(f"The peak day is: {peak_day} with {peak_day_visits} visits.")

    # Group visits by week
    visits_by_week = df.groupby('week').size()
    st.write("\nVisits by week:")
    st.write(visits_by_week)

    # Find the week with the highest number of visits
    peak_week = visits_by_week.idxmax()
    peak_week_visits = visits_by_week.max()

    st.write(f"The peak week is: week {peak_week} with {peak_week_visits} visits.")

    # Group visits by month
    visits_by_month = df.groupby('month').size()
    #traffic_per_month = df.groupby('month').size().reset_index(name='count')
    st.write("\nVisits by month:")
    st.write(visits_by_month)

    # Find the month with the highest number of visits
    peak_month_number = int(visits_by_month.idxmax())
    peak_month_visits = visits_by_month.max()
    # Convert month number to month name
    peak_month_name = calendar.month_name[peak_month_number]

    st.write(f"The peak month is in {peak_month_name} with {peak_month_visits} visits.")
    
    
    # Number of Visits Analysis
    st.subheader("NUMBER OF VISITS ANALYSIS")
    
    # Basic summary statistics
    st.subheader("Basic Statistics")
    st.write("Average number of visits per day:")
    st.write(df.groupby(df['Timestamp Start'].dt.date).size().mean())
    st.write("Maximum number of visits in a single day:")
    st.write(df.groupby(df['Timestamp Start'].dt.date).size().max())
    st.write("Minimum number of visits in a single day:")
    st.write(df.groupby(df['Timestamp Start'].dt.date).size().min())
   

    # Number of Visits to Each Page
    st.subheader("Number of Visits to Each Page")
    page_visits = df['Request'].apply(lambda x: x.split()[1]).value_counts()
    st.write("Number of Visits to Each Page:")
    st.write(page_visits)

    # Display popular pages
    st.subheader("Popular Pages")
    popular_pages = page_visits.head(5)  # Display the top 5 most visited pages
    st.write(popular_pages)

    # Traffic source Analysis
    st.subheader("TRAFFIC SOURCE ANALYSIS")
    
    # Basic Statistics for Traffic Sources
    st.subheader("Basic Statistics for Traffic Sources")
    traffic_source_counts = df['Traffic Source'].value_counts()
    st.write("Number of Visits by Traffic Source:")
    st.write(traffic_source_counts)
    st.write("Total Number of Unique Traffic Sources:", len(traffic_source_counts))
    st.write("Most Common Traffic Source:", traffic_source_counts.idxmax())
    
    # Traffic source Analysis
    st.subheader(" ERROR ANALYSIS")
    
    # Distribution of status codes
    st.subheader("Basic Statistics for Status Codes")
    
    # Basic Statistics for Status Codes
    status_code_counts = df['Status Code'].value_counts()
    st.write("Number of Occurrences by Status Code:")
    st.write(status_code_counts)
    st.write("Total Number of Unique Status Codes:", len(status_code_counts))
    st.write("Most Common Status Code:", status_code_counts.idxmax())

    # MAIN INTERESTS ANALYSIS

    st.subheader("Main Interests (Based on Selected/Viewed Sports)")

    # Top sports
    st.write("Favourites Analysis:")
    st.write("Top Favourite Sports")
    top_sports_events = df[df['Request'].str.contains('/sports/')]['Request'].value_counts().head(5)
    st.write(top_sports_events)


    st.subheader("Top Sports Selected/Viewed")
    
    # Extract the sports event and interaction type from the 'Request' column
    df[['Sports Event', 'Interaction']] = df['Request'].str.extract(r'/olympic-channel/live-stream/(\w+)/(.*?)\b')

    # Count the number of interactions for each sports event
    top_sports = df.groupby('Sports Event').size().reset_index(name='Interactions').sort_values(by='Interactions', ascending=False)
    
    # Display the top viewed or selected sports
    st.write("Top Viewed/Selected Sports:")
    st.write(top_sports)

    live_streams = df[df['Request'].str.contains('/olympic-channel/live-stream')]
    chats = df[df['Request'].str.contains('/olympic-channel/live-stream/.*/chat')]
    polls = df[df['Request'].str.contains('/olympic-channel/live-stream/.*/poll')]
    share_reactions = df[df['Request'].str.contains('/olympic-channel/live-stream/.*/share-reaction')]

    # Count the number of live stream sessions, chats, polls, and share reactions
    num_live_streams = len(live_streams)
    num_chats = len(chats)
    num_polls = len(polls)
    num_share_reactions = len(share_reactions)

    # Display the results
    st.subheader("Viewership Analysis")
    st.write("Number of Live Stream Sessions:", num_live_streams)
    st.write("Number of Chats:", num_chats)
    st.write("Number of Polls:", num_polls)
    st.write("Number of Share Reactions:", num_share_reactions)

    # Extract the sports being streamed from the request URLs
    live_streams['Sport'] = live_streams['Request'].str.extract(r'/olympic-channel/live-stream/(\w+)')

    # Calculate the duration of each live stream session
    live_streams['Timestamp Start'] = pd.to_datetime(live_streams['Timestamp Start'])
    live_streams['Timestamp End'] = pd.to_datetime(live_streams['Timestamp End'])
    live_streams['Duration'] = (live_streams['Timestamp End'] - live_streams['Timestamp Start']).dt.total_seconds()

    # Calculate the average duration of live stream sessions for each sport
    average_durations = live_streams.groupby('Sport')['Duration'].mean()

    # Display the average duration of live stream sessions for each sport
    st.subheader("Average Duration of Live Stream Sessions by Sport")
    st.write(average_durations)  


    #Analysing user agents
    st.subheader("USER AGENT ANALYSIS")

    # Extract relevant information from User Agent strings
    df['Browser'] = df['User Agent'].str.extract(r'(?P<Browser>Chrome|Firefox|Edge|Safari)')
    df['Device'] = df['User Agent'].str.extract(r'(?P<Device>\bAndroid\b|\biPad\b|\biPhone\b|\bWindows\b|\bMacintosh\b|\bLinux\b)')

    # Count occurrences of each unique combination
    browser_counts = df['Browser'].value_counts()
    device_counts = df['Device'].value_counts()

    # Display the counts as dataframes
    st.write("Browser Distribution")
    st.dataframe(browser_counts)

    st.write("Device Distribution")
    st.dataframe(device_counts)

# Main function
def main():
    st.sidebar.image("paris2024.png", caption="PAYRIS FUN OLYMPICS" )
    selected_page = st.sidebar.radio("Navigation", ["Dashboard", "Exploratory Data Analysis"])

    if selected_page == "Dashboard":
        cleaned_data = load_and_clean_data("web_logs.csv")
        dashboard_page(cleaned_data)
    elif selected_page == "Exploratory Data Analysis":
        df = load_and_clean_data("web_logs.csv")
        perform_eda(df)

if __name__ == "__main__":
    while True:
        main()
        time.sleep(60)  # Sleep for 60 seconds before rerunning
        st.rerun()
