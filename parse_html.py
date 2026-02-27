"""Utility for parsing roster HTML snippets and exporting CSV rows."""

from bs4 import BeautifulSoup
import re
import csv
import sys


def parse_roster_html(html: str, team: str) -> list[dict]:
    """Return list of player dicts extracted from the roster page HTML."""
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for tr in soup.find_all('tr', class_='SortTable_tr__L9yVC'):
        # skip section headers
        if tr.find('span', class_='SortTable_section__qZQT6'):
            continue
        cols = tr.find_all('td')
        if len(cols) < 11:
            continue
        number = cols[1].get_text(strip=True)
        # nationality column may contain flag images, ignore
        player_cell = cols[3]
        a = player_cell.find('a')
        name = a.get_text(strip=True)
        m = re.match(r"(.+)\s+\((.)\)$", name)
        position = ''
        if m:
            name = m.group(1).strip()
            pos = m.group(2)
            position = {'G':'G','D':'D','F':'F'}.get(pos, '')
        first, last = name.split(' ',1)
        age = cols[4].get_text(strip=True)
        born = cols[5].get_text(strip=True)
        birthplace = cols[6].get_text(strip=True)
        hp, country = ('', '')
        if ',' in birthplace:
            parts = [p.strip() for p in birthplace.rsplit(',',1)]
            hp = parts[0]
            country = parts[1]
        height = cols[7].get_text(strip=True)
        weight = cols[8].get_text(strip=True)
        shoots = cols[9].get_text(strip=True)
        rows.append({
            'first_name': first,
            'last_name': last,
            'team': team,
            'number': number,
            'position': position,
            'age': age,
            'born': born,
            'birth_place': hp,
            'country': country,
            'height': height,
            'weight': weight,
            'shoots': shoots,
        })
    return rows




def extract_team_links(list_html: str) -> list[tuple[str,str]]:
    """Given the HTML of the NCAA team list, return (team_name, href) pairs."""
    soup = BeautifulSoup(list_html, "html.parser")
    teams = []
    for a in soup.select("ul.ColumnsList_columnsList__c50AO a.TextLink_link__RhSiC"):
        name = a.get_text(strip=True)
        href = a.get('href', '')
        teams.append((name, href))
    return teams


def batch_parse(list_file: str, html_dir: str, output_csv: str = 'players.csv'):
    with open(list_file, 'r', encoding='utf-8') as f:
        team_list_html = f.read()
    teams = extract_team_links(team_list_html)
    all_players = []
    for name, href in teams:
        slug = href.rstrip('/').split('/')[-1]
        html_path = f"{html_dir}/{slug}.html"
        try:
            with open(html_path, 'r', encoding='utf-8') as hf:
                page = hf.read()
        except FileNotFoundError:
            print(f"warning: roster html for '{name}' not found ({html_path})")
            continue
        players = parse_roster_html(page, name)
        all_players.extend(players)
    if all_players:
        headers = list(all_players[0].keys())
        with open(output_csv, 'w', newline='') as out:
            writer = csv.DictWriter(out, fieldnames=headers)
            writer.writeheader()
            writer.writerows(all_players)
        print(f"batch wrote {len(all_players)} players to {output_csv}")
    else:
        print("no players parsed")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Parse roster HTML to CSV')
    parser.add_argument('--list', help='HTML file containing the team list')
    parser.add_argument('--html-dir', help='Directory where individual roster HTML files are stored')
    parser.add_argument('team', nargs='?', help='Single team name')
    parser.add_argument('html', nargs='?', help='HTML file for single team')
    args = parser.parse_args()
    if args.list and args.html_dir:
        batch_parse(args.list, args.html_dir)
    elif args.team and args.html:
        team = args.team
        with open(args.html, 'r', encoding='utf-8') as f:
            html = f.read()
        players = parse_roster_html(html, team)
        writer = csv.DictWriter(sys.stdout, fieldnames=list(players[0].keys()) if players else [])
        writer.writeheader()
        writer.writerows(players)
    else:
        parser.print_usage()
        sys.exit(1)


if __name__ == '__main__':
    main()


