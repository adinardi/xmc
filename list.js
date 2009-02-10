var IN_DRAG_VM = false;
var CURRENT_OVER_PM = null;
var LAST_PM_POPUP = null;

function go_go_gadget_loader() {
  go_go_load_data();
}

function go_go_load_data() {
  hide_pm_popup(null);
  
  var r = new thetr.Request({
    url: 'check.py/list_all',
    handler: listDataHandler
    });
  //var vmlist = document.getElementById('vmlist-body');
  //vmlist.innerHTML = '';
  var container = document.getElementById('container');
  container.innerHTML = '';
  set_load_indicator('Loading Data...');
  r.send();
}

function listDataHandler(args) {
  var vmlist = document.getElementById('vmlist-body');
  var data = eval('(' + args.request.data + ')');
  vmlist.innerHTML = '';
  var pmList = [];
  for (pm in data) {
    pmList.push(pm);
  }
  var container = document.getElementById('container');
  container.innerHTML = '';
  // Iterate over all PMs, pm = string, 'clusterfuck', 'cluster2', etc.
  for (pm in data) {
    // Make PM Row
    var pm_div = get_div();
    pm_div.style.height = '35px';
    container.appendChild(pm_div);

    // Make PM Block
    var pm_block = get_div();
    pm_block.style.width = '77px';
    pm_block.style.height = '33px';
    var mem_free = data[pm]['mem_free'];
    if (typeof mem_free != 'undefined') {
      mem_free = " (" + Math.ceil(parseInt(mem_free)/1024/1024) + ")"
    } else {
      mem_free = "";
    }
    pm_block.innerHTML = pm + '<br>' + data[pm]['mem'] + mem_free;
    pm_block.style.cssFloat = 'left';
    pm_block.style.border = '1px dashed purple';
    pm_div.appendChild(pm_block);

    if (data[pm]['up'] == 0) {
      pm_block.style.backgroundColor = 'grey';
    } else {
      thetr.event.listen({
        on: pm_block,
        action: 'mouseover',
        handler: handle_pm_mouse_over,
        args: {
          over: pm,
          element: pm_block
          }
        });
      thetr.event.listen({
        on: pm_block,
        action: 'mouseout',
        handler: handle_pm_mouse_out,
        args: {
          over: pm,
          element: pm_block
          }
        });
    }
    thetr.event.listen({
      on: pm_block,
      action: 'click',
      handler: handle_pm_mouse_click,
      args: {
        clicked: data[pm],
        pm_name: pm,
        element: pm_block
      }
    });

    for (var iter = 0, vm; vm = data[pm]['vms'][iter]; iter++) {
      // Make VM Block
      var vm_block = get_div();
      vm_block.style.width = '77px';
      vm_block.style.height = '33px';
      vm_block.style.cssFloat = 'left';
      // Mem is in bytes, mem/1024/1024 = MB
      vm_block.innerHTML = vm.name + "<br>" + (parseInt(vm.mem_static_max)/1048576);
      vm_block.style.border = '1px solid black';
      vm_block.style.cursor = 'move';
      pm_div.appendChild(vm_block);

      thetr.event.listen({
        on: vm_block,
        action: 'mousedown',
        handler: handle_mouse_down_vm,
        args: {
          uuid: vm.uuid,
          from: pm
          }
        });
    }
  }
  set_load_indicator('');
}

function handle_mouse_down_vm(args) {
  var be = args.browserEvent;
  var startX = be.clientX;
  var startY = be.clientY;
  document.body.onselectstart = function() { return false; }
  thetr.event.listen({
    on: document,
    action: 'mouseup',
    handler: handle_doc_mouse_up,
    args: {
      startX: startX,
      startY: startY,
      uuid: args.uuid,
      from: args.from
      }
    });
  IN_DRAG_VM = true;
}

function handle_doc_mouse_up(args) {
  thetr.event.unlisten({
    on: document,
    action: 'mouseup',
    handler: handle_doc_mouse_up
    });
  document.body.onselectstart = null;
  IN_DRAG_VM = false;
  var be = args.browserEvent;
  var eX = be.clientX;
  var eY = be.clientY;
  var sX = args.startX;
  var sY = args.startY;
  if (sX + 10 > eX &&
      sY + 10 > eY &&
      sX - 10 < eX &&
      sY - 10 < eY) {
    handle_mouse_click_vm(args);
  } else {
    if (CURRENT_OVER_PM != null) {
      migrate_change({
        from: args.from,
        to: CURRENT_OVER_PM,
        uuid: args.uuid
        });
    } else {
      console.log('CURRENT PM NOT SET');
    }
  }
}

