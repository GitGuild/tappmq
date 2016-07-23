import unittest
import json
import redis
import time

from tappmq import subscription_handler, publish

red = redis.StrictRedis()


def command_saver(channel, message):
    red.lpush('%s_saver' % channel, message)


def saver_retrieve(channel):
    return red.rpop('%s_saver' % channel)


class SingleTestCase(unittest.TestCase):
    def setUp(self):
        red.flushall()

    def tearDown(self):
        red.flushall()

    def test_pubsub_single_channel(self):
        cmdmap = {'saver': command_saver}
        now = str(time.time())
        publish('test', 'saver', now)
        subscription_handler('test', cmdmap, multi=False)
        message = saver_retrieve('test')
        assert json.loads(message)['data'] == now


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(SingleTestCase)


if __name__ == '__main__':
    unittest.main()
