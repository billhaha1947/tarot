import os, datetime, jwt
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from model_manager import generate_reply, stream_generate_reply
from database import init_db, db

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("TAROT_SECRET", "LOCAL_SECRET_TAROT")
app.config["UPLOAD_FOLDER"] = "static/avatar"
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

init_db(app)
socketio = SocketIO(app, cors_allowed_origins="*")
db = db

JWT_SECRET = os.getenv("TAROT_JWT_SECRET","LOCAL_JWT_SECRET")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(128))
    avatar = db.Column(db.String(128), default="/static/avatar/default.png")
    role = db.Column(db.String(16), default="user")

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    title = db.Column(db.String(128))
    created = db.Column(db.String(32), default=str(datetime.datetime.utcnow()))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conv_id = db.Column(db.Integer)
    sender = db.Column(db.String(16))
    content = db.Column(db.String)
    created = db.Column(db.String(32), default=str(datetime.datetime.utcnow()))

def jwt_encode(data):
    return jwt.encode(data, JWT_SECRET, algorithm="HS256")

def jwt_decode(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except:
        return None

@app.route("/")
def home():
    return render_template("chat.html")

@app.post("/api/register")
def register():
    data = request.json
    if not data or not data.get("username") or not data.get("password"):
        return {"error":"Thiếu dữ liệu"},400
    if User.query.filter_by(username=data["username"]).first():
        return {"error":"User tồn tại"},400
    u = User(username=data["username"], password=data["password"])
    db.session.add(u)
    db.session.commit()
    return {"status":"ok"}

@app.post("/api/login")
def login():
    data=request.json
    u=User.query.filter_by(username=data["username"],password=data["password"]).first()
    if not u:
        return {"error":"Sai tài khoản"},401
    token = jwt_encode({"uid":u.id,"username":u.username,"avatar":u.avatar,"role":u.role})
    return {"token":token}

@app.post("/api/avatar")
def upload_avatar():
    info = jwt_decode(request.headers.get("Authorization",""))
    if not info: return {"error":"Unauthorized"},401
    if "file" not in request.files: return {"error":"No file"},400
    f=request.files["file"]
    name=secure_filename(f.filename)
    path=os.path.join(app.config["UPLOAD_FOLDER"], name)
    f.save(path)
    u=User.query.get(info["uid"])
    u.avatar="/static/avatar/"+name
    db.session.commit()
    return {"avatar":u.avatar}

@app.get("/api/conversations")
def list_conv():
    info=jwt_decode(request.headers.get("Authorization",""))
    if not info:return {"error":"unauthorized"},401
    convs=Conversation.query.filter_by(user_id=info["uid"]).all()
    return {"items":[{"id":c.id,"title":c.title} for c in convs]}

@app.post("/api/newchat")
def new_chat():
    info=jwt_decode(request.headers.get("Authorization",""))
    if not info:return {"error":"unauthorized"},401
    t=datetime.datetime.utcnow().strftime("%H:%M %d/%m/%Y")
    c=Conversation(user_id=info["uid"],title=f"Chat {t}")
    db.session.add(c);db.session.commit()
    return {"id":c.id,"title":c.title}

@app.get("/api/history/<cid>")
def history(cid):
    info=jwt_decode(request.headers.get("Authorization",""))
    if not info:return {"error":"unauthorized"},401
    msgs=Message.query.filter_by(conv_id=int(cid)).all()
    return {"items":[{"s":m.sender,"c":m.content} for m in msgs]}

@app.post("/api/chat/<cid>")
def chat(cid):
    info=jwt_decode(request.headers.get("Authorization",""))
    if not info:return {"error":"unauthorized"},401
    body=request.json
    msg=body.get("message","")
    m_user=Message(conv_id=int(cid),sender="user",content=msg)
    db.session.add(m_user);db.session.commit()
    reply=generate_reply(msg)
    m_ai=Message(conv_id=int(cid),sender="ai",content=reply)
    db.session.add(m_ai);db.session.commit()
    return jsonify({
        "prediction":reply,
        "tarot_card":"The Moon",
        "lucky_numbers":[7,15,23,42],
        "luck_pct":88,
        "advice":"Giữ vững niềm tin",
        "emoji":"🔮",
        "color":"neon-blue"
    })

@socketio.on("connect")
def connected():
    emit("status",{"msg":"Connected"})

@socketio.on("oracle_stream")
def oracle_stream(data):
    for token in stream_generate_reply(data["prompt"],data["temp"],data["max"]):
        emit("oracle_token",{"t":token})
        socketio.sleep(0.03)
    emit("oracle_end")
