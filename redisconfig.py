#!/usr/bin/env python


from ConfigParser import SafeConfigParser

DELIMITER = "\r\n"


class RedisCommands(object):

    def __init__(self):
        pass

    @staticmethod
    def encode(res):
        result = []
        result.append("*")
        result.append(str(len(res)*2))
        result.append(DELIMITER)
        for arg in res:
            for test in arg:
                result.append("$")
                result.append(str(len(test)))
                result.append(DELIMITER)
                result.append(test)
                result.append(DELIMITER)
        # "".join(result)
        return "".join(result)

    @staticmethod
    def encode_new(res):
        result = []
        result.append("*")
        result.append(str(len(res)))
        result.append(DELIMITER)
        for arg in res:
            result.append("$")
            result.append(str(len(arg)))
            result.append(DELIMITER)
            result.append(arg)
            result.append(DELIMITER)
        return "".join(result)

    @staticmethod
    def encode_keys(res):
        result = []
        result.append("*")
        result.append(str(len(res)))
        result.append(DELIMITER)
        for arg in res:
            result.append("$")
            result.append(str(len(arg)))
            result.append(DELIMITER)
            result.append(str(arg))
            result.append(DELIMITER)
        return "".join(result)

    @staticmethod
    def set_config(key, value):
        flag = 0
        with open('config/info', 'r') as f:
            lines = f.readlines()
        with open('config/info', 'w') as m:
            for line in lines:
                l = line.strip().split()
                if l[0] == key:
                    flag = 1
                    l[1] = value
                    new_line = " ".join(l)
                    m.write(new_line+"\r\n")
                else:
                    m.write(line)
        print "ok"
        return flag

    @staticmethod
    def parse_config(param):
        l = []
        input = open('config/info', 'r')
        data = input.readlines()
        pos = param.find("*")
        for i in data:
            if param == "*":
                if len(i.strip().split()) > 1:
                    l.append(i.strip().split())
            elif pos != 0 and pos != -1:
                if len(i.strip().split()) > 1 and i.startswith(param[:pos]):
                    l.append(i.strip().split())
            elif pos == -1:
                if len(i.strip().split()) > 1 and i.startswith(param):
                    l.append(i.strip().split())
        print l
        red_enc_data = RedisCommands.encode(l)
        return red_enc_data

    @staticmethod
    def parse_info(time, connections, cmds):
        s = []
        parser = SafeConfigParser()
        parser.read('redis.conf')
        parser.set('info', 'uptime_in_seconds', str(time))
        parser.set('info', 'total_connections_received', str(connections))
        parser.set('info', 'total_commands_processed', str(cmds))
        with open('redis.conf', 'wb') as configfile:
            parser.write(configfile)
        parser.read('redis.conf')
        someinfo = parser.items('info')
        for i in someinfo:
             s.append(":".join(i))
        data = RedisCommands.encode_new(s)
        return data
