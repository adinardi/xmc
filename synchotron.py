import xmclib

data = xmclib.list_all()

#print datao

dbconn = xmclib._get_db_conn()
cur = dbconn.cursor()

# Clear the current locations of EVERYTHING!
cur.execute("UPDATE vmmachines SET pmmachine_id=NULL, last_uuid=NULL, power_state=NULL")

for machine in data:
  vms = data[machine]['vms']
  for vm in vms:
    # print vm
    print 'adding ' + vm['name'] + ' to ' + machine + '\n'
    cur.execute("UPDATE vmmachines SET pmmachine_id=(SELECT id FROM pmmachines WHERE name='" + machine + "' LIMIT 1), last_uuid='" + vm['uuid'] + "', power_state='" + vm['power_state'] + "' WHERE name='" + vm['name'] + "'")
  # print vms
    
    
    
xmclib.cleanup()
