# glsp.py

from sqlalchemy import Table, Column, Integer, String, Float, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


Base = declarative_base()

def getsess(fn='glsp.db'):
    engine = create_engine('sqlite:///{}'.format(fn))
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

class Player(Base):

    __tablename__ = 'player'
    _table_args__ = (UniqueConstraint('name', 'yr', 'week', name='uix_nyr'),)

    id = Column(Integer, primary_key=True)
    name = Column(String)
    pos = Column(String)
    yr = Column(Integer)
    week = Column(Integer)
    std_low = Column(Float)
    std_med = Column(Float)
    std_high = Column(Float)
    hppr_low = Column(Float)
    hppr_med = Column(Float)
    hppr_high = Column(Float)
    ppr_low = Column(Float)
    ppr_med = Column(Float)
    ppr_high = Column(Float)
    created_at = Column(DateTime)
    
    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))
        return ', '.join(sb)
 
    def __repr__(self):
        return self.__str__() 



if __name__ == '__main__':
    pass
