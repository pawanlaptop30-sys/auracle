from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, ForeignKey
from datetime import datetime
from services.database import Base
import random
import string


def generate_squad_code() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


class Squad(Base):
    __tablename__ = "squads"
    id           = Column(Integer, primary_key=True, index=True)
    code         = Column(String, unique=True, index=True, nullable=False)
    name         = Column(String, nullable=False, default="The Squad")
    creator_id   = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    members      = Column(JSON, default=list)   # list of user_ids
    results      = Column(JSON, nullable=True)  # computed results
    awards       = Column(JSON, nullable=True)
    group_roast  = Column(String, nullable=True)
    is_complete  = Column(Boolean, default=False)
    max_members  = Column(Integer, default=4)
    created_at   = Column(DateTime, default=datetime.utcnow)
    expires_at   = Column(DateTime, nullable=True)


class Battle(Base):
    __tablename__ = "battles"
    id           = Column(Integer, primary_key=True, index=True)
    slug         = Column(String, unique=True, index=True, nullable=False)
    user_a_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user_b_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    user_a_data  = Column(JSON, nullable=True)
    user_b_data  = Column(JSON, nullable=True)
    verdict      = Column(JSON, nullable=True)
    winner_name  = Column(String, nullable=True)
    created_at   = Column(DateTime, default=datetime.utcnow)
