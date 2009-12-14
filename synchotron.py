import xmclib

#print datao

dbconn = xmclib._get_db_conn()
cur = dbconn.cursor()

# Clear the current locations of EVERYTHING!
cur.execute("UPDATE vmmachines SET pmmachine_id=NULL, last_uuid=NULL, power_state=NULL")
cur.execute("UPDATE pmmachines SET up = 1");

data = xmclib.list_all()

for machine in data:
  if (data[machine]['responding'] == 0):
    print 'machine ' + machine + 'appears down'
    cur.execute("UPDATE pmmachines SET up = 0 WHERE name = '" + machine + "'");
  vms = data[machine]['vms']
  for vm in vms:
    # print vm
    print 'adding ' + vm['name'] + ' to ' + machine + '\n'
    cur.execute("UPDATE vmmachines SET pmmachine_id=(SELECT id FROM pmmachines WHERE name='" + machine + "' LIMIT 1), last_uuid='" + vm['uuid'] + "', power_state='" + vm['power_state'] + "' WHERE name='" + vm['name'] + "'")
  # print vms
    
cur.execute("UPDATE meta SET last_refresh = now()")
    
xmclib.cleanup()
