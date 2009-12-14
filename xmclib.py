from xen.xm.XenAPI import Session
import MySQLdb
import pgdb
import time
from pgdb import IntegrityError
import struct, socket
import os
import xmlrpclib

# MySQL Database Connection, xen DB
conn = None

# Postgres Database Connection, network DB
pg_conn = None

API_CONNECTIONS = {}
MACHINES= None

def _handle_cleanup():
  _release_db_conn()
  
def get_last_sync_time():
  conn = _get_db_conn()
  cur = conn.cursor()
  cur.execute("SELECT last_refresh FROM meta LIMIT 1")
  row = cur.fetchone()
  return row[0].strftime("%d/%m/%Y %H:%M:%S")

def get_machines(onlineOnly=True):
  global MACHINES
  if (MACHINES is None):
    conn = _get_db_conn()
    cur = conn.cursor()
    extra = ' WHERE live = 1'
    if (onlineOnly):
      extra = ' WHERE up = 1 and live = 1'
    cur.execute("SELECT id, name, mac, mem, up FROM pmmachines" + extra)

    machines = []
    rows = cur.fetchall()
    for row in rows:
      machines.append({'id': row[0], 'name': row[1], 'mac': row[2], 'mem': row[3], 'up': row[4]})
    MACHINES = machines
  else:
    machines = MACHINES

  return machines

def is_admin(username):
  conn = _get_db_conn();
  cur = conn.cursor();
  cur.execute("SELECT admin FROM users WHERE user='" + username + "'");
  row = cur.fetchone();
  if (row == None):
    return False
  if (row[0] == 1):
    return True;
  return False;

def cleanup():
  _release_db_conn()
  _release_pg_db_conn()

def _get_db_conn():
  global conn
  if (conn is None):
    conn = MySQLdb.connect(host='db.csh.rit.edu', user='xen', passwd='<XEN PASS HERE>', db='xen')
  return conn

def _release_db_conn():
  global conn
  if (conn is not None):
    conn.close()
    conn = None

def _get_pg_db_conn():
  global pg_conn
  if (pg_conn is None):
    pg_conn = pgdb.connect(host='db.csh.rit.edu', user='net_user', password='<NET PASS HERE>', database='network')
  return pg_conn

def _release_pg_db_conn():
  global pg_conn
  if (pg_conn is not None):
    pg_conn.close()
    pg_conn = None

def _get_vblade_server():
  server = xmlrpclib.ServerProxy("http://10.6.9.200:31337")
  return server
  
def _start_vblade(id, vm_name, disk_name):
  server = _get_vblade_server()
  server.start_vblade(id, vm_name, disk_name)
  
def _stop_vblade(id, vm_name, disk_name):
  server = _get_vblade_server()
  server.stop_vblade(id, vm_name, disk_name)

def get_api(machine):
  global API_CONNECTIONS
  if (machine in API_CONNECTIONS):
    xenapi = API_CONNECTIONS[machine]
  else:
    session=Session('http://' + machine + ':9363');
    try:
      session.login_with_password('','');
      xenapi = session.xenapi;
      xenapi.VM.get_all_records();
      API_CONNECTIONS[machine] = xenapi
    except:
      xenapi = None;
  
  return xenapi;

def find_vm(name):
  machines = get_machines(True)
  for mach in machines:
    machine = mach['name']
    xenapi = get_api(machine);
    if (xenapi is None):
      continue;
    records = xenapi.VM.get_by_name_label(name)
    if len(records) > 0:
      record = xenapi.VM.get_record(records[0]);
      ps = record['power_state']
      return {'found': 1, 'power_state': ps, 'machine': machine, 'uuid': record['uuid']}
  return {'found': 0, 'power_state': 'Off'}
  
def get_vm_state(name, ignoreFail = False):
  failed = False
  pm = get_vm_location(name)
  if (res == None):
    # We need to locate the VM, we don't know where it is.
    failed = True

  if (failed == False):
    xenapi = get_api(pm)
    if (xenapi is None):
      failed = True
    if (failed == False):
      records = xenapi.VM.get_by_name(name)
      if len(records) > 0:
        record = xenapi.VM.get_record(records[0]);
        ps = record['power_state']
        return {'found': 1, 'power_state': ps, 'machine': machine, 'uuid': record['uuid']}
  return {}

def get_vm_location(name):
  conn = _get_db_conn()
  cur = conn.cursor()
  cur.execute("SELECT pmmachines.name FROM pmmachines, vmmachines WHERE pmmachines.id = vmmachines.pmmachine_id AND vmmachines.name = '" + MySQLdb.escape_string(name) + "'")
  res = cur.fetchone()
  if (res == None):
    return None
  else:
    return res[0]

