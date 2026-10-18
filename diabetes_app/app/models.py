import json
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db, login_manager


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    predictions = db.relationship(
        "Prediction", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Float, nullable=False)
    hypertension = db.Column(db.Integer, nullable=False)
    heart_disease = db.Column(db.Integer, nullable=False)
    smoking_history = db.Column(db.String(20), nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    hba1c_level = db.Column(db.Float, nullable=False)
    blood_glucose_level = db.Column(db.Float, nullable=False)
    risk_probability = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    predicted_class = db.Column(db.Integer, nullable=False)
    recommendations = db.Column(db.Text, nullable=False, default="[]")
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False, index=True)

    @property
    def probability_pct(self):
        return round(self.risk_probability * 100, 1)

    @property
    def level_class(self):
        return {"Low": "success", "Moderate": "warning", "High": "danger"}[self.risk_level]

    @property
    def recommendation_groups(self):
        groups = {}
        for item in json.loads(self.recommendations):
            groups.setdefault(item["category"], []).append(item["text"])
        return groups


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
