from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    owner_email = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class FreelancerProfile(Base):
    __tablename__ = "freelancer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    skills = Column(String, nullable=False)
    bio = Column(Text, nullable=False)
    owner_email = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
