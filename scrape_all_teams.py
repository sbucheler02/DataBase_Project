import requests
from bs4 import BeautifulSoup
import csv
import re
import json
from typing import List, Dict, Optional

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
)


def extract_country(birthplace: str) -> (str, str):
    parts = [p.strip() for p in birthplace.split(",") if p.strip()]
    if len(parts) >= 3:
        return ", ".join(parts[:-1]), parts[-1]
    if len(parts) == 2:
        last = parts[-1]
        if len(last) > 2 or last.isupper():
            return parts[0], last
        return birthplace, ""
    return birthplace, ""


def fetch_roster_from_next_data(html: str) -> List[Dict]:
    """Parse the Next.js `__NEXT_DATA__` JSON from a team page and return
    the list of player dicts in our CSV format."""
    m = re.search(r'<script[^>]+id="__NEXT_DATA__"[^>]*>([\s\S]+?)</script>', html)
    if not m:
        return []
    data = m.group(1)
    try:
        payload = requests.utils.json.loads(data)
    except Exception:
        payload = json.loads(data)
    roster = payload.get("props", {}).get("pageProps", {}).get("rosterList", {})
    edges = roster.get("tableData", {}).get("edges", [])
    players = []
    for edge in edges:
        tp = edge.get("player") or {}
        name = tp.get("name") or ""
        parts = name.split()
        first = parts[0] if parts else ""
        last = " ".join(parts[1:]) if len(parts) > 1 else ""
        num = edge.get("jerseyNumber")
        if num is None:
            num = ""
        country = tp.get("nationality", {}).get("name", "")
        birthplace = tp.get("placeOfBirth") or ""
        city_state, country2 = extract_country(birthplace)
        if not country and country2:
            country = country2
        # safe extraction for nested dicts that might be None
        height_obj = tp.get("height") or {}
        weight_obj = tp.get("weight") or {}
        shoots_val = tp.get("shoots") or tp.get("catches") or ""
        players.append({
            "first_name": first,
            "last_name": last,
            "team": "",  # caller may set
            "number": str(num),
            "position": tp.get("position", ""),
            "age": str(tp.get("age", "")),
            "born": tp.get("yearOfBirth", ""),
            "birth_place": city_state,
            "country": country,
            "height": height_obj.get("imperial", ""),
            "weight": str(weight_obj.get("imperial", "")),
            "shoots": shoots_val,
        })
    return players




# names which occasionally appear on the NCAA listing but are not actual NCAA
# college teams; we filter them out below so their players are not scraped.
EXCLUDED_TEAMS = {
    'U.S. National U17 Team',
    'Oshawa Generals',
    'Seattle Jr. Kraken 18U AAA',
    'Langley Rivermen',
    'Red Deer Rebels',
}

def get_ncaa_team_links() -> List[tuple[str,str]]:
    """Return list of (team_name, team_href) from the NCAA league page.

    The league page sometimes includes non‑NCAA organizations (U17, junior
    clubs, etc.).  We explicitly exclude those names using `EXCLUDED_TEAMS`.
    """
    url = "https://www.eliteprospects.com/league/ncaa"
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "html.parser")
    teams: List[tuple[str,str]] = []
    for a in soup.select("a.TextLink_link__RhSiC"):
        text = a.get_text(strip=True)
        href = a.get('href', '')
        if href.startswith('/team/') and text not in EXCLUDED_TEAMS:
            teams.append((text, href))
    return teams


def scrape_all_teams(output_csv: str = 'players.csv'):
    teams = get_ncaa_team_links()
    all_players = []
    base = "https://www.eliteprospects.com"
    for name, href in teams:
        print(f"Processing team: {name}")
        url = base + href
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
        if resp.status_code != 200:
            print(f"  failed to fetch team page ({resp.status_code})")
            continue
        players = fetch_roster_from_next_data(resp.text)
        for p in players:
            p['team'] = name
        all_players.extend(players)
        print(f"  found {len(players)} players")
    # write csv
    headers = [
        "first_name","last_name","team","number","position",
        "age","born","birth_place","country","height","weight","shoots"
    ]
    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(all_players)
    print(f"wrote {len(all_players)} total players to {output_csv}")


if __name__ == "__main__":
    scrape_all_teams()
