from sqlalchemy import Column, Integer, TEXT

from tgbot.infrastucture.database.models.base import Base


class ChannelPhoto(Base):
    __tablename__ = 'channel_photos'

    photo_id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    file_id = Column(TEXT, nullable=False)