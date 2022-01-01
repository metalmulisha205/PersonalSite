from uuid import uuid4
import os
from PIL import Image
from werkzeug.utils import secure_filename

from flask import Flask, flash, render_template, url_for, redirect, request
import flask_login
from flask_login.utils import _secret_key, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_manager, login_user, LoginManager, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt, bcrypt



import forms
import datetime
import pytz

DATABASE_FILE = 'sqlite:///database.db'
PROFILE_FOLDER = 'static/images/uploads/profile'
BG_FOLDER = 'static/images/uploads/bgs'
ICON_FOLDER = 'static/images/uploads/icons'

app = Flask(__name__)



app.config['PROFILE_FOLDER'] = PROFILE_FOLDER
app.config['BG_FOLDER'] = BG_FOLDER
app.config['ICON_FOLDER'] = ICON_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

uri = os.environ.get("DATABASE_URL", DATABASE_FILE)
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SECRET_KEY'] = os.environ.get('secret_key', 'dev')



bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(20), nullable=False, unique=False)
    password = db.Column(db.LargeBinary(), nullable=False)
    isAdmin = db.Column(db.Boolean, nullable=False)
    profile = db.Column(db.String(20), nullable=False, default="defaultProfile.jpg")
    bgPic = db.Column(db.String(20), nullable=False, default="defaultBG.jpg")

class Icon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    iconPic = db.Column(db.String(20), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(150), nullable=False)

#command to create tables
@app.cli.command('create_tables')
def create_tables():
    db.create_all()

#method to save images for profile pictures
def saveImage(directory, image):
    imageName = f'{uuid4().__str__()}-{secure_filename(image.filename)}'
    path = os.path.join(app.root_path, directory, imageName)
    i = Image.open(image)
    output_size = (200, 200)
    i.thumbnail(output_size)
    i.save(path)
    return(imageName)




@app.route('/')
def index():
    # welcome message 
    if current_user.is_authenticated:
        name = current_user.name
    else: 
        name = "Stranger"
    currHour = datetime.datetime.now(pytz.timezone('EST')).hour
    if currHour < 12:
        welcome = "Good Morning, " + name + "!"
    elif currHour < 18: 
        welcome = "Good Afternoon, " + name + "!"
    elif currHour < 21:
        welcome = "Good Evening, " + name + "!"
    else:
        welcome = "Good Night, " + name + "!"
    
    # icon loading
    if current_user.is_authenticated:
        icons = Icon.query.filter_by(uID=current_user.id).order_by(Icon.order).all()
        n = len(icons) 
        # if n > 9 then set w proportional to the root of n, otherwise make it 3
        if n > 9:
            w = int(n**0.5)
        else: 
            w = 3
        
        # calculate the amount of rows required with a width w
        h = -(n//-w) #ceiling division 
        size = (w, h)
    else:
        size = (0,0)
        icons = []
    return render_template('index.html', welcome=welcome, icons=icons, size=size)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect("/profile")
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, name = form.name.data, password=hashed_password, isAdmin = False)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/login")
    return render_template('register.html', form=form)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profileForm = forms.EditProfilePicture()
    iconForm = forms.AddIcon()
    if profileForm.validate_on_submit() and profileForm.profileSubmit.data:
        if profileForm.profilePicture.data:
            image = saveImage(app.config['PROFILE_FOLDER'], profileForm.profilePicture.data)
            current_user.profile = image
            db.session.commit()
    if iconForm.validate_on_submit() and iconForm.iconSubmit.data:
        if iconForm.iconPicture.data:
            image = saveImage(app.config['ICON_FOLDER'], iconForm.iconPicture.data)
            location = iconForm.website.data
            if "htt" not in location:
                location = "https://" + location

            newIcon = Icon(
                uID = current_user.id, 
                name = iconForm.name.data, 
                iconPic=image, 
                order=iconForm.loadOrder.data, 
                width=iconForm.width.data, 
                height=iconForm.height.data, 
                location=location
            )
            db.session.add(newIcon)
            db.session.commit()
    icons = Icon.query.filter_by(uID=current_user.id).order_by(Icon.order).all()
    return render_template("profile.html", icons=icons, profileForm=profileForm, iconForm=iconForm, profilePic = flask_login.current_user.profile)

@app.route('/profile/delete/<int:iconID>', methods=['POST'])
@login_required
def deleteIcon(iconID):
    icon = Icon.query.get_or_404(iconID)
    db.session.delete(icon)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('profile'))
if __name__ == '__main__':
    app.run(debug=False)