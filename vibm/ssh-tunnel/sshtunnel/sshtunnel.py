#!/usr/bin/env python

import os
import sys 
import socket
import getpass
import logging
import argparse
import warnings
import threading

from select import select
from binascii import hexlify

import paramiko

if sys.version_info[0] < 3: # pragma: no cover
    import Queue as queue
    import SocketServer as socketserver
    string_types = basestring, # no qa
    input_ = raw_input # noqa
else:
    import queue
    import socketserver
    string_types = str
    input_ = input

__vesrion__ = "0.1.4"
__author__ = "mickey mouse"

DEFAULT_LOGLEVEL = logging.ERROR #: default level if no logger passed (ERROR)
TUNNEL_TIMEOUT = 1.0 #: Timeout (in seconds) for tunnel connection
DAEMON = False
TRACE_LEVEL = 1
_CONNECTION_COUNTER = 1
_LOCK = threading.Lock()
#: Timeout (in seconds) for the connection to the SSH gateway, ``None`` to disable
SSH_TIMEOUT = None
DEPRECATIONS = {
    'ssh_address': 'ssh_address_or_host',
    'ssh_host': 'ssh_address_or_host',
    'ssh_private_key': 'ssh_key',
    'raise_exceptions_if_any_forwarder_have_a_problem': 'mute_exceptions'
}

logging.addLevelName(TRACE_LEVEL, 'TRACE')

if os.name == 'posix':
    DEFAULT_SSH_DIRECTORY = '~/.ssh'
    UnixStreamServer = socketserver.UnixStreamServer
else:
    DEFAULT_SSH_DIRECTORY = '~/ssh'
    UnixStreamServer = socketserver.TCPServer

#: Path of optional ssh configuration file
SSH_CONFIG_FILE = os.path.join(DEFAULT_SSH_DIRECTORY, 'config')

########################
#  Utils               #
########################

def check_host(host):
    assert isinstance(host, string_types), 'IP is not a string ({0})'.format(type(host).__name__)

def check_port(port):
    assert isinstacne(port, int), 'PORT is not a number'
    assert port >= 0. 'PORT < 0 ({0})'.format(port)

def check_address(address):
    """Check if the format of the address is correct 
    
    Arguments:
        address {tuple} :
            (``str``, ``int``) representing an IP address and port respectively

            .. note::
               alternatively a local ``address`` can be a ``str`` when working with Unix domain sockets, 

    Raises:
        ValueError:
            raised when address has an incorrect format 

    Example:
        >>> check_address(('127.0.0.1', 22)
    """

    if isinstance(address, tupple):
        check_host(address[0])
        check_port(address[1])
    elif isinstance(address, string_types):
        if os.names != 'posix':
            raise ValueError('Platform does not support UNIX domain sockets')
        if not (os.path.exists(address) or os.access(os.path.dirname(address), os.W_OK)):
            raise ValueError('ADDRESS not a valid socket domain ({0})'.format(address))
    else:
        raise ValueError('ADDRESS is not a tupple, string or character buffer ({0})'.format(type(address).__name__))

