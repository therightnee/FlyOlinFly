# all the imports
from flask import Flask \

#set variables
SECRET_KEY = "development_key"
FLASKR_SETTINGS = ''

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
#app.config.from_envvar('FLASKR_SETTINGS', silent=True)


from FlyOlinFly.database import init_db, db_session
from FlyOlinFly.models import Entry
import FlyOlinFly.views

@app.teardown_request
def shutdown_session(exception=None):
	db_session.remove()

if __name__ == '__main__':
    init.db()
    app.run()
