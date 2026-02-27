import requests
from bs4 import BeautifulSoup

# Try different possible URLs for Air Force Academy
urls_to_try = [
    "https://www.eliteprospects.com/team/3805/air-force-academy/roster",
    "https://www.eliteprospects.com/team/4000/air-force-academy/roster",
    "https://www.eliteprospects.com/team/3806/air-force-academy/roster",
]

# Try a direct search
search_url = "https://www.eliteprospects.com/search?q=Air+Force+Academy"
try:
    response = requests.get(search_url, timeout=10)
    if response.status_code == 200:
        print("Search request successful")
        soup = BeautifulSoup(response.content, 'html.parser')
        print("Parsed response")
        # Try to find any team links
        team_links = soup.find_all('a', href=True)
        count = 0
        for link in team_links:
            href = link.get('href', '')
            text = link.text.strip()
            if 'air' in text.lower() or 'air' in href.lower():
                print(f"Link: {text} -> {href}")
                count += 1
                if count > 10:
                    break
except Exception as e:
    print(f"Error: {e}")