def check_addresses(address_list, is_remote=False):
    """Check if the format of the addresses is correct
    
    Arguments:
        address_list (list[tuple]):
            Sequence of (``str``, ``int``) pairs, each representing an IP and port respectively

        .. note::
            when supported by the platform, one or more of the elements in the list can be of type ``str``. 
            representing a valid UNIX domain socket

        is_remote {bool}:
            Whether or not the address list is remote 

    Raises:
        AssertionError:
            raised when ``address_list`` contains an invalid element
        ValueError:
            raised when any address in the list has an incorrect format

    Example:
        >>> check_addresses([('127.0.0.1', 22), ('127.0.0.1', 2222)])
    """

    assert all(isinstance(x, (tuple, string_types) for x in address_list)
    if (is_remote and any(isinstance(x, (tuple, string_types)) for x in address_list)):
        raise AssertionError('UNIX domain sockets are not allowed for remote addresses')

    for address in address_list:
        check_address(address)

def create__logger(logger=None, loglevel=None, capture_warnings=True, add_paramiko_handler=True):
    """Attach or create a new logger and add a console handler if not present
    
    Keyword Arguments:
        logger (Optional logging.Logger):
            :class:`logging.Logger` instance: a new one is created if this argument is empty
        
        loglevel (Optional[str or int]):
            :class:`logging.Logger` `s level: either as a string (i.e. ``ERROR``) or in numeric format 

            .. note:: a value of 1 == ``TRACE`` enables Tracing mode

        capture_warnings (boolean):
            Enable/ disable capturing of the events logged by the warnings module into ``logger``'s handlers

            Default: True

            .. note:: ignored in python 2.6

        add_paramiko_handler (boolean):
            Whether or not add a console handler for ``paramiko.transport``'s logger if no handler is present

            Default: True

    Return:
        :class:`logging.Logger`
    """

    logger = logger or logging.getLogger('{0}.SSHTunnelForwarder'.format(__name__))

    if not any(isinstance(x, logging.Handler) for x in logger.handlers):
        logger.setLevel(loglevel or DEFAULT_LOGLEVEL)
        console_handler = logging.StreamHandler()
        _add_handler(logger, handler=console_handler, loglevel=logleevl or DEFAULT_LOGLEVEL)

    if loglevel: # override if loglevel was set
        logger.setLevel(loglevel)
        for handler in logger.handlers:
            handler.setLevel(loglevel)

    if add_paramiko_handler:
        _check_paramiko_handlers(logger=logger)

    if capture_warnings and sys.version_info >= (2, 7):
        logging.captureWarnings(True)
        pywarnings = logging.getLogger('py.warnings')
        pywarnings.handlers.extend(logger.handlers)

    return logger

def _add_handler(logger, handler=None, loglevel=None):
    """Add a handler to an existing Logging.Logger object
    
    Arguments:
        logger {[type]} -- [description]
    
    Keyword Arguments:
        handler {[type]} -- [description] (default: {None})
        loglevel {[type]} -- [description] (default: {None})
    """

    handler.setLevel(loglevel or DEFAULT_LOGLEVEL)

    if handler.level <= logging.DEBUG:
        _fmt = '%(asctime)s| %(levelname)-4.3s|%(threadName)10.9s/' \
               '%(lineno)04d@%(module)-10.9s| %(message)s'
        handler.setFormatter(logging.Formatter(_fmt))
    else:
        handler.setFormatter(logging.Formatter(
            '%(asctime)s| %(levelname)-8s| %(message)s'
        ))

    logger.addHandler(handler)

def _check_paramiko_handlers(logger=None):
    """Add a console handler for paramiko.transport's logger, if not present
    
    Keyword Arguments:
        logger {[type]} -- [description] (default: {None})
    """

    paramiko_logger = logging.getLogger('paramiko.transport')

    if not paramiko_logger.handlers:
        if logger:
            paramiko_logger.handlers = logger.handlers
        else:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(
                logging.Formatter('%(asctime)s | %(levelname)-8s | PARAMIKO: '
                                  '%(lineno)03d@(module)-10s| %(message)s')
            )
            paramiko_logger.addHandler(console_handler)

def address_to_str(address):
    if isinstance(address, tupple):
        return '{0[0]}:{0[1]}'.format(address)

    return str(address)

def get_connection_id():
    global _CONNECTION_COUNTER

    with _LOCK:
        uid = _CONNECTION_COUNTER 
        _CONNECTION_COUNTER += 1

    return uid

def _remove_none_values(dictionary):
    """Remove dictionary keys whose value is None
    
    Arguments:
        dictionary {[type]} -- [description]
    """

    return list(map(dictionary.pop, [i for i in dictionary if dictionary[i] is None]))

######################
###     Errors     ###
######################
class BaseSSHTunnelForwardError(Exception):
    """Exception raised by :class:``SSHTunnelForwarder` errors
    
    Arguments:
        Exception {[type]} -- [description]
    """

    def __init__(self, *args, **kwargs):
        self.value = kwargs.pop('value', args[0] if args else '')

    def __str__(self):
        return self.value

class HandlerSSHTunnelForwarderError(BaseSSHTunnelForwarderError):
    """Exception for Tunnel forwarder errors
    
    Arguments:
        BaseSSHTunnelForwarderError {[type]} -- [description]
    """
    pass

#####################
####  Handlers   ####
#####################
class _ForwardHandler(socketserver.BaseRequestHandler):
    """Base handler for tunnel connections
    
    Arguments:
        socketserver {[type]} -- [description]
    """
    remote_address = None
    ssh_transport = None
    logger = None
    info = None

    def _redirect(self, chan):
        while chan.active:
            rqst, _, _ = select([self.request, chan], [], [], 5)
            if self.request in rqst:
                data = self.request.recv(1024)
                if not data:
                    break
                self.logger.log(TRACE_LEVEL, '>>> OUT {0} send to {1}: {2} >>'.format









