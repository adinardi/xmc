# Copyright (c) 2009, Angelo DiNardi (adinardi@csh.rit.edu)

import xmlrpclib
import time

server = xmlrpclib.ServerProxy("http://10.6.9.200:31337")
stuff = server.start_vblade(200, "coffee", "disk")
time.sleep(10)
stuff = server.stop_vblade(200, "coffee", "disk")

print stuff
