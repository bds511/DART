from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import or_

app = Flask(__name__)
app.secret_key = "Daeseung's super  powerful secret key"
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)


from board_module import *
from model import *


if __name__ == '__main__':
    app.run()