import os, jwt, datetime, random
from flask import Flask, render_template, request, jsonify, redirect
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from sqlalchemy import Column, Integer, String, Text, DateTime
from database import db
from model_manager import generate_reply, stream_generate_reply
from pseudo_ai import TAROT_CARDS, draw_three, decode_symbols
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key="local_render_dev"
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///oracle.db"
app.config['UPLOAD_FOLDER']="static/avatar"
bcrypt=Bcrypt(app)
db.init_app(app)
socketio=SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")
JWT_SECRET="tarot_local_secret"

# Models DB
class User(db.Model):
    __tablename__="users"
    id=Column(Integer,primary_key=True)
    username=Column(String(64),unique=True)
    password_hash=Column(String(128))
    avatar=Column(String(256),default="default.png")
    role=Column(String(32), default="user")
    def set_password(self,pw): self.password_hash=bcrypt.generate_password_hash(pw).decode('utf8')
    def check_password(self,pw): return bcrypt.check_password_hash(self.password_hash,pw)

class Conversation(db.Model):
    __tablename__="conversations"
    id=Column(Integer,primary_key=True)
    user=Column(String(64))
    title=Column(String(120))
    created_at=Column(DateTime, default=datetime.datetime.utcnow)

class Message(db.Model):
    __tablename__="messages"
    id=Column(Integer,primary_key=True)
    convo_id=Column(Integer)
    sender=Column(String(16))
    text=Column(Text)
    created_at=Column(DateTime, default=datetime.datetime.utcnow)

with app.app_context(): db.create_all()

# JWT helpers
def create_token(user):
    return jwt.encode({"username":user.username,
                       "role":user.role,
                       "exp":datetime.datetime.utcnow()+datetime.timedelta(days=7)},
                       JWT_SECRET,"HS256")

def current_user():
    t=request.cookies.get("access_token","")
    try:
        d=jwt.decode(t,JWT_SECRET,algorithms=["HS256"])
        return User.query.filter_by(username=d['username']).first()
    except: return None

# ROUTES
@app.route("/register",methods=['GET','POST'])
def register():
    if request.method=="POST":
        u=request.form['username']; p=request.form['password']
        if User.query.filter_by(username=u).first(): return "Tồn tại ❌"
        user=User(username=u); user.set_password(p)
        db.session.add(user); db.session.commit()
        return redirect("/login")
    return render_template("register.html",title="Đăng ký",avatar="default.png",content="")

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method=="POST":
        u=request.form['username']; p=request.form['password']
        user=User.query.filter_by(username=u).first()
        if user and user.check_password(p):
            res=redirect("/chat")
            res.set_cookie("access_token", create_token(user))
            return res
        return "Sai ❌"
    return render_template("login.html",title="Đăng nhập",avatar="default.png",content="")

@app.route("/logout")
def logout():
    r=redirect("/login"); r.delete_cookie("access_token"); return r

@app.route("/chat")
def chat():
    user=current_user()
    if not user: return redirect("/login")
    return render_template("chat.html",title="Oracle Hub",avatar=user.avatar,username=user.username)

@app.route("/settings")
def settings():
    return render_template("settings.html",title="Cài đặt",avatar="default.png",content="")

@app.route("/avatar",methods=['POST'])
def avatar():
    user=current_user()
    if not user: return jsonify({"error":"unauthorized"}),401
    f=request.files['avatar']; fn=secure_filename(f.filename)
    f.save(os.path.join(app.config['UPLOAD_FOLDER'],fn))
    user.avatar=fn; db.session.commit()
    return jsonify({"avatar":fn})

# SOCKET STREAM
@socketio.on("prompt")
def on_prompt(msg):
    user=current_user()
    if not user: return socketio.emit("stream","")
    text=msg['text']
    socketio.emit("typing")
    buf=""
    for token in stream_generate_reply(text,0.7,160):
        buf+=token
        socketio.emit("stream", token)
    # JSON oracle
    card=random.choice(TAROT_CARDS)
    oracle={
        "prediction":"Tín hiệu chiêm tinh đang mở…",
        "tarot_card":card,
        "lucky_numbers":random.sample(range(1,49),4),
        "luck_pct":random.randint(50,100),
        "advice":random.choice(["Tin trực giác","Điềm tĩnh","Hành động đúng lúc"]),
        "emoji":random.choice(["🔮","✨","🌙","💎"]),
        "color":random.choice(["#ff00d4","#00f2ff","#39ff14","#ffd700"]),
        "symbols": decode_symbols(text),
        "three": draw_three()
    }
    socketio.emit("oracle_json",oracle)
    # save convo
    c=Conversation(user=user.username,title="Chat "+str(random.randint(100,999)))
    db.session.add(c); db.session.commit()
    db.session.add(Message(convo_id=c.id,sender="user",text=text))
    db.session.commit()
