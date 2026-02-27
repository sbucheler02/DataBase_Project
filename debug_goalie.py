import requests
import json
import re
from bs4 import BeautifulSoup

url = "https://www.eliteprospects.com/team/5047/boston-college/stats"
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})
resp = session.get(url, timeout=10)

# Check __NEXT_DATA__
match = re.search(r'<script[^>]+id="__NEXT_DATA__"[^>]*>([\s\S]+?)</script>', resp.text)
if match:
    try:
        data = json.loads(match.group(1))
        props = data.get('props', {}).get('pageProps', {})
        print("Available props keys:", list(props.keys()))
        
        if "goalieStats" in props:
            print("\nFound goalieStats!")
            print("goalieStats structure:", type(props['goalieStats']))
        
        # Check for any key containing 'goalie'
        for key in props.keys():
            if 'goalie' in key.lower():
                print(f"Found goalie-related key: {key}")
    except Exception as e:
        print(f"Error parsing JSON: {e}")
else:
    print("No __NEXT_DATA__ found")

# Also check HTML for Goalie text
soup = BeautifulSoup(resp.content, 'html.parser')
goalie_headers = [th for th in soup.find_all('th') if 'Goalie' in th.get_text()]
print(f"\nGoalie headers in HTML: {len(goalie_headers)}")
if goalie_headers:
    parent_tr = goalie_headers[0].find_parent('tr')
    if parent_tr:
        headers = [h.get_text(strip=True) for h in parent_tr.find_all('th')]
        print(f"Header row: {headers[:15]}")
