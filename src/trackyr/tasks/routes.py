from flask import (Blueprint, abort, flash, redirect, render_template, request, url_for)
from wtforms import FieldList, SelectField, FormField
from trackyr import db
from trackyr.models import Task, Source, NotificationAgent
from trackyr.tasks.forms import TaskForm, AddSourceForm, AddNotificationAgentForm

from lib.utils import cron
import lib.core.task as task
from lib.core.state import State

import lib.utils.logger as log

tasks = Blueprint('tasks', __name__)

@tasks.route("/tasks/create", methods=['GET', 'POST'])
def create_tasks():
    State.load()

    form = TaskForm()
    sourceform = AddSourceForm()
    notificationagentform = AddNotificationAgentForm()

    sourceform.source_select.choices=get_source_choices()
    notificationagentform.notification_agent_select.choices=get_notification_agents_choices()
    
    if form.colour_flag.data == "":
        cf="#ff8c00"
    else:
        cf=form.colour_flag.data

#    if form.validate_on_submit():
    if form.submit.data:
        source_list = sorted(request.form.getlist('source_select'), key=int)
        for i in range(0, len(source_list)):
            source_list[i] = int(source_list[i])
        source_list = list(set(source_list))

        notification_agent_list = sorted(request.form.getlist('notification_agent_select'), key=int)
        for i in range(0, len(notification_agent_list)):
            notification_agent_list[i] = int(notification_agent_list[i])
        notification_agent_list = list(set(notification_agent_list))

        new_task = Task(name=form.name.data,
                    frequency=form.frequency.data,
                    source=source_list,
                    notification_agent=notification_agent_list,
                    colour_flag=cf,
                    must_contain=form.must_contain.data,
                    exclude=form.exclude.data)

        db.session.add(new_task)
        db.session.commit()

        State.refresh_tasks()
        cron.add(int(form.frequency.data), "minutes")

        prime_task = task.Task(source_ids=source_list, notif_agent_ids=notification_agent_list, include=[form.must_contain.data], exclude=[form.exclude.data], colour_flag=form.colour_flag.data)
        task.prime(prime_task, notify=True, recent_ads=int(form.prime_count.data))

        flash('Your task has been created!', 'top_flash_success')

        return redirect(url_for('main.tasks'))
    return render_template('create-task.html', title='Create a Task',
                            form=form, sourceform=sourceform, notificationagentform=notificationagentform, action='create', legend='Create a Task')

@tasks.route("/tasks/<int:task_id>/edit", methods=['GET', 'POST'])
def edit_task(task_id):
    State.load()
    edit_task = Task.query.get_or_404(task_id)

    source_count = len(edit_task.source)
    notification_agent_count = len(edit_task.notification_agent)

    class LocalForm(TaskForm):pass
    LocalForm.sources = FieldList(FormField(AddSourceForm), min_entries=source_count)
    LocalForm.notification_agents = FieldList(FormField(AddNotificationAgentForm), min_entries=notification_agent_count)

    form = LocalForm()
    sourceform = AddSourceForm()
    notificationagentform = AddNotificationAgentForm()

    sourceform.source_select.choices=get_source_choices()
    notificationagentform.notification_agent_select.choices=get_notification_agents_choices()

#    if form.validate_on_submit():
    if form.submit.data:
        source_list = sorted(request.form.getlist('source_select'), key=int)
        for i in range(0, len(source_list)):
            source_list[i] = int(source_list[i])
        source_list = list(set(source_list))

        notification_agent_list = sorted(request.form.getlist('notification_agent_select'), key=int)
        for i in range(0, len(notification_agent_list)):
            notification_agent_list[i] = int(notification_agent_list[i])
        notification_agent_list = list(set(notification_agent_list))

        edit_task.id = task_id
        edit_task.name = form.name.data
        edit_task.frequency = form.frequency.data
        edit_task.source = source_list
        edit_task.notification_agent = notification_agent_list
        edit_task.colour_flag = form.colour_flag.data
        edit_task.must_contain = form.must_contain.data
        edit_task.exclude = form.exclude.data
        db.session.commit()

        State.refresh_tasks()
        task.refresh_cron()

        flash('Your task has been updated!', 'top_flash_success')
        return redirect(url_for('main.tasks', task_id=edit_task.id))
    elif request.method == 'GET':
        form.name.data = edit_task.name
        form.frequency.data = edit_task.frequency
        sourceform.source_select.data = edit_task.source
        notificationagentform.notification_agent_select.data = edit_task.notification_agent
        form.colour_flag.data = edit_task.colour_flag
        form.must_contain.data = edit_task.must_contain
        form.exclude.data = edit_task.exclude

    return render_template('create-task.html', title='Update Task', 
                            form=form, sourceform=sourceform, notificationagentform=notificationagentform, source_data=edit_task.source, notification_agent_data=edit_task.notification_agent, action='edit', legend='Update Task')
                            
@tasks.route("/tasks/<int:task_id>/delete", methods=['GET', 'POST'])
def delete_task(task_id):
    delete_task = Task.query.get_or_404(task_id)
    db.session.delete(delete_task)
    db.session.commit()

    State.refresh_tasks()
    task.refresh_cron()

    flash('Your task has been deleted.', 'top_flash_success')
    return redirect(url_for('main.tasks'))

def get_source_choices():
    source_choices = db.session.query(Source.name).all()
    return [(g.id, g.name) for g in Source.query.order_by('name')]

def get_notification_agents_choices():
    notification_agents_choices = db.session.query(NotificationAgent.name).all()
    return [(g.id, g.name) for g in NotificationAgent.query.order_by('name')]
