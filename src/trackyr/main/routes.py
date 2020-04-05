from flask import render_template, request, Blueprint
from trackyr.models import NotificationAgent, Source, Task

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
@main.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

@main.route("/tasks")
def tasks():
    sources = Source.query.all()
    notification_agents = NotificationAgent.query.all()
    tasks = Task.query.all()
    return render_template('tasks.html', title='Tasks', sources=sources, notification_agents=notification_agents, tasks=tasks)

@main.route("/notification_agents")
def notification_agents():
    notification_agents = NotificationAgent.query.all()
    return render_template('notification-agents.html', title='Notification Agents', notification_agents=notification_agents)

@main.route("/sources")
def sources():
    sources = Source.query.all()
    return render_template('sources.html', title='Sources', sources=sources)

@main.route("/trackyr_config")
def trackyr_config():
    return render_template('trackyr-config.html', title='Config')