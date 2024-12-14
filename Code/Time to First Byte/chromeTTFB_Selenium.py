import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import uuid
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

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


def append_cache_bust(url):
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    query['cache_bust'] = str(uuid.uuid4())
    new_query = urlencode(query, doseq=True)
    new_url = urlunparse(parsed_url._replace(query=new_query))
    return new_url

# Redirect stdout to a file
output_file = "VPN_test_results_ttfb.txt"
sys.stdout = Tee(output_file)

#runs to measure TTFB
num_runs = 100

# Path to ChromeDriver
chrome_driver_path = "/usr/local/bin/chromedriver"

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

#Chrome browser with cache disabling
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--incognito")
options.add_argument("--disable-cache")
options.add_argument("--disable-application-cache")
options.add_argument("--disable-offline-load-stale-cache")
options.add_argument("--disable-background-networking")
options.add_argument("--disable-service-worker")
options.add_argument("--disk-cache-size=0")
options.add_argument("--media-cache-size=0")
options.add_argument("--headless")  #Run in headless mode
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Disable cache using CDP
driver.execute_cdp_cmd('Network.enable', {})
driver.execute_cdp_cmd('Network.setCacheDisabled', {'cacheDisabled': True})

# Log browser and driver versions
browser_version = driver.capabilities['browserVersion']
chrome_version = driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]
sys.stdout.file.write(f"Browser Version: {browser_version}\n")
sys.stdout.file.write(f"ChromeDriver Version: {chrome_version}\n")

def clear_cache(driver):
    driver.execute_cdp_cmd('Network.clearBrowserCache', {})
    driver.execute_cdp_cmd('Network.clearBrowserCookies', {})

# Function to measure TTFB for a URL
def measure_ttfb(driver, url):
    try:
        unique_url = append_cache_bust(url)
        clear_cache(driver)  # Clear cache before each measurement
        driver.get(unique_url)
        performance_entries = driver.execute_script("return performance.getEntriesByType('navigation')[0]")
        request_start = performance_entries['requestStart']
        response_start = performance_entries['responseStart']
        ttfb = response_start - request_start
        return ttfb
    except Exception as e:
        error_message = f"Error loading {url}: {e}\n"
        sys.stdout.file.write(error_message)
        sys.stdout.console.write(error_message)
        return None

# TTFB multiple times and average it
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

        # average to the file
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

# Clean up
driver.quit()
sys.stdout.file.close()
sys.stdout = sys.stdout.console
print(f"All results saved to {output_file}")