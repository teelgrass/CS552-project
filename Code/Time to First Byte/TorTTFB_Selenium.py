import sys
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

# duplicate output to console and file
class Tee:
    def __init__(self, file_path):
        self.file = open(file_path, "w")
        self.console = sys.stdout

    def write(self, message):
        self.file.write(message)
        self.console.write(message)

    def flush(self):
        self.file.flush()
        self.console.flush()

# Redirect stdout to a file
output_file = "TOR_test_results_ttfb.txt"
sys.stdout = Tee(output_file)

#runs to measure TTFB
num_runs = 100

# Path to Geckodriver
geckodriver_path = "/usr/local/bin/geckodriver"

# Path to Firefox binary (Tor Browser)
firefox_binary_path = "/Applications/Tor Browser.app/Contents/MacOS/firefox"


websites = [
    'https://simplecss.org',
    'https://docs.python.org/3/',
    'https://www.apache.org',
    'https://perldoc.perl.org',
    'https://www.amazon.com',
    'https://www.airbnb.com',
    'https://www.tripadvisor.com',
    'https://www.youtube.com',
    'https://www.tiktok.com',
    'https://www.netflix.com',
    'https://www.twitch.tv'

]




# Firefox options with proxy configurations
options = Options()
options.binary_location = firefox_binary_path
options.set_preference("network.proxy.type", 1)  #proxy configuration
options.set_preference("network.proxy.socks", "127.0.0.1")
options.set_preference("network.proxy.socks_port", 9150)  # Tor's SOCKS proxy port
options.set_preference("network.proxy.socks_version", 5)  #SOCKS5
options.set_preference("network.proxy.no_proxies_on", "")  # No URLs should bypass the proxy


options.set_preference("browser.cache.disk.enable", False)
options.set_preference("browser.cache.memory.enable", False)
options.set_preference("browser.cache.offline.enable", False)
options.set_preference("network.http.use-cache", False)

service = Service(geckodriver_path)
driver = webdriver.Firefox(service=service, options=options)

browser_version = driver.capabilities['browserVersion']
geckodriver_version = driver.capabilities['moz:geckodriverVersion']
sys.stdout.file.write(f"Browser Version: {browser_version}\n")
sys.stdout.file.write(f"Geckodriver Version: {geckodriver_version}\n")

# Pause for VPN connection
input("Please activate the Tor VPN (or ensure the proxy is running) and press Enter to continue...")


# Function to measure TTFB for a URL
def measure_ttfb(driver, url):
    try:
        driver.get(url)
        performance_entries = driver.execute_script("return performance.getEntriesByType('navigation')[0]")
        request_start = performance_entries['requestStart']
        response_start = performance_entries['responseStart']
        ttfb = response_start - request_start
        return ttfb
    except Exception as e:
        print(f"Error loading {url}: {e}")
        return None

#TTFB multiple times and average it
avg_ttfb_times = []

print("Starting TTFB measurements...")
for site in websites:
    ttfb_times = []

    print(f"\nTesting {site}...")  # Console
    sys.stdout.file.write(f"\nResults for {site}:\n")  #file

    for run in range(num_runs):
        ttfb = measure_ttfb(driver, site)
        if ttfb is not None:
            ttfb_times.append(ttfb)
            sys.stdout.file.write(f"Run {run + 1}: TTFB = {ttfb:.2f} ms\n")
        else:
            sys.stdout.file.write(f"Run {run + 1}: Failed to measure TTFB\n")

    if ttfb_times:
        avg_ttfb = sum(ttfb_times) / len(ttfb_times)
        avg_ttfb_times.append((site, avg_ttfb))

        #average to the file
        sys.stdout.file.write(f"Average TTFB for {site}: {avg_ttfb:.2f} ms\n")

        # Console output
        sys.stdout.console.write(f"Average TTFB for {site}: {avg_ttfb:.2f} ms\n")
    else:
        sys.stdout.file.write(f"All runs failed for {site}. No average calculated.\n")
        sys.stdout.console.write(f"Failed to calculate TTFB for {site}.\n")

#final results to the file and console
sys.stdout.file.write("\nFinal TTFB Results:\n")
sys.stdout.console.write("\nFinal TTFB Results:\n")
for site, avg_ttfb in avg_ttfb_times:
    result_line = f"Average TTFB for {site}: {avg_ttfb:.2f} ms\n"
    sys.stdout.file.write(result_line)
    sys.stdout.console.write(result_line)

driver.quit()
sys.stdout.file.close()
sys.stdout = sys.stdout.console
print(f"All results saved to {output_file}")
