#!/usr/bin/env python
#-*- coding:utf-8 -*- 
from tornado import web
from tornado import websocket
from message import Factory
import os, logging, json, uuid, tornado, time

log = logging.getLogger()

serverFactory = Factory() 

server = serverFactory.getServerHandler("chat")

class MainHandler(web.RequestHandler):

    def initialize(self, server):
        self.server = server

    def get(self):
        self.user = user = self.get_cookie('user','')
        users = self.server.getUsers()
        if not user:
            self.user = user = str(uuid.uuid4())
            self.set_cookie('user', user)
        self.render("index.html")


class ChatWSHandler(websocket.WebSocketHandler):

    def initialize(self, server):
        self.server = server

    def open(self):
        self.server.insert(self)
        content = {"type":"system", "content":{"body":"当前用户:" + str(self.server.getUserNum())}}
        self.write_message(json.dumps(content))
        self.broadcast("有人来了！", "system")

    def on_message(self, msg):
        getMsg = json.loads(msg)
        self.broadcast(getMsg.get("content")) 

    def broadcast(self, msg, type="message"):
        content = {"type":type, "content":{"type":"o", "body":msg}}
        self.server.broadcast(json.dumps(content), self);

    def on_close(self):
        self.server.remove(self)
        self.broadcast("有人走了！", "system")

class ChatLPHandler(web.RequestHandler):

    def initialize(self, server):
        self.server = server

    def write_new_message(self, message):
        if self.request.connection.stream.closed():
            return
        print "write:" + self.user + message
        self.write(message)
        self.finish()

    @web.asynchronous
    def get(self):
        self.user = user = self.get_cookie('user','')
        users = self.server.getUsers()
        if not user:
            self.user = user = str(uuid.uuid4())
            self.set_cookie('user', user)
        self.server.insert(self)
        if user not in users:
            self.server.broadcast("有人来了！当前用户" + str(self.server.getUserNum()),"system")

    def post(self):
        content = json.loads(self.get_argument("d","{}"))
        if content:
            print "broadcast:" + json.dumps(content)
            self.server.broadcast(content["content"], notInclude=self.get_cookie('user',''))

    def on_connection_close(self):
        self.server.remove(self.user)


settings = dict(
    cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    autoescape="xhtml_escape",
)

handlers = [
    (r"/", MainHandler, dict(server = server)),
    (r"/message", ChatLPHandler, dict(server = server)),
]