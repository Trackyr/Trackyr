from flask import (Blueprint, abort, flash, redirect, render_template, request, url_for)

from trackyr import db
from trackyr.models import Task, Source, NotificationAgent
from trackyr.tasks.forms import TaskForm

from lib.utils import cron
import lib.core.task as task
from lib.core.state import State

tasks = Blueprint('tasks', __name__)

@tasks.route("/tasks/create", methods=['GET', 'POST'])
def create_tasks():
    State.load()
    form = TaskForm()

    form.source.choices=get_source_choices()
    form.notification_agent.choices=get_notification_agents_choices()

    if form.colour_flag.data == "":
        cf="#ff8c00"
    else:
        cf=form.colour_flag.data

    if form.validate_on_submit():
        new_task = Task(name=form.name.data,
                    frequency=form.frequency.data,
                    source=form.source.data,
                    notification_agent=form.notification_agent.data,
                    colour_flag=cf,
                    must_contain=form.must_contain.data,
                    exclude=form.exclude.data)
        db.session.add(new_task)
        db.session.commit()

        State.refresh_tasks()

        cron.add(int(form.frequency.data), "minutes")

        prime_task = task.Task(source_ids=[form.source.data], notif_agent_ids=[form.notification_agent.data], include=[form.must_contain.data], exclude=[form.exclude.data], colour_flag=form.colour_flag.data)
        task.prime(prime_task, notify=True, recent_ads=int(form.prime_count.data))

        flash('Your task has been created!', 'top_flash_success')

        return redirect(url_for('main.tasks'))
    return render_template('create-task.html', title='Create a Task', 
                            form=form, legend='Create a Task')

@tasks.route("/tasks/<int:task_id>/edit", methods=['GET', 'POST'])
def edit_task(task_id):
    State.load()
    edit_task = Task.query.get_or_404(task_id)
    form = TaskForm()

    form.source.choices=get_source_choices()
    form.notification_agent.choices=get_notification_agents_choices()

    if form.validate_on_submit():
        edit_task.id = task_id
        edit_task.name = form.name.data
        edit_task.frequency = form.frequency.data
        edit_task.source = form.source.data
        edit_task.notification_agent = form.notification_agent.data
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
        form.source.data = edit_task.source
        form.notification_agent.data = edit_task.notification_agent
        form.colour_flag.data = edit_task.colour_flag
        form.must_contain.data = edit_task.must_contain
        form.exclude.data = edit_task.exclude
    return render_template('create-task.html', title='Update Task', 
                            form=form, legend='Update Task')

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
