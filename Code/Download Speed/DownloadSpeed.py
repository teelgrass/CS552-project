import requests
import time
import os

use_Tor = True

# Configure Tor SOCKS5 proxy
proxies = {
    'http': 'socks5h://127.0.0.1:9150',
    'https': 'socks5h://127.0.0.1:9150'
}

# List of websites to test
websites = [
    "https://simplecss.org/",
    "https://docs.python.org/",
    "https://www.apache.org/",
    "https://perldoc.perl.org/",
    "https://www.amazon.com/",
    "https://www.airbnb.com/",
    "https://www.tripadvisor.com/",
    "https://www.bestbuy.com/",
    "https://www.youtube.com/",
    "https://www.tiktok.com/",
    "https://www.netflix.com/",
    "https://www.twitch.tv/"
]

# Function to measure download speed
def measure_download_speed(url):
    speeds = []
    for _ in range(100):  # Run 100 tests per website
        start = time.time()
        try:
            if use_Tor: r = requests.get(url, proxies=proxies, timeout=10)  # Request via Tor
            else: r = requests.get(url, timeout=10)  # Request without Tor

            size = r.headers.get('content_length')
            if size == None:
                with open('file.txt', 'wb') as f:
                    f.write(r.content)
                size = os.path.getsize('file.txt')
            size = size/1024 # Convert to Kb

            speed = size / (time.time() - start)
            speeds.append(speed)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            
    return (sum(speeds) / len(speeds)) if speeds else None

# Measure download speed for each website
def main():
    for site in websites:
        print(f"Testing {site}...")
        avg_speed = measure_download_speed(site)
        if avg_speed:
            print(f"Average speed for {site}: {avg_speed:.2f} KB/s")
        else:
            print(f"Failed to get a response from {site}")

if __name__ == "__main__":
    main()