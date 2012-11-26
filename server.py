#!/usr/bin/env python
#-*- coding:utf-8 -*-
import logging
from tornado import web
from tornado import websocket
from tornado import httpserver
from tornado import ioloop
from tornado import database
from tornado.options import define, options, parse_config_file
from chat import handlers, settings
#from app import routes, settings

define("port", default=8000, help="http port", type=int)

application = web.Application(handlers, **settings)

if __name__ == "__main__":
    server = httpserver.HTTPServer(application)
    server.listen(options.port)
    ioloop.IOLoop.instance().start()
