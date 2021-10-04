import datetime as datetime
from datetime import datetime, timedelta

from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

login_manager = LoginManager()
db = SQLAlchemy()
from sqlalchemy import event


class UserModel(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String())
    ballots = db.relationship("BallotsModel", backref="users", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(id):
    return UserModel.query.get(int(id))


class LotteryModel(db.Model):
    __tablename__ = "lottery"

    id = db.Column(db.Integer, primary_key=True)
    lottery_name = db.Column(db.String(100), unique=True)
    ballots = db.relationship("BallotsModel", backref="lottery", lazy=True)
    due_date = db.Column(db.Date, nullable=True)


@event.listens_for(LotteryModel.__table__, "after_create")
def create_departments(*args, **kwargs):
    due_date = datetime.utcnow() + timedelta(days=1)
    db.session.add(LotteryModel(lottery_name="Big Chance", due_date=due_date))
    db.session.add(LotteryModel(lottery_name="Extra Win", due_date=due_date))
    db.session.commit()


class BallotsModel(db.Model):
    __tablename__ = "Ballots"

    id = db.Column(db.Integer, primary_key=True)
    lottery_id = db.Column(db.String(100), db.ForeignKey("lottery.id"))
    user_id = db.Column(db.String(100), db.ForeignKey("users.id"), nullable=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)


class WinnersModel(db.Model):
    __tablename__ = "Winners"

    id = db.Column(db.Integer, primary_key=True)
    lottery_name = db.Column(db.String(100))
    user_name = db.Column(db.String(100))
    ballot_id = db.Column(db.Integer())
    date = db.Column(db.Date, nullable=False)
