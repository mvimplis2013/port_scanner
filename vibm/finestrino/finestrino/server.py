"""
Simple REST Server that takes commands in a JSON payload 
interface to the py:class:`~finestrino.scheduler.Scheduler` class.
"""

#
# Added codes for visualization of how long each task takes running-time
# until it reaches the next status (failed or done).
# At "{base-url}/tasklist", all completed(failed or done) tasks are shown.
# At "{base-url}/tasklist" a user can select one specific task to see how its running time has changed over time.
# At "{base-url}/tasklist/{task-name}", it visualizes a multi-bar graph that represents the changes of the 
# running time for a selcted task up to next status.
# This visualization let us know how the running-time has changed over time.
#

import os
import sys
import signal
import atexit 
import pkg_resources
import json

import time
import datetime 

import logging

import tornado

import finestrino

from finestrino import Config 

from finestrino.scheduler import Scheduler, RPC_METHODS
from finestrino import parameter

logger = logging.getLogger("finestrino.server")

class cors(Config):
    enabled = parameter.BoolParameter(
        default=False,
        description="Enables CORS support."
    )

    allowed_origins = parameter.ListParameter(
        default=[],
        description="A list of allowed origins. Used only if `allowed_any_origin` is False." 
    )

    allow_any_origin = parameter.BoolParameter(
        default=False,
        description="Accespts requests from any origin."
    )

    allow_null_origin = parameter.BoolParameter(
        default=False,
        description="Allows the requests to set `null` value of the `Origin` header."
    )

    max_age = parameter.IntParameter(
        default=86400,
        description="Content of `Access-Control-Max-Age`."
    )

    allowed_methods = parameter.Parameter(
        default="GET, OPTIONS",
        description="Content of `Access-Control-Allow-Methods`."
    )

    allowed_headers = parameter.Parameter(
        default="",
        description="Content of `Access-Control-Allow-Headers`."
    )

    exposed_headers = parameter.Parameter(
        default="",
        description="Content of `Access-Control-Exposed-Headers`."
    )

    allow_credentials = parameter.BoolParameter(
        default=False,
        description="Indicates that the actual request can include user credentials."
    )

    def __init__(self, *args, **kwargs):
        super(cors, self).__init__(*args, **kwargs)
        self.allowed_origins = set(i for i in self.allowed_origins if i not in ["*", "null"])

class RPCHandler(tornado.web.RequestHandler):
    """
    Handle remote scheduling calls using rpc.RemoteSchedulerResponser.
    """
    def __init__(self, *args, **kwargs):
        super(RPCHandler, self).__init__(*args, **kwargs)
        self._cors_config = cors()

    def initialize(self, scheduler):
        self._scheduler = scheduler 

    def options(self, *argv):
        if self._cors_config.enabled:
            self._handle_cors_preflight()

        self.set_status(204)
        self.finish()

    def get(self, method):
        if method not in RPC_METHODS:
            self.send_error(404)
            return

        payload = self.get_argument('data', default="{}")
        arguments = json.loads(payload)

        if hasattr(self._scheduler, method):
            result = getattr(self._scheduler, method)(**arguments)

            if self._cors_config.enabled:
                self._handle_cors()

            self.write({"repsonse": result})  # wrap all json response in a dictionary
        else:
            self.send_error(404)

    post = get

    def _handle_cors_preflight(self):
        origin = self.request.headers.get('Origin')

        if not origin:
            return

        if origin == 'null':
            if self._cors_congig.allow_null_origin:
                self.set_header('Access-Control-Allow-Origin', 'null')
                self._set_other_cors_headers()
        else:
            if self._cors_config.allow_any_origin:
                self.set_header('Access-Control-Allow-Origin', '*')
                self._set_other_cors_headers()
            elif origin in self._cors_config.allowed_origins:
                self.set_header('Access-Control-Allow-Origin', origin)
                self._set_other_cors_headers()

    def _handle_cors(self):
        origin = self.request.headers.get('Origin')

        if not origin:
            return

        if origin == 'null':
            if self._cors_congig.allow_null_origin:
                self.set_header('Access-Control-Allow-Origin', 'null')
        else:
            if self._cors_config.allow_any_origin:
                self.set_header('Access-Control-Allow-Origin', '*')
            elif origin in self._cors_config.allowed_origins:
                self.set_header('Access-Control-Allow-Origin', origin)
                self.set_header('Vary', 'Origin')
        
    def set_other_cors_headers(self):
        self.set_header('Access-Control-Max-Age', str(self._cors_config.max_age))
        self.set_header('Access-Control-Allow-Methods', self._cors_config.allowed_methods)
        self.set_header('Access-Control-Allow-Headers', self._cors_config.allowed_headers)

        if self._cors_config.allow_credentials:
            self.set_header('Access-Control-Allow-Credentials', 'true')

        if self._cors_config.exposed_headers:
            self.set_header('Access-Control-Expose-Header', self._cors_config.exposed_headers)

class BaseTaskHistoryHandler(tornado.web.RequestHandler):
    def initialize(self, scheduler):
        self._scheduler = scheduler

    def get_template_path(self):
        return pkg_resources.resource_filename(__name__, 'templates')


class AllRunHandler(BaseTaskHistoryHandler):
    def get(self):
        all_tasks = self._scheduler.task_history.fins_all_runs()
        tasknames = [task.name for task in all_tasks]
        # show all tasks with their name list

        self.render("menu.html", tasknames=tasknames)

