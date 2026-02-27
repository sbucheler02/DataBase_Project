import csv
from sqlmodel import Session, select
from models import engine, Player_Stats


def parse_int(v):
    try:
        return int(v)
    except Exception:
        return None


def load_skaters(csv_path='skater_stats.csv'):
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

                stmt = select(Player_Stats).where(Player_Stats.first_name == first, Player_Stats.last_name == last)
                existing = session.exec(stmt).first()

                plus_minus = None
                # csv header uses '+/-' for plus/minus
                if '+/-' in row:
                    try:
                        plus_minus = int(row.get('+/-'))
                    except Exception:
                        plus_minus = None

                ps = Player_Stats(
                    first_name=first,
                    last_name=last,
                    GP=parse_int(row.get('GP', '').strip()),
                    G=parse_int(row.get('G', '').strip()),
                    A=parse_int(row.get('A', '').strip()),
                    TP=parse_int(row.get('TP', '').strip()),
                    PIM=parse_int(row.get('PIM', '').strip()),
                    plus_minus=plus_minus,
                    team=row.get('team') or None,
                )

                if existing:
                    for k, v in ps.dict().items():
                        setattr(existing, k, v)
                    session.add(existing)
                    updated += 1
                else:
                    session.add(ps)
                    inserted += 1

            session.commit()

    print(f"Player_Stats: inserted={inserted}, updated={updated}")


if __name__ == '__main__':
    load_skaters('skater_stats.csv')
