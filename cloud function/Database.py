import firebase_admin
from firebase_admin import credentials

# conf.json not included in the repo because  it have write access to the database
cred = credentials.Certificate("conf.json")

firebase_admin.initialize_app(
    cred, {"databaseURL": "https://covid19maroc-632de.firebaseio.com"}
)
# Import database module.
from firebase_admin import db

morocco = db.reference("maroc")
