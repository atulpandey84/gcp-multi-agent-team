from sqlalchemy import Column, String, Text, Integer, TIMESTAMP, JSON, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Agent(Base):
    __tablename__ = 'agents'
    id = Column(String, primary_key=True)
    role = Column(String)
    team = Column(String)
    mission = Column(Text)
    status = Column(String)
    last_seen = Column(String)


class Audit(Base):
    __tablename__ = 'audit'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
    action = Column(String, nullable=False)
    agent_id = Column(String, nullable=True)
    details = Column(Text)


class Approval(Base):
    __tablename__ = 'approvals'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
    requester = Column(String)
    action = Column(String)
    agent_id = Column(String, ForeignKey('agents.id', ondelete='SET NULL'))
    details = Column(JSON, nullable=True)
    status = Column(String)
    approver = Column(String)
    approver_comments = Column(Text)
    decision_timestamp = Column(TIMESTAMP(timezone=True))
