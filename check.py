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

def list_all(req):
  #data = "{";
  datao = {}
  m = 0;
  machines = xmclib.get_machines(False)
  for mach in machines:
    machine = mach['name'];
    #if (m):
      #data += ', ';
    #data += machine + ': [';
    datao[machine] = {'up': mach['up'], 'mem': int(mach['mem']), 'responding': 1}
    datao[machine]['vms'] = []
    m += 1

    if (mach['up'] == 1):
      xenapi = xmclib.get_api(machine);
      if (xenapi is None):
        #data += ']';
        datao[machine]['responding'] = 0
        continue;
      mach_api = xenapi.host_metrics.get_all_records()
      total_mem = mach_api.popitem()[1]['memory_total']
      # 196 is the base mem that must be free on the host
      datao[machine]['mem_free'] = int(total_mem) - (192+18)*1024*1024
      records=xenapi.VM.get_all_records();
    else:
      #data += ']';
      continue;
    #data += ']';

    i = 0;
    for item in records:
      if (records[item]['name_label'] != 'Domain-0'):
        #if (i):
          #data += ", ";
        #data += "{name:'" + records[item]['name_label'] + "', uuid:'" + records[item]['uuid'] + "', mem_static_max:'" + records[item]['memory_static_max'] + "'}";
        ri = records[item]
        datao[machine]['vms'].append({'name': ri['name_label'], 'uuid': ri['uuid'], 'mem_static_max': ri['memory_static_max']})
        datao[machine]['mem_free'] = datao[machine]['mem_free'] - int(ri['memory_static_max'])
        i += 1;
    #data += ']';
  #data += "}";
  #_release_db_conn()
  return datao;

def migrate_live(req, frommachine, machineid, tomachine):
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

def get_user_info(req):
  user = _get_username(req);
  info = xmclib.get_user_info(user);
  #_release_db_conn()
  return {'user': info};

def get_create_user_info(req):
  user = _get_username(req);
  info = xmclib.get_user_info(user);
  allocvms = xmclib.get_unused_vms(user);
  all_info = {'user': info, 'allocvms': allocvms}
  #_release_db_conn()
  return all_info;

def create_vm(req, hname, dsize, ssize, imagename, mac, allocid, mem, owner, start_register):
  return xmclib.create_vm(_get_username(req), hname, dsize, ssize, imagename, mac, allocid, mem, owner, start_register)

def list_my_vms(req, all=0):
  user = _get_username(req)
  return xmclib.list_user_vms(user, all)

def boot_vm(req, name, machine='clusterfuck'):
  user = _get_username(req)
  return xmclib.boot_vm(user, name, machine)

def shutdown_vm(req, name):
  user = _get_username(req)
  return xmclib.shutdown_vm(user, name)

def destroy_vm(req, name):
  user = _get_username(req)
  return xmclib.destroy_vm(user, name)

def get_base_images(req):
  user = _get_username(req)
  return xmclib.get_base_images(user)

def check_name_avail(req, name):
  return xmclib.check_name_avail(name)

def boot_pm(req, name):
  user = _get_username(req)
  return xmclib.boot_pm(user, name)

def shutdown_pm(req, name):
  user = _get_username(req)
  return xmclib.shutdown_pm(user, name)