function handle_pm_mouse_over(args) {
  if (IN_DRAG_VM) {
    console.log('mouse over');
    CURRENT_OVER_PM = args.over;
    args.element.style.backgroundColor = 'green';
  }
}

function handle_pm_mouse_out(args) {
  if (IN_DRAG_VM && CURRENT_OVER_PM == args.over) {
    
    CURRENT_OVER_PM = null;
    args.element.style.backgroundColor = '';
  }
}

function migrate_change(args) {
  //alert('move uuid:' + args.uuid + ' to '  + args.migrate_select.value + ' from ' + args.migrate_from);
  var postArgs = new thetr.Request.ArgGen({
    frommachine: args.from,
    tomachine: args.to,
    machineid: args.uuid
    });
  var r = new thetr.Request({
    url: 'check.py/migrate_live',
    post: postArgs.toString(),
    handler: migrate_done
    });
  set_load_indicator('Migrating...');
  r.send();
}

function migrate_done(args) {
  //alert('done migrating...');
  set_load_indicator('');
  go_go_load_data(); 
}

function handle_pm_mouse_click(args) {
  show_pm_popup(args);
}

function show_pm_popup(args) {
  hide_pm_popup(null);
  
  var pm = args.clicked;
  var pm_block = args.element;
  var pm_name = args.pm_name;
  
  var top = pm_block.offsetTop + 10;
  var left = pm_block.offsetLeft + 10;
  
  var container = document.createElement('div');
  container.style.position = 'absolute';
  container.style.left = left;
  container.style.top = top;
  container.style.border = '2px solid orange';
  container.style.backgroundColor = 'white';
  
  var html = [];
  html.push(pm_name);
  
  if (pm['up'] == 0) {
    html.push('<button name="boot_pm" onclick="boot_pm({pm: \'' + pm_name + '\'})">Boot</button>');
  } else {
    html.push('<button name="shutdown_pm" onclick="shutdown_pm({pm: \'' + pm_name + '\'})">Shutdown</button>'); 
  }
  
  container.innerHTML = html.join('<br>');
  
  LAST_PM_POPUP = container;
  document.body.appendChild(container);
  thetr.event.listen({
    on:document.body,
    action: 'mousedown',
    handler: hide_pm_popup
  });
}

function hide_pm_popup(args) {
  if (args && (
      args.browserEvent.target.name == 'boot_pm' ||
      args.browserEvent.target.name == 'shutdown_pm')) {
        return;
  }
  if (typeof LAST_PM_POPUP != 'undefined' && LAST_PM_POPUP != null) {
    document.body.removeChild(LAST_PM_POPUP);
    LAST_PM_POPUP = null;
  }
  
  thetr.event.unlisten({
    on: document.body,
    action: 'mousedown',
    handler: hide_pm_popup
    });
}

function boot_pm(args) {
  var pm = args.pm;
  
  var check = confirm("Are you sure you want to boot '" + pm + "'?");
  if (!check) {
    return;
  }
  
  var postArgs = new thetr.Request.ArgGen({
    name: pm
    });
  var r = new thetr.Request({
    url: 'check.py/boot_pm',
    post: postArgs.toString(),
    handler: boot_pm_done
    });
  set_load_indicator('Booting Phyical host "' + pm + '"...');
  r.send();
}

function boot_pm_done(args) {
  set_load_indicator('');
  go_go_load_data();
}

function shutdown_pm(args) {
  var pm = args.pm;
  
  var check = confirm("Are you sure you want to SHUTDOWN '" + pm + "'?\n\nALL VMs LEFT ON THE HOST WILL BE TERMINATED!");
  if (!check) {
    return;
  }
  
  var postArgs = new thetr.Request.ArgGen({
    name: pm
    });
  var r = new thetr.Request({
    url: 'check.py/shutdown_pm',
    post: postArgs.toString(),
    handler: shutdown_pm_done
    });
  set_load_indicator('Shutting down Phyical host "' + pm + '"...');
  r.send();
}

function shutdown_pm_done(args) {
  set_load_indicator('');
  go_go_load_data();
}