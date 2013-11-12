import time
import threading
import irc.client
import logging

logger = logging.getLogger(__name__)


class MessageQueue(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)

        self.queue = []
        self.started = False
        self.should_stop = False

    def run(self):
        self.started = True
        while not self.should_stop:
            if len(self.queue) > 0:
                fn, args = self.queue.pop(0)
                fn(*args)
                time.sleep(0.7)
            time.sleep(0.1)

    def stop(self):
        self.should_stop = True

    def append(self, target, *args):
        self.queue.append([target, args])


class RateLimitedServerConnection(irc.client.ServerConnection):
    """This class functions exactly like a normal server class, but the
    output of the connection is rate limited.
    """
    def __init__(self, irclibobj):
        irc.client.ServerConnection.__init__(self, irclibobj)
        self.queue = MessageQueue()

    def connect(self, server, port, nickname, password=None, username=None,
            ircname=None, localaddress="", localport=0, ssl=False, ipv6=False):
        if not self.queue.started:
            self.queue.start()
        irc.client.ServerConnection.connect(
            self, server, port, nickname, password, username,
            ircname, #localaddress, localport, ssl, ipv6
        )
        self.buffer.errors = 'replace'

    def disconnect(self, message):
        irc.client.ServerConnection.disconnect(self, message)

    def privmsg(self, target, string):
        self.queue.append(self._privmsg, target, string)

    def _privmsg(self, target, string):
        return irc.client.ServerConnection.privmsg(self, target, string)

    def _handle_event(self, event):
        """[Internal]"""
        logger.debug('handle event: %s %s %s', event, event.type, event.arguments)
        super(RateLimitedServerConnection, self)._handle_event(event)


class RateLimitedIRC(irc.client.IRC):
    def server(self):
        """Creates a flood protected server connection. """

        c = RateLimitedServerConnection(self)
        self.connections.append(c)
        return c
