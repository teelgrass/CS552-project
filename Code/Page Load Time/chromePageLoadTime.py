import sys
import psutil
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

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
output_file = "CHROME_test_results2.txt"
sys.stdout = Tee(output_file)

# Number of cycles to measure page load time
num_cycles = 100  # Change this value for your data collection needs

# Path to ChromeDriver
chrome_driver_path = "C:\\Program Files\\Chromedriver\\chromedriver-win64\\chromedriver.exe"  # Replace with the actual path

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

# Set up Chrome browser once
options = Options()
options.add_argument("--headless")  # Run in headless mode (optional)
options.add_argument("--disable-gpu")  # Disable GPU for headless
options.add_argument("--no-sandbox")  # Optional for certain environments
options.add_argument("--enable-unsafe-webgl") # Enable WebGL fallback for trusted content
options.add_argument("--enable-unsafe-swiftshader")  # Enable SwiftShader fallback for trusted content
options.add_argument("--use-gl=swiftshader") # Wse the SwiftShader software renderer to avoid the fallback loop
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Function to measure full page load time
def measure_page_load_time(driver, url):
    try:
        navigation_start = driver.execute_script("return window.performance.timing.navigationStart")
        load_event_end = driver.execute_script("return window.performance.timing.loadEventEnd")
        return load_event_end - navigation_start  # Time in milliseconds
    except Exception as e:
        print(f"Error loading {url}: {e}")
        return None

# Function to monitor bandwidth during the test
def monitor_bandwidth(duration):
    start_time = time.time()
    initial_counters = psutil.net_io_counters()

    max_bandwidth = 0
    total_bandwidth = 0
    samples = 0

    while time.time() - start_time < duration:
        time.sleep(1)
        counters = psutil.net_io_counters()
        sent = counters.bytes_sent - initial_counters.bytes_sent
        recv = counters.bytes_recv - initial_counters.bytes_recv

        bandwidth = (sent + recv) / 1_000_000  # Convert to MB
        max_bandwidth = max(max_bandwidth, bandwidth)
        total_bandwidth += bandwidth
        samples += 1

    avg_bandwidth = total_bandwidth / samples
    return avg_bandwidth, max_bandwidth

# Measure page load time multiple times and average it
avg_load_times = []
test_duration = 0  # To record total test duration for bandwidth monitoring

print("Starting bandwidth monitoring...")
bandwidth_start_time = time.time()

for site in websites:
    print(f"Testing {site} for {num_cycles} cycles...")
    load_times = []

    for cycle in range(num_cycles + 1):
        print(f"Cycle {cycle}/{num_cycles}...")
        if cycle == 0: print("Warming up...")
        driver.get(site)  # Navigate to the URL
        start_time = time.time()
        load_time = measure_page_load_time(driver, site)
        if load_time is not None:
            print(f"Page Load Time: {load_time:.2f} ms")
            load_times.append(load_time)
        else:
            print(f"Cycle {cycle}: Failed to measure page load time.")
        test_duration += time.time() - start_time

    if load_times:
        avg_load_time = sum(load_times[1:]) / (len(load_times) - 1)
        print(f"Average Page Load Time for {site}: {avg_load_time:.2f} ms")
        avg_load_times.append((site, avg_load_time))
    else:
        print(f"All cycles failed for {site}. No average calculated.")
    print("-" * 50)

bandwidth_end_time = time.time()
total_duration = bandwidth_end_time - bandwidth_start_time

# Monitor bandwidth usage during the tests
avg_bandwidth, max_bandwidth = monitor_bandwidth(test_duration)

# Print the results
print("\nPage Load Time Results:")
for site, avg_load_time in avg_load_times:
    print(f"Average Page Load Time for {site}: {avg_load_time:.2f} ms")

print(f"\nBandwidth Results:")
print(f"Average Bandwidth: {avg_bandwidth:.2f} MB/s")
print(f"Maximum Bandwidth: {max_bandwidth:.2f} MB/s")

# Close the browser after all tests
driver.quit()

# Restore stdout to default
sys.stdout.file.close()
sys.stdout = sys.stdout.console

print(f"All results saved to {output_file}")