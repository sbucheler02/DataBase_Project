import requests
from bs4 import BeautifulSoup
import csv
import re

# This script finds the Air Force Academy roster on EliteProspects
# and writes every player (G, D, F) into players.csv using the
# field layout defined in models.py.
#
# Usage: python full_scraper.py
#
# Because the interactive environment may not allow running
# commands, you may need to execute this script yourself in a
# Python environment with network access.

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
)


def find_team_url(search_term="Air Force Academy"):
    """Searches EliteProspects for a team and returns the roster URL.

    The most reliable source for NCAA team links is the league page
    (`/league/ncaa`). We fetch it, look for an anchor whose text matches
    the requested team name, and extract the href. If that fails (e.g.
    network problems), we fall back to the previous search/page slug
    techniques.
    """
    base = "https://www.eliteprospects.com"

    # 1. try the NCAA league page which lists every team
    try:
        league_url = f"{base}/league/ncaa"
        resp = requests.get(league_url, headers={"User-Agent": USER_AGENT}, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
        for a in soup.select("a.TextLink_link__RhSiC"):
            if a.text.strip().lower() == search_term.lower():
                href = a.get("href")
                if href:
                    roster = href.rstrip("/") + "/roster"
                    return base + roster
    except Exception:
        # league page unavailable; continue to fallbacks
        pass

    # 2. search endpoint fallback
    try:
        search_url = f"{base}/search?q={requests.utils.quote(search_term)}"
        resp = requests.get(search_url, headers={"User-Agent": USER_AGENT}, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
        for a in soup.select("a[href*='/team/']"):
            href = a.get("href")
            if href and "roster" in href:
                return base + href
        for a in soup.select("a[href*='/team/']"):
            href = a.get("href")
            if href:
                return base + href.rstrip("/") + "/roster"
    except Exception:
        pass

    # 3. slug-based fallback
    slug = search_term.lower().replace(" ", "-")
    fallback = f"{base}/team/{slug}/roster"
    resp2 = requests.get(fallback, headers={"User-Agent": USER_AGENT}, timeout=10)
    if resp2.status_code == 200:
        return fallback
    fallback2 = f"{base}/team/{slug}"
    resp3 = requests.get(fallback2, headers={"User-Agent": USER_AGENT}, timeout=10)
    if resp3.status_code == 200:
        return fallback2.rstrip("/") + "/roster"

    raise RuntimeError(f"Could not locate team roster URL for '{search_term}'")


def extract_country(birthplace: str) -> tuple[str, str]:
    parts = [p.strip() for p in birthplace.split(",") if p.strip()]
    if len(parts) >= 3:
        return ", ".join(parts[:-1]), parts[-1]
    if len(parts) == 2:
        # assume last part is the country if it is 3 letters or known
        last = parts[-1]
        if len(last) == 3 or last.isalpha():
            return parts[0], last
        return birthplace, ""
    return birthplace, ""


def pos_abbr(pos: str) -> str:
    p = pos.lower()
    if "goal" in p:
        return "G"
    if "defen" in p:
        return "D"
    if "forw" in p or "skater" in p:
        return "F"
    return pos


def parse_roster_page(url: str) -> list[dict]:
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "html.parser")
    players = []
    current_position = None

    for tbody in soup.find_all("tbody", class_="SortTable_tbody__VrcrZ"):
        for row in tbody.find_all("tr", class_="SortTable_tr__L9yVC"):
            # header row with colspan indicates section
            td = row.find("td", colspan=True)
            if td:
                span = td.find("span")
                current_position = span.text.strip() if span else None
                continue
            if not current_position:
                continue
            cells = row.find_all("td", class_="SortTable_trow__T6wLH")
            if len(cells) < 10:
                continue
            try:
                num = cells[1].text.strip().lstrip("#")
                name_a = cells[3].find("a")
                full_name = name_a.text.strip() if name_a else cells[3].text.strip()
                full_name = re.sub(r"\s*\([^)]*\)", "", full_name).strip()
                parts = full_name.split()
                first = parts[0] if parts else ""
                last = " ".join(parts[1:]) if len(parts) > 1 else ""
                age = cells[4].text.strip()
                born = ""
                born_span = cells[5].find("span")
                if born_span and born_span.get("title"):
                    m = re.search(r"(\d{4})", born_span["title"])
                    if m:
                        born = m.group(1)
                bp_text = cells[6].text.strip()
                city_state, country = extract_country(bp_text)
                ht = cells[7].text.strip()
                wt = cells[8].text.strip()
                shoots = cells[9].text.strip()

                # derive position from section header or from name suffix
                position_code = pos_abbr(current_position) if current_position else ""
                # attempt to read from parentheses in the name if not clear
                mpos = re.search(r"\((G|D|F)\)$", full_name)
                if mpos:
                    position_code = mpos.group(1)
                
                players.append({
                    "first_name": first,
                    "last_name": last,
                    "team": "Air Force Academy",
                    "number": num,
                    "position": position_code,
                    "age": age,
                    "born": born,
                    "birth_place": city_state,
                    "country": country,
                    "height": ht,
                    "weight": wt,
                    "shoots": shoots,
                })
            except Exception as e:
                # skip any malformed rows
                print(f"skipped row due to {e}")
    return players


def save_csv(players: list[dict], path="players.csv"):
    headers = [
        "first_name",
        "last_name",
        "team",
        "number",
        "position",
        "age",
        "born",
        "birth_place",
        "country",
        "height",
        "weight",
        "shoots",
    ]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(players)


def main():
    print("Finding team roster URL...")
    roster_url = find_team_url()
    print(f"Roster page: {roster_url}")

    # attempt to fetch roster page; if it 404s try to derive a correct link
    try:
        players = parse_roster_page(roster_url)
    except requests.HTTPError as he:
        # if 404, attempt to look for a roster link on the team page
        if he.response.status_code == 404:
            print(f"Initial roster URL returned 404, attempting to inspect team page")
            team_page = roster_url.rstrip("/roster")
            resp = requests.get(team_page, headers={"User-Agent": USER_AGENT}, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, "html.parser")
                candidate = None
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if "/roster" in href and href != "/roster":  # avoid empty
                        candidate = href
                        break
                if candidate:
                    new_url = "https://www.eliteprospects.com" + candidate
                    print(f"Found alternate roster URL: {new_url}")
                    players = parse_roster_page(new_url)
                else:
                    raise
            else:
                raise
        else:
            raise
    print(f"Found {len(players)} players")
    # do not enforce a specific count; different teams may vary in roster size
    save_csv(players)
    print("CSV updated")


if __name__ == "__main__":
    main()
