import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate(
    "conf_read_only.json"
)  # conf.json not included in the repo

firebase_admin.initialize_app(
    cred, {"databaseURL": "https://covid19maroc-632de.firebaseio.com"}
)
# Import database module.
from firebase_admin import db

morocco = db.reference("maroc")