def fix_vm_location(name):
  
  return ""

def get_user_info(user):
  conn = _get_db_conn();
  cur = conn.cursor();
  cur.execute("SELECT admin FROM users WHERE user='" + MySQLdb.escape_string(user) + "'");
  res = cur.fetchone()
  if (res == None):
    return {'admin': 0, 'username': user}
  info = {'admin': res[0], 'username': user}
  return info

def get_unused_vms(user):
  conn = _get_db_conn();
  cur = conn.cursor();
  cur.execute("SELECT id, mac, disk, mem, swap, owner FROM allocvmmachines WHERE owner = '" + MySQLdb.escape_string(user) + "'");
  rows = cur.fetchall()
  vms = []
  for row in rows:
    mac = row[1]
    if  (mac == None):
      mac = ''
    vms.append({'id': str(row[0]), 'mac': mac, 'disk': int(row[2]), 'mem': int(row[3]), 'swap': int(row[4]), 'owner': row[5]});
  return vms

# Downloaded from http://code.activestate.com/recipes/358449/
# No license specifically attached.
def _wake_on_lan(macaddress):
    """ Switches on remote computers using WOL. """
    # Check macaddress format and try to compensate.
    if len(macaddress) == 12:
        pass
    elif len(macaddress) == 12 + 5:
        sep = macaddress[2]
        macaddress = macaddress.replace(sep, '')
    else:
        raise ValueError('Incorrect MAC address format')
    # Pad the synchronization stream.
    data = ''.join(['FFFFFFFFFFFF', macaddress * 20])
    send_data = '' 
    # Split up the hex values and pack.
    for i in range(0, len(data), 2):
        send_data = ''.join([send_data,
                             struct.pack('B', int(data[i: i + 2], 16))])
    # Broadcast it to the LAN.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(send_data, ('10.6.9.255', 7))

# Create a VM based on the parameters.
def create_vm(uname, hname, dsize, ssize, imagename, mac, allocid, mem, owner, start_register, start_range):
  user = get_user_info(uname);
  conn = _get_db_conn();
  cur = conn.cursor();

  adsize = None
  assize = None
  amac = None
  amem = None
  aowner = None
  usingPrealloc = 0

  if allocid == 'new':
    allocid = None

  # Check if we got an alloc id or else that we're an admin
  if (allocid == None and user['admin'] != 1):
    #_release_db_conn()
    return "{status: 'FAIL', reason: 'Not an admin. Must use preallocated VM'}";

  # Get the allocation we're going to use, if we're using one.
  if (allocid != None):
    cur.execute("SELECT mac, disk, swap, mem, owner FROM allocvmmachines WHERE id = " + str(int(allocid)) + ";");
    row = cur.fetchone()
    if (row != None):
      usingPrealloc = 1
      amac = row[0]
      adsize = row[1]
      assize = row[2]
      amem = row[3]
      aowner = row[4]

  if (usingPrealloc == 0 and user['admin'] != 1):
    #_release_db_conn()
    return "{status: 'FAIL', reason: 'Not authorized to create new VM'}"

  # Check that the base image name is legitimate
  cur.execute("SELECT name FROM images WHERE name = '" + MySQLdb.escape_string(imagename) + "'")
  row = cur.fetchall()
  if (row is None):
    #_release_db_conn()
    return {'status': 'OK', 'reason': 'image name is not valid'}

  # If we're using a pre-allocated VM, make sure un-changeable settings aren't changed.
  if (usingPrealloc == 1 and ((amac != None and amac != mac) or (adsize != None and int(adsize) != int(dsize)) or (assize != None and int(assize) != int(ssize)) or (amem != None and int(amem) != int(mem)) or (aowner != None and aowner != owner))):
    #_release_db_conn()
    return "{status: 'FAIL', reason: 'Locked attributes do not match amac:" + str(amac) + " adsize:" + str(adsize) + " assize:" + str(assize) + " amem:" + str(amem) + " aowner:" + str(aowner) + "'}"


  # If the user chose to do a registration on start, register it
  if (start_register == 'on'):
    # DO Network Registration
    pg_conn = _get_pg_db_conn()
    pg_cur = pg_conn.cursor()

    # Figure out the IP range we want to deal with.
    if (start_range == 'userrack'):
      first_ip = '129.21.50.176'
      last_ip = '129.21.60.249'
    elif (start_range == 'projects'):
      first_ip = '129.21.50.1'
      last_ip = '129.21.50.64'
      
    pg_cur.execute("SELECT ip_address FROM host_cache WHERE ip_address BETWEEN '" + first_ip + "' AND '" + last_ip + "' AND in_use = false ORDER BY ip_address LIMIT 1")
    row = pg_cur.fetchone()
    if (row is not None):
      ip_addr = row[0]
      pg_cur.execute("UPDATE host_cache SET in_use = true WHERE ip_address = '" + str(ip_addr) +"'")

      try:
        pg_cur.execute("INSERT INTO hosts (hardware_address, ip_address, hostname, username, auth_user) VALUES ('" + pgdb.escape_string(mac) + "', '" + ip_addr + "', '" + pgdb.escape_string(hname) + "', '" + pgdb.escape_string(owner) + "', 'adinardi')")
      except pgdb.DatabaseError:
        # END HERE. Return failure since we can't register
        pg_conn.rollback()
        #_release_db_conn()
        return {'status': 'FAIL', 'reason': 'Hostname or MAC address already registered.'}

      pg_cur.execute("INSERT INTO process_queue (event_class) VALUES ('RELDHCP')")
      pg_conn.commit()
    else:
      return {'status': 'FAIL', 'reason': 'No more IP addresses available to be registered'}


  # ADD MYSQL DB WRITE HERE.
  cur.execute("INSERT INTO vmmachines (name, owner, mac, disk, mem, swap) VALUES('" + MySQLdb.escape_string(hname) + "', '" + MySQLdb.escape_string(owner) + "', '" + MySQLdb.escape_string(mac) + "', '" + MySQLdb.escape_string(dsize) + "', '" + MySQLdb.escape_string(mem) + "', '" + MySQLdb.escape_string(ssize) + "')");
  vmid = conn.insert_id()
  cur.execute("INSERT INTO vmdisks (file, device, vmmachineid) VALUES ('disk', 'xvda2', " + str(vmid) + ")")
  cur.execute("INSERT INTO vmdisks (file, device, vmmachineid) VALUES ('swap', 'xvda1', " + str(vmid) + ")")
  if (usingPrealloc == 1):
    cur.execute("DELETE FROM allocvmmachines WHERE id = " + str(int(allocid)))

  # Write Config
  FILE = open('/mnt/vms/configs/new/' + hname + '.defs', "w");
  FILE.write("-n " + hname + " -d " + dsize + " -s " + ssize + " -b " + imagename + " -m " + mac + " -e " + mem);
  FILE.close();

  #_release_db_conn()
  return "{status: 'OK'}"

