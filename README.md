# DataBase_Project

This repository collects NCAA hockey player data from EliteProspects.com. It includes helper scripts to scrape team rosters and assemble a consolidated CSV.

## Available scripts

* `scrape_team.py` - fetch a single team roster by providing either a team slug or full URL.
* `full_scraper.py` - earlier experimental scraper with search fallbacks (superseded by `scrape_all_teams.py`).
* `scrape_all_teams.py` - iterate over all 63 NCAA teams and write `players.csv` with full roster information. This is the primary entry point for league-wide scraping.
* `parse_html.py` - utility to parse a provided HTML snippet and print CSV rows; useful when external requests are not possible.

## Usage

### Running on a machine with internet access

The scraper no longer relies on finding an HTML table; the roster data is embedded
as JSON inside the Next.js `__NEXT_DATA__` script tag.  That makes the scraper
much more reliable and eliminates the need for a headless browser.

1. Make sure Python 3.10+ is installed.
2. Install dependencies:
   ```bash
   pip install requests beautifulsoup4
   ```
3. Execute the main script:
   ```bash
   python scrape_all_teams.py
   ```
   The script will visit each team page, pull the in‑page JSON payload, and write
   `players.csv` with a row for every rostered player.  No JavaScript execution is
   required and ordinary `requests` calls succeed (network connectivity is not an
   issue).

   **Note:** a handful of non‑NCAA organizations sometimes appear on the NCAA
   league listing (U‑S National U17, junior clubs, etc.).  These are filtered out
   automatically by the script.

### When network access is blocked

If you cannot reach EliteProspects from this environment (as in our Codespace), you can still populate the CSV by saving roster HTML pages locally and parsing them.

* **Single team** – save the roster page to a file and run:
  ```bash
  python parse_html.py "Air Force Academy" airforce.html
  ```
* **Batch mode** – copy the NCAA team list (an `<ul>` with links) to a file (e.g. `teams.html`).
  Save each roster page in a directory using the final path segment as the filename (e.g. `air-force-academy.html`).
  Then run:
  ```bash
  python parse_html.py --list teams.html --html-dir rosters/
  ```
  The script will read the team names, load corresponding HTML files, and write a combined `players.csv`.

The repository includes the Air Force roster as an example.
## Data model

Player records conform to the `Bio` class defined in `models.py`. Fields include first/last name, team, number, position, age, birth date and place, height, weight, and shooting side.

---

Feel free to adapt or extend the scrapers for other leagues or sites.