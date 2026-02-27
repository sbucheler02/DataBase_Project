import requests
from bs4 import BeautifulSoup
import csv
import re

def extract_country(birthplace):
    """Extract country from birthplace string"""
    if not birthplace:
        return "", ""
    
    # Common patterns: "City, State, Country"
    parts = [p.strip() for p in birthplace.split(',')]
    
    if len(parts) >= 3:
        # Has city, state/region, country
        country = parts[-1]
        city_state = ", ".join(parts[:-1])
        return city_state, country
    elif len(parts) == 2:
        # Could be "City, Country" or "City, State"
        # Check if the last part is a country
        last_part = parts[-1].strip()
        if last_part in ["USA", "CAN", "Canada", "Czech", "Czechia", "Sweden", "Finland", "Russia", "Germany", "France", "Switzerland"]:
            return parts[0], last_part
        else:
            return birthplace, ""
    else:
        return birthplace, ""

def position_abbreviation(position):
    """Convert position name to abbreviation"""
    position_lower = position.lower()
    if 'goal' in position_lower:
        return 'G'
    elif 'defense' in position_lower:
        return 'D'
    elif 'forward' in position_lower:
        return 'F'
    else:
        return position

def scrape_air_force():
    """Scrape Air Force Academy roster"""
    
    # Try multiple URL possibilities
    urls = [
        "https://www.eliteprospects.com/team/3805/air-force-academy/roster",
        "https://www.eliteprospects.com/team/4126/air-force-academy/2024-2025/roster",
        "https://www.eliteprospects.com/team/air-force-academy",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    soup = None
    for url in urls:
        try:
            print(f"Trying URL: {url}")
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                team_element = soup.find('h1')
                if team_element and 'air' in team_element.text.lower():
                    print(f"Successfully loaded: {team_element.text}")
                    break
        except Exception as e:
            print(f"Error with {url}: {e}")
            continue
    
    if not soup:
        print("Failed to load roster page")
        return []
    
    players_data = []
    
    # Find all table bodies
    table_bodies = soup.find_all('tbody', class_='SortTable_tbody__VrcrZ')
    current_position = None
    
    for tbody in table_bodies:
        rows = tbody.find_all('tr', class_='SortTable_tr__L9yVC')
        
        for row in rows:
            # Check if this is a position header row
            td_with_colspan = row.find('td', {'colspan': True})
            if td_with_colspan:
                # This is a position header
                current_position = td_with_colspan.find('span')
                if current_position:
                    current_position = current_position.text.strip()
                    print(f"\nFound position: {current_position}")
                continue
            
            # This is a player row
            if current_position:
                cells = row.find_all('td', class_='SortTable_trow__T6wLH')
                
                if len(cells) >= 10:
                    try:
                        # Extract data from cells
                        # 0: pronunciation (skip)
                        # 1: number
                        # 2: nationality (skip)
                        # 3: player name
                        # 4: age
                        # 5: born
                        # 6: birthplace
                        # 7: height
                        # 8: weight
                        # 9: shoots
                        
                        # Extract number (remove # symbol)
                        number_text = cells[1].text.strip().replace('#', '')
                        
                        # Extract player name
                        player_link = cells[3].find('a')
                        if not player_link:
                            continue
                        
                        full_name = player_link.text.strip()
                        # Remove position indicator like "(G)" from name
                        full_name = re.sub(r'\s*\([^)]*\)\s*', '', full_name).strip()
                        name_parts = full_name.split()
                        first_name = name_parts[0] if len(name_parts) > 0 else ""
                        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
                        
                        # Extract age
                        age = cells[4].text.strip()
                        
                        # Extract born year
                        born = ""
                        born_element = cells[5].find('span')
                        if born_element and born_element.get('title'):
                            born_date = born_element.get('title', '')
                            # Extract year from format like "03/12/2002"
                            match = re.search(r'(\d{4})', born_date)
                            if match:
                                born = match.group(1)
                        
                        # Extract birthplace
                        birthplace_link = cells[6].find('a')
                        birthplace_text = birthplace_link.text.strip() if birthplace_link else cells[6].text.strip()
                        
                        # Split birthplace and country
                        city_state, country = extract_country(birthplace_text)
                        
                        # Extract height
                        height = cells[7].text.strip()
                        
                        # Extract weight
                        weight = cells[8].text.strip()
                        
                        # Extract shoots
                        shoots = cells[9].text.strip()
                        
                        player = {
                            'first_name': first_name,
                            'last_name': last_name,
                            'team': 'Air Force Academy',
                            'number': number_text,
                            'position': position_abbreviation(current_position),
                            'age': age,
                            'born': born,
                            'birth_place': city_state,
                            'country': country,
                            'height': height,
                            'weight': weight,
                            'shoots': shoots
                        }
                        
                        players_data.append(player)
                        print(f"  → {first_name} {last_name} #{number_text}")
                        
                    except Exception as e:
                        print(f"  Error extracting player: {e}")
                        continue
    
    return players_data

if __name__ == "__main__":
    print("Scraping Air Force Academy roster...")
    players = scrape_air_force()
    
    if players:
        print(f"\nTotal players found: {len(players)}")
        
        # Write to CSV
        csv_file = '/workspaces/DataBase_Project/players.csv'
        headers = ['first_name', 'last_name', 'team', 'number', 'position', 'age', 'born', 'birth_place', 'country', 'height', 'weight', 'shoots']
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(players)
        
        print(f"\nCSV file updated with {len(players)} players")
    else:
        print("No players found")
