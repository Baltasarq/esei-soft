
import os
import jinja2

from flask import Flask, request
from flask_babel import Babel

# Definicion del Enviroment
JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)+"/templates"),
                                       extensions=["jinja2.ext.autoescape"],
                                       autoescape=True)

app = Flask(__name__)
babel = Babel(app)

app.secret_key = 'some secret key'

class Config(object):
    LANGUAGES = ['gl', 'en', 'es']


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(Config.LANGUAGES)


import handlers.handlers

