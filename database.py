import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class QueryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_type = db.Column(db.String(50), nullable=False)
    case_number = db.Column(db.String(50), nullable=False)
    filing_year = db.Column(db.Integer, nullable=False)
    query_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    raw_response = db.Column(db.Text, nullable=True) # To store the raw HTML/JSON response from scraping
    status = db.Column(db.String(20), nullable=True) # e.g., 'SUCCESS', 'ERROR'
    error_message = db.Column(db.Text, nullable=True) # For logging specific errors

    def __repr__(self):
        return f"<QueryLog {self.case_type}-{self.case_number}/{self.filing_year}>"

def init_db(app):
    # Determine the absolute path for the database file
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'court_data.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Suppress warning

    db.init_app(app)
    with app.app_context():
        # Create the instance folder if it doesn't exist
        instance_path = os.path.join(basedir, 'instance')
        os.makedirs(instance_path, exist_ok=True)
        db.create_all() # Create tables if they don't exist