hook-proxy
===============

Run an IRC bot reporting commits, checking compilation and reporting test results to a channel.

The bot can be triggered either from a git hook or from the post-receive payload sent by github.com.

Dependencies :
--------------
- Tornado (a python web server)
- sandbox (to compile and run the tests)
- irctk (to run the IRC bot)

Installation :
--------------
- Install the dependencies
- Create a directory where the local copies of the repositories will go, let's call it `copies`
- Configure sandbox such that programs are allowed to write in `copies` and its subdirectories
- Create a link in the server's working directory to copies :
  `ln -s /the/path/to/the/copies copies`


