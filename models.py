from typing import Optional
from sqlmodel import SQLModel, Field, create_engine
from sqlalchemy import PrimaryKeyConstraint


class Bio(SQLModel, table=True):
	first_name: str = Field(index=True)
	last_name: str = Field(index=True)
	team: Optional[str] = None
	number: Optional[str] = None
	position: Optional[str] = None
	age: Optional[int] = None
	born: Optional[str] = None
	birth_place: Optional[str] = None
	country: Optional[str] = None
	height: Optional[str] = None
	weight: Optional[str] = None
	shoots: Optional[str] = None
    
	__table_args__ = (PrimaryKeyConstraint("first_name", "last_name"),)

class Player_Stats(SQLModel, table=True):
	first_name: str = Field(index=True)
	last_name: str = Field(index=True)
	GP: Optional[int] = None
	G: Optional[int] = None
	A: Optional[int] = None
	TP: Optional[int] = None
	PIM: Optional[int] = None
	plus_minus: Optional[int] = Field(default=None, description="Plus/minus")
	team: Optional[str] = None
    
	__table_args__ = (PrimaryKeyConstraint("first_name", "last_name"),)

class Goalie_Stats(SQLModel, table=True):
	first_name: str = Field(index=True)
	last_name: str = Field(index=True)
	GP: Optional[int] = None
	GAA: Optional[float] = None
	save_pct: Optional[float] = None
	W: Optional[int] = None
	L: Optional[int] = None
	T: Optional[int] = None
	SO: Optional[int] = None
	TOI: Optional[str] = None
	SVS: Optional[int] = None
	team: Optional[str] = None
    
	__table_args__ = (PrimaryKeyConstraint("first_name", "last_name"),)

engine = create_engine("sqlite:///ncaa_hockey.db")
SQLModel.metadata.create_all(engine)