import inspect
import os

import jinja2
from flask import session, redirect, url_for, render_template, request
from flask import Blueprint
from flask import Markup

from ..plugin_parser.prepared import prepare_plugins

jana_blueprint = Blueprint('main', __name__)


@jana_blueprint.route('/', methods=['GET', 'POST'])
def index():
    """Login form to enter a room."""

    return render_template('plugins.html', layout="short", plugins=prepare_plugins())


def render_jinja_html(template_loc, file_name, **context):
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_loc + '/')
    ).get_template(file_name).render(context)


def offline_render():
    templates_dir = os.path.join(os.path.dirname(inspect.stack()[0][1]), 'templates')
    return render_jinja_html(templates_dir, 'plugins.html', plugins=prepare_plugins())



#
#
@jana_blueprint.route('/full', methods=['GET', 'POST'])
def full():
    """Login form to enter a room."""

    return render_template('plugins.html', layout="full", plugins=prepare_plugins(), plugin_data="""
    {'params': {'nevents': 10000, 'nthreads': 1},
     'plugins': {'beagle_reader': {}, 'event_writer': {}},
     'flags': [],
     'input_files': []}""")


@jana_blueprint.route('/start', methods=['GET', 'POST'])
def start_gui():
    """Login form to enter a room."""

    return render_template('start.html', layout="full", plugins=prepare_plugins(), plugin_data="")


@jana_blueprint.route('/chat')
def chat():
    """Chat room. The user's name and room must be stored in
    the session."""
    name = session.get('name', '')
    room = session.get('room', '')
    if name == '' or room == '':
        return redirect(url_for('.index'))
    return render_template('chat.html', name=name, room=room)


if __name__ == "__main__":
    print(offline_render())