# Copyright (c) 2008-2009, Angelo DiNardi (adinardi@csh.rit.edu)

from mod_python import apache
from mod_python import Session as MPSession
import xmclib
import time

def handle_req():
  return apache.OK

def _get_username(req):
  pw = req.get_basic_auth_pw();
  return req.user;

def _is_admin(req):
  pw = req.get_basic_auth_pw();
  u = req.user;
  return xmclib.is_admin(u)

def _cleanup():
  xmclib.cleanup()

# List all of the Physical Machines and the VMs running on them
# This function loads data cached in the DB.
def list_all(req):
  # datao = xmclib.list_all()
  conn = xmclib._get_db_conn()
  cur = conn.cursor()
  
  datao = {}
  
  cur.execute("SELECT name, up, mem FROM pmmachines ORDER BY name")
  rows = cur.fetchall()
  for row in rows:
    machine_name = row[0]
    datao[machine_name] = {'up': row[1], 'mem': int(row[2])}
    datao[machine_name]['vms'] = []
    datao[machine_name]['mem_free'] = (int(row[2]) - 192 - 18) * 1024 * 1024
    
  cur.execute("SELECT vmmachines.name, vmmachines.mem, pmmachines.name, vmmachines.last_uuid FROM vmmachines, pmmachines WHERE vmmachines.pmmachine_id = pmmachines.id")
  rows = cur.fetchall()
  for row in rows:
    machine_name = row[2]
    datao[machine_name]['vms'].append({'name': row[0], 'uuid': row[3], 'mem_static_max': int(row[1]) * 1024 * 1024})
    datao[machine_name]['mem_free'] = datao[machine_name]['mem_free'] - (int(row[1]) * 1024 * 1024)
  
  _cleanup()
  return datao;

def migrate_live(req, frommachine, machineid, tomachine):
  #req.register_cleanup(_cleanup)
  if (not _is_admin(req)):
    return "{}";
  xenapi = xmclib.get_api(frommachine);
  xenapi.VM.migrate(machineid, tomachine, 1, {});

  # Make sure the existing VM is completely destroyed from the original host
  cleaning = 1
  while (cleaning):
    time.sleep(1)
    record = None
    try:
      record = xenapi.VM.get_by_uuid(machineid)
    except:
      record = None

    if (record is None):
      cleaning = 0
      continue
    try:
      if (xenapi.VM.get_record(record)['power_state'] == 'Halted'):
        xenapi.VM.destroy(record)
        cleaning = 0
    except:
      cleaning = 0
  #_release_db_conn()
  _cleanup()

def get_user_info(req):
  #req.register_cleanup(_cleanup)
  user = _get_username(req);
  info = xmclib.get_user_info(user);
  #_release_db_conn()
  _cleanup()
  return {'user': info};

def get_create_user_info(req):
  #req.register_cleanup(_cleanup)
  user = _get_username(req);
  info = xmclib.get_user_info(user);
  allocvms = xmclib.get_unused_vms(user);
  all_info = {'user': info, 'allocvms': allocvms}
  #_release_db_conn()
  _cleanup()
  return all_info;

def create_vm(req, hname, dsize, ssize, imagename, mac, allocid, mem, owner, start_register, start_range):
  #req.register_cleanup(_cleanup)
  ret = xmclib.create_vm(_get_username(req), hname, dsize, ssize, imagename, mac, allocid, mem, owner, start_register, start_range)
  _cleanup()
  return ret

def list_my_vms(req, all=0):
  #req.register_cleanup(_cleanup)
  user = _get_username(req)
  ret = xmclib.list_user_vms(user, all)
  _cleanup()
  return ret

def boot_vm(req, name, machine=''):
  #req.register_cleanup(_cleanup)
  user = _get_username(req)
  ret = xmclib.boot_vm(user, name, machine)
  _cleanup()
  return ret

def shutdown_vm(req, name):
  #req.register_cleanup(_cleanup)
  user = _get_username(req)
  ret = xmclib.shutdown_vm(user, name)
  _cleanup()
  return ret

def destroy_vm(req, name):
  #req.register_cleanup(_cleanup)
  user = _get_username(req)
  ret = xmclib.destroy_vm(user, name)
  _cleanup()
  return ret

def get_base_images(req):
  #req.register_cleanup(_cleanup)
  user = _get_username(req)
  ret = xmclib.get_base_images(user)
  _cleanup()
  return ret

def check_name_avail(req, name):
  #req.register_cleanup(_cleanup)
  ret = xmclib.check_name_avail(name)
  _cleanup()
  return ret

def boot_pm(req, name):
  #req.register_cleanup(_cleanup)
  user = _get_username(req)
  ret = xmclib.boot_pm(user, name)
  _cleanup()
  return ret

def shutdown_pm(req, name):
  #req.register_cleanup(_cleanup)
  user = _get_username(req)
  ret = xmclib.shutdown_pm(user, name)
  _cleanup()
  return ret
