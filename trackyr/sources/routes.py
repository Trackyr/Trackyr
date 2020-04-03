from flask import (Blueprint, abort, flash, redirect, render_template, request, url_for)

from trackyr import db
from trackyr.models import Source
from trackyr.sources.forms import SourceForm

sources = Blueprint('sources', __name__)

@sources.route("/sources/create", methods=['GET', 'POST'])
def create_source():
    form = SourceForm()
    if form.validate_on_submit():
        source = Source(module=form.module.data,
                        name=form.name.data,
                        website=form.website.data,
                        location=form.location.data,
                        range=form.range.data,
                        # subreddit=form.subreddit.data
                        )
        db.session.add(source)
        db.session.commit()
        flash('Your source has been saved!', 'success')
        return redirect(url_for('main.sources'))
    return render_template('create-source.html', title='Create Source', 
                            form=form, legend='Create Source')

@sources.route("/sources/<int:source_id>/edit", methods=['GET', 'POST'])
def edit_source(source_id):
    source = Source.query.get_or_404(source_id)
    form = SourceForm()
    if form.validate_on_submit():
        source.module = form.module.data
        source.name = form.name.data
        source.website = form.website.data
        source.location = form.location.data
        source.range = form.range.data
        # source.subreddit = form.subreddit.data
        db.session.commit()
        flash('Your source has been updated!', 'success')
        return redirect(url_for('main.sources', source_id=source.id))
    elif request.method == 'GET':
        form.module.data = source.module
        form.name.data = source.name
        form.website.data = source.website
        form.location.data = source.location
        form.range.data = source.range
        # form.subreddit.data = source.subreddit
    return render_template('create-source.html', title='Update Source', 
                            form=form, legend='Update Source')

@sources.route("/sources/<int:source_id>/delete", methods=['GET', 'POST'])
def delete_source(source_id):
    source = Source.query.get_or_404(source_id)
    db.session.delete(source)
    db.session.commit()
    flash('Your source has been deleted.', 'success')
    return redirect(url_for('main.sources'))