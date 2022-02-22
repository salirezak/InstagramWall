from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Enum, PickleType, DateTime, Text, ForeignKey
import enum, pickle
from jdatetime import datetime

from app import db


class AdminRolesEnum(enum.Enum):
    root = 0
    admin = 1
    viewer = 2
    banned = 3

class Admin(db.Model):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), nullable=False, unique=True)
    role = Column(Enum(AdminRolesEnum), nullable=False, unique=False, default=AdminRolesEnum.admin)
    timestamp = Column(DateTime(), default=datetime.now, nullable=False)
    password = Column(String(128), nullable=False, unique=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def role_name(self):
        return self.role.name


class InstagramCookie(db.Model):
    __tablename__ = 'instagram_cookies'
    id = Column(Integer, primary_key=True)
    cookie = Column(PickleType, nullable=False, unique=False)

    def set_cookie(self, cookie:list):
        self.cookie = pickle.dumps(cookie)

    def get_cookie(self):
        return pickle.loads(self.cookie)


class InstagramError(db.Model):
    __tablename__ = 'errors_log'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(), default=datetime.now, nullable=False)
    url  = Column(String(70), nullable=False, unique=False)
    status_code = Column(Integer, nullable=True, unique=False)
    story_id = Column(Integer, nullable=True, unique=False)
    text = Column(Text, nullable=False, unique=False)