import requests
from bs4 import BeautifulSoup
import csv

# URL for Air Force Academy roster
url = "https://www.eliteprospects.com/team/3805/air-force-academy/roster"

# Fetch the page
response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.content, 'html.parser')

# Extract team name from the page
team_name_element = soup.find('h1')
team_name = team_name_element.text.strip() if team_name_element else "Air Force Academy"

print(f"Team: {team_name}")

# Find all table sections (positions)
positions_found = []
players_data = []

# Find the table body elements
table_bodies = soup.find_all('tbody', class_='SortTable_tbody__VrcrZ')

current_position = None

for tbody in table_bodies:
    rows = tbody.find_all('tr', class_='SortTable_tr__L9yVC')
    
    for row in rows:
        # Check if this is a position header row
        td_with_colspan = row.find('td', {'colspan': True})
        if td_with_colspan:
            # This is a position header
            current_position = td_with_colspan.find('span').text.strip()
            print(f"Position found: {current_position}")
            continue
        
        # This is a player row
        if current_position:
            cells = row.find_all('td', class_='SortTable_trow__T6wLH')
            
            if len(cells) >= 10:
                # Extract data from cells in order
                # 0: pronunciation (skip)
                # 1: number
                # 2: nationality (skip N column for now)
                # 3: player name
                # 4: age
                # 5: born
                # 6: birthplace
                # 7: height
                # 8: weight
                # 9: shoots
                
                # Extract number (remove # symbol)
                number_text = cells[1].text.strip().replace('#', '')
                
                # Extract player name and extract first and last name
                player_link = cells[3].find('a')
                full_name = player_link.text.strip() if player_link else ""
                # Remove position indicator like "(G)" from name
                full_name = full_name.split('(')[0].strip()
                name_parts = full_name.split()
                first_name = name_parts[0] if len(name_parts) > 0 else ""
                last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
                
                # Extract age
                age = cells[4].text.strip()
                
                # Extract born year
                born_element = cells[5].find('span')
                born = born_element.get('title', '').split('/')[2] if born_element else ""
                
                # Extract birthplace
                birthplace_link = cells[6].find('a')
                birthplace = birthplace_link.text.strip() if birthplace_link else cells[6].text.strip()
                
                # Extract height
                height = cells[7].text.strip()
                
                # Extract weight
                weight = cells[8].text.strip()
                
                # Extract shoots
                shoots = cells[9].text.strip()
                
                player = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'team': team_name,
                    'number': number_text,
                    'position': current_position,
                    'age': age,
                    'born': born,
                    'birth_place': birthplace,
                    'height': height,
                    'weight': weight,
                    'shoots': shoots
                }
                
                players_data.append(player)
                print(f"Extracted: {first_name} {last_name} - #{number_text} - {current_position}")

# Write to CSV
csv_file = '/workspaces/DataBase_Project/players.csv'
headers = ['first_name', 'last_name', 'team', 'number', 'position', 'age', 'born', 'birth_place', 'height', 'weight', 'shoots']

with open(csv_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    
    # Write first player (first goaltender)
    if players_data:
        writer.writerow(players_data[0])
        print(f"\nFirst player written to CSV: {players_data[0]['first_name']} {players_data[0]['last_name']}")
    else:
        print("No players found")

print(f"Total players on page: {len(players_data)}")
