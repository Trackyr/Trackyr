from flask import render_template, request, Blueprint
from trackyr.models import NotificationAgent, Source, Task, Modules
from trackyr.main.forms import BlankForm
import lib.core.version as versionCheck

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
    form = BlankForm()
    notification_agents = NotificationAgent.query.all()
    tasks = Task.query.all()
    return render_template('notification-agents.html', title='Notification Agents', notification_agents=notification_agents, tasks=tasks, form=form)

@main.route("/sources")
def sources():
    form = BlankForm()
    sources = Source.query.all()
    tasks = Task.query.all()
    modules = Modules.query.all()
    return render_template('sources.html', title='Sources', sources=sources, tasks=tasks, modules=modules, form=form)

@main.route("/trackyr_config", methods=['GET', 'POST'])
def trackyr_config():
    vcheck = versionCheck.is_latest_version()
    return render_template('trackyr-config.html', title='Config', update_available=vcheck)
