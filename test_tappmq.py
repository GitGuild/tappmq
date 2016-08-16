import unittest
import redis
import time

from tappmq.tappmq import MQHandlerBase, subscription_handler, publish

red = redis.StrictRedis()


def saver_retrieve(channel):
    return red.rpop('%s_saver' % channel)


class Helper(MQHandlerBase):
    NAME = 'Helper'

    def saver(self, message):
        red.lpush('%s_saver' % self.NAME.lower(), message)


class SingleTestCase(unittest.TestCase):
    def setUp(self):
        red.flushall()

    def tearDown(self):
        red.flushall()

    def test_pubsub_single_channel(self):
        helper = Helper()
        helper.setup_connections()
        now = {'message': str(time.time())}
        publish('helper', 'saver', now)
        subscription_handler('helper', helper, multi=False)
        message = saver_retrieve('helper')
        assert message == now['message']


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(SingleTestCase)


if __name__ == '__main__':
    unittest.main()
