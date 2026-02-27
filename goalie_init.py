import csv
from sqlmodel import Session, select
from models import engine, Goalie_Stats


def parse_int(v):
    try:
        return int(v)
    except Exception:
        return None


def parse_float(v):
    try:
        return float(v)
    except Exception:
        return None


def load_goalies(csv_path='goalie_stats.csv'):
    inserted = 0
    updated = 0
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        with Session(engine) as session:
            for row in reader:
                first = row.get('first_name', '').strip()
                last = row.get('last_name', '').strip()
                if not first or not last:
                    continue

                stmt = select(Goalie_Stats).where(Goalie_Stats.first_name == first, Goalie_Stats.last_name == last)
                existing = session.exec(stmt).first()

                gs = Goalie_Stats(
                    first_name=first,
                    last_name=last,
                    GP=parse_int(row.get('GP', '').strip()),
                    GAA=parse_float(row.get('GAA', '').strip()),
                    save_pct=parse_float(row.get('save_pct', '').strip()),
                    W=parse_int(row.get('W', '').strip()),
                    L=parse_int(row.get('L', '').strip()),
                    T=parse_int(row.get('T', '').strip()),
                    SO=parse_int(row.get('SO', '').strip()),
                    TOI=row.get('TOI') or None,
                    SVS=parse_int(row.get('SVS', '').strip()),
                    team=row.get('team') or None,
                )

                if existing:
                    for k, v in gs.dict().items():
                        setattr(existing, k, v)
                    session.add(existing)
                    updated += 1
                else:
                    session.add(gs)
                    inserted += 1

            session.commit()

    print(f"Goalie_Stats: inserted={inserted}, updated={updated}")


if __name__ == '__main__':
    load_goalies('goalie_stats.csv')
