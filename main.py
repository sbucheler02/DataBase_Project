

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select
from models import Bio, Player_Stats, Goalie_Stats, engine

app = FastAPI()

@app.get("/teams")
def get_teams():
    print("Teams endpoint called")
    with Session(engine) as session:
        # Query unique teams from Bio table
        teams_bio = session.exec(select(Bio.team).where(Bio.team.isnot(None)).distinct()).all()
        # Query unique teams from Player_Stats table
        teams_player = session.exec(select(Player_Stats.team).where(Player_Stats.team.isnot(None)).distinct()).all()
        # Query unique teams from Goalie_Stats table
        teams_goalie = session.exec(select(Goalie_Stats.team).where(Goalie_Stats.team.isnot(None)).distinct()).all()
        
        # Combine and get unique teams
        all_teams = set(teams_bio + teams_player + teams_goalie)
        print(f"Found {len(all_teams)} teams")
        return {"teams": sorted(list(all_teams))}

@app.get("/team/{team_name}/players")
def get_team_players(team_name: str):
    with Session(engine) as session:
        # Query players from Bio table for the team
        players = session.exec(select(Bio.first_name, Bio.last_name, Bio.position).where(Bio.team == team_name)).all()
        
        # Group players by position
        players_by_position = {}
        for player in players:
            position = player.position or "Unknown"
            full_name = f"{player.first_name} {player.last_name}"
            if position not in players_by_position:
                players_by_position[position] = []
            players_by_position[position].append(full_name)
        
        # Sort players within each position
        for position in players_by_position:
            players_by_position[position].sort()
        
        return {"team": team_name, "players_by_position": players_by_position}

@app.get("/player/{first_name}/{last_name}")
def get_player_details(first_name: str, last_name: str, team: str):
    with Session(engine) as session:
        # Get bio info
        bio = session.exec(select(Bio).where(Bio.first_name == first_name, Bio.last_name == last_name, Bio.team == team)).first()
        if not bio:
            return {"error": "Player not found"}
        
        bio_data = {
            "first_name": bio.first_name,
            "last_name": bio.last_name,
            "team": bio.team,
            "number": bio.number,
            "position": bio.position,
            "age": bio.age,
            "born": bio.born,
            "birth_place": bio.birth_place,
            "country": bio.country,
            "height": bio.height,
            "weight": bio.weight,
            "shoots": bio.shoots
        }
        
        # Get stats based on position
        if bio.position == 'G':
            stats = session.exec(select(Goalie_Stats).where(Goalie_Stats.first_name == first_name, Goalie_Stats.last_name == last_name)).first()
            if stats:
                stats_data = {
                    "GP": stats.GP,
                    "GAA": stats.GAA,
                    "save_pct": stats.save_pct,
                    "W": stats.W,
                    "L": stats.L,
                    "T": stats.T,
                    "SO": stats.SO,
                    "TOI": stats.TOI,
                    "SVS": stats.SVS
                }
            else:
                stats_data = None
        else:
            stats = session.exec(select(Player_Stats).where(Player_Stats.first_name == first_name, Player_Stats.last_name == last_name)).first()
            if stats:
                stats_data = {
                    "GP": stats.GP,
                    "G": stats.G,
                    "A": stats.A,
                    "TP": stats.TP,
                    "PIM": stats.PIM,
                    "plus_minus": stats.plus_minus
                }
            else:
                stats_data = None
        
        return {"bio": bio_data, "stats": stats_data}

app.mount("/", StaticFiles(directory = "static", html = True), name = "static")