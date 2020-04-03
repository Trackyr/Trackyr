from flask import (Blueprint, abort, flash, redirect, render_template, request, url_for)

from trackyr import db
from trackyr.models import Task, Source, NotificationAgent
from trackyr.tasks.forms import TaskForm

tasks = Blueprint('tasks', __name__)

@tasks.route("/tasks/create", methods=['GET', 'POST'])
def create_tasks():
    form = TaskForm()
    
    form.source.choices=get_source_choices()
    form.notification_agent.choices=get_notification_agents_choices()
    
    if form.validate_on_submit():
        task = Task(name=form.name.data, 
                    frequency=form.frequency.data, 
                    source=form.source.data,
                    notification_agent=form.notification_agent.data,
                    colour_flag=form.colour_flag.data, 
                    must_contain=form.must_contain.data, 
                    exclude=form.exclude.data)
        db.session.add(task)
        db.session.commit()
        flash('Your task has been created!', 'success')
        return redirect(url_for('main.tasks'))
    return render_template('create-task.html', title='Create a Task', 
                            form=form, legend='Create a Task')
    
@tasks.route("/tasks/<int:task_id>/edit", methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = TaskForm()

    form.source.choices=get_source_choices()
    form.notification_agent.choices=get_notification_agents_choices()

    if form.validate_on_submit():
        task.id = task_id
        task.name = form.name.data
        task.frequency = form.frequency.data
        task.source = form.source.data
        task.notification_agent = form.notification_agent.data
        task.colour_flag = form.colour_flag.data
        task.must_contain = form.must_contain.data
        task.exclude = form.exclude.data
        db.session.commit()
        flash('Your task has been updated!', 'success')
        return redirect(url_for('main.tasks', task_id=task.id))
    elif request.method == 'GET':
        form.name.data = task.name
        form.frequency.data = task.frequency
        form.source.data = task.source
        form.notification_agent.data = task.notification_agent
        form.colour_flag.data = task.colour_flag
        form.must_contain.data = task.must_contain
        form.exclude.data = task.exclude
    return render_template('create-task.html', title='Update Task', 
                            form=form, legend='Update Task')

@tasks.route("/tasks/<int:task_id>/delete", methods=['GET', 'POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Your task has been deleted.', 'success')
    return redirect(url_for('main.tasks'))

def get_source_choices():
    source_choices = db.session.query(Source.name).all()
    return [(g.id, g.name) for g in Source.query.order_by('name')]
    
def get_notification_agents_choices():
    notification_agents_choices = db.session.query(NotificationAgent.name).all()
    return [(g.id, g.name) for g in NotificationAgent.query.order_by('name')]