import re
import time
import irc.bot
import datetime
from irc.dict import IRCDict
from client import RateLimitedIRC
from event import Event
import logging
logger = logging.getLogger(__name__)

# \x03 is coloured text (\x033,4 for foreground, background)
# \x02 bold
# \x1F underline
# \x1D italic
# \x16 reverse colours

# Colors:
# 1 - Black
# 2 - Navy Blue
# 3 - Green
# 4 - Red
# 5 - Brown
# 6 - Purple
# 7 - Olive
# 8 - Yellow
# 9 - Lime Green
# 10 - Teal
# 11 - Aqua Light
# 12 - Royal Blue
# 13 - Hot Pink
# 14 - Dark Gray
# 15 - Light Gray
# 16 - White

def green(message):
    return u'\x0303{0}\x03'.format(message)


class Bot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667, username=None, password=None, **connect_params):
        # SimpleIRCClient init
        self.ircobj = RateLimitedIRC()
        self.connection = self.ircobj.server()
        self.dcc_connections = []
        self.ircobj.add_global_handler("all_events", self._dispatcher, -10)
        self.ircobj.add_global_handler("dcc_disconnect", self._dcc_disconnect, -10)

        #SingleServerIRCBot init
        self._SingleServerIRCBot__connect_params = connect_params
        self.channels = IRCDict()
        self.server_list = [irc.bot.ServerSpec(server, port)]
        self.reconnection_interval = 30
        self.pinged_at = datetime.datetime.utcnow()

        self._nickname = nickname
        self._realname = nickname
        for i in ["disconnect", "join", "kick", "mode",
                  "namreply", "nick", "part", "quit"]:
            self.connection.add_global_handler(
                i,
                getattr(self, "_on_" + i),
                -20
            )
        self.connection.add_global_handler("ping", self.pinged, -41)
        self.connection.add_global_handler("pong", self.pinged, -41)

        self.connection.add_global_handler('join', self.joined, -10)

        self.username = username
        self.password = password
        self.channel = channel
        self.actions = {}

        self.activity = Event()
        self.part = Event()
        self.death = Event()
        self.join = Event()

    def pinged(self, connection, event):
        self.pinged_at = datetime.datetime.utcnow()

    def joined(self, connection, event):
        self.join(connection, event)

    def ping_check(self):
        logger.info('Checking for recent pings: last ping was at %s', self.pinged_at)
        if self.connection.is_connected():
            self.connection.ping(self._nickname)
            if datetime.datetime.utcnow() - self.pinged_at > datetime.timedelta(seconds=120):
                self.disconnect()
        self.connection.execute_delayed(60, self.ping_check)

    def on_nicknameinuse(self, connection, event):
        logger.info('Nickname in use.')
        connection.nick(connection.get_nickname() + "_")

    def on_welcome(self, connection, event):
        logger.info('Received welcome.')
        if self.username and self.password:
            self.authenticate()
        connection.mode(connection.get_nickname(), '+x')
        time.sleep(5)
        logger.info('Joining channel.')
        connection.join(self.channel)

        self.ping_check()

    def on_privmsg(self, connection, event):
        logger.info('PRIVMSG {0}'.format(event.arguments[0]))
        self.process_command(event, event.source.nick)

    def on_pubmsg(self, connection, event):
        self.process_command(event, self.channel)
        self.activity(event.source.nick)

    def _on_part(self, connection, event):
        irc.bot.SingleServerIRCBot._on_part(self, connection, event)
        self.part(event.source.nick)

    def _on_quit(self, connection, event):
        irc.bot.SingleServerIRCBot._on_quit(self, connection, event)
        self.part(event.source.nick)

    def _on_disconnect(self, connection, event):
        logger.info('Disconnected from server - will try and reconnect in %s seconds', self.reconnection_interval)
        irc.bot.SingleServerIRCBot._on_disconnect(self, connection, event)

    def authenticate(self):
        logger.info('Authenticating with Q as {0}.'.format(self.username))
        self.connection.privmsg("Q@CServe.quakenet.org", "AUTH {0} {1}".format(self.username, self.password))

    def process_command(self, event, target):
        request = event.arguments[0].strip()

        for regex, fn in self.actions.values():
            match = re.match(regex, request)
            if match:
                try:
                    fn(self, event, *match.groups())
                except Exception, e:
                    logger.exception(e)
                    self.say('Something went wrong with that command.')
                break

    def serve_forever(self):
        logger.info('Starting to serve.')
        try:
            self.start()
        except Exception, e:
            logger.exception(e)
        finally:
            self.die('Stopped by exception.')
            try:
                self.connection.queue.stop()
            except:
                pass

    def die(self, msg="Bot terminated."):
        logger.info('Bot terminated: %s', msg)
        self.death()
        self.connection.disconnect(msg)

    def action(self, regex):
        def decorator(f):
            logger.info('Registering action {0}'.format(regex))
            if regex in self.actions:
                logger.info('Overwriting regex {0}'.format(regex))
            self.actions[regex] = (re.compile(regex, re.IGNORECASE), f)
            return f
        return decorator

    def topic(self, message):
        self.connection.topic(self.channel, message)

    def say(self, message):
        self.connection.privmsg(
            self.channel,
            green(message)
        )

    def whisper(self, nick, message):
        logger.info('whisper to {0}: {1}'.format(nick, message))
        self.connection.privmsg(
            nick,
            green(message)
        )
