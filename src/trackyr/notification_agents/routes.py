from flask import (Blueprint, flash, redirect, render_template, request, url_for)
from trackyr import db
from trackyr.models import NotificationAgent, Task
from trackyr.notification_agents.forms import NotificationAgentForm

import lib.core.notif_agent as notifAgent
from lib.core.state import State

notification_agents = Blueprint('notification_agents', __name__)

@notification_agents.route("/notification_agents/create", methods=['GET', 'POST'])
def create_notification_agents():
    State.load()
    form = NotificationAgentForm()
    if form.validate_on_submit():
        if form.submit.data:
            notification_agent = NotificationAgent(module=form.module.data,
                                                   name=form.name.data,
                                                   webhook_url=form.webhook_url.data,
                                                   username=form.username.data,
                                                   icon=form.icon.data)
            db.session.add(notification_agent)
            db.session.commit()

            State.refresh_notif_agents()

            flash('Your notification agent has been saved!', 'top_flash_success')
            return redirect(url_for('main.notification_agents'))
    return render_template('create-notification-agent.html', title='Create Notification Agent', 
                            form=form, legend='Create Notification Agent')

@notification_agents.route("/notification_agents/<int:notification_agent_id>/edit", methods=['GET', 'POST'])
def edit_notification_agent(notification_agent_id):
    State.load()
    notification_agents = NotificationAgent.query.get_or_404(notification_agent_id)
    form = NotificationAgentForm()
    if form.validate_on_submit():
        notification_agents.id = notification_agent_id
        notification_agents.module = form.module.data
        notification_agents.name = form.name.data
        notification_agents.webhook_url = form.webhook_url.data
        notification_agents.username = form.username.data
        notification_agents.icon = form.icon.data
        db.session.commit()

        State.refresh_notif_agents()

        flash('Your notification agent has been updated!', 'top_flash_success')
        return redirect(url_for('main.notification_agents', notification_agent_id=notification_agents.id))
    elif request.method == 'POST':
        form.module.data = notification_agents.module
        form.name.data = notification_agents.name
        form.webhook_url.data = notification_agents.webhook_url
        form.username.data = notification_agents.username
        notification_agents.icon = form.icon.data
        db.session.commit()

        State.refresh_notif_agents()

        flash('Your notification agent has been updated!', 'top_flash_success')
        return redirect(url_for('main.notification_agents', notification_agent_id=notification_agents.id))
    elif request.method == 'GET':
        form.module.data = notification_agents.module
        form.name.data = notification_agents.name
        form.webhook_url.data = notification_agents.webhook_url
        form.username.data = notification_agents.username
        form.icon.data = notification_agents.icon
        return render_template('create-notification-agent.html', title='Update Notification Agent',
                            form=form, legend='Update Notification Agent')

@notification_agents.route("/notification_agents/<int:notification_agent_id>/delete", methods=['GET', 'POST'])
def delete_notification_agent(notification_agent_id):
    State.load()

    notification_agent = NotificationAgent.query.get_or_404(notification_agent_id)
    tasks = Task.query.all()

    for task in tasks:
        task.notification_agent = [s for s in task.notification_agent if s != notification_agent_id]

        # if this causes a task to  go down to 0 notification agents, then it should be deleted.
        if len(task.notification_agent) == 0:
            db.session.delete(task)
            
    db.session.delete(notification_agent)
    db.session.commit()

    State.refresh_notif_agents()

    flash('Your notification agent has been deleted.', 'top_flash_success')
    return redirect(url_for('main.notification_agents'))

@notification_agents.route("/notification_agents/test", methods=['POST'])
def test_notification_agent():
    json = request.json
    webhook_url = json['webhook']
    if json['username']:
        username = json['username']
    else:
        username = "Trackyr"
    Dict = {1: 'discord'}

    test_notify = notifAgent.NotifAgent(module=Dict.get(int(json['module'])),
                                        module_properties={'webhook': webhook_url,
                                                           'botname': username,
                                                           'avatar': json['avatar']})

    notifAgent.test_notif_agent(test_notify)

    return "Success"
