"""
Dinh nghia single page pplication
"""

from . import app
from . import app_config
from flask import render_template
from flask import send_from_directory

@app.route(app_config.get_route_path('/<path:path>'))
def single_page_app(path):

    return render_template('index.html',app=app_config)

@app.route(app_config.get_route_path('/'))
@app.route('/index')
def index():
    name = 'Rosalia'
    return render_template('index.html',app=app_config)

