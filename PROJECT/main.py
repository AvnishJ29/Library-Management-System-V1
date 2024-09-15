from flask import Flask
from Application.model import *

app = Flask(__name__)
app.secret_key="53736y47rijN^%RW^&#*(DMeo,f[r0.gr])"
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///library.sqlite3"

db.init_app(app)
app.app_context().push()
from Application.controller import *
from Application.controller_librarian import *
from Application.api import *


if __name__ == "__main__":
    app.run()