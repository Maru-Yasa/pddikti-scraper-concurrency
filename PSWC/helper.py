import requests
from requests.adapters import HTTPAdapter
from PSWC import Logger

class Helper:
    def __init__(self):
        self.logger = Logger()

    def convert_to_one_x_ratio(self, numerator, denominator):
        if numerator == 0:
            return f"1:-"

        x = denominator / numerator

        return f"1:{x:.2f}"
    
    def get(self, url):
        self.logger.log(f"Hitting {url}")
        http = requests.Session()
        http.mount('https://', HTTPAdapter(max_retries=3))

        try:
            response = http.get(url, timeout=15)
        except requests.exceptions.Timeout:
            self.logger.log(f"Timeout hitting {url}")
            return None
        
        self.logger.log(f"{response.status_code} - {url}")
        if response.status_code != 200:
            return None
        return response.json()