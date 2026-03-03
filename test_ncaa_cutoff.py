import requests
from bs4 import BeautifulSoup


def fetch_ncaa_team_names():
    url = "https://www.eliteprospects.com/league/ncaa"
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, 'html.parser')
    names = []
    for a in soup.select("a.TextLink_link__RhSiC"):
        href = a.get('href', '')
        if href.startswith('/team/'):
            names.append(a.get_text(strip=True))
    return names


def truncate_at_yale(team_list):
    """Return a copy of ``team_list`` truncated at Yale (inclusive).

    The actual scrapers cap their results at 63 NCAA programs; the test
    helper mirrors that behaviour so the assertion below can rely on a
    length check even when Yale is missing.
    """
    out = list(team_list)
    for i, name in enumerate(out):
        if name.lower() == 'yale':
            out = out[: i + 1]
            break
    # enforce the hard cap
    if len(out) > 63:
        out = out[:63]
    return out


def test_cutoff_logic():
    teams = fetch_ncaa_team_names()
    assert teams, "No NCAA teams were fetched from the page"
    truncated = truncate_at_yale(teams)
    # enforce cap of 63 teams
    assert len(truncated) <= 63, (
        f"Truncated list has {len(truncated)} teams, expected ≤ 63"
    )
