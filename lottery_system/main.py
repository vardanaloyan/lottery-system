import logging
from datetime import date, datetime

from sqlalchemy import and_

logging.basicConfig(
    format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)
logger.setLevel("INFO")
import random

from flask import Flask, redirect, render_template, request
from flask_apscheduler import APScheduler
from flask_login import current_user, login_required, login_user, logout_user

from models.models import (
    BallotsModel,
    LotteryModel,
    UserModel,
    WinnersModel,
    db,
    login_manager,
)

# Initialize Flask application with development configs
app = Flask(__name__)
app.config.from_object("config.development")

# Initialize db
db.init_app(app)

# Initialize scheduler for midnight award
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# Initialize login_manager
login_manager.init_app(app)
login_manager.login_view = "login"


@app.before_first_request
def create_all():
    """
    Function that run only in first request and creates all db structure
    defined in models.py
    Returns: None
    """
    db.create_all()


@scheduler.task("cron", id="the end of lottery event", hour="23", minute="59")
def midnight_award():
    """
    Function is attached to the scheduler, will run every day at 23:59
    and will randomly choose the winner of the lottery event

    Function's flow is the following
        -   Getting the list of active lotteries
        -   Getting the list of active lotteries' ballots of the day
        -   Randomly choose the winner from the list above
        -   Struct new winner object filling WinnersModel by winner's properties
        -   Add new winner to db and commit
    Returns:
        None
    """
    with app.app_context():
        logger.info("Choosing the winner...")
        lotteries = LotteryModel.query.filter(
            datetime.utcnow() <= LotteryModel.due_date
        ).all()
        lottery_ids = [lot.id for lot in lotteries]
        if not lottery_ids:
            logger.warning("No active lotteries")
            return
        now = datetime.utcnow()
        today_date = date(now.year, now.month, now.day)
        ballots_of_the_day = BallotsModel.query.filter(
            and_(
                BallotsModel.lottery_id.in_(lottery_ids),
                BallotsModel.date == today_date,
            )
        ).all()
        if not ballots_of_the_day:
            logger.warning("No active ballots")
            return
        winner = random.choice(ballots_of_the_day)
        lottery_name = (
            LotteryModel.query.filter_by(id=winner.lottery_id).first().lottery_name
        )
        username = UserModel.query.filter_by(id=winner.user_id).first().username
        new_winner = WinnersModel(
            lottery_name=lottery_name,
            user_name=username,
            ballot_id=winner.id,
            date=today_date,
        )
        db.session.add(new_winner)
        db.session.commit()
        logger.info("Winning Ballot for %s", today_date)
        logger.info(
            "Ballot: %s, Lottery: %s, User: %s", winner.id, lottery_name, username
        )


@app.route("/", methods=["POST", "GET"])
@login_required
def root():
    """
    View function for root path of the application, which uses `index.html` template.
    Function has 2 purposes
        1. Show active lotteries and number of ballots for each lotteries for current user # GET request
        2. Submit new ballots for lotteries # POST request
    Returns:
        str
    """
    # Submitting a new ballot
    if request.method == "POST":
        lottery_name = request.form["lottery_name"]
        lottery = LotteryModel.query.filter_by(lottery_name=lottery_name).first()
        ballot = BallotsModel(user_id=current_user.id, lottery_id=lottery.id)
        db.session.add(ballot)
        db.session.commit()

    # Getting the list of active lotteries
    lotteries = LotteryModel.query.filter(
        datetime.utcnow() <= LotteryModel.due_date
    ).all()

    # Extracting lottery ids and names
    if lotteries:
        lottery_ids = [lot.id for lot in lotteries]
        lottery_names = [lot.lottery_name for lot in lotteries]
    else:
        lottery_names = []
        lottery_ids = []

    # Calculating the count of ballots for each lottery
    lottery_cnts = []
    for lot_id in lottery_ids:
        query_users = BallotsModel.query.filter(
            and_(
                lot_id == BallotsModel.lottery_id,
                BallotsModel.user_id == current_user.id,
                datetime.utcnow() <= LotteryModel.due_date,
            )
        ).all()
        lottery_cnts.append(len(query_users))

    # Zipping together lottery name and corresponding ballots number in a dict
    zipped_lotteries = []
    for lot_name, lot_cnt in zip(lottery_names, lottery_cnts):
        dct = dict()
        dct["lottery_name"] = lot_name
        dct["lottery_count"] = lot_cnt
        zipped_lotteries.append(dct)
    data = {"lotteries": zipped_lotteries}
    return render_template("index.html", current_user=current_user, **data)


