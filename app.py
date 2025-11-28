# app.py (production-ready for Render + Socket.IO)
import os
import datetime
import eventlet
eventlet.monkey_patch()  # bắt buộc cho eventlet + socketio

import jwt
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# load env
load_dotenv()

# local imports (database, model manager)
from database import init_db, db
from model_manager import generate_reply, stream_generate_reply

# Config
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "static/avatar")
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif"}
JWT_SECRET = os.getenv("TAROT_JWT_SECRET", "LOCAL_JWT_SECRET")
SECRET_KEY = os.getenv("TAROT_SECRET", "LOCAL_SECRET_TAROT")

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["SECRET_KEY"] = SECRET_KEY
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024

# Initialize DB (will create tables)
init_db(app)

# SocketIO with eventlet async mode
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# --- Models (using SQLAlchemy instance from database.py) ---
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar = db.Column(db.String(256), default="/static/avatar/default.png")
    role = db.Column(db.String(32), default="user")
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Conversation(db.Model):
    __tablename__ = "conversations"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(256), default="Trò chuyện mới")
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    conv_id = db.Column(db.Integer, nullable=False)
    sender = db.Column(db.String(16))  # 'user' or 'ai'
    content = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# --- Auth helpers ---
def jwt_encode(data: dict):
    payload = data.copy()
    payload["iat"] = datetime.datetime.utcnow()
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def jwt_decode_token(auth_header: str):
    """
    Accepts Authorization header value. Supports:
    - "Bearer <token>"
    - raw token
    Returns decoded payload or None.
    """
    if not auth_header:
        return None
    token = auth_header
    parts = token.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        token = parts[1]
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except Exception:
        return None

# --- Routes (UI) ---
@app.route("/")
def home():
    return render_template("layout.html")

@app.route("/health")
def health():
    return jsonify({"ok": True, "ts": datetime.datetime.utcnow().isoformat()})

# --- API: auth & user ---
@app.post("/api/register")
def register():
    data = request.json or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        return jsonify({"error": "Thiếu dữ liệu"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User tồn tại"}), 400
    u = User(username=username, password_hash=generate_password_hash(password))
    db.session.add(u)
    db.session.commit()
    token = jwt_encode({"uid": u.id, "username": u.username, "role": u.role})
    return jsonify({"status": "ok", "token": token})

@app.post("/api/login")
def login():
    data = request.json or {}
    username = data.get("username") or ""
    password = data.get("password") or ""
    u = User.query.filter_by(username=username).first()
    if not u or not check_password_hash(u.password_hash, password):
        return jsonify({"error": "Sai tài khoản"}), 401
    token = jwt_encode({"uid": u.id, "username": u.username, "avatar": u.avatar, "role": u.role})
    return jsonify({"token": token})

@app.post("/api/avatar")
def upload_avatar():
    auth = request.headers.get("Authorization", "")
    info = jwt_decode_token(auth)
    if not info:
        return jsonify({"error": "Unauthorized"}), 401
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400
    f = request.files["file"]
    filename = secure_filename(f.filename)
    if "." in filename:
        ext = filename.rsplit(".", 1)[1].lower()
    else:
        ext = ""
    if ext not in ALLOWED_EXT:
        return jsonify({"error": "Invalid file type"}), 400
    save_name = f"user_{info['uid']}.{ext}"
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], save_name)
    f.save(save_path)
    u = User.query.get(int(info["uid"]))
    if u:
        u.avatar = f"/static/avatar/{save_name}"
        db.session.commit()
        return jsonify({"avatar": u.avatar})
    return jsonify({"error": "User not found"}), 404

# --- Conversations & messages ---
@app.get("/api/conversations")
def list_conv():
    auth = request.headers.get("Authorization", "")
    info = jwt_decode_token(auth)
    if not info:
        return jsonify({"error": "unauthorized"}), 401
    convs = Conversation.query.filter_by(user_id=int(info["uid"])).order_by(Conversation.updated.desc()).all()
    items = [{"id": c.id, "title": c.title, "updated": c.updated.isoformat()} for c in convs]
    return jsonify({"items": items})

@app.post("/api/newchat")
def new_chat():
    auth = request.headers.get("Authorization", "")
    info = jwt_decode_token(auth)
    if not info:
        return jsonify({"error": "unauthorized"}), 401
    t = datetime.datetime.utcnow().strftime("%H:%M %d/%m/%Y")
    c = Conversation(user_id=int(info["uid"]), title=f"Chat {t}")
    db.session.add(c)
    db.session.commit()
    return jsonify({"id": c.id, "title": c.title})

