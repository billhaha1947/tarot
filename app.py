from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from database import db, User, Conversation, Message
from model_manager import generate_reply, stream_generate_reply
import jwt, os, random, json
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tarot_hub.db'
app.config['SECRET_KEY'] = "LOCAL_SECRET_KEY"

db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

JWT_SECRET = "LOCAL_JWT_SECRET"
AVATAR_DIR = "static/avatar"
os.makedirs(AVATAR_DIR, exist_ok=True)

@app.before_request
def init_db():
    if not os.path.exists("tarot_hub.db"):
        with app.app_context():
            db.create_all()

def create_jwt(uid, role):
    return jwt.encode({"uid": uid, "role": role}, JWT_SECRET, algorithm="HS256")

def decode_jwt(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except:
        return None

# --- Auth API ---
@app.route("/api/register", methods=["POST"])
def register():
    u = request.json["username"]
    p = request.json["password"]
    if User.query.filter_by(username=u).first():
        return jsonify({"error":"Tài khoản đã tồn tại"})
    user = User(username=u, password=generate_password_hash(p))
    db.session.add(user); db.session.commit()
    return jsonify({"msg":"Đăng ký thành công"})

@app.route("/api/login", methods=["POST"])
def login():
    u = request.json["username"]
    p = request.json["password"]
    user = User.query.filter_by(username=u).first()
    if not user or not check_password_hash(user.password, p):
        return jsonify({"error":"Sai thông tin đăng nhập"})
    token = create_jwt(user.id, user.role)
    return jsonify({"token": token})

@app.route("/api/change_password", methods=["POST"])
def change_password():
    info = decode_jwt(request.headers.get("Authorization","").replace("Bearer ",""))
    if not info: return jsonify({"error":"Unauthorized"})
    user = User.query.get(info["uid"])
    old = request.json["old"]; new = request.json["new"]
    if not check_password_hash(user.password, old):
        return jsonify({"error":"Mật khẩu cũ sai"})
    user.password = generate_password_hash(new)
    db.session.commit()
    return jsonify({"msg":"Đổi mật khẩu thành công"})

@app.route("/api/upload_avatar", methods=["POST"])
def upload_avatar():
    token = request.headers.get("Authorization","").replace("Bearer ","")
    info = decode_jwt(token)
    if not info: return jsonify({"error":"Unauthorized"})
    file = request.files["avatar"]
    fn = secure_filename(file.filename)
    path = f"{AVATAR_DIR}/{info['uid']}_{fn}"
    file.save(path)
    user = User.query.get(info["uid"])
    user.avatar = path; db.session.commit()
    return jsonify({"avatar": path})

# --- Web pages ---
@app.route("/")
def home():
    return render_template("login.html")

@app.route("/chat")
def chat_page():
    return render_template("chat.html")

@app.route("/settings")
def settings_page():
    return render_template("settings.html")

# --- SocketIO Chat streaming ---
@socketio.on("send_prompt")
def handle_prompt(data):
    token = decode_jwt(data.get("jwt"))
    if not token:
        emit("reply_chunk", {"chunk":"\n❌ Bạn chưa đăng nhập!"})
        return

    uid = token["uid"]
    convo = Conversation.query.filter_by(user_id=uid).order_by(Conversation.id.desc()).first()
    if not convo:
        convo = Conversation(user_id=uid, title="Chat mới")
        db.session.add(convo); db.session.commit()

    emit("typing", {"status":True})

    prompt = data["prompt"]
    # Lưu message user
    db.session.add(Message(convo_id=convo.id, sender="user", text=prompt))
    db.session.commit()

    # Streaming AI
    full = ""
    for ch in stream_generate_reply(prompt, data.get("temperature",0.7), data.get("max_tokens",200)):
        emit("reply_chunk", {"chunk":ch})
        full += ch
    emit("typing", {"status":False})

    # Lưu AI message
    db.session.add(Message(convo_id=convo.id, sender="ai", text=full))
    db.session.commit()

    # Auto-title nếu là chat đầu tiên
    if convo.title == "Chat mới":
        words = prompt.split()
        convo.title = " ".join(words[:4]) + "…" if len(words)>=4 else prompt[:24]
        db.session.commit()
        emit("convo_title", {"title":convo.title})

    # Oracle JSON bổ trợ
    oracle = json.loads(generate_reply(prompt))
    emit("oracle_json", oracle)

# --- Lịch sử ---
@app.route("/api/history")
def history():
    token = decode_jwt(request.headers.get("Authorization","").replace("Bearer ",""))
    if not token: return jsonify([])
    convos = Conversation.query.filter_by(user_id=token["uid"]).all()
    res = {}
    for c in convos:
        msgs = Message.query.filter_by(convo_id=c.id).all()
        res[c.id] = {
            "title": c.title,
            "messages": [{"sender":m.sender,"text":m.text} for m in msgs]
        }
    return jsonify(res)

# --- Manifest, service-worker ---
@app.route('/manifest.json')
def manifest():
    return send_from_directory(".", "manifest.json")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
