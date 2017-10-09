#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
"""

import logging
import sys
from .spec import *


LOGGER = logging.getLogger(__name__)


CLIENT_PROPERTIES = {'product': 'CPOS FOUNDATION',
                     'platform': 'Python %s' % str(sys.version_info),
                     'capabilities': {'authentication_failure_close': True,
                                      'basic.nack': True,
                                      'connection.blocked': True,
                                      'consumer_cancel_notify': True,
                                      'publisher_confirms': True},
                     'information': 'See http://www.baidu.com',
                     'version': '0.1'}


class PlainCredentials(object):
    TYPE = 'PLAIN'

    def __init__(self, username, password, erase_on_connect=False):
        self.username = username
        self.password = password

    def response_for(self, start):
        if PlainCredentials.TYPE not in start.mechanisms.split():
            return None, None
        res = '\0%s\0%s' % (self.username, self.password)
        return (PlainCredentials.TYPE, res)


class Parameters(object):

    """Base connection parameters class definition

    Args:
        str DEFAULT_HOST: 'localhost'
        int DEFAULT_PORT: 5672
        str DEFAULT_VIRTUAL_HOST: '/'
        str DEFAULT_USERNAME: 'guest'
        str DEFAULT_PASSWORD: 'guest'
        int DEFAULT_HEARTBEAT_INTERVAL: 0
        int DEFAULT_CHANNEL_MAX: 0
        int DEFAULT_FRAME_MAX: pika.spec.FRAME_MAX_SIZE
        str DEFAULT_LOCALE: 'en_US'
        int DEFAULT_CONNECTION_ATTEMPTS: 1
        int|float DEFAULT_RETRY_DELAY: 2.0
        int|float DEFAULT_SOCKET_TIMEOUT: 0.25
        bool DEFAULT_SSL: False
        dict DEFAULT_SSL_OPTIONS: {}
        int DEFAULT_SSL_PORT: 5671
        bool DEFAULT_BACKPRESSURE_DETECTION: False

    """
    DEFAULT_BACKPRESSURE_DETECTION = False
    DEFAULT_CONNECTION_ATTEMPTS = 1
    DEFAULT_CHANNEL_MAX = 0
    DEFAULT_FRAME_MAX = FRAME_MAX_SIZE
    DEFAULT_HEARTBEAT_INTERVAL = 0
    DEFAULT_HOST = 'localhost'
    DEFAULT_LOCALE = 'en_US'
    DEFAULT_PORT = 5672
    DEFAULT_RETRY_DELAY = 2.0
    DEFAULT_SOCKET_TIMEOUT = 0.25
    DEFAULT_SSL = False
    DEFAULT_SSL_OPTIONS = {}
    DEFAULT_SSL_PORT = 5671
    DEFAULT_VIRTUAL_HOST = '/'

    def __init__(self):
        self.virtual_host = self.DEFAULT_VIRTUAL_HOST
        self.backpressure_detection = self.DEFAULT_BACKPRESSURE_DETECTION
        self.channel_max = self.DEFAULT_CHANNEL_MAX
        self.connection_attempts = self.DEFAULT_CONNECTION_ATTEMPTS
        self.credentials = self._credentials('guest', 'guest')
        self.frame_max = self.DEFAULT_FRAME_MAX
        self.heartbeat_interval = self.DEFAULT_HEARTBEAT_INTERVAL
        self.host = self.DEFAULT_HOST
        self.locale = self.DEFAULT_LOCALE
        self.port = self.DEFAULT_PORT
        self.retry_delay = self.DEFAULT_RETRY_DELAY
        self.ssl = self.DEFAULT_SSL
        self.ssl_options = self.DEFAULT_SSL_OPTIONS
        self.socket_timeout = self.DEFAULT_SOCKET_TIMEOUT

    def _credentials(self, username, password):
        """Return a plain credentials object for the specified username and
        password.

        Args:
            str username: The username to use
            str password: The password to use
        Returns:
            credentials.PlainCredentials

        """
        return PlainCredentials(username, password)


class ConnectionParameters(Parameters):

    """Connection parameters object that is passed into the connection adapter
    upon construction.

    """

    def __init__(self,
                 host=None,
                 port=None,
                 virtual_host=None,
                 credentials=None,
                 channel_max=None,
                 frame_max=None,
                 heartbeat_interval=None,
                 ssl=None,
                 ssl_options=None,
                 connection_attempts=None,
                 retry_delay=None,
                 socket_timeout=None,
                 locale=None,
                 backpressure_detection=None):
        """Create a new ConnectionParameters instance.

        Args:
             str host: Hostname or IP Address to connect to
             int port: TCP port to connect to
             str virtual_host: AMQP virtual host to use
             credentials.Credentials credentials: auth credentials
             int channel_max: Maximum number of channels to allow
             int frame_max: The maximum byte size for an AMQP frame
             int heartbeat_interval: How often to send heartbeats
             bool ssl: Enable SSL
             dict ssl_options: Arguments passed to ssl.wrap_socket as
             int connection_attempts: Maximum number of retry attempts
             int|float retry_delay: Time to wait in seconds, before the next
             int|float socket_timeout: Use for high latency networks
             str locale: Set the locale value
             bool backpressure_detection: Toggle backpressure detection

        """
        super(ConnectionParameters, self).__init__()

        # Assign the values
        if host is not None:
            self.host = host
        if port is not None:
            self.port = port
        if virtual_host is not None:
            self.virtual_host = virtual_host
        if credentials is not None:
            self.credentials = credentials
        if channel_max is not None:
            self.channel_max = channel_max
        if frame_max is not None:
            self.frame_max = frame_max
        if locale is not None:
            self.locale = locale
        if heartbeat_interval is not None:
            self.heartbeat_interval = heartbeat_interval
        if ssl is not None:
            self.ssl = ssl

        self.ssl_options = ssl_options or dict()

        if connection_attempts is not None:
            self.connection_attempts = connection_attempts
        if retry_delay is not None:
            self.retry_delay = retry_delay
        if socket_timeout is not None:
            self.socket_timeout = socket_timeout
        if backpressure_detection is not None:
            self.backpressure_detection = backpressure_detection


def build_connection_parameter(host, port, socket_timeout, connection_attempts, user_name=None, pass_word=None):
    '''To build up a parameter object for connecting to the AMQP server.


    Args:
        host - [str] The AMQP server host.
        port - [str] The AMQP server port.
        socket_timeout - [int , in seconds] The timeout period for connecting to AMQP server.
        connection_attempts - [int] Connection attempts.
        user_name - [str] Credential info(user) for AMQP.
        pass_word - [str] Credential info(pass word) for AMQP.
    Returns:
        A ConnectionParameters object that contains all the information to connecto to AMQP.
    '''
    if user_name is None or pass_word is None:
        user_name = 'guest'
        pass_word = 'guest'

    cd = PlainCredentials(user_name, pass_word)
    param = ConnectionParameters(heartbeat_interval=0,
                                 host=host, port=port, socket_timeout=socket_timeout, connection_attempts=connection_attempts,
                                 credentials=cd)
    return param


if __name__ == '__main__':
    cp = build_connection_parameter('localhost', 5672, 4, 1, 'sjdev', 'cpos')
