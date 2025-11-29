"""
WSGI entry point for production deployment
"""
import eventlet
eventlet.monkey_patch()

from app import app, socketio, db
import os

# Initialize database
with app.app_context():
    db.create_all()
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    print("✓ Database initialized")
    print("✓ Upload folder created")

# Export for gunicorn
application = socketio

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
