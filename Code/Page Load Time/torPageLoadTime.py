import sys
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time
import psutil

# Custom class to duplicate output to console and file
class Tee:
    def __init__(self, file_path):
        self.file = open(file_path, "w")  # Open the file for writing
        self.console = sys.stdout  # Save the original `sys.stdout`

    def write(self, message):
        self.file.write(message)  # Write to the file
        self.console.write(message)  # Write to the console

    def flush(self):
        self.file.flush()
        self.console.flush()

# Redirect stdout to a file - rename for chrome or vpn
output_file = "TOR_test_results2.txt"
sys.stdout = Tee(output_file)

# Path to Geckodriver
geckodriver_path = r"C:\Program Files\Geckodriver\geckodriver.exe"  # Replace with the actual path

# Path to Firefox binary (part of the Tor Browser in your case)
firefox_binary_path = r"C:\Users\Owner\Desktop\Tor Browser\Browser\firefox.exe"  # Replace with the actual path

# Tor SOCKS5 proxy configuration
tor_proxy = "127.0.0.1:9150"  # Default Tor proxy port

# List of websites to test
websites = [
    'https://simplecss.org',
    'https://docs.python.org/3/',
    'https://www.apache.org',
    'https://perldoc.perl.org',
    'https://www.amazon.com',
    'https://www.airbnb.com',
    'https://www.tripadvisor.com',
    # 'https://www.bestbuy.com',
    'https://www.youtube.com',
    'https://www.tiktok.com',
    'https://www.netflix.com',
    'https://www.twitch.tv'
]

# Number of cycles to measure page load time
num_cycles = 100  # Change this value for your data collection needs

# Set up Firefox options with proxy configurations
options = Options()
options.binary_location = firefox_binary_path  # Specify the Firefox binary location
options.headless = True  # Run in headless mode (optional)

# Configure Tor as a SOCKS5 proxy
options.set_preference("network.proxy.type", 1)  # Manual proxy configuration
options.set_preference("network.proxy.socks", "127.0.0.1")
options.set_preference("network.proxy.socks_port", 9150)  # Match Tor's SOCKS proxy port
options.set_preference("network.proxy.socks_version", 5)  # Use SOCKS5
options.set_preference("network.proxy.no_proxies_on", "")  # No URLs should bypass the proxy

# Initialize the WebDriver
service = Service(geckodriver_path)
driver = webdriver.Firefox(service=service, options=options)

# Pause for VPN connection
input("Please activate the Tor VPN (or ensure the proxy is running) and press Enter to continue...")

# Function to measure full page load time
def measure_page_load_time(driver, url):
    try:
        start_time = time.time()
        driver.get(url)  # Navigate to the URL
        end_time = time.time()
        return (end_time - start_time) * 1000  # Time in milliseconds
    except Exception as e:
        print(f"Error loading {url}: {e}")
        return None

# Bandwidth metrics
bandwidths = []

# Function to calculate average and max bandwidth during a test
def calculate_bandwidth():
    global bandwidths
    net_io = psutil.net_io_counters()
    return net_io.bytes_sent + net_io.bytes_recv

# Measure page load time multiple times and average it
avg_load_times = []
for site in websites:
    print(f"Testing {site} for {num_cycles} cycles...")
    load_times = []

    for cycle in range(num_cycles + 1):
        print(f"Cycle {cycle}/{num_cycles}...")
        if cycle == 0:
            print("Warming up...")
        start_bandwidth = calculate_bandwidth()
        load_time = measure_page_load_time(driver, site)
        end_bandwidth = calculate_bandwidth()
        bandwidths.append((end_bandwidth - start_bandwidth) / (load_time / 1000) if load_time else 0)
        
        if load_time is not None:
            print(f"Page Load Time: {load_time:.2f} ms")
            load_times.append(load_time)
        else:
            print(f"Cycle {cycle}: Failed to measure page load time.")

    if load_times:
        # Discard the first cycle (warm-up) and calculate the average
        avg_load_time = sum(load_times[1:]) / (len(load_times) - 1)
        print(f"Average Page Load Time for {site}: {avg_load_time:.2f} ms")
        avg_load_times.append((site, avg_load_time))
    else:
        print(f"All cycles failed for {site}. No average calculated.")
    print("-" * 50)

# Print the results
for site, avg_load_time in avg_load_times:
    print(f"Average Page Load Time for {site}: {avg_load_time:.2f} ms")

# Calculate bandwidth metrics
if bandwidths:
    avg_bandwidth = sum(bandwidths) / len(bandwidths)
    max_bandwidth = max(bandwidths)
    print(f"Average Bandwidth: {avg_bandwidth / 1024:.2f} KB/s")
    print(f"Max Bandwidth: {max_bandwidth / 1024:.2f} KB/s")

# Close the browser after all tests
driver.quit()

# Restore stdout to default
sys.stdout.file.close()
sys.stdout = sys.stdout.console

print(f"All results saved to {output_file}")