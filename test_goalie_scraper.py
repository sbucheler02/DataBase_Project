import requests
import json
import re

BASE_URL = "https://www.eliteprospects.com"

def fetch_goalie_stats_from_next_data(html, team_name):
    """
    Extract goalie stats from __NEXT_DATA__ JSON on the stats page.
    Returns a list of dicts with: first_name, last_name, GP, GAA, save_pct, W, L, T, SO, TOI, SVS, team
    """
    match = re.search(
        r'<script[^>]+id="__NEXT_DATA__"[^>]*>([\s\S]+?)</script>',
        html
    )
    if not match:
        print("  No __NEXT_DATA__ found")
        return []
    
    try:
        data = json.loads(match.group(1))
        page_props = data.get('props', {}).get('pageProps', {})
        goalie_stats = page_props.get('goalieStats', {})
        stats_data = goalie_stats.get('stats', {})
        edges = stats_data.get('edges', [])
        
        print(f"  Found {len(edges)} goalie entries")
        
        results = []
        for edge in edges:
            try:
                player = edge.get('player', {})
                player_name = player.get('name', '')
                regular_stats = edge.get('regularStats')
                
                # Skip if no stats
                if regular_stats is None:
                    continue
                
                # Split name: assume "FirstName LastName" format
                parts = player_name.strip().split(maxsplit=1)
                first_name = parts[0] if len(parts) > 0 else ''
                last_name = parts[1] if len(parts) > 1 else ''
                
                gp = regular_stats.get('GP', '')
                
                # Skip if no games played
                if not gp or gp == 0:
                    continue
                
                stat_row = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'GP': regular_stats.get('GP', ''),
                    'GAA': regular_stats.get('GAA', ''),
                    'save_pct': regular_stats.get('SVP', ''),  # Save Percentage = SVP
                    'W': regular_stats.get('W', ''),
                    'L': regular_stats.get('L', ''),
                    'T': regular_stats.get('T', ''),
                    'SO': regular_stats.get('SO', ''),
                    'TOI': regular_stats.get('TOI', ''),
                    'SVS': regular_stats.get('SVS', ''),
                    'team': team_name,
                }
                results.append(stat_row)
            except Exception as e:
                print(f"  Error processing goalie: {e}")
                continue
        
        return results
    
    except json.JSONDecodeError as e:
        print(f"  JSON decode error: {e}")
        return []
    except Exception as e:
        print(f"  Unexpected error: {e}")
        return []


# Test with Boston College
print("Testing Boston College...")
url = f"{BASE_URL}/team/5047/boston-college/stats?tab=goalies"
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})

try:
    resp = session.get(url, timeout=10)
    resp.raise_for_status()
    print(f"Got response, status: {resp.status_code}")
    
    stats = fetch_goalie_stats_from_next_data(resp.text, "Boston College")
    print(f"Extracted {len(stats)} goalies")
    
    for goalie in stats:
        print(f"  {goalie['first_name']} {goalie['last_name']}: {goalie['GP']} GP, {goalie['save_pct']} SV%")
    
except Exception as e:
    print(f"Error: {e}")
