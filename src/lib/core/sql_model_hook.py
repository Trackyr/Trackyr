from sqlalchemy import create_engine
from sqlalchemy.orm import Session

#,from database import metadata, Job
from trackyr.config import Config
from trackyr.models import Task
from trackyr.models import Source
from trackyr.models import NotificationAgent

import lib.core as core

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
session = Session(engine)

def task_model_to_core_task(task_model):
    t = task_model

    if isinstance(t.source, str):
        t.source = [t.source]

    if isinstance(t.notification_agent, str):
        t.notification_agent = [t.notification_agent]

    return core.task.Task(
            name = t.name,
            id = t.id,
            frequency = t.frequency,
            frequency_unit = "minutes",
            source_ids = t.source,
            notif_agent_ids = t.notification_agent,
            include = t.must_contain.split(","),
            exclude = t.exclude
        )

def load_tasks():
    task_models = session.query(Task).all()
    tasks = []

    for task_model in task_models:
        tasks.append(
            task_model_to_core_task(task_model)
        )

    return tasks

