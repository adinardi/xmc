from xen.xm.XenAPI import Session
from mod_python import apache
from mod_python import Session as MPSession
import MySQLdb
import time

machines = [ 'fuck', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '16', 'tp' ];

def handle_req():
  return apache.OK

def _get_username(req):
  pw = req.get_basic_auth_pw();
  return req.user;

def _is_admin(req):
  pw = req.get_basic_auth_pw();
  u = req.user;
  conn = _get_db_conn();
  cur = conn.cursor();
  cur.execute("SELECT admin FROM users WHERE user='" + u + "'");
  row = cur.fetchone();
  if (row == None):
    return False
  if (row[0] == 1):
    return True;
  return False;

def _get_db_conn():
  conn = MySQLdb.connect(host='db.csh.rit.edu', user='xen', passwd='tFQNBKB,JzGxESLm', db='xen')
  return conn

def _get_api(machine):
  session=Session('http://' + machine + ':9363');
  try:
    session.login_with_password('','');
    xenapi = session.xenapi;
  except:
    xenapi = None;
  return xenapi;

def list_all(req):
  data = "{";
  m = 0;
  for machine in machines:
    machine = 'cluster' + machine;
    xenapi = _get_api(machine);
    if (xenapi is None):
      continue;
    records=xenapi.VM.get_all_records();
    if (m):
      data += ', ';
    data += machine + ': [';
    i = 0;
    for item in records:
      if (records[item]['name_label'] != 'Domain-0'):
        if (i):
          data += ", ";
        data += "{name:'" + records[item]['name_label'] + "', uuid:'" + records[item]['uuid'] + "', mem_static_max:'" + records[item]['memory_static_max'] + "'}";
        i += 1;
    data += ']';
    m += 1
  data += "}";
  return data;

def _find_vm(name):
  for machine in machines:
    machine = 'cluster' + machine
    xenapi = _get_api(machine);
    if (xenapi is None):
      continue;
    records = xenapi.VM.get_by_name_label(name)
    if len(records) > 0:
      record = xenapi.VM.get_record(records[0]);
      ps = record['power_state']
      return {'found': 1, 'power_state': ps, 'machine': machine, 'uuid': record['uuid']}
  return {'found': 0, 'power_state': 'Off'}

def migrate_live(req, frommachine, machineid, tomachine):
  if (not _is_admin(req)):
    return "{}";
  xenapi = _get_api(frommachine);
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

def _get_user_info(user):
  conn = _get_db_conn();
  cur = conn.cursor();
  cur.execute("SELECT admin FROM users WHERE user='" + MySQLdb.escape_string(user) + "'");
  res = cur.fetchone()
  if (res == None):
    return None
  info = {'admin': res[0], 'username': user}
  return info

def get_user_info(req):
  user = _get_username(req);
  info = _get_user_info(user);
  return {'user': info};

def get_create_user_info(req):
  user = _get_username(req);
  info = _get_user_info(user);
  allocvms = _get_unused_vms(user);
  all_info = {'user': info, 'allocvms': allocvms};
  return all_info;

def _get_unused_vms(user):
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

def create_vm(req, hname, dsize, ssize, imagename, mac, allocid, mem, owner):
  user = _get_user_info(_get_username(req));
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
    return "{status: 'FAIL', reason: 'Not authorized to create new VM'}"

  # Check that the base image name is legitimate
  cur.execute("SELECT name FROM images WHERE name = '" + MySQLdb.escape_string(imagename) + "'")
  row = cur.fetchall()
  if (row is None):
    return {'status': 'OK', 'reason': 'image name is not valid'}

  # If we're using a pre-allocated VM, make sure un-changeable settings aren't changed.
  if (usingPrealloc == 1 and ((amac != None and amac != mac) or (adsize != None and int(adsize) != int(dsize)) or (assize != None and int(assize) != int(ssize)) or (amem != None and int(amem) != int(mem)) or (aowner != None and aowner != owner))):
    return "{status: 'FAIL', reason: 'Locked attributes do not match amac:" + str(amac) + " adsize:" + str(adsize) + " assize:" + str(assize) + " amem:" + str(amem) + " aowner:" + str(aowner) + "'}"

  # ADD MYSQL DB WRITE HERE.
  cur.execute("INSERT INTO vmmachines (name, owner, mac, disk, mem, swap) VALUES('" + MySQLdb.escape_string(hname) + "', '" + MySQLdb.escape_string(owner) + "', '" + MySQLdb.escape_string(mac) + "', '" + MySQLdb.escape_string(dsize) + "', '" + MySQLdb.escape_string(mem) + "', '" + MySQLdb.escape_string(ssize) + "')");
  vmid = conn.insert_id()
  cur.execute("INSERT INTO vmdisks (file, device, vmmachineid) VALUES ('disk.img', 'xvda2', " + str(vmid) + ")")
  cur.execute("INSERT INTO vmdisks (file, device, vmmachineid) VALUES ('swap.img', 'xvda1', " + str(vmid) + ")")
  if (usingPrealloc == 1):
    cur.execute("DELETE FROM allocvmmachines WHERE id = " + str(int(allocid)))

  # Write Config
  FILE = open('/mnt/vms/configs/new/' + hname + '.defs', "w");
  FILE.write("-n " + hname + " -d " + dsize + " -s " + ssize + " -b " + imagename + " -m " + mac + " -e " + mem);
  FILE.close();
  return "{status: 'OK'}"

