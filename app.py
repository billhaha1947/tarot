import os
import datetime
import json
import random
from flask import Flask, render_template, request, jsonify, redirect
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO

from database import db
from model_manager import generate_reply, stream_generate_reply
from pseudo_ai import TAROT_CARDS, draw_three, decode_symbols

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///oracle.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "LOCAL_DEPLOY_SECRET_KEY"
app.config["UPLOAD_FOLDER"] = "static/avatar"
app.secret_key = "LOCAL_FLASK_SECRET"

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar = db.Column(db.String(256), default="default.png")
    role = db.Column(db.String(32), default="user")

    def set_password(self, pw):
        self.password_hash = bcrypt.generate_password_hash(pw).decode("utf8")

    def check_password(self, pw):
        return bcrypt.check_password_hash(self.password_hash, pw)

class Conversation(db.Model):
    __tablename__ = "conversations"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(64))
    title = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    convo_id = db.Column(db.Integer)
    sender = db.Column(db.String(64))
    text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

with app.app_context():
    db.init_app(app)
    db.create_all()

@app.route("/")
def home():
    return redirect("/chat")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")
        r = request.form.get("role","user")
        if not u or not p:
            return "Thiếu thông tin", 400
        if User.query.filter_by(username=u).first():
            return "Đã tồn tại", 400
        user = User(username=u, role=r)
        user.set_password(p)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html", title="Đăng ký", avatar="default.png")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")
        user = User.query.filter_by(username=u).first()
        if not user or not user.check_password(p):
            return "Sai đăng nhập", 401
        access = create_access_token(identity=u, expires_delta=datetime.timedelta(days=30))
        return jsonify({"token":access,"avatar":user.avatar})
    return render_template("login.html", title="Đăng nhập", avatar="default.png")

@app.route("/change-password", methods=["POST"])
@jwt_required(optional=True)
def change_password():
    u = get_jwt_identity()
    user = User.query.filter_by(username=u).first()
    old = request.json.get("old")
    new = request.json.get("new")
    if not user.check_password(old):
        return "Sai mật khẩu", 400
    user.set_password(new)
    db.session.commit()
    return jsonify({"msg":"ok"})

@app.route("/upload-avatar", methods=["POST"])
@jwt_required(optional=True)
def upload_avatar():
    u = get_jwt_identity()
    user = User.query.filter_by(username=u).first()
    f = request.files.get("avatar")
    fn = secure_filename(f.filename)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    f.save(os.path.join(app.config["UPLOAD_FOLDER"], fn))
    user.avatar = fn
    db.session.commit()
    return jsonify({"avatar":fn})

@app.route("/api/reply", methods=["POST"])
@jwt_required(optional=True)
def api_reply():
    prompt = request.json.get("prompt","")
    temp = float(request.json.get("temperature",0.7))
    mt = int(request.json.get("max_tokens",150))
    r = generate_reply(prompt,temp,mt)
    return jsonify({"reply":r})

@socketio.on("generate_reply")
def ws_ai(data):
    prompt = data.get("prompt","")
    temp = data.get("temperature",0.7)
    mt = data.get("max_tokens",150)
    socketio.emit("typing", {"status": True})
    for t in stream_generate_reply(prompt,temp,mt):
        socketio.emit("stream", {"token":t})
    socketio.emit("typing", {"status": False})
    oracle = {
        "prediction": f"Thông điệp dành cho bạn từ {random.choice(TAROT_CARDS)}",
        "tarot_card": random.choice(TAROT_CARDS),
        "lucky_numbers": random.sample(range(1,50),4),
        "luck_pct": random.randint(50,99),
        "advice":"Giữ vững niềm tin.",
        "emoji":"🔮",
        "color":"Tím neon",
        "three_draw": draw_three(),
        "symbol_decode": decode_symbols(prompt)
    }
    socketio.emit("oracle_json", oracle)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)
