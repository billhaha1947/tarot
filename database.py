from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Không có init_db nữa, Flask init bằng db.init_app()
