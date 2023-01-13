from sqlalchemy import Column, Integer, BIGINT
from tgbot.infrastucture.database.models.base import Base


class Admins(Base):
    __tablename__ = 'admins'

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    telegram_id = Column(BIGINT, nullable=False, unique=True)