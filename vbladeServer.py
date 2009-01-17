# Copyright (c) 2009, Angelo DiNardi (adinardi@csh.rit.edu)

import SimpleXMLRPCServer
from threading import Thread
import subprocess
import os

# List to contain all of the vbladeExport threads which contain vlbade processes
VBLADES = {}

# Start up a vblade instance for a given VM and disk.
def start_vblade(id, vm_name, disk_name):
  print "start requested: " + str(id) + ":" + vm_name + ":" + disk_name
  vbladeProc = vbladeExport()
  VBLADES[vm_name + '-' + disk_name] = vbladeProc
  vbladeProc.vm_name = vm_name
  vbladeProc.disk_name = disk_name
  vbladeProc.disk_id = id
  vbladeProc.start()
  return {'status': 'OK'}
  
# Stop a vblade instance for a VM and disk
def stop_vblade(id, vm_name, disk_name):
  print "stop requested: " + str(id) + ":" + vm_name + ":" + disk_name
  key = vm_name + '-'+ disk_name
  if key not in VBLADES:
    return {'status': 'FAIL', 'reason': 'Disk not exported'}
  vbladeProc = VBLADES[key]
  if vbladeProc is not None:
    os.kill(vbladeProc.p.pid, 15)
    vbladeProc.p.wait()
    VBLADES[vm_name + '-' + disk_name] = None
  return {'status': 'OK'}

# Thread which does the main running of the XMLRPC server.
class vbladeServer(Thread):
  def run(self):
    server = SimpleXMLRPCServer.SimpleXMLRPCServer(("10.6.9.200", 31337))
    server.register_function(start_vblade)
    server.register_function(stop_vblade)
    server.serve_forever()
    
# Code to actually get the server started when this script runs.
server = vbladeServer()
server.start()

# The thread which is used to contain the actual vblade process
class vbladeExport(Thread):
  def __init__(self):
    Thread.__init__(self)
    self.vm_name = ''
    self.disk_name = ''
    self.disk_id = ''
    self.p = None
  def run(self):
    print "starting process...."
    print "calling: " + str(self.disk_id) + " 0 eth1 /space/vm/vms/domains/" + self.vm_name + "/" + self.disk_name + ".img"
    self.p = subprocess.Popen("/usr/sbin/vblade " + str(self.disk_id) + " 0 eth1 /space/vm/vms/domains/" + self.vm_name + "/" + self.disk_name + ".img", shell=True)
    print "done...?"
