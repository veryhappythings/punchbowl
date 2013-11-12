import logging
from punchbowl import Bot

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s,%(msecs)03d %(levelname)-5.5s [%(name)s] %(message)s")

bot = Bot(
    channel='#punchbowltest',
    nickname='punchbowl',
    server='se.quakenet.org'
)

@bot.action('^hello$')
def hello(bot, event):
    bot.say('Hi there, {0}!'.format(event.source.nick))

bot.serve_forever()
