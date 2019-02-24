# --coding=UTF-8 --
from twisted.python import log
from twisted.internet.protocol import Protocol, ServerFactory
from twisted.internet import reactor
import redis_protocol
import sys
import fakeredis
import time
from redisconfig import RedisCommands
from record import JsonLog


global time_elapse
time_elapse = time.time()


class RedisServer(Protocol):
    connectionNb = 0

    def __init__(self):
        self.command = ['get', 'set', 'config', 'info', 'quit', 'ping', 'del', 'keys', "save", "flushall", "flushdb"]
        self.r = fakeredis.FakeStrictRedis() 

    def connectionMade(self):
        self.connectionNb += 1
        print "New connection: %s from %s" % (self.connectionNb, self.transport.getPeer().host)

    def dataReceived(self, rcvdata):
        cmd_count = 0
        cmd_count += 1
        data = redis_protocol.decode(rcvdata)  # data类型:list
        command = " ".join(redis_protocol.decode(rcvdata))  # command类型:string
        # print str(command)
        logger = JsonLog()
        logger.get_log(command, self.transport.getPeer().host, self.transport.getPeer().port)
        if data[0] in self.command:
            if data[0].lower() == "quit":
                self.transport.loseConnection()
            elif data[0].lower() == "ping":
                self.transport.write("+PONG\r\n")
            elif data[0].lower() == "info":
                diff = round(time.time() - time_elapse) % 60
                self.transport.write(RedisCommands.parse_info(diff, self.connectionNb, cmd_count))
            elif data[0].lower() == "save" or data[0].lower() == "flushall" or data[0].lower() == "flushdb":
                self.transport.write("+OK\r\n")
            else:
                if command.lower().startswith('config get') and len(data) == 3:
                    s = RedisCommands.parse_config(data[2])
                    self.transport.write(s)
                elif command.lower().startswith('config set') and len(data) == 4:
                    flag = RedisCommands.set_config(data[2], data[3])
                    if flag:
                        self.transport.write("+OK\r\n")
                    else:
                        self.transport.write("-(error) ERR Unsupported CONFIG parameter: {0}".format(data[2]))
                elif data[0].lower() == "set" and len(data) == 3:
                    if self.r.set(data[1], data[2]):
                        self.transport.write("+OK\r\n")
                elif data[0].lower().startswith('del') and len(data) == 2:
                    if self.r.delete(data[1]):
                        self.transport.write("+(integer) 1\r\n")
                    else:
                        self.transport.write("+(integer) 0\r\n")
                elif data[0].lower() == 'get' and len(data) == 2:
                    if self.r.get(data[1]):
                        s = self.r.get(data[1])
                        self.transport.write("+{0}\r\n".format(s))
                    else:
                        self.transport.write("+(nil)\r\n")
                elif data[0].lower() == 'keys' and len(data) == 2:
                    if self.r.keys() and (data[1] in self.r.keys() or data[1] == '*'):
                        keys = self.r.keys()
                        self.transport.write(RedisCommands.encode_keys(keys))
                    elif len(self.r.keys()) == 0:
                        self.transport.write("+(empty list or set)\r\n")
                else:
                    self.transport.write("-ERR wrong number of arguments for '{0}' command\r\n".format(data[0]))
        else:
            self.transport.write("-ERR unknown command '{0}'\r\n".format(data[0]))

    def connectionLost(self, reason):
        self.connectionNb -= 1
        print "End connection: ", reason.getErrorMessage()


class RedisServerFactory(ServerFactory):
    protocol = RedisServer


log.startLogging(sys.stdout)
reactor.listenTCP(6379, RedisServerFactory())
reactor.run()