def list_my_vms(req, all=0):
  user = _get_username(req)
  info = _get_user_info(user)
  doall = 0
  if (info['admin'] == 1 and int(all) == 1):
    doall = 1
  conn = _get_db_conn()
  cur = conn.cursor()
  extra = ''
  if (doall == 0):
    extra = " WHERE owner='" + user + "'"
  cur.execute("SELECT id, name, owner, mac, disk, mem, swap, enabled FROM vmmachines" + extra)
  rows = cur.fetchall()
  vms = []
  for row in rows:
    vms.append({'id': int(row[0]), 'name': row[1], 'owner': row[2], 'mac': row[3], 'disk': int(row[4]), 'mem': int(row[5]), 'swap': int(row[6]), 'enabled': int(row[7]), 'online': _find_vm(row[1])})
  return vms

def boot_vm(req, name, machine='clusterfuck'):
  user = _get_username(req)
  info = _get_user_info(user)

  xenapi = _get_api(machine)
  conn = _get_db_conn()
  cur = conn.cursor()
  cur.execute("SELECT id, name, mac, mem, kernel, kernel_args, owner FROM vmmachines WHERE name = '" + MySQLdb.escape_string(name) + "'")
  row = cur.fetchone()
  if row is None:
    return {'status': 'FAIL', 'reason': 'VM does not exist'}

  if (row[6] != user and info['admin'] != 1):
    return {'status': 'FAIL', 'reason': 'No permission on this VM'}

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

  cur.execute("SELECT file, device FROM vmdisks WHERE vmmachineid = " + str(int(vmid)))
  rows = cur.fetchall()
  for row in rows:
    dfile = row[0]
    ddevice = row[1]

    disk_vdi = xenapi.VDI.create({
      'name_label': 'disk',
      'type': 'system',
      'SR': xenapi.SR.get_all()[0],
      'other_config': {'location': 'tap:aio:/mnt/vms/domains/' + vmname + '/' + dfile}
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
  return {'status': 'OK'}

def shutdown_vm(req, name):
  user = _get_username(req)
  info = _get_user_info(user)

  conn = _get_db_conn()
  cur = conn.cursor()

  cur.execute("SELECT owner FROM vmmachines WHERE name = '" + MySQLdb.escape_string(name) + "'")
  row = cur.fetchone()
  if row is None:
    return {'status': 'FAIL', 'reason': 'VM Machine does not exist'}

  if (row[0] != user and info['admin'] != 1):
    return {'status': 'FAIL', 'reason': 'No permission for this VM'}

  vminfo = _find_vm(name)
  xenapi = _get_api(vminfo['machine'])
  xenapi.VM.clean_shutdown(xenapi.VM.get_by_uuid(vminfo['uuid']))

  still_on = 1
  while (still_on):
    time.sleep(1)
    info = _find_vm(name)
    if (info['power_state'] == 'Halted'):
      destroy_vm(req, name)
    if (info['power_state'] == 'Off'):
      still_on = 0
  
  return {'status': 'OK'}

def destroy_vm(req, name):
  user = _get_username(req)
  info = _get_user_info(user)

  conn = _get_db_conn()
  cur = conn.cursor()

  cur.execute("SELECT owner FROM vmmachines WHERE name = '" + MySQLdb.escape_string(name) + "'")
  row = cur.fetchone()
  if row is None:
    return {'status': 'FAIL', 'reason': 'VM Machine does not exist'}

  if (row[0] != user and info['admin'] != 1):
    return {'status': 'FAIL', 'reason': 'No permission for this VM'}

  vminfo = _find_vm(name)
  xenapi = _get_api(vminfo['machine'])
  vm_ref = xenapi.VM.get_by_name_label(name)
  if vm_ref is None:
    return {'status': 'FAIL', 'reason':'No VM with that name'}

  xenapi.VM.destroy(vm_ref[0])
  return {'status': 'OK'}

def get_base_images(req):
  user = _get_username(req)
  info = _get_user_info(user)

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
  return images

def check_name_avail(req, name):
  conn = _get_db_conn()
  cur = conn.cursor()
  cur.execute("SELECT name FROM vmmachines WHERE name = '" + MySQLdb.escape_string(name) + "'")
  row = cur.fetchone()
  if row is None:
    return {'status': 'OK', 'avail': 1}
  return {'status': 'OK', 'avail': 0}
