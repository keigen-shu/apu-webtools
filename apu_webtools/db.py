# Database metadata
# (C) 2013 Keigen Shu

import os

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import Date, DateTime, Integer, String

engine = create_engine(os.environ.get('HEROKU_POSTGRESQL_TEAL_URL', 'postgresql:///timetable'))
session = scoped_session(sessionmaker(bind=engine, autoflush=False))

Base = declarative_base(bind=engine)


class Intake(Base):
    __tablename__ = 'intake'

    code = Column(String, primary_key=True)
    last_update = Column(DateTime)
    entries = relationship(
        "Entry",
        backref="intake",
        cascade="all, delete, delete-orphan"
    )


class Module(Base):
    __tablename__ = 'module'

    code = Column(String, primary_key=True)
    entries = relationship(
        "Entry",
        backref="module",
        cascade="all, delete, delete-orphan"
    )


class Lecturer(Base):
    __tablename__ = 'lecturer'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    entries = relationship(
        "Entry",
        backref="lecturer",
        cascade="all, delete, delete-orphan"
    )


class Location(Base):
    __tablename__ = 'location'

    id = Column(Integer, primary_key=True)
    room = Column(String, nullable=False)
    entries = relationship(
        "Entry",
        backref="location",
        cascade="all, delete, delete-orphan"
    )


class Entry(Base):
    __tablename__ = 'entry'

    id = Column(Integer, nullable=False, primary_key=True)
    intake_code = Column(String, ForeignKey('intake.code'), nullable=False)
    module_code = Column(String, ForeignKey('module.code'), nullable=False)
    lecturer_id = Column(Integer, ForeignKey('lecturer.id'), nullable=False)
    location_id = Column(Integer, ForeignKey('location.id'), nullable=False)
    day = Column(Date, nullable=False)
    time_slot = Column(String, nullable=False)


def pack_timeslot(source):
    return source[:2] + source[3:5] \
        + source[-5:-3] + source[-2:]


def unpack_timeslot(source):
    return source[:2] + ':' + source[2:4] + ' - ' \
        + source[4:6] + ':' + source[6:8]


