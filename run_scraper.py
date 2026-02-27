#!/usr/bin/env python3
import subprocess
import sys

result = subprocess.run([sys.executable, '/workspaces/DataBase_Project/scrape_goalie_stats.py'], 
                       capture_output=False, text=True)
sys.exit(result.returncode)
