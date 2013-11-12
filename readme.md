# Punchbowl

An IRC bot framework built in the style of [Flask](http://flask.pocoo.org).

## About

About a year ago, the guys at [UKDota.net](http://www.ukdota.net) asked [Simon Engledew](https://github.com/simon-engledew) and I to build an IRC bot for their new inhouse league. The bot required a pretty large set of commands, so we built a framework to manage it. This is that framework, slightly adapted for general use.

Flask is really cool, and the paths of a web framework aren't all that different to the commands given to an IRC bot, so Flask became a model for everything I've put into this. I've used this framework to build a bot with over 30 commands across 3 states and 3 different kinds of user, so I'm pretty confident that it scales well, but it doesn't do a lot for you at that point and you may find that you want to get your hands dirty with the inner workings of it.

I have only written for Quakenet, so I can't really guarantee that this will work anywhere else. Quakenet's Q authentication is built in, should you wish to use it.

## Requirements

All you'll need is what's in requirements.txt.

## Installation/Usage

    pip install punchbowl

That should be all you have to do, and then you should be ready to roll!

Usage is a lot like Flask - just a few more configuration options needed to kick off:

    from punchbowl import Bot

    bot = Bot('#punchbowltest', 'punchbowl', 'se.quakenet.org', 6667)

    @bot.action('^hello$')
    def hello(bot, event):
        bot.say('Hi there, {0}!'.format(event.source.nick))

    bot.serve_forever()

It's worth noting that the re.IGNORECASE flag is set on all regexes passed into action - IRC is a little funny about capitals so I've made the decision to run with that.
