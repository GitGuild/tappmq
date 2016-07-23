#import bitjws
import json
import redis
import time

red = redis.StrictRedis()


def subscription_handler(channel, cmdmap, mykey=None, auth=False, multi=True):
    """

    :param str channel: The channel to subscribe to.
    :param dict cmdmap: A map of commands and function handlers.
    :param mykey: A bitjws public key to use in authenticating requests
    :param bool auth: If true, authenticate all requests, otherwise assume plain json encoding.
    """
    while True:
        message = red.rpop(channel)
        if message is not None:
            if not auth:
                # assume json encoding
                mess = json.loads(message)
                if 'command' not in mess or mess['command'] not in cmdmap:
                    # nothing to do
                    pass
                else:
                    cmdmap[mess['command']](channel, message)
            else:
                # TODO implement auth options
                raise NotImplementedError("auth not supported yet.")
            if not multi:
                return
        else:
            time.sleep(0.1)


def publish(channel, command, data, key=None, auth=False):
    if not auth:
        red.lpush(channel, json.dumps({'command': command, 'data': data}))
    else:
        # TODO implement auth options
        raise NotImplementedError("auth not supported yet.")
