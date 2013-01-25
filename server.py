import tornado.ioloop
import tornado.web
import sys
import json
import subprocess

channel = "#bots"

fifo = open("fifo", "w")
fifo.write("/join "+channel+"\n")
fifo.flush()

class HookHandler(tornado.web.RequestHandler):
    def write_msg(self, msg):
        fifo.write("["+channel+"] "+msg+"\n")
        fifo.flush()

    def check_make(self, name):
        retcode = subprocess.call(["make"])
        if retcode != 0:
            self.write_msg(name+" should learn to type")

    def post(self, command):
        if command == "hook":
            json_data = json.loads(self.get_argument("payload", default=None, strip=False))
            print(json_data["ref"])
            last_name = ""
            for cmt in json_data["commits"]:
                last_name = cmt["author"]["name"]
                self.write_msg("commit from "+cmt["author"]["email"]+" : "+cmt["message"]+"\n")
            self.check_make(last_name)
                
                
application = tornado.web.Application([
    (r"/(.*)", HookHandler, dict()),
])

if __name__ == "__main__":
    application.listen(8765)
    tornado.ioloop.IOLoop.instance().start()

