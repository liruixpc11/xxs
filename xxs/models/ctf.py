# coding=UTF-8

from .common import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship, backref


class IdentifiedObject(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)


class Group(IdentifiedObject):
    __tablename__ = 'Group_'

    name = Column(String(128), nullable=False)


class Task(IdentifiedObject):
    __tablename__ = 'CtfTask'

    name = Column(String(128), nullable=False)


class Execution(IdentifiedObject):
    __tablename__ = 'CtfExecution'

    group_id = Column(Integer(), ForeignKey("Group_.id"), nullable=False)
    group = relationship('Group', backref=backref("executions"))

    task_id = Column(Integer(), ForeignKey('CtfTask.id'), nullable=False)
    task = relationship('Task', backref=backref('executions'))


class CampTypes(object):
    File = 'file'

    names = (File, )


class CampDesc(IdentifiedObject):
    __tablename__ = 'Camp'

    name = Column(String(128), nullable=False)
    type = Column(Enum(*CampTypes.names), nullable=False)
    target_node = Column(String(128), nullable=False)
    score = Column(Integer(), nullable=False)

    service_port = Column(Integer())
    service_type = Column(String(32), nullable=False)


class TeamCamp(IdentifiedObject):
    __tablename__ = 'TeamCamp'

    execution_id = Column(Integer(), ForeignKey('CtfExecution.id'), nullable=False)
    execution = relationship('Execution', backref='camps')

    desc_id = Column(Integer(), ForeignKey('Camp.id'), nullable=False)
    desc = relationship('CampDesc', backref=backref('camps'))

    target_node = Column(String(255))
    ip = Column(String(64), nullable=False)


class TeamCampRound(IdentifiedObject):
    __tablename__ = 'TeamCampRound'

    index = Column(Integer(), nullable=False)

    camp_id = Column(Integer(), ForeignKey('TeamCamp.id'), nullable=False)
    camp = relationship('TeamCamp', backref=backref('flags'))

    flag = Column(String(255), nullable=False)
    begin_time = Column(DateTime())
    end_time = Column(DateTime())


class FlagSubmit(IdentifiedObject):
    __tablename__ = 'FlagSubmit'

    content = Column(String(255), nullable=False)
    submit_time = Column(DateTime(), nullable=False)

    group_id = Column(Integer(), ForeignKey("Group_.id"), nullable=False)
    group = relationship('Group', backref=backref("flags"))

    round_id = Column(Integer(), ForeignKey('TeamCampRound.id'))
    round = relationship('TeamCampRound', backref=backref('submits'))


class TeamServiceState(object):
    Running = 'Running'
    Blocked = 'Blocked'
    Unknown = 'Unknown'

    names = (Running, Blocked, Unknown)


class TeamServiceCheckLog(IdentifiedObject):
    __tablename__ = 'TeamServiceCheckLog'

    state = Column(Enum(*TeamServiceState.names), nullable=False)
    trigger_time = Column(DateTime(), nullable=False)
    finish_time = Column(DateTime(), nullable=False)
    detail = Column(String(1023), nullable=False)

    round_id = Column(Integer(), ForeignKey('TeamCampRound.id'), nullable=False)
    round = relationship('TeamCampRound', backref=backref('logs'))
