"""
A simple message queue for TAPPs using Redis.
"""
import json
import time
from sqlalchemy_models import create_session_engine, setup_database, util
from tapp_config import setup_redis, get_config, setup_logging
from trade_manager import em, um, wm


def subscription_handler(channel, client, mykey=None, auth=False, multi=True):
    """
    :param str channel: The channel to subscribe to.
    :param client: A plugin manager client.
    :param mykey: A bitjws public key to use in authenticating requests (unused)
    :param bool auth: If true, authenticate all requests, otherwise assume plain json encoding.
    :param multi: Process multiple results if True, otherwise return after 1
    """
    while True:
        message = client.red.rpop(channel)
        if message is not None:
            toprint = message if len(message) < 60 else message[:59]
            client.logger.info("handling message %s..." % toprint)
            if not auth:
                # assume json encoding
                mess = json.loads(message)
                client.logger.debug("handling message:\n%s" % json.dumps(mess, indent=2))
                if 'command' not in mess or not hasattr(client, mess['command']):
                    # nothing to do
                    pass
                else:
                    try:
                        getattr(client, mess['command'])(**mess['data'])
                    except Exception as e:
                        client.logger.exception(e)
                        client.session.rollback()
                        client.session.flush()
            else:
                # TODO implement auth options
                raise NotImplementedError("auth not supported yet.")
            if not multi:
                return
        else:
            time.sleep(0.01)


def publish(channel, command, data, key=None, auth=False, red=None):
    """
    Publish a command to a redis channel.

    :param channel: The channel to send the command to
    :param command: The command name
    :param data: The data to send (parameters)
    :param key: The key to sign with (unused)
    :param auth: If true, authenticate the message before sending (unused)
    :param red: The StrictRedis client to use for redis communication
    """
    if red is None:
        red = setup_redis()
    if not auth:
        red.lpush(channel, json.dumps({'command': command, 'data': data}))
    else:
        # TODO implement auth options
        raise NotImplementedError("auth not supported yet.")


def set_status(nam, status='loading', red=None):
    if red is None:
        red = setup_redis()
    if status in ['loading', 'running', 'stopped']:
        red.set("%s_status" % nam.lower(), status)


def get_status(nam, red=None):
    if red is None:
        red = setup_redis()
    status = red.get("%s_status" % nam.lower())
    return status if status is not None else 'stopped'


def get_running_workers(wlist, red=None):
    """
    Search list for only the workers which return status 'running'.

    :param wlist: The list of workers to search through.
    :param red: The redis connection.
    :return: The worker list filtered for status 'running'.
    """
    if red is None:
        red = setup_redis()
    workers = []
    for work in wlist:
        if get_status(work, red=red) == 'running':
            workers.append(work)
    return workers


class MQHandlerBase(object):
    """
    A parent class for Message Queue Handlers.
    Plugins should inherit from this class, and overwrite all of the methods
    that raise a NotImplementedError.
    """
    NAME = 'Base'
    KEY = 'PubKey'
    _user = None
    session = None

    def __init__(self, key=None, secret=None, session=None, engine=None, red=None, cfg=None):
        self.cfg = get_config(self.NAME.lower()) if cfg is None else cfg
        self.key = key if key is not None else self.cfg.get(self.NAME.lower(), 'key')
        self.secret = secret if secret is not None else self.cfg.get(self.NAME.lower(), 'secret')
        self.session = session
        self.engine = engine
        self.red = red
        self.logger = None

    """
    Daemonization and process management section. Do not override.
    """

    def setup_connections(self):
        if self.session is None or self.engine is None:
            self.session, self.engine = create_session_engine(cfg=self.cfg)
            setup_database(self.engine, modules=[wm, em, um])
        self.red = setup_redis() if self.red is None else self.red

    def setup_logger(self):
        self.logger = setup_logging(self.NAME.lower(), cfg=self.cfg)

    def cleanup(self):
        if self.session is not None:
            self.session.close()

    @property
    def manager_user(self):
        """
        Get the User associated with this plugin Manager.
        This User is the owner of records for the plugin.

        :rtype: User
        :return: The Manager User
        """
        if not self._user:
            # try to get existing user
            self._user = self.session.query(um.User).filter(um.User.username == '%sManager' % self.NAME) \
                .first()
        if not self._user:
            # create a new user
            userpubkey = self.cfg.get(self.NAME.lower(), 'userpubkey')
            self._user = util.create_user('%sManager' % self.NAME, userpubkey, self.session)
        return self._user

    def run(self):
        """
        Run this manager as a daemon. Subscribes to a redis channel matching self.NAME
        and processes messages received there.
        """
        set_status(self.NAME.lower(), 'loading', self.red)
        self.setup_connections()
        self.setup_logger()
        self.logger.info("%s loading" % self.NAME)
        set_status(self.NAME.lower(), 'running', self.red)
        self.logger.info("%s running" % self.NAME)
        subscription_handler(self.NAME.lower(), client=self)
