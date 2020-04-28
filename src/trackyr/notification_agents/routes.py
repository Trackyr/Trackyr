from flask import (Blueprint, abort, flash, redirect, render_template, request, url_for)
from trackyr import db
from trackyr.models import NotificationAgent
from trackyr.notification_agents.forms import NotificationAgentForm

import json
import requests

import lib.core.notif_agent as notifAgent

notification_agents = Blueprint('notification_agents', __name__)

@notification_agents.route("/notification_agents/create", methods=['GET', 'POST'])
def create_notification_agents():
    form = NotificationAgentForm()
    if form.validate_on_submit():
        if form.test.data:
            # This button will send a test notification to the Notification Agent.
            # Will need to add IF statements to send different notification messages to different agents.

            webhook_url=form.webhook_url.data
            if form.username.data:
                username=form.username.data
            else:
                username="Trackyr"

            Dict = {1: 'discord'}

            test_notify = notifAgent.NotifAgent(module=Dict.get(form.module.data), module_properties={'webhook':webhook_url,'botname':username})
            notifAgent.test_notif_agent(test_notify)
            
            # Notification message on webui
            flash("A test message has been sent to your notification agent", "notification")
        else:
            notification_agent = NotificationAgent(module=form.module.data,
                                                    name=form.name.data,
                                                    webhook_url=form.webhook_url.data,
                                                    username=form.username.data,
                                                    icon=form.icon.data,
                                                    channel=form.channel.data)
            db.session.add(notification_agent)
            db.session.commit()
            flash('Your notification agent has been saved!', 'top_flash_success')
            return redirect(url_for('main.notification_agents'))
    return render_template('create-notification-agent.html', title='Create Notification Agent', 
                            form=form, legend='Create Notification Agent')

@notification_agents.route("/notification_agents/<int:notification_agent_id>/edit", methods=['GET', 'POST'])
def edit_notification_agent(notification_agent_id):
    notification_agents = NotificationAgent.query.get_or_404(notification_agent_id)
    form = NotificationAgentForm()
    if form.validate_on_submit():
        notification_agents.id = notification_agent_id
        notification_agents.module = form.module.data
        notification_agents.name = form.name.data
        notification_agents.webhook_url = form.webhook_url.data
        notification_agents.username = form.username.data
        notification_agents.icon = form.icon.data
        notification_agents.channel = form.channel.data
        db.session.commit()
        flash('Your notification agent has been updated!', 'top_flash_success')
        return redirect(url_for('main.notification_agents', notification_agent_id=notification_agents.id))
    elif request.method == 'GET':
        form.module.data = notification_agents.module
        form.name.data = notification_agents.name
        form.webhook_url.data = notification_agents.webhook_url
        form.username.data = notification_agents.username
        form.icon.data = notification_agents.icon
        form.channel.data = notification_agents.channel
    return render_template('create-notification-agent.html', title='Update Notification Agent', 
                            form=form, legend='Update Notification Agent')

@notification_agents.route("/notification_agents/<int:notification_agent_id>/delete", methods=['GET', 'POST'])
def delete_notification_agent(notification_agent_id):
    notification_agent = NotificationAgent.query.get_or_404(notification_agent_id)
    db.session.delete(notification_agent)
    db.session.commit()
    flash('Your notification agent has been deleted.', 'top_flash_success')
    return redirect(url_for('main.notification_agents'))