@app.get("/api/history/<cid>")
def history(cid):
    auth = request.headers.get("Authorization", "")
    info = jwt_decode_token(auth)
    if not info:
        return jsonify({"error": "unauthorized"}), 401
    msgs = Message.query.filter_by(conv_id=int(cid)).order_by(Message.created.asc()).all()
    items = [{"s": m.sender, "c": m.content, "t": m.created.isoformat()} for m in msgs]
    return jsonify({"items": items})

@app.post("/api/chat/<cid>")
def chat_sync(cid):
    auth = request.headers.get("Authorization", "")
    info = jwt_decode_token(auth)
    if not info:
        return jsonify({"error": "unauthorized"}), 401
    body = request.json or {}
    msg = body.get("message", "")
    # Save user message
    m_user = Message(conv_id=int(cid), sender="user", content=msg)
    db.session.add(m_user)
    db.session.commit()
    # Generate reply (blocking)
    payload = generate_reply(msg)
    # If generate_reply returns dict, we may want stringified content
    reply_text = payload if isinstance(payload, str) else str(payload)
    m_ai = Message(conv_id=int(cid), sender="ai", content=reply_text)
    db.session.add(m_ai)
    db.session.commit()
    # Return structured payload if available
    if isinstance(payload, dict):
        return jsonify(payload)
    else:
        # default structured
        return jsonify({
            "prediction": reply_text,
            "tarot_card": "The Moon",
            "lucky_numbers": [7, 15, 23, 42],
            "luck_pct": 88,
            "advice": "Giữ vững niềm tin",
            "emoji": "🔮",
            "color": "neon-blue"
        })

# --- Socket.IO streaming endpoint ---
@socketio.on("connect")
def connected():
    emit("status", {"msg": "Connected"})

@socketio.on("oracle_stream")
def oracle_stream(data):
    """
    data: { prompt, temp, max, conv_id (optional), token: 'Bearer ...' optional }
    We accept token either in data.auth_token or standard Authorization header.
    """
    # auth
    bearer = data.get("auth_token") or request.headers.get("Authorization", "")
    info = jwt_decode_token(bearer)
    if not info:
        emit("error", {"error": "unauthorized"})
        return

    prompt = data.get("prompt", "")
    temp = float(data.get("temp", 0.7))
    max_tokens = int(data.get("max", 150))
    conv_id = data.get("conv_id")

    # Save user message to DB (optional)
    try:
        if conv_id:
            m_user = Message(conv_id=int(conv_id), sender="user", content=prompt)
            db.session.add(m_user)
            db.session.commit()
    except Exception:
        pass

    # stream tokens from model_manager.stream_generate_reply (generator)
    try:
        gen = stream_generate_reply(prompt, temp, max_tokens)
    except Exception as e:
        # If stream_generate_reply raises, try generate_reply fallback
        final = generate_reply(prompt, temp, max_tokens)
        # emit final result as single payload
        emit("oracle_end", {"payload": final})
        return

    buffer = ""
    for chunk in gen:
        # chunk may be str tokens, or final dict
        if isinstance(chunk, str):
            buffer += chunk
            emit("oracle_token", {"t": chunk})
        elif isinstance(chunk, dict):
            # final structured payload
            final_payload = chunk
            # Save AI message into DB if conv_id present
            try:
                if conv_id:
                    m_ai = Message(conv_id=int(conv_id), sender="ai", content=str(final_payload))
                    db.session.add(m_ai)
                    db.session.commit()
            except Exception:
                pass
            emit("oracle_end", {"payload": final_payload})
        else:
            # unknown type -> stringify and send
            s = str(chunk)
            buffer += s
            emit("oracle_token", {"t": s})
        # cooperative sleep (eventlet)
        socketio.sleep(0)
    # If generator completed without dict final, emit end with text
    if not isinstance(chunk, dict):
        emit("oracle_end", {"payload": {"prediction": buffer}})

# Serve static files for default avatar or others (optional)
@app.route("/static/avatar/<path:filename>")
def static_avatar(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# --- Run app ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", os.environ.get("RENDER_PORT", 5000)))
    # Use eventlet server
    socketio.run(app, host="0.0.0.0", port=port)
