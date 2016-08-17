"""
A supervisord event listener based on the childutils example.

http://supervisord.org/events.html#example-event-listener-implementation
"""
from supervisor.childutils import EventListenerProtocol, get_headers
from tapp_config import setup_redis
from tappmq import set_status


class MQEventListener(EventListenerProtocol):
    def __init__(self):
        self.red = setup_redis()

    def update_state(self):
        headers, payload = self.wait()
        payload = get_headers(payload)  # also useful for getting the payload :)
        if "PROCESS_STATE_" in headers['eventname']:
            nam = payload['processname']
            state = headers['eventname'].replace("PROCESS_STATE_", "")
            if state == "STARTING":
                set_status(nam, 'loading', self.red)
            elif state == "RUNNING":
                set_status(nam, 'running', self.red)
            elif state == "STOPPING":
                set_status(nam, 'stopped', self.red)
            else:
                set_status(nam, 'stopped', self.red)
        self.ok()


def main():
    listener = MQEventListener()
    while 1:
        listener.update_state()

if __name__ == '__main__':
    main()
