import requests
import json
import csv
import re
from bs4 import BeautifulSoup

BASE_URL = "https://www.eliteprospects.com"

# Mapping of team names to slugs (will be populated dynamically)
TEAM_MAPPING = {}


def fetch_skater_stats_from_next_data(html, team_name):
    """
    Extract skater stats from __NEXT_DATA__ JSON on the stats page.
    Returns a list of dicts with: first_name, last_name, GP, G, A, TP, PIM, +/-, team
    """
    match = re.search(
        r'<script[^>]+id="__NEXT_DATA__"[^>]*>([\s\S]+?)</script>',
        html
    )
    if not match:
        return []
    
    try:
        data = json.loads(match.group(1))
        page_props = data.get('props', {}).get('pageProps', {})
        skater_stats = page_props.get('skaterStats', {})
        stats_data = skater_stats.get('stats', {})
        edges = stats_data.get('edges', [])
        
        results = []
        for edge in edges:
            try:
                player = edge.get('player', {})
                player_name = player.get('name', '')
                regular_stats = edge.get('regularStats')
                
                # Skip if no stats (e.g., goalie or player with no games)
                if regular_stats is None:
                    continue
                
                # Split name: assume "FirstName LastName" format
                parts = player_name.strip().split(maxsplit=1)
                first_name = parts[0] if len(parts) > 0 else ''
                last_name = parts[1] if len(parts) > 1 else ''
                
                stat_row = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'GP': regular_stats.get('GP', ''),
                    'G': regular_stats.get('G', ''),
                    'A': regular_stats.get('A', ''),
                    'TP': regular_stats.get('PTS', ''),  # Total Points = PTS
                    'PIM': regular_stats.get('PIM', ''),
                    '+/-': regular_stats.get('PM', ''),  # Plus-Minus = PM
                    'team': team_name,
                }
                results.append(stat_row)
            except Exception as e:
                print(f"Error processing player in {team_name}: {e}")
                continue
        
        return results
    
    except json.JSONDecodeError as e:
        print(f"JSON decode error for {team_name}: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error extracting stats for {team_name}: {e}")
        return []


def scrape_all_team_stats():
    """
    Scrape skater stats for all NCAA teams and write to skater_stats.csv
    """
    # Get list of NCAA teams from the league page
    print("Fetching NCAA team list...")
    url = "https://www.eliteprospects.com/league/ncaa"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        resp = session.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Extract team links
        teams = []
        excluded = {
            'U.S. National U17 Team',
            'Oshawa Generals',
            'Seattle Jr. Kraken 18U AAA',
            'Langley Rivermen',
            'Red Deer Rebels',
        }
        
        for a in soup.select("a.TextLink_link__RhSiC"):
            text = a.get_text(strip=True)
            href = a.get('href', '')
            if href.startswith('/team/') and text not in excluded:
                # Extract team_id and slug from href: /team/{id}/{slug}
                parts = href.split('/')
                if len(parts) >= 4:
                    team_id = parts[2]
                    team_slug = parts[3]
                    teams.append((text, team_id, team_slug))
        
        print(f"Found {len(teams)} NCAA teams\n")
        
    except Exception as e:
        print(f"Error fetching team list: {e}")
        return
    
    all_stats = []
    
    for team_name, team_id, team_slug in teams:
        url = f"{BASE_URL}/team/{team_id}/{team_slug}/stats"
        print(f"Scraping {team_name}...", end=" ", flush=True)
        
        try:
            resp = session.get(url, timeout=10)
            resp.raise_for_status()
            
            stats = fetch_skater_stats_from_next_data(resp.text, team_name)
            all_stats.extend(stats)
            print(f"✓ ({len(stats)} players)")
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Error: {e}")
            continue
    
    # Write to CSV
    if all_stats:
        csv_path = '/workspaces/DataBase_Project/skater_stats.csv'
        fieldnames = ['first_name', 'last_name', 'GP', 'G', 'A', 'TP', 'PIM', '+/-', 'team']
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_stats)
        
        print(f"\n✓ Wrote {len(all_stats)} stats records to {csv_path}")
    else:
        print("\n✗ No stats records found")


if __name__ == '__main__':
    scrape_all_team_stats()
