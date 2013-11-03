import tornado.ioloop
import tornado.web
import sys
import os
import json
import subprocess
import random
import codecs

fifo = codecs.open("fifo", "w", "utf-8")

insultsdb = [
        "%s should learn to type.",
        "Take a stress pill, %s, and think things over.",
        "Too much blood in %s's cafeine stream.",
        "%s, do you think like you type ?",
        "%s pushed garbage to the repository.",
        "git blame %s" ]

class RepoConfig:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.has_local_copy = False
        self.has_joined = False
        self.channel = "#bots"

    def join(self, chan):
        fifo.write("/join "+chan+"\n")
        fifo.flush()
        self.channel = chan
        self.has_joined = True

    def write(self, msg):
        if self.has_joined:
            fifo.write("["+self.channel+"] "+msg+"\n")
            fifo.flush()

    def go_to_copy(self):
        self.wd_save = os.getcwd()
        os.chdir(os.path.join(os.path.abspath(sys.path[0]),
            "copies/"+self.name))
    
    def back_to_cwd(self):
        os.chdir(self.wd_save)

    def clone(self):
        self.has_local_copy = (subprocess.call(["test", "-d",
            "copies/"+self.name]) == 0)
        if not self.has_local_copy:
            self.has_local_copy = True
            retcode = subprocess.call(["mkdir", "-p", "copies/"+self.name])
            self.go_to_copy()
            retcode = subprocess.call(["git", "clone", self.url, "."])
            self.back_to_cwd()

    def pull(self):
        self.clone()
        self.go_to_copy()
        retcode = subprocess.call(["git", "pull"])
        self.back_to_cwd()

    def check_make(self, to_be_blamed):
        self.clone()
        self.pull()
        self.go_to_copy()
        retcode = subprocess.call(["sandbox", "make"])
        self.back_to_cwd()
        if retcode != 0:
            idx = random.randint(0, len(insultsdb)-1)
            cfg.write(insultsdb[idx] % to_be_blamed)

cfg = RepoConfig("kahn", "https://github.com/ccompile/kahn")
cfg.join("#devroom")

class HookHandler(tornado.web.RequestHandler):
    def post(self, command):
        print "got command "+command
        if command == "hook":
            json_data = json.loads(self.get_argument("payload", default=None,
                strip=False))
            last_name = ""
            for cmt in json_data["commits"]:
                last_name = cmt["author"]["name"]
                cfg.write("commit from "+cmt["author"]["email"]+
                        " : "+cmt["message"])
            # cfg.check_make(last_name)
                
                
application = tornado.web.Application([
    (r"/(.*)", HookHandler, dict()),
])

if __name__ == "__main__":
    application.listen(8765)
    tornado.ioloop.IOLoop.instance().start()

