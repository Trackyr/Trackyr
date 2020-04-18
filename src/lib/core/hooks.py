from copy import deepcopy

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import lib.core.task as task
import lib.core.source as source
import lib.core.notif_agent as notif_agent

from trackyr import models
from trackyr.config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
session = Session(engine)


def to_core_tasks(task_models):
    tasks = {}

    for t in task_models:
        core_task = to_new_core_task(t)
        tasks[core_task.id] = core_task

    return tasks

def to_new_core_task(task_model):
    t = deepcopy(task_model)

    if not isinstance(t.source, list):
        t.source = [t.source]

    if not isinstance(t.notification_agent, list):
        t.notification_agent = [t.notification_agent]

    return task.Task(
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

    source_ids = []
    if c.source_ids is not None and len(c.source_ids) > 0:
        source_ids = c.source_ids[0]

    notif_agent_ids = []
    if c.notif_agent_ids is not None and len(c.notif_agent_ids) > 0:
        notif_agent_ids = c.notif_agent_ids[0]

    m.name = c.name
    m.id = c.id
    m.frequency = c.frequency
    #m.frequency_unit = "minutes"
    m.source = source_ids
    m.notification_agent = notif_agent_ids
    m.must_contain = ",".join(c.include)
    m.exclude = ",".join(c.exclude)

def delete_task_model(core_task):
    task_model = session.query(models.Task).get(core_task.id)
    session.delete(task_model)

def to_core_sources(source_models):
    sources = {}

    for source_model in source_models:
        sources[source_model.id] = to_new_core_source(source_model)

    return sources

def to_new_core_source(source_model):
    s = source_model

    module = 0
    if s.module == 1:
        module = "kijiji"

    module_properties = {
        "url": s.website
    }

    return source.Source(
                id = s.id,
                name = s.name,
                module = module,
                module_properties = module_properties
            )

def to_new_source_model(core_source):
    c = core_source

    module = 0
    if c.module == "kijiji":
        module = 1

    m = models.Source()
    m.id = c.id
    m.name = c.name
    m.module = module
    m.website = c.module_properties["url"]
    return m

def to_existing_source_model(core_source, source_model):
    c = core_source
    m = source_model

    module = 0
    if c.module == "kijiji":
        module = 1

    m.id = c.id
    m.name = c.name
    m.module = module
    m.website = c.module_properties["url"]

def delete_source_model(core_source):
    source_model = session.query(models.Source).get(core_source.id)
    session.delete(source_model)

def to_core_notif_agents(notif_agent_models):
    notif_agents = {}

    for notif_agent_model in notif_agent_models:
        notif_agents[notif_agent_model.id] = to_new_core_notif_agent(notif_agent_model)

    return notif_agents

def to_new_core_notif_agent(notif_agent_model):
    import lib.core.notif_agent as notif_agent

    n = notif_agent_model

    module = 0
    if n.module == 1:
        module = "discord"

    module_properties = {
        "webhook": n.webhook_url,
        "botname": n.username
    }

    return notif_agent.NotifAgent(
                id = n.id,
                name = n.name,
                module = module,
                module_properties = module_properties,
            )

def to_new_notif_agent_model(core_notif_agent):
    c = core_notif_agent

    module = 0
    if c.module == "discord":
        module = 1

    m = models.NotificationAgent()
    m.id = c.id
    m.name = c.name
    m.module = module
    m.webhook_url = c.module_properties["webhook"]
    m.username = c.module_properties["botname"]
    m.icon = ""
    m.channel = ""

    return m

def to_existing_notif_agent_model(core_notif_agent, notif_agent_model):
    c = core_notif_agent

    module = 0
    if c.module == "discord":
        module = 1

    m = notif_agent_model
    m.id = c.id
    m.name = c.name
    m.module = module
    m.webhook_url = c.module_properties["webhook"]
    m.username = c.module_properties["botname"]

def delete_notif_agent_model(core_notif_agent):
    import lib.core.notif_agent as notif_agent

    notif_agent_model = session.query(models.NotificationAgent).get(core_notif_agent.id)
    session.delete(notif_agent_model)

def load_core_tasks():
    task_models = session.query(models.Task).all()
    return to_core_tasks(task_models)

def load_core_sources():
    source_models = session.query(models.Source).all()
    return to_core_sources(source_models)

def load_core_notif_agents():
    notif_agent_models = session.query(models.NotificationAgent).all()
    return to_core_notif_agents(notif_agent_models)

def save_to_db(tosave):
    to_model_type = {
        task.Task: models.Task,
        source.Source: models.Source,
        notif_agent.NotifAgent: models.NotificationAgent
    }

    to_new_model = {
        task.Task: to_new_task_model,
        source.Source: to_new_source_model,
        notif_agent.NotifAgent: to_new_notif_agent_model
    }

    to_existing_model = {
        task.Task: to_existing_task_model,
        source.Source: to_existing_source_model,
        notif_agent.NotifAgent: to_existing_notif_agent_model
    }

    for id in tosave:
        core_type = type(tosave[id])
        model = to_model_type[core_type]
        found = session.query(model).get(id)
        if found is not None:
            to_existing_model[core_type](tosave[id], found)

        else:
            task_model = to_new_model[core_type](tosave[id])
            session.add(task_model)

    session.commit()
