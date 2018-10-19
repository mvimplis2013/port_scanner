import os
import uuid
from datetime import datetime

import bson
import flask_restful
from bson.json_util import dumps
from flask import Flask, send_from_directory, make_response, Response
from werkzeug.exceptions import NotFound

from cc.auth import init_jwt
from cc.database import mongo, database
from cc.environment.environment import env
from cc.resources.client_run import ClientRun


def init_app(mongo_url):
    app = Flask(__name__)