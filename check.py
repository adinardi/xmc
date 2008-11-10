from xen.xm.XenAPI import Session
from mod_python import apache
from mod_python import Session as MPSession
import MySQLdb

machines = [ 'fuck', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14' ];

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
      return 1
  return 0

def migrate_live(req, frommachine, machineid, tomachine):
  if (not _is_admin(req)):
    return "{}";
  xenapi = _get_api(frommachine);
  xenapi.VM.migrate(machineid, tomachine, 1, {});

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
  return info;

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

  # If we're using a pre-allocated VM, make sure un-changeable settings aren't changed.
  if (usingPrealloc == 1 and ((amac != None and amac != mac) or (adsize != None and int(adsize) != int(dsize)) or (assize != None and int(assize) != int(ssize)) or (amem != None and int(amem) != int(mem)) or (aowner != None and aowner != owner))):
    return "{status: 'FAIL', reason: 'Locked attributes do not match amac:" + str(amac) + " adsize:" + str(adsize) + " assize:" + str(assize) + " amem:" + str(amem) + " aowner:" + str(aowner) + "'}"

  # ADD MYSQL DB WRITE HERE.
  cur.execute("INSERT INTO vmmachines (name, owner, mac, disk, mem, swap) VALUES('" + MySQLdb.escape_string(hname) + "', '" + MySQLdb.escape_string(owner) + "', '" + MySQLdb.escape_string(mac) + "', '" + MySQLdb.escape_string(dsize) + "', '" + MySQLdb.escape_string(mem) + "', '" + MySQLdb.escape_string(ssize) + "')");
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
  cur.execute("SELECT id, name, owner, mac, disk, mem, swap FROM vmmachines" + extra)
  rows = cur.fetchall()
  vms = []
  for row in rows:
    vms.append({'id': int(row[0]), 'name': row[1], 'owner': row[2], 'mac': row[3], 'disk': int(row[4]), 'mem': int(row[5]), 'swap': int(row[6]), 'online': _find_vm(row[1])})
  return vms

def boot_vm(req, name):
  xenapi = _get_api('clusterfuck')
#  xenapi.VM.create({
 #   'name_label': 'test1',
  #  'memory_static_max': 128,
  #  'PV_kernel': '/boot/vmlinuz',
  #  '
