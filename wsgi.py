"""
WSGI entry point for production deployment with Socket.IO
"""
from app import app, socketio

# Export socketio for gunicorn (not app)
application = socketio

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
