import requests
from bs4 import BeautifulSoup
import csv
import time

# Try multiple possible URLs
urls_to_try = [
    "https://www.eliteprospects.com/team/3805/air-force-academy/roster",
    "https://www.eliteprospects.com/team/4126/air-force-academy/2024-2025/roster",
    "https://www.eliteprospects.com/team/air-force-academy/roster",
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

for url in urls_to_try:
    print(f"Trying: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Check if we got useful content
            team_element = soup.find('h1')
            if team_element:
                print(f"Found team: {team_element.text}")
            
            # Check for table
            table_bodies = soup.find_all('tbody', class_='SortTable_tbody__VrcrZ')
            if table_bodies:
                print(f"Found {len(table_bodies)} table section(s)")
                break
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(1)  # Be respectful to the server
