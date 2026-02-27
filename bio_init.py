import csv
from sqlmodel import Session, select
from models import engine, Bio


def parse_int(v):
    try:
        return int(v)
    except Exception:
        return None


def load_players(csv_path="players.csv"):
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

                stmt = select(Bio).where(Bio.first_name == first, Bio.last_name == last)
                existing = session.exec(stmt).first()

                bio = Bio(
                    first_name=first,
                    last_name=last,
                    team=row.get('team') or None,
                    number=row.get('number') or None,
                    position=row.get('position') or None,
                    age=parse_int(row.get('age', '').strip()),
                    born=row.get('born') or None,
                    birth_place=row.get('birth_place') or row.get('birthplace') or None,
                    country=row.get('country') or None,
                    height=row.get('height') or None,
                    weight=row.get('weight') or None,
                    shoots=row.get('shoots') or None,
                )

                if existing:
                    # update fields
                    for k, v in bio.dict().items():
                        setattr(existing, k, v)
                    session.add(existing)
                    updated += 1
                else:
                    session.add(bio)
                    inserted += 1

            session.commit()

    print(f"Bio: inserted={inserted}, updated={updated}")


if __name__ == '__main__':
    load_players('players.csv')
