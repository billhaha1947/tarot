import os, datetime, jwt
from flask import Flask, request, render_template, redirect, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from database import db
from model_manager import generate_reply, stream_generate_reply
from pseudo_ai import stream_pseudo_reply
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///oracle.db"
app.config['JWT_SECRET_KEY'] = "LOCAL_DEPLOY_SECRET"
app.config['UPLOAD_FOLDER'] = "static/avatar"
bcrypt = Bcrypt(app)
app.app_context().push()
db.init_app(app)
db.create_all()

jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(256))
    avatar = db.Column(db.String(256), default="default.png")

    def set_password(self, pw):
        self.password_hash = bcrypt.generate_password_hash(pw).decode('utf8')

    def check_password(self,pw):
        return bcrypt.check_password_hash(self.password_hash, pw)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(64))
    title = db.Column(db.String(128))
    messages = db.Column(db.Text)

@app.route("/")
def home():
    return redirect("/chat")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        u = request.json.get("username")
        p = request.json.get("password")
        if User.query.filter_by(username=u).first():
            return jsonify({"msg":"User exists"}),400
        user = User(username=u)
        user.set_password(p)
        db.session.add(user)
        db.session.commit()
        return jsonify({"msg":"ok"})
    return render_template("register.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        u = request.json.get("username")
        p = request.json.get("password")
        user = User.query.filter_by(username=u).first()
        if not user or not user.check_password(p):
            return jsonify({"msg":"Bad login"}),401
        token = create_access_token(identity=u,expires_delta=datetime.timedelta(days=30))
        return jsonify({"token":token,"avatar":user.avatar})
    return render_template("login.html")

@app.route("/chat")
def chat_page():
    return render_template("chat.html")

@app.route("/settings",methods=["GET","POST"])
@jwt_required(optional=True)
def settings():
    if request.method=="POST":
        return jsonify({"msg":"saved"})
    return render_template("settings.html")

@app.route("/upload-avatar",methods=["POST"])
@jwt_required(optional=True)
def avatar_upload():
    user = User.query.filter_by(username=get_jwt_identity()).first()
    f = request.files["avatar"]
    name = secure_filename(f.filename)
    f.save(os.path.join(app.config['UPLOAD_FOLDER'], name))
    user.avatar=name
    db.session.commit()
    return jsonify({"avatar":name})

@app.route("/reply",methods=["POST"])
@jwt_required(optional=True)
def reply():
    data = request.json
    prompt = data.get("prompt","")
    temp = float(data.get("temperature",0.7))
    tokens = int(data.get("max_tokens",200))
    reply = generate_reply(prompt,temp,tokens)
    return jsonify({"reply":reply})

@socketio.on("generate_reply")
def handle_ai(data):
    temp = data.get("temperature",0.7)
    tokens = data.get("max_tokens",150)
    prompt = data.get("prompt","")
    emit("typing",{"status":True})

    for token in stream_generate_reply(prompt,temp,tokens):
        emit("stream",{"token":token})
    emit("typing",{"status":False})
