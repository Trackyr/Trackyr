from lib import core

from copy import deepcopy

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

#,from database import metadata, Job
from trackyr.config import Config

from trackyr import models

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
session = Session(engine)

def to_new_core_task(task_model):
    t = deepcopy(task_model)

    if not isinstance(t.source, list):
        t.source = [t.source]

    if not isinstance(t.notification_agent, list):
        t.notification_agent = [t.notification_agent]

    return core.Task(
            name = t.name,
            id = t.id,
            frequency = t.frequency,
            frequency_unit = "minutes",
            source_ids = t.source,
            notif_agent_ids = t.notification_agent,
            include = t.must_contain.split(","),
            exclude = t.exclude.split(",")
        )

def to_new_task_model(core_task):
    c = core_task

    m = models.Task()

    m.name = c.name
    m.id = c.id
    m.frequency = c.frequency
    #m.frequency_unit = "minutes"
    m.source = c.source_ids[0]
    m.notification_agent = c.notif_agent_ids[0]
    m.must_contain = ",".join(c.include)
    m.exclude = ",".join(c.exclude)

    m.colour_flag = ""
    return m

def to_existing_task_model(core_task, task_model):
    c = core_task
    m = task_model

    m.name = c.name
    m.id = c.id
    m.frequency = c.frequency
    #m.frequency_unit = "minutes"
    m.source = c.source_ids[0]
    m.notification_agent = c.notif_agent_ids[0]
    m.must_contain = ",".join(c.include)
    m.exclude = ",".join(c.exclude)

def delete_task_model(core_task):
    task_model = session.query(models.Task).get(core_task.id)
    session.delete(task_model)

def to_new_core_notif_agent(notif_agent_model):
    n = deepcopy(notif_agent_model)
    n.module_properties = {
        "webhook": n.webhook_url,
        "botname": n.username
    }

    return core.NotifAgent(
                id = n.id,
                name = n.name,
                module = n.module,
                module_properties = n.module_properties,
            )

def to_new_core_source(source_model):
    s = deepcopy(source_model)

    s.module_properties = {
        "url": s.website
    }

    return core.Source(
                id = s.id,
                name = s.name,
                module = s.module,
                module_properties = s.module_properties
            )

def to_task_model(core_task):
    pass

def to_source_model(core_source):
    pass

def to_notif_agent_model(core_notif_agent):
    pass

def load_core_tasks():
    task_models = session.query(models.Task).all()
    tasks = {}

    for task_model in task_models:
        tasks[task_model.id] = to_new_core_task(task_model)

    return tasks

def load_core_sources():
    source_models = session.query(models.Source).all()
    sources = {}

    for source_model in source_models:
        sources[source_model.id] = to_new_core_source(source_model)

    return sources

def load_core_notif_agents():
    notif_agent_models = session.query(models.NotificationAgent).all()
    notif_agents = {}

    for notif_agent_model in notif_agent_models:
        notif_agents[notif_agent_model.id] = to_new_core_notif_agent(notif_agent_model)

    return notif_agents

def save_to_db(core_tasks):
    for id in core_tasks:

        found = session.query(models.Task).get(id)
        if found is not None:
            to_existing_task_model(core_tasks[id], found)

        else:
            task_model = to_new_task_model(core_tasks[id])
            session.add(task_model)

    session.commit()
