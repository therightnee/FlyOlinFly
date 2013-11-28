from sqlalchemy import Column, Integer, String, DateTime
from FlyOlinFly.database import Base

class Entry(Base):
    __tablename__ = 'entry'
    id = Column(Integer, primary_key=True)
    fname = Column(String(50), unique=False)
    lname = Column(String(50), unique=False)
    phonenum = Column(String(20), unique=True)
    email = Column(String(70), unique=True)
    flightdesc = Column(String(200), unique=False)
    datetime  = Column(DateTime(timezone=False))
    unique = Column(String(50), unique=True)
    #comment = Column(String(140), unique=False)
   

    def __init__(self, fname=None, lname=None, phonenum=None, email=None,\
	 flightdesc=None, date=None, unique=None):
        
	self.fname = fname
	self.lname = lname
    self.phonenum = phonenum
	self.email = email
	self.flightdesc = flightdesc
	self.datetime = date
	self.unique = unique
    #self.comment = comment


    def __repr__(self):
        return '<Entry %r>' % (self.fname + self.lname)
