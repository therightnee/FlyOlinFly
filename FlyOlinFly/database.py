from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

try:
	postgresurl = os.environ['DATABASE_URL']
except:
	postgresurl = 'postgresql://postgres:testing@localhost/postgres'
engine = create_engine(postgresurl, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import FlyOlinFly.models
    Base.metadata.create_all(bind=engine)
