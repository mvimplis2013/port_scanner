import logging

from flask import request, jsonify

import flask_restful

from cc.services.node import NodeService

__author__ = 'Mickey.Mouse'

logger = logging.getLogger(__name__)