@app.route("/check-winner", methods=["POST", "GET"])
@login_required
def check_winner():
    """
    View function for Check Winner page.

    For preventing confusion:
        winner, no_winner flags needed for jinja templating.
        They have been used in condition operations

    Function has 2 purposes
        1. Query for winner by specifying the date # POST request
        2. Show winner information # GET request
    Returns:
        str
    """
    additional = (
        {}
    )  # It will stay empty in case of GET request, POST request if there's no winner
    date_ = None  # It will stay None in case of GET request
    no_winner = False  # It will stay False in case of GET request, POST request if there's a winner

    if request.method == "POST":
        date_ = request.form["date"]
        winner = WinnersModel.query.filter_by(date=date_).all()
        if winner:
            winner = winner[-1]
            additional = {
                "username": winner.user_name,
                "lottery_name": winner.lottery_name,
                "ballot_number": winner.ballot_id,
            }
        else:
            no_winner = True

    now = datetime.utcnow()
    now = now.strftime("%Y-%m-%d")

    if date_:  # Showing right date in calendar form
        now = date_

    return render_template(
        "check_winner.html",
        note="Check Winner page",
        current_user=current_user,
        check_winner=True,
        today=now,
        winner=additional,
        no_winner=no_winner,
    )


@app.route("/login", methods=["POST", "GET"])
def login():
    """
    View function for login page.
    Flow of the function:
        -   To check if username exist in the database, and check password matching
        -   If so login_user called and redirected to root page
        -   Otherwise shows notification page with message User "{username}" does not exist"§
    Returns:
        str
    """
    if current_user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        username = request.form["username"]
        user = UserModel.query.filter_by(username=username).first()
        if user is not None and user.check_password(request.form["password"]):
            login_user(user)
            return redirect("/")
        else:
            note = f'User "{username}" does not exist'
            return render_template(
                "note.html",
                note=note,
                redirect_register=True,
                current_user=current_user,
            )

    return render_template("login.html", current_user=current_user)


@app.route("/register", methods=["POST", "GET"])
def register():
    """
    View function for register page.
    Flow of the function:
        -   If user is authenticated, redirect root page
        -   To check if username exists in the database, if exists, it shows notification page
        -   To check if username was filled (I am not checking the password, for allowing users register without passwords)
        -   Create new UserModel object, add to db and commit
        -   Show notification page
    Returns:
        str
    """
    if current_user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if UserModel.query.filter_by(username=username).first():
            note = f'User "{username}" already exists'
            return render_template(
                "note.html", note=note, redirect_login=True, current_user=current_user
            )
        if not username.strip():
            note = "Fill the username field"
            return render_template(
                "note.html",
                note=note,
                redirect_register=True,
                current_user=current_user,
            )

        user = UserModel(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        note = f'User "{username}" successfully registered'
        return render_template(
            "note.html", note=note, redirect_login=True, current_user=current_user
        )

    return render_template("register.html", current_user=current_user)


@app.route("/logout")
@login_required
def logout():
    """
    Logout function
    Logout current user and redirect to the root path
    """
    logout_user()
    return redirect("/")


if __name__ == "__main__":
    logger.info("Lottery System application started...")
    app.run(host="localhost", port=5000)