def list_user_vms(user, all=0):
  info = get_user_info(user)
  doall = 0
  if (info['admin'] == 1 and int(all) == 1):
    doall = 1
  conn = _get_db_conn()
  cur = conn.cursor()
  extra = ''
  if (doall == 0):
    extra = " WHERE vmmachines.owner='" + user + "'"
  cur.execute("SELECT vmmachines.id, vmmachines.name, vmmachines.owner, vmmachines.mac, vmmachines.disk, vmmachines.mem, vmmachines.swap, vmmachines.enabled, pmmachines.name, vmmachines.last_uuid, vmmachines.power_state FROM vmmachines LEFT JOIN pmmachines ON vmmachines.pmmachine_id = pmmachines.id" + extra + " ORDER BY vmmachines.owner, vmmachines.name")
  rows = cur.fetchall()
  vms = []
  for row in rows:
    if row[10] is None:
      power_state = 'Off'
    else:
      power_state = row[10]
      
    if row[8] is None:
      machine = ''
    else:
      machine = row[8]
      
    if row[9] is None:
      uuid = ''
      found = 0
    else:
      uuid = row[9]
      found = 1
      
    vms.append({'id': int(row[0]), 'name': row[1], 'owner': row[2], 'mac': row[3], 'disk': int(row[4]), 'mem': int(row[5]), 'swap': int(row[6]), 'enabled': int(row[7]), 'online': {'found': found, 'power_state': power_state, 'machine': machine, 'uuid': uuid}})
  #_release_db_conn()
  return vms

