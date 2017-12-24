from sqlalchemy import Column, String, Boolean, Date, Integer, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from sqlalchemy import create_engine
from sqlalchemy import update

Base = declarative_base()
engine = create_engine('sqlite:///point_system.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class Points(Base):
    __tablename__ = 'points'
    username = Column(String, primary_key=True)
    num_points = Column(Integer, nullable=False)
    server_name = Column(String, nullable=False)
    server_id = Column(Integer, nullable=False)


Base.metadata.create_all(engine)


def get_top_5(guild):
    return session.query(Points).filter(Points.server_id == int(guild.id)).order_by(Points.num_points.desc()).limit(5)


def insert_user_in_table(msg_obj):
    new_submission = Points(username=str(msg_obj.author), num_points=0, server_name=str(msg_obj.guild.name),
                            server_id=int(msg_obj.guild.id))
    session.add(new_submission)
    session.commit()
    session.close()


def query_points(msg_obj):
    return session.query(Points).filter(Points.username == str(msg_obj.author),
                                        Points.server_id == int(msg_obj.guild.id)).all()


def check_if_user_in_table(msg_obj):
    if session.query(Points).filter(Points.username == str(msg_obj.author),
                                    Points.server_id == int(msg_obj.guild.id)).all():
        return True
    else:
        return False


def update_table(msg_obj, points):
    update_submission = update(Points). \
        where(and_(Points.username == str(msg_obj.author), Points.server_id == int(msg_obj.guild.id))).values(
        num_points=points)
    session.execute(update_submission)
    session.commit()
    session.close()


def insert_user_in_table_new_MSG(key, points, guild):
    new_submission = Points(username=str(key), num_points=points, server_name=str(guild.name),
                            server_id=int(guild.id))
    session.add(new_submission)
    session.commit()
    session.close()

def check_if_user_in_table_new_MSG(key, guild):
    session = DBSession()
    if session.query(Points).filter(Points.username == key,
                                    Points.server_id == int(guild.id)).all():
        return True
    else:
        return False

def update_table_new_MSG(key, points, guild):
    update_submission = update(Points). \
        where(and_(Points.username == key, Points.server_id == int(guild.id))).values(
        num_points=points)
    session.execute(update_submission)
    session.commit()
    session.close()

