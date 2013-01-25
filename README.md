hook-proxy
===============

Run an IRC bot reporting commits, checking compilation and reporting test results to a channel.

The bot can be triggered either from a git hook or from the post-receive payload sent by github.com.

Dependencies : Tornado (a python web server), sandbox (to compile and run the tests), irctk (to run the IRC bot)


