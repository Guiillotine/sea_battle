from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship # Для создания связей мжд таблицами
from app.database import Base

class Player(Base):
    __tablename__ = "player"
    id = Column(Integer, primary_key=True, index=True)
    sid = Column(String, unique=True, index=True)
    login = Column(String, unique=True, index=True)
    password = Column(String, index=True)


class Game(Base):
    __tablename__ = "game"
    id = Column(Integer, primary_key=True, index=True)
    sid = Column(String, unique=True, index=True)
    board = Column(JSON)
    start_date = Column(DateTime, index=True)
    end_date = Column(DateTime, nullable=True, index=True)
    id_player1 = Column(Integer, ForeignKey("player.id"), index=True)
    id_player2 = Column(Integer, ForeignKey("player.id"), index=True)
    id_winner = Column(Integer, ForeignKey("player.id"), nullable=True, index=True)
    id_status = Column(Integer, ForeignKey("status.id"), index=True)

class Status(Base):
    __tablename__ = "status"
    id = Column(Integer, primary_key=True, index=True)
    status_name = Column(String, unique=True)