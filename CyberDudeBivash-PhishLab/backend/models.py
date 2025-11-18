# backend/models.py

from datetime import datetime
from .extensions import db

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    targets = db.relationship("Target", backref="campaign", lazy=True)
    events = db.relationship("Event", backref="campaign", lazy=True)

class Target(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaign.id"), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=True)
    token = db.Column(db.String(64), unique=True, nullable=False)
    status = db.Column(db.String(32), default="not_clicked")
    first_clicked_at = db.Column(db.DateTime, nullable=True)
    first_submitted_at = db.Column(db.DateTime, nullable=True)

    events = db.relationship("Event", backref="target", lazy=True)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaign.id"), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey("target.id"), nullable=False)
    type = db.Column(db.String(32), nullable=False)  # clicked / submitted / reported
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_agent = db.Column(db.String(512))
    ip = db.Column(db.String(64))
