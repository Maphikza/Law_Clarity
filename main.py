from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from datetime import datetime
import os
import openai
from registration_request_notice import NotificationManager
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
year = datetime.now().year

# Creating database for regulations.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///legislation.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

notification_manager = NotificationManager()

login_manager = LoginManager()
login_manager.init_app(app)


# document_path = "ADMINISTRATION OF ESTATES ACT 66 OF 1965.pdf"
#
# raw_document = DocumentUploader(document_path)
#
# document = raw_document.extract()

# regulation = Legislation(name="ADMINISTRATION OF ESTATES ACT 66 OF 1965",
#                          body=document)
# db.session.add(regulation)
# db.session.commit()

class Legislation(db.Model):
    __tablename__ = "regulations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    body = db.Column(db.String, nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)


# db.create_all()

# To manually register users for now.
def register_user(name, email, password):
    hashed_and_salted_password = generate_password_hash(password=password, method='pbkdf2:sha256', salt_length=6)
    new_user = User(name=name,
                    email=email,
                    password=hashed_and_salted_password)
    db.session.add(new_user)
    db.session.commit()


# register_user(name="siphiwe", email="stapisi155@protonmail.me", password="bellslover")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        notification_manager.send_email_notification(name=name, email=email, message=message)
    return render_template("register.html")


@app.route("/")
def home():
    if current_user.is_anonymous:
        flash("You need to login or register to use this website.")
        return redirect(url_for('login'))
    elif current_user.is_authenticated:
        return render_template("index.html", year=year)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        entered_password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("That email doesn't exist, please try again.")
            return redirect(url_for('login'))
        elif user:
            password = check_password_hash(pwhash=user.password, password=entered_password)
            if not password:
                flash("password incorrect, please try again")
                return redirect(url_for('login'))
            elif password:
                login_user(user=user)
                return redirect(url_for('home'))
    return render_template("login.html", year=year)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/", methods=["GET", 'POST'])
@login_required
def get_data():
    if request.method == "POST":
        prompt = request.form.get('prompt')
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.Completion.create(
            model="code-davinci-002",
            prompt=f"\"\"\"\n{prompt}\n\"\"\"",
            temperature=0,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        output = response["choices"][0]["text"]
        return render_template('index.html', year=year, prompt=prompt, output=output,)


@app.route("/law", methods=["GET", "POST"])
@login_required
def dashboard():
    return render_template("display.html")


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def test_dashboard():
    return render_template("dashboard.html")


@app.route("/fica", methods=["GET"])
@login_required
def fica():
    return render_template("fica.html")


@app.route("/fais", methods=["GET"])
@login_required
def fais():
    return render_template("fais.html")

@app.route("/cisca", methods=["GET"])
@login_required
def cisca():
    return render_template("cisca.html")




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
