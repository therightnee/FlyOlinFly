from FlyOlinFly import app
import os

app.run(port=os.environ.get("PORT", 5000), debug=False)
