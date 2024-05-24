from flask import Flask, jsonify, request
import random
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# Define weighted probabilities for countries
countries_weights = {
    'US': 600,
    'IN': 470,
    'CN': 300,
    'BR': 230,
    'RU': 180,
    'JP': 130,
    'DE': 110,
    'ID': 110,
    'NG': 400,
    'PK': 120,
    'MX': 100,
    'FR': 90,
    'IT': 80,
    'KR': 70,
    'TR': 60,
    'GB': 50,
    'IR': 40,
    'TH': 30,
    'EG': 25,
    'VN': 20,
    'AR': 15,
    'PH': 10,
    'ES': 5,
    'CA': 3,
    'SA': 2
}

# Define weighted probabilities for status codes
status_codes_weights = {
    200: 400,
    301: 20,
    404: 150,
    500: 50,
    
}

# Define weighted probabilities for traffic sources
traffic_sources_weights = {
    'Organic Search': 300,
    'Facebook': 200,
    'Paid Advertising': 150,
    'Tik tok': 120,
    'Twitter': 100,
    'Youtube': 50
}

# Define weighted probabilities for pages
pages_weights = {
    '/home': 150,
    '/sports': 200,
    '/olympic-channel': 300,
    '/news': 30,
    '/schedule': 5
}

# Define weighted probabilities for sports events
sports_events_weights = {
    'Athletics': 300,
    'Basketball': 100,
    'Badminton': 80,
    'Cricket': 120,
    'Diving': 70,
    'Fencing': 90,
    'Football': 200,
    'Golf': 40,
    'hockey': 150,
    'Gymnastics': 100,
    'karate': 60,
    'Swimming': 110,
    'Tennis': 130,
    'Volleyball': 80,
    'Weightlifting': 70
}


# List of example HTTP methods
http_methods = ['GET', 'POST']

# Define user agents
user_agents = [
    # Windows Browsers
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/17.17134 Safari/537.36",
    # macOS Browsers
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/61.0",
    # Linux Browsers
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0",
    # Mobile Browsers
    "Mozilla/5.0 (Linux; Android 8.0.0; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_6 like Mac OS X) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0 Mobile/15D100 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 9; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Mobile Safari/537.36",
    # Tablet Browsers
    "Mozilla/5.0 (iPad; CPU OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Mobile/15E148 Safari/604.1",  # iPad
    "Mozilla/5.0 (Linux; Android 8.0.0; SM-T350 Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.101 Safari/537.36",  # Android Tablet
    "Mozilla/5.0 (Linux; Android 9; SM-T350) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.101 Safari/537.36"  # Android Tablet
]

# Function to randomly select an item based on weighted probabilities
def weighted_random(weights):
    total_weight = sum(weights.values())
    rand = random.uniform(0, total_weight)
    for item, weight in weights.items():
        rand -= weight
        if rand <= 0:
            return item

# Function to generate a single log entry within a specific date range
def generate_raw_log_entry(start_date, end_date):
    ip_address = '.'.join(str(random.randint(0, 255)) for _ in range(4))
    country_code = weighted_random(countries_weights)
    status_code = weighted_random(status_codes_weights)
    traffic_source = weighted_random(traffic_sources_weights)
    sports_event = weighted_random(sports_events_weights)

    timestamp_start = (start_date + timedelta(seconds=random.randint(0, int((end_date - start_date).total_seconds())))).strftime("%d/%b/%Y:%H:%M:%S")
    session_duration = random.randint(60, 3600)  # Random session duration between 1 minute and 1 hour (in seconds)
    timestamp_end = (datetime.strptime(timestamp_start, "%d/%b/%Y:%H:%M:%S") + timedelta(seconds=session_duration)).strftime("%d/%b/%Y:%H:%M:%S")
    http_method = random.choice(http_methods)
    page = weighted_random(pages_weights)
    request = f'{http_method} {page} HTTP/1.1'

    if page == '/home':
        if random.random() < 0.3:  # 20% chance of accessing upcoming events
            request = 'GET /home/upcoming-events HTTP/1.1'
        elif random.random() < 0.45:  # 20% chance of accessing popular videos
            request = 'GET /home/popular-videos HTTP/1.1'
        elif random.random() < 0.6:  # 20% chance of accessing news updates
            request = 'GET /home/news-updates HTTP/1.1'
        else: 
            request = 'GET /home/highlights HTTP/1.1' 
    elif page == '/olympic-channel':
        sports_event = weighted_random(sports_events_weights)
        if random.random() < 0.5:  # 50% chance of joining/ watching live stream sessions  
            request = f'POST /olympic-channel/live-stream/{sports_event} HTTP/1.1'
        elif random.random() < 0.75:  # 25% chance of interacting with live chat, polls, or reactions that are related to the sport being live streamed
            request = random.choice([f'POST /olympic-channel/live-stream/{sports_event}/chat HTTP/1.1', f'POST /olympic-channel/live-stream/{sports_event}/poll HTTP/1.1', f'POST /olympic-channel/live-stream/{sports_event}/share-reaction HTTP/1.1'])
        else:  # 50% chance of ending live stream
            request = f'POST /olympic-channel/live-stream/{sports_event}/end HTTP/1.1'  # Example: Ending live stream for a specific sport
    elif page == '/sports':
        if random.random() < 0.2:   # 20% chance of browsing sports categories
            sports_event = weighted_random(sports_events_weights)
            request = f'GET /sports/{sports_event} HTTP/1.1'
        elif random.random() < 0.3:  # 10% chance of checking the schedule
            request = 'GET /sports/schedule HTTP/1.1'
        else:  # 40% chance of favoriting or following specific sports
            sports_event = weighted_random(sports_events_weights)
            request = f'POST /sports/{sports_event}/favorite HTTP/1.1'

    response_size = random.randint(100, 1000)
    user_agent = random.choice(user_agents)
    return f"{ip_address} - - [{timestamp_start}] - [{timestamp_end}]\"{request}\" {status_code} {response_size} \"{user_agent}\" \"{country_code}\" \"{traffic_source}\""

# Function to generate logs within a specific date range
def generate_raw_logs(start_date, end_date, num_logs):
    raw_logs = []
    for _ in range(num_logs):
        raw_log_entry = generate_raw_log_entry(start_date, end_date)
        raw_logs.append(raw_log_entry)
    return raw_logs

@app.route('/')
def index():
    return "Welcome to the Payris fun Olympic API. To access logs, please visit the '/generate-logs' endpoint."

@app.route('/generate-logs', methods=['GET'])
def get_raw_logs():
    start_date = datetime(2024, 5, 30)
    end_date = datetime(2024, 8, 30)
    count = int(request.args.get('count', random.randint(300, 5000)))  # Get the count parameter from the request, default to a random value between 50 and 200
    raw_logs = generate_raw_logs(start_date, end_date, count)
    return jsonify(raw_logs)

if __name__ == '__main__':
    app.run(debug=True)