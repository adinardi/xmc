# Copyright (c) 2009, Angelo DiNardi (adinardi@csh.rit.edu)

import xmlrpclib
import time
import sys

server = xmlrpclib.ServerProxy("http://10.6.9.200:31337")
#time.sleep(10)

if len(sys.argv) < 5:
  print sys.argv[0] + " (start/stop) <slot> <vm_name> <disk_name>"
  exit()

if sys.argv[1] == "start":
  stuff = server.start_vblade(sys.argv[2], sys.argv[3], sys.argv[4])
elif sys.argv[1] == "stop":
  stuff = server.stop_vblade(sys.argv[2], sys.argv[3], sys.argv[4])
else:
  print sys.argv[0] + " (start/stop) <slot> <vm_name> <disk_name>"
  exit()

#stuff = server.start_vblade(75, "telltale", "disk")
#stuff = server.start_vblade(76, "telltale", "swap")

#stuff = server.start_vblade(93, "kernelvm", "kernelmirror")
#stuff = server.start_vblade(88, "kernelvm", "swap")
#stuff = server.start_vblade(87, "kernelvm", "disk")


#stuff = server.start_vblade(95, "codehub", "swap")
#stuff = server.start_vblade(94, "codehub", "disk")

#stuff = server.start_vblade(71, "vote", "disk")
#stuff = server.start_vblade(72, "vote", "swap")

#stuff = server.start_vblade(84, "drunkard", "swap")
#stuff = server.start_vblade(83, "drunkard", "disk")

#stuff = server.start_vblade(85, "infosysssh", "disk")
#stuff = server.start_vblade(86, "infosysssh", "swap")

#stuff = server.start_vblade(41, "coffee", "disk")
#stuff = server.start_vblade(42, "coffee", "swap")

print stuff