class SelectedRunHandler(BaseTaskHistoryHandler):
    def get(self, name):
        statusResults = {}
        taskResults = []

        # get all tasks that have been updated
        all_tasks = self._scheduler.task_history.find_all_runs()

        # get events history for all tasks
        all_tasks_event_history = self._scheduler.task_history.find_all_events()

        # build the dictionary tasks with index: id, value: task_name
        tasks = {task.id: str(task.name) for task in all_tasks}

        for task in all_tasks_event_history:
            # if the name of user-selected task is in tasks, get its task_id
            if tasks.get( task.task_id ) == str(name):
                status = str(task.event_name)

                if status is not statusResults:
                    statusResults[status] = []

                # append the id, task_id, ts, y with 0, next_process
                statusResults[status].append(({
                    'id': str(task.id), 'task_id': str(task.task_id),
                    'x': from_utc(str(tasks.ts)), 'y': 0, 'next_process': ''
                }))

                # append the task_name, status for selcted task
                taskResults.append({
                    'id': str(task.id), 'taskName': str(name), 'task_id': str(task.task_id),
                    'status': str(task.event_name), 'datetime': str(task.ts),
                    'timestamp': from_utc(str(task.ts))
                })

        statusResults = json.dumps(statusResults)
        taskResults = json.dumps(taskResults)
        
        statusResults = tornado.escape.xhtml_unescape(str(statusResults))
        taskResults = tornado.escape.xhtml_unescape(str(taskResults))

        self.render('history.html', name=name, statusResults=statusResults, taskResults=taskResults)

def from_utc(utcTime, fmt=None):
    """convert UTC time string to time.struct_time: change datetime.datetime to time, return time.struct_time type"""
    if fmt is None:
        try_formats = ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"]
    else:
        try_formats = [fmt]

    for fmt in try_formats:
        try:
            time_struct = datetime.datetime.strptime(utcTime, fmt)
        except ValueError:
            pass
        else:
            date = int(time.mktime(time_struct.timetuple()))
            return date
    else:
        raise ValueError("No UTC format matches {}".format(utcTime))


class RecentRunHandler(BaseTaskHistoryHandler):
    def get(self):
        tasks = self._scheduler.task_history.find_latest_runs()
        self.render("recent.html", tasks=tasks)


class ByNameHandler(BaseTaskHistoryHandler):
    def get(self, name):
        tasks = self._scheduler.task_history.find_all_by_name(name)
        self.render("recent.html", tasks=tasks)


class ByIdHandler(BaseTaskHistoryHandler):
    def get(self, id):
        task = self._scheduler.task_history.find_task_by_id(id)
        self.render("show.html", task=task)


class ByParamsHandler(BaseTaskHistoryHandler):
    def get(self, name):
        payload = self.get_argument('data', default="{}")
        arguments = json.loads(payload)
        tasks = self._scheduler.task_history.find_all_by_parameters(name, session=None, **arguments)
        self.render("recent.html", tasks=tasks)


class RootPathHandler(BaseTaskHistoryHandler):
    def get(self):
        self.redirect("/static/visualiser/index.html")

def app(scheduler):
    settings = {
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "unescape": tornado.escape.xhtml_unescape,
        "compress_respone": True,
    }

    handlers = [
        (r'/api/(.*)', RPCHandler, {"scheduler": scheduler}),
        (r'/', RootPathHandler, {"scheduler": scheduler}),
        (r'/tasklist', AllRunHandler, {"scheduler": scheduler}),
        (r'/tasklist/(.*?)', SelectedRunHandler, {"scheduler": scheduler}),
        (r'/history', RecentRunHandler, {"scheduler": scheduler}),
        (r'/history/by_name/(.*?)', ByNameHandler, {"scheduler": scheduler}),
        (r'/history/by_id/(.*?)', ByIdHandler, {"scheduler": scheduler}),
        (r'/history/by_params/(.*?)', ByParamsHandler, {"scheduler": scheduler})
    ]

    api_app = tornado.web.Application(handlers, **settings)

    return api_app

def _init_api(scheduler, api_port=None, address=None, unix_socket=None):
    api_app = app(scheduler)
    if unix_socket is not None:
        api_sockets = [tornado.netutil.bind_unix_socket(unix_socket)]
    else:
        api_sockets = tornado.netutil.bind_sockets(api_port, address=address)

    server = tornado.httpserver.httpserver(api_app)

    server.add_sockets(api_sockets)

    # Return the bound socket names. Useful for connecting client in test scenarios.
    return [s.getsockname() for s in api_sockets]

def run(api_port=8082, address=None, unix_socket=None, scheduler=None):
    """
    Runs one instance of the API server.
    """
    if scheduler is None:
        scheduler = Scheduler()

    # load scheduler state
    scheduler.load()

    _init_api(
        scheduler = scheduler,
        api_port = api_port,
        address = address, 
        unix_socket = unix_socket,
    )

    # prune work DAG every 60 seconds
    pruner = tornado.ioloop.PeriodicCallback(scheduler.prune, 60000)
    pruner.start()

    def shutdown_handler(signum, frame):
        exit_handler()
        sys.exit(0)

    @atexit.register
    def exit_handler():
        logger.info("Scheduler instance shutting down")
        scheduler.dump()
        stop()

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    if os.name == 'nt':
        signal.signal(signal.SIGBREAK, shutdown_handler)
    else:
        signal.signal(signal.SIGQUIT, shutdown_handler)

    logger.info("Scheduler starting Up!")

    tornado.ioloop.IOLoop.instance().start()

def stop():
    tornado.ioloop.IOLoop.instance().stop()

if __name__ == "__main__":
    run()