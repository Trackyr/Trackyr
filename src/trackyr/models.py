from flask import current_app
from pip import locations

from trackyr import db
from trackyr.notification_agents.forms import NotificationAgentForm
from trackyr.sources.forms import SourceForm
from trackyr.tasks.forms import TaskForm


class NotificationAgent(db.Model):
    __tablename__ = 'notification_agents'
    id = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    webhook_url = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(100), nullable=False)
    channel = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Notification Agent('{self.name}')"

class Source(db.Model):
    __tablename__ = 'sources'
    id = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    website = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    range = db.Column (db.String(100), nullable=True)
    subreddit = db.Column (db.String(100), nullable=True)

    def __repr__(self):
        return f"Source('{self.name}')"

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.Integer, nullable=False)
    source = db.Column(db.Integer, nullable=False)
    notification_agent = db.Column(db.Integer, nullable=False)
    colour_flag = db.Column(db.String(100), nullable=True)
    must_contain = db.Column(db.String(100), nullable=True)
    exclude = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"Task('ID: {self.id}','{self.name}','{self.frequency} Minutes','Source: {self.source}','Notification Agent: {self.notification_agent}','Must Contain: {self.must_contain}','Exclude: {self.exclude}')"