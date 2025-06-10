import requests
import time
from datetime import datetime

auth = ('hdw', 'HoneyDuo2025!')
base_url = 'http://localhost:5000'

print("Testing local connection every 10 seconds...")
while True:
    try:
        # Test local
        r = requests.get(f'{base_url}/health', auth=auth, timeout=5)
        print(f"{datetime.now()}: Local - {r.status_code}")
        
        # Test through domain
        r2 = requests.get('https://hdw.honey-duo.com/health', auth=auth, timeout=5)
        print(f"{datetime.now()}: Domain - {r2.status_code}")
    except Exception as e:
        print(f"{datetime.now()}: ERROR - {str(e)}")
    
    time.sleep(10)
