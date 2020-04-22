
import flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user


app = flask.Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://anandh85:test123@localhost/anandh"
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'e20d1a5fad51dd8ed7bfea22954d9da319ba70316e132d9f02b4520510bf7ca317fc657f7b0700d85423908f9b4332513c562725d2f73f083242c2dc8a920a96'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
