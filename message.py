import json

class Factory():
    def __init__(self):
        self.servers = {}
    
    def getServerHandler(self, name):
        serverHandler = self.servers.get(name, None)
        if not serverHandler:
            serverHandler = self.servers[name] = LongPollServer(name)
        return serverHandler

class LongPollServer(object):

    def __init__(self, name):
        self.users = {}
        self.messageCache = []
         
    def broadcast(self, message, type = "message", notInclude = None):
        content = json.dumps({"type":type, "content":{"body":message, "type":"o"}})
        for u, h in self.users.items():
            if h and u != notInclude:
                print "write :" + u
                h.write_new_message(content)
                self.users[u] = None

    def insert(self, u):
        self.users[u.user] = u
        print self.users

    def getUserNum(self):
        return len(self.users.keys())

    def getUsers(self):
        return self.users.keys()

    def finishOne(self, u):
        u.write_new_message("{}")
        self.users[u.user] = None
    def remove(self, u):
        self.users.pop(u)

        
class MessageServer():
    def __init__(self, name):
        self.connects = []
        self.messageCache = []
        self.name = name

    def getName(self):
        return self.name

    def insert(self, connect):
        self.connects.append(connect)

    def broadcast(self, msg, notInclude = None):
        for c in self.connects:
            if notInclude == c:
                continue
            c.write_message(msg)

    def getUserNum(self):
        return len(self.connects)

    def remove(self, connect):
        self.connects.remove(connect)
