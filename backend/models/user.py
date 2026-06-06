from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from services.database import Base
import random
import string


def generate_slug(name: str) -> str:
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
    clean = "".join(c.lower() if c.isalnum() else "-" for c in name.strip())[:20]
    return f"{clean}-{suffix}"


class User(Base):
    __tablename__ = "users"
    id           = Column(Integer, primary_key=True, index=True)
    spotify_id   = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    email        = Column(String, nullable=True)
    avatar_url   = Column(String, nullable=True)
    public_slug  = Column(String, unique=True, index=True, nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)
    token        = relationship("UserToken", back_populates="user", uselist=False, cascade="all, delete")


class UserToken(Base):
    __tablename__ = "user_tokens"
    id            = Column(Integer, primary_key=True)
    user_id       = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    access_token  = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    expires_at    = Column(DateTime, nullable=False)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user          = relationship("User", back_populates="token")
