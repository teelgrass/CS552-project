import requests
import time
import matplotlib.pyplot as plt
import subprocess

# Configure Tor SOCKS5 proxy
proxies = {
    'http': 'socks5h://127.0.0.1:9150',
    'https': 'socks5h://127.0.0.1:9150'
}

# List of websites to test
websites = [
    'https://simplecss.org',
    'https://docs.python.org/3/',
    'https://www.apache.org',
    'https://perldoc.perl.org',
    'https://www.amazon.com',
    'https://www.airbnb.com',
    'https://www.tripadvisor.com',
    'https://www.bestbuy.com',
    'https://www.youtube.com',
    'https://www.tiktok.com',
    'https://www.netflix.com',
    'https://www.twitch.tv'
]

# Function to measure latency
def measure_latency(url):
    latencies = []
    for _ in range(1):  # Run 10 latency tests per website
        start = time.time()
        try:
            requests.get(url, proxies=proxies, timeout=10)  # Request via Tor
            latency = (time.time() - start) * 1000  # Convert to milliseconds
            latencies.append(latency)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    return sum(latencies) / len(latencies) if latencies else None

# Function to measure hops using traceroute/tracert
def get_hops(url):
    hostname = url.split('//')[1].split('/')[0]  # Extract the hostname
    try:
        # Use tracert for Windows, traceroute for Unix-based systems
        command = ["tracert", "-d", hostname]  # "-d" skips DNS resolution
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output = result.stdout

        # Parse the output to count hops
        hops = 0
        for line in output.splitlines():
            if line.strip().startswith(str(hops + 1)):  # Hops are numbered sequentially
                hops += 1
        return hops
    except Exception as e:
        print(f"Error measuring hops for {hostname}: {e}")
        return None

# Measure latency and hops for each website and store results
results = {}
for site in websites:
    print(f"Testing {site}...")

    # Measure latency
    avg_latency = measure_latency(site)
    if avg_latency:
        print(f"Average latency for {site}: {avg_latency:.2f} ms")
    else:
        print(f"Failed to get a response from {site}")

    # Measure hops
    hops = get_hops(site)
    if hops is not None:
        print(f"Hops for {site}: {hops}")
    else:
        print(f"Failed to measure hops for {site}")

    # Store results
    results[site] = {'latency': avg_latency, 'hops': hops}

# Filter out failed results
filtered_results = {
    site: data for site, data in results.items()
    if data['latency'] is not None and data['hops'] is not None
}

# Generate separate bar charts for latency and hops
if filtered_results:
    sites = list(filtered_results.keys())
    latencies = [data['latency'] for data in filtered_results.values()]
    hops = [data['hops'] for data in filtered_results.values()]

    # Latency Chart
    plt.figure(figsize=(12, 6))
    plt.bar(sites, latencies, color='skyblue')
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Average Latency (ms)')
    plt.xlabel('Websites')
    plt.title('Average Latency of Websites via Tor')
    plt.tight_layout()
    plt.show()

    # Hops Chart
    plt.figure(figsize=(12, 6))
    plt.bar(sites, hops, color='orange')
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Number of Hops')
    plt.xlabel('Websites')
    plt.title('Number of Hops to Reach Websites via Tor')
    plt.tight_layout()
    plt.show()
else:
    print("No successful latency or hops measurements to display.")