def boot_vm(user, name, machine=''):
  info = get_user_info(user)
  conn = _get_db_conn()
  cur = conn.cursor()
  
  #cur.execute("SELECT id FROM pmmachines WHERE name = '" + MySQLdb.escape_string(machine) + "'")
  #row = cur.fetchone()
  #if row is None:
  #  return {'status': 'FAIL', 'reason': 'Phyical Machine does not exist'}
  #pm_id = int(row[1])
  
  cur.execute("SELECT id, name, mac, mem, kernel, kernel_args, owner FROM vmmachines WHERE name = '" + MySQLdb.escape_string(name) + "'")
  row = cur.fetchone()
  if row is None:
    return {'status': 'FAIL', 'reason': 'VM does not exist'}

  if (row[6] != user and info['admin'] != 1):
    return {'status': 'FAIL', 'reason': 'No permission on this VM'}

  # If not an admin, force a machine that we choose.
  # We'll try and pick a machine that:
  #   1. Has enough free memory to support this VM
  #   2. Has the most free memory of all the machines
  if (info['admin'] != 1 or machine == ''):
    #machine = 'clusterfuck'
    all_machines = list_all()
    most_free = 0
    for m in all_machines:
      # The machine needs to be responding & up for it to be useful to us
      if (all_machines[m]['responding'] == 1 and all_machines[m]['up'] == 1):
        # Check if this machine has enough free memory and if it has the MOST free memory we've seen
        free_mem = int(all_machines[m]['mem_free'])/1024/1024
        if (free_mem > int(row[3]) and free_mem > most_free):
          most_free = free_mem
          machine = m
    # We didn't seem to find a machine with space available. OH SHIT.
    if machine == '':
      return {'status': 'FAIL', 'reason': 'No space avilable on host machines'}

  xenapi = get_api(machine)

  vmid = row[0]
  vmname = row[1]
  vmmac = row[2]
  vmmem = row[3]
  vmkernel = row[4]
  vmkernelargs = row[5]

  vm_ref = xenapi.VM.create({
    'name_label': vmname,
    'memory_static_max': vmmem * 1024 * 1024,
    'memory_dynamic_max': vmmem * 1024 * 1024,
    'memory_static_min': vmmem * 1024 * 1024,
    'memory_dynamic_min': vmmem * 1024 * 1024,
    'PV_kernel': '/boot/' + vmkernel,
    'PV_args': vmkernelargs,
    'platform': {},
    'actions_after_shutdown': 'destroy'
    })

  xenapi.VIF.create({
    'device': 'eth0',
    'VM': vm_ref,
    'MAC': vmmac
    })

  cur.execute("SELECT file, device, id FROM vmdisks WHERE vmmachineid = " + str(int(vmid)))
  rows = cur.fetchall()
  for row in rows:
    dfile = row[0]
    ddevice = row[1]
    did = row[2]

    # Check if we actually have a filename.
    # If we do, then loopback, otherwise we're going AoE baby
    if (dfile.find('.') == -1):
      location = 'phy:/dev/etherd/e' + str(did) + '.0'
      _start_vblade(str(did), vmname, dfile)
    else:
      location = 'tap:aio:/mnt/vms/domains/' + vmname + '/' + dfile

    disk_vdi = xenapi.VDI.create({
      'name_label': 'disk',
      'type': 'system',
      'SR': xenapi.SR.get_all()[0],
      'other_config': {'location': location}
      })
    disk_vbd = xenapi.VBD.create({
      'VM': vm_ref,
      'VDI': disk_vdi,
      'device': ddevice,
      'bootable': 1,
      'mode': 'RW',
      'type': 'Disk'
      })
  xenapi.VM.start(vm_ref, 0)

  # Update the database as to where we're putting this VM
  #cur.execute("UPDATE vmmachines SET pmmachine_id = " + MySQLdb.escape_string(pm_id) + " WHERE name = '" + MySQLdb.escape_string(name) + "'")
  
  #_release_db_conn()
  return {'status': 'OK'}

def destroy_vm(user, name):
  info = get_user_info(user)

  conn = _get_db_conn()
  cur = conn.cursor()

  cur.execute("SELECT owner, id FROM vmmachines WHERE name = '" + MySQLdb.escape_string(name) + "'")
  row = cur.fetchone()
  if row is None:
    return {'status': 'FAIL', 'reason': 'VM Machine does not exist'}

  if (row[0] != user and info['admin'] != 1):
    return {'status': 'FAIL', 'reason': 'No permission for this VM'}
    
  vmid = row[1]

  vminfo = find_vm(name)
  xenapi = get_api(vminfo['machine'])
  vm_ref = xenapi.VM.get_by_name_label(name)
  if vm_ref is None:
    return {'status': 'FAIL', 'reason':'No VM with that name'}

  xenapi.VM.hard_shutdown(vm_ref[0])
  xenapi.VM.destroy(vm_ref[0])
  
  cur.execute("SELECT id, file FROM vmdisks WHERE vmmachineid = " + str(vmid))
  rows = cur.fetchall()
  for row in rows:
      if (row[1].find('.') == -1):
        _stop_vblade(str(row[0]), name, row[1])
  
  #_release_db_conn()
  return {'status': 'OK'}

