from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Text
import enum
from jdatetime import datetime

from app import db


class StoryStagesEnum(enum.Enum):
    received = 0
    uploading = 1
    uploaded = 2
    failed = 3

class Story(db.Model):
    __tablename__ = 'stories_log'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(), default=datetime.now, nullable=False)
    stage = Column(Enum(StoryStagesEnum), nullable=False, unique=False, default=StoryStagesEnum.received)
    error_id = Column(Integer, nullable=True, unique=False)
    text = Column(Text, nullable=False, unique=False)

    def stage_name(self):
        return self.stage.name