from flask import (Blueprint, abort, flash, redirect, render_template, request, url_for)

import json
import os

from trackyr import db
from trackyr.models import Source, Task, Modules
from trackyr.sources.forms import SourceForm

import lib.core.source as prime
from lib.core.state import State

import lib.core.modules as mod

sources = Blueprint('sources', __name__)

@sources.route("/sources/create/<int:module_id>", methods=['GET', 'POST'])
def create_source(module_id):
    State.load()

    for m in mod.get_sources_list():
        if m[0] == module_id:
            module_name = m[1]

    form = SourceForm()
    module_form = mod.generate_form(module_id)

    if form.test.data:
        website = request.form.get('Website')

        prime_source = prime.Source(module=module_name.lower(), module_properties={'url':website,'botname':"prime"})

        try:
            total_ads = prime.test_webui_source(prime_source).total_new_ads
        except:
            message = "Not a valid source"
        else:
            message = f"Found {total_ads} new ads" \
                if total_ads != 1 else "Found 1 new ad"
        finally:
            if website == "":
                message = "Not a valid source"
            flash(message, "notification")

    elif form.submit.data:
        name = request.form.get('Name')
        website = request.form.get('Website')
        
        source = Source(module=module_id,
                        name=name,
                        website=website)

        db.session.add(source)
        db.session.commit()

        State.refresh_sources()

        flash('Your source has been saved!', 'top_flash_success')
        return redirect(url_for('main.sources'))

    return render_template('create-source.html', title='Create Source',
                            legend=f'Create Source - {module_name}', form=form, module_form=module_form)

@sources.route("/sources/<int:source_id>/edit", methods=['GET', 'POST'])
def edit_source(source_id):
    State.load()
    source = Source.query.get_or_404(source_id)

    for m in mod.get_sources_list():
        if m[0] == source.module:
            module_name = m[1]

    form = SourceForm()
    module_form = mod.generate_form(source.module)

    if form.test.data:
        website = request.form.get('Website')

        prime_source = prime.Source(module=module_name.lower(), module_properties={'url':website,'botname':"prime"})

        try:
            total_ads = prime.test_webui_source(prime_source).total_new_ads
        except:
            message = "Not a valid source"
        else:
            message = f"Found {total_ads} new ads" \
                if total_ads != 1 else "Found 1 new ad"
        finally:
            if web_url == "":
                message = "Not a valid source"
            flash(message, "notification")

    elif form.submit.data:
        name = request.form.get('Name')
        website = request.form.get('Website')

        db.session.commit()

        State.refresh_sources()

        flash('Your source has been updated!', 'top_flash_success')
        return redirect(url_for('main.sources', source_id=source.id))
    
    if request.method == 'GET':
        pass
    
    return render_template('create-source.html', title='Update Source',
                            legend='Update Source', form=form, module_form=module_form)

@sources.route("/sources/<int:source_id>/delete", methods=['GET', 'POST'])
def delete_source(source_id):
    State.load()

    source = Source.query.get_or_404(source_id)
    tasks = Task.query.all()

    for task in tasks:
        task.source = [s for s in task.source if s != source_id]

        # if this causes a task to  go down to 0 sources, then it should be deleted.
        if len(task.source) == 0:
            db.session.delete(task)
            
    db.session.delete(source)
    db.session.commit()

    flash('Your source has been deleted.', 'top_flash_success')
    return redirect(url_for('main.sources'))
    
@sources.route("/sources/generate_form/<int:module_id>", methods=['GET', 'POST'])
def generate_form(module_id):
    mod.generate_form(module_id)
    
    form = SourceForm()
    
    return render_template('create-source.html', title='Create Source',
                            form=form, legend='Create Source')