def get_base_images(user):
  info = get_user_info(user)

  conn = _get_db_conn()
  cur = conn.cursor()
  extra = ""
  if (info['admin'] != 1):
    extra = " WHERE available = 1"
  cur.execute("SELECT name, `desc` FROM images" + extra)
  rows = cur.fetchall()
  images = []
  for row in rows:
    images.append({'name': row[0], 'desc': row[1]})
  #_release_db_conn()
  return images

def check_name_avail(name):
  conn = _get_db_conn()
  cur = conn.cursor()
  cur.execute("SELECT name FROM vmmachines WHERE name = '" + MySQLdb.escape_string(name) + "'")
  row = cur.fetchone()
  if row is None:
    pg_conn = _get_pg_db_conn()
    pg_cur = pg_conn.cursor()
    pg_cur.execute("SELECT hostname FROM hosts WHERE hostname = '" + pgdb.escape_string(name) + "'")
    row = pg_cur.fetchone()
    if row is not None:
      # Found in PG Start DB, FAIL
      return {'status': 'OK', 'avail':0}
    #_release_db_conn()
    # NOT Found in Start OR vm list, OK
    return {'status': 'OK', 'avail': 1}
  #_release_db_conn()
  # Found Somewhere, FAIL
  return {'status': 'OK', 'avail': 0}

def boot_pm(user, name):
  info = get_user_info(user)
  if (info['admin'] != 1):
    return {'status': 'FAIL', 'reason': 'You do not have permission to boot this machine'}
    
  conn = _get_db_conn()
  cur = conn.cursor()
  cur.execute("SELECT mac FROM pmmachines WHERE name = '" + MySQLdb.escape_string(name) + "'")
  row = cur.fetchone()
  if row is None:
    #_release_db_conn()
    return {'status': 'FAIL', 'reason': 'Cannot lookup machine information.'}

  # Boot the machine
  _wake_on_lan(row[0])
  # cur.execute("UPDATE pmmachines SET up = 1 WHERE name = '" + MySQLdb.escape_string(name) + "'")
  
  #_release_db_conn()
  return {'status': 'OK'}

def shutdown_pm(user, name):
  info = get_user_info(user)
  if (info['admin'] != 1):
    return {'status': 'FAIL', 'reason': 'You do not have permission to shutdown this machine'}
  
  conn = _get_db_conn()
  cur = conn.cursor()
  cur.execute("UPDATE pmmachines SET up = 0 WHERE name = '" + MySQLdb.escape_string(name) + "'")
  
  # We need to not ask about confirming the host key... this isn't interactive.
  os.system( 'ssh -ostricthostkeychecking=no -oUserKnownHostsFile=/dev/null root@' + name + ' shutdown -h now' )
  return {'status': 'OK'}

def shutdown_vm(user, name):
  info = get_user_info(user)

  conn = _get_db_conn()
  cur = conn.cursor()

  cur.execute("SELECT owner, id FROM vmmachines WHERE name = '" + MySQLdb.escape_string(name) + "'")
  row = cur.fetchone()
  if row is None:
    return {'status': 'FAIL', 'reason': 'VM Machine does not exist'}

  if (row[0] != user and info['admin'] != 1):
    return {'status': 'FAIL', 'reason': 'No permission for this VM'}
    
  vmid = row[1]

  vminfo = find_vm(name)
  xenapi = get_api(vminfo['machine'])
  xenapi.VM.clean_shutdown(xenapi.VM.get_by_uuid(vminfo['uuid']))

  still_on = 1
  while (still_on):
    time.sleep(1)
    info = find_vm(name)
    if (info['power_state'] == 'Halted'):
      destroy_vm(user, name)
    if (info['power_state'] == 'Off'):
      still_on = 0
  
  #_release_db_conn()
  return {'status': 'OK'}

def list_all():
  #req.register_cleanup(_cleanup)
  #data = "{";
  datao = {}
  m = 0;
  machines = get_machines(False)
  for mach in machines:
    machine = mach['name'];
    #if (m):
      #data += ', ';
    #data += machine + ': [';
    datao[machine] = {'up': mach['up'], 'mem': int(mach['mem']), 'responding': 1}
    datao[machine]['vms'] = []
    m += 1

    if (mach['up'] == 1):
      xenapi = get_api(machine);
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
        datao[machine]['vms'].append({'name': ri['name_label'], 'uuid': ri['uuid'], 'mem_static_max': ri['memory_static_max'], 'power_state': ri['power_state']})
        datao[machine]['mem_free'] = datao[machine]['mem_free'] - int(ri['memory_static_max'])
        i += 1;
    #data += ']';
  #data += "}";
  #_release_db_conn()
  return datao
