# vim: et:ts=4:sw=4
# Database metadata
# (C) 2013 Keigen Shu

from datetime import datetime

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.schema import Column
from sqlalchemy.types import Date, DateTime, Integer, String


engine = create_engine('sqlite:///timetable.db')
session = scoped_session(sessionmaker(bind=engine, autoflush=False))

Base = declarative_base(bind=engine)


class Intake(Base):
    __tablename__ = 'intake'

    id = Column(Integer, nullable=False, primary_key=True)
    code = Column(String, nullable=False, unique=True)
    last_update = Column(DateTime)
    entries = relationship("Entry", backref="intake", cascade="all, delete, delete-orphan")


class Module(Base):
    __tablename__ = 'module'

    id = Column(Integer, nullable=False, primary_key=True)
    code = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    entries = relationship("Entry", backref="module", cascade="all, delete, delete-orphan")


class Lecturer(Base):
    __tablename__ = 'lecturer'

    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    entries = relationship("Entry", backref="lecturer", cascade="all, delete, delete-orphan")


class Location(Base):
    __tablename__ = 'location'

    id = Column(Integer, nullable=False, primary_key=True)
    room = Column(String, nullable=False)
    entries = relationship("Entry", backref="location", cascade="all, delete, delete-orphan")


class Entry(Base):
    __tablename__ = 'entry'

    id = Column(Integer, nullable=False, primary_key=True)
    intake_id = Column(Integer, ForeignKey('intake.id'), nullable=False)
    module_id = Column(Integer, ForeignKey('module.id'), nullable=False)
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


