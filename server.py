# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import tornado.ioloop
import tornado.web
import sys
import os
import json
import subprocess
import random
import codecs
import re


fifo = codecs.open("fifo", "w", "utf-8")

insultsdb = [
        "%s should learn to type.",
        "Take a stress pill, %s, and think things over.",
        "Too much blood in %s's caffeine stream.",
        "%s, do you think like you type?",
        "%s pushed garbage to the repository.",
        "git blame %s" ]

usernamedb = {
        'threonorm':'bThom',
        'wetneb':'pintoch',
        'axeldavy':'davy',
        'Lysxia':'lyxia',
        'nguyentito':'tito',
        'MathurinD':'Ish',
        'p4bl0-':'p4bl0',
        'bmsherman':'ben',
        }

repo_to_channel = {
        'dissemin':'#openaccess',
        'communication':'#openaccess',
        'proaixy':'#openaccess',
        'deposits':'#dissemin',
        'arxiv_metadata':'#openaccess',
        'libbmc':'#openaccess',
        'finite':'#coqstructiveMaths',
        'sigmalocales':'#coqstructiveMaths',
        }


class RepoConfig:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.has_local_copy = False
        self.channels = []
        self.default_channel = ""

    def join(self, chan):
        fifo.write("/join "+chan+"\n")
        fifo.flush()
        if not self.default_channel:
            self.default_channel = chan
        self.channels.append(chan)

    def write(self, project, msg):
        chan = repo_to_channel.get(project, self.default_channel) 
        if chan in self.channels:
            fifo.write("["+chan+"] "+msg+"\n")
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
        retcode = subprocess.call(["make"])
        self.back_to_cwd()
        if retcode != 0:
            idx = random.randint(0, len(insultsdb)-1)
            cfg.write(insultsdb[idx] % to_be_blamed)

cfg = RepoConfig("stocpreg", "https://github.com/wetneb/stocpreg")
cfg.join("#openaccess")
cfg.join('#dissemin')
cfg.join("#devroom")
cfg.join("#coqstructiveMaths")

class HookHandler(tornado.web.RequestHandler):
    def post(self, command):
        print "got command "+command
        if command == "hook":
            json_data = json.loads(self.get_argument("payload", default=None,
                strip=False))

            if 'pull_request' in json_data or 'issue' in json_data:
                repo = json_data['repository']['name']
                user = json_data['sender']['login']
                action = json_data['action']
                if action != 'opened':
                    return
                if user in usernamedb:
                    user = usernamedb[user]

                typ = ''
                details = {}
                if 'pull_request' in json_data:
                    typ = 'PR'
                    details = json_data['pull_request']
                elif 'issue' in json_data:
                    typ = 'issue'
                    details = json_data['issue']

                title = details['title']
                number = str(details['number'])
                cfg.write(repo,
                    "\x0314[\x0322" + repo +
                    "\x0314:\x0324" + user +
                    "\x0314]: \x0315opened "+typ+" #"+number+": "+title)

            elif 'ref' in json_data:
                # Push
                last_name = ""
                branch = "master"
                prefix = 'refs/heads/'
                if json_data['ref'].startswith(prefix):
                    branch = json_data['ref'][len(prefix):]
                branch_msg = ''
                repo = json_data['repository']['name']
                if branch != 'master':
                    branch_msg = '('+branch+')'
                commits = list(json_data['commits'])
                if len(commits) > 5:
                    cfg.write(repo, "... lots of commits ...")
                    commits = [commits[-1]]
                for cmt in commits:
                    last_name = cmt["author"]["name"]
                    firstline = cmt["message"].split("\n")[0]

                    user = cmt['author']['name']
                    if 'username' in cmt['author']:
                        user = cmt['author']['username']
                    if user in usernamedb:
                        user = usernamedb[user]

                    if not firstline.startswith("Merge branch 'master' "):
                        cfg.write(repo,
                                "\x0314[\x0322" + repo + branch_msg +
                                "\x0314:\x0324" + user +
                                "\x0314]: \x0315"+firstline)

                
        elif command == "l10n":
            repo = 'dissemin'
            rx = re.compile(r'http://paste\.fulltxt\.net/[^ ]+')
            secret_key = "003937feb"
            if self.get_argument("secret", default="", strip=True) != secret_key:
                return

            try:
                match = int(self.get_argument("nblines", default="", strip=True))
                cfg.write(repo, ('\x0314[translations]\x0315 a3nm: %d lines' % match))
            except ValueError:
                pass
        elif command == "deposit":
            try:
                name = self.get_argument("name", default="Inconnu", strip=True)
                repo = self.get_argument("repo", default="Dépôt inconnu", strip=True)
                url = self.get_argument("paperurl", default="", strip=True)
                cfg.write("deposits",
                    ('\x0314[\x0322%s\x0314]: \x0324%s\x0314 a déposé %s' %
                    (repo, name, url)))
            except ValueError:
                pass
                
application = tornado.web.Application([
    (r"/(.*)", HookHandler, dict()),
])

if __name__ == "__main__":
    application.listen(8765)
    tornado.ioloop.IOLoop.instance().start()

