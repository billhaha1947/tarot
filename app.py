from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import jwt
import datetime
import os
import json
from functools import wraps
from database import db, User, Chat, Message
from model_manager import ModelManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tarot-oracle-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tarot_oracle.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/avatar'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
model_manager = ModelManager()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
        except:
            return jsonify({'error': 'Token invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Tarot Oracle is running'}), 200

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/chat')
def chat_page():
    return render_template('chat.html')

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not username or not email or not password:
        return jsonify({'error': 'Vui lòng điền đầy đủ thông tin'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Tên đăng nhập đã tồn tại'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email đã được sử dụng'}), 400
    
    hashed_password = generate_password_hash(password)
    user = User(username=username, email=email, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'message': 'Đăng ký thành công',
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'avatar': user.avatar
        }
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'error': 'Vui lòng điền đầy đủ thông tin'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Tên đăng nhập hoặc mật khẩu không đúng'}), 401
    
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'message': 'Đăng nhập thành công',
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'avatar': user.avatar
        }
    }), 200

@app.route('/api/user', methods=['GET'])
@token_required
def get_user(current_user):
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'avatar': current_user.avatar
    }), 200

@app.route('/api/user/password', methods=['PUT'])
@token_required
def change_password(current_user):
    data = request.json
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')
    
    if not check_password_hash(current_user.password, old_password):
        return jsonify({'error': 'Mật khẩu cũ không đúng'}), 400
    
    current_user.password = generate_password_hash(new_password)
    db.session.commit()
    
    return jsonify({'message': 'Đổi mật khẩu thành công'}), 200

@app.route('/api/user/avatar', methods=['POST'])
@token_required
def upload_avatar(current_user):
    if 'avatar' not in request.files:
        return jsonify({'error': 'Không có file nào được tải lên'}), 400
    
    file = request.files['avatar']
    
    if file.filename == '':
        return jsonify({'error': 'Không có file nào được chọn'}), 400
    
    if file and allowed_file(file.filename):
        filename = f"user_{current_user.id}_{secure_filename(file.filename)}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        current_user.avatar = f'/static/avatar/{filename}'
        db.session.commit()
        
        return jsonify({
            'message': 'Tải avatar thành công',
            'avatar': current_user.avatar
        }), 200
    
    return jsonify({'error': 'Định dạng file không hợp lệ'}), 400

@app.route('/api/chats', methods=['GET'])
@token_required
def get_chats(current_user):
    chats = Chat.query.filter_by(user_id=current_user.id).order_by(Chat.updated_at.desc()).all()
    return jsonify([{
        'id': chat.id,
        'title': chat.title,
        'created_at': chat.created_at.isoformat(),
        'updated_at': chat.updated_at.isoformat()
    } for chat in chats]), 200

@app.route('/api/chats', methods=['POST'])
@token_required
def create_chat(current_user):
    data = request.json
    title = data.get('title', 'Cuộc trò chuyện mới')
    
    chat = Chat(user_id=current_user.id, title=title)
    db.session.add(chat)
    db.session.commit()
    
    return jsonify({
        'id': chat.id,
        'title': chat.title,
        'created_at': chat.created_at.isoformat(),
        'updated_at': chat.updated_at.isoformat()
    }), 201

@app.route('/api/chats/<int:chat_id>', methods=['GET'])
@token_required
def get_chat(current_user, chat_id):
    chat = Chat.query.filter_by(id=chat_id, user_id=current_user.id).first()
    
    if not chat:
        return jsonify({'error': 'Không tìm thấy cuộc trò chuyện'}), 404
    
    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.created_at).all()
    
    return jsonify({
        'id': chat.id,
        'title': chat.title,
        'messages': [{
            'id': msg.id,
            'role': msg.role,
            'content': msg.content,
            'oracle_data': json.loads(msg.oracle_data) if msg.oracle_data else None,
            'created_at': msg.created_at.isoformat()
        } for msg in messages]
    }), 200

@app.route('/api/chats/<int:chat_id>', methods=['DELETE'])
@token_required
def delete_chat(current_user, chat_id):
    chat = Chat.query.filter_by(id=chat_id, user_id=current_user.id).first()
    
    if not chat:
        return jsonify({'error': 'Không tìm thấy cuộc trò chuyện'}), 404
    
    Message.query.filter_by(chat_id=chat_id).delete()
    db.session.delete(chat)
    db.session.commit()
    
    return jsonify({'message': 'Đã xóa cuộc trò chuyện'}), 200

@app.route('/api/models', methods=['GET'])
@token_required
def get_models(current_user):
    return jsonify(model_manager.get_available_models()), 200

@app.route('/api/settings', methods=['GET'])
@token_required
def get_settings(current_user):
    return jsonify({
        'model': model_manager.current_model,
        'temperature': model_manager.temperature,
        'max_tokens': model_manager.max_tokens
    }), 200

@app.route('/api/settings', methods=['PUT'])
@token_required
def update_settings(current_user):
    data = request.json
    
    if 'model' in data:
        model_manager.set_model(data['model'])
    if 'temperature' in data:
        model_manager.temperature = float(data['temperature'])
    if 'max_tokens' in data:
        model_manager.max_tokens = int(data['max_tokens'])
    
    return jsonify({'message': 'Cập nhật cài đặt thành công'}), 200

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('send_message')
def handle_message(data):
    try:
        token = data.get('token')
        if not token:
            emit('error', {'message': 'Token missing'})
            return
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user = User.query.get(decoded['user_id'])
        
        if not user:
            emit('error', {'message': 'User not found'})
            return
        
        chat_id = data.get('chat_id')
        prompt = data.get('message', '')
        
        if not chat_id or not prompt:
            emit('error', {'message': 'Chat ID and message required'})
            return
        
        chat = Chat.query.filter_by(id=chat_id, user_id=user.id).first()
        if not chat:
            emit('error', {'message': 'Chat not found'})
            return
        
        user_message = Message(chat_id=chat_id, role='user', content=prompt)
        db.session.add(user_message)
        db.session.commit()
        
        emit('user_message', {
            'id': user_message.id,
            'content': prompt,
            'created_at': user_message.created_at.isoformat()
        })
        
        full_response = ""
        oracle_data = None
        
        for chunk in model_manager.stream_generate_reply(prompt):
            if chunk['type'] == 'token':
                full_response += chunk['content']
                emit('ai_token', {'content': chunk['content']})
            elif chunk['type'] == 'oracle':
                oracle_data = chunk['data']
        
        ai_message = Message(
            chat_id=chat_id,
            role='assistant',
            content=full_response,
            oracle_data=json.dumps(oracle_data) if oracle_data else None
        )
        db.session.add(ai_message)
        
        if Message.query.filter_by(chat_id=chat_id).count() <= 2:
            chat.title = prompt[:50] + ('...' if len(prompt) > 50 else '')
        
        chat.updated_at = datetime.datetime.utcnow()
        db.session.commit()
        
        emit('ai_complete', {
            'id': ai_message.id,
            'content': full_response,
            'oracle_data': oracle_data,
            'created_at': ai_message.created_at.isoformat()
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    with app.app_context():
        db.create_all()
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        print("✓ Database initialized")
        print("✓ Upload folder created")
    
    print(f"🔮 Starting Tarot Oracle on port {port}...")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
