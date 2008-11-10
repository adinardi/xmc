var IN_DRAG_VM = false;
var CURRENT_OVER_PM = null;

function go_go_gadget_loader() {
  go_go_load_data();
}

function go_go_load_data() {
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
    pm_div.style.height = '75px';
    container.appendChild(pm_div);

    // Make PM Block
    var pm_block = get_div();
    pm_block.style.width = '73px';
    pm_block.style.height = '73px';
    pm_block.innerHTML = pm;
    pm_block.style.cssFloat = 'left';
    pm_block.style.border = '1px dashed purple';
    pm_div.appendChild(pm_block);

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

    for (var iter = 0, vm; vm = data[pm][iter]; iter++) {
      // Make VM Block
      var vm_block = get_div();
      vm_block.style.width = '73px';
      vm_block.style.height = '73px';
      vm_block.style.cssFloat = 'left';
      vm_block.innerHTML = vm.name;
      vm_block.style.border = '1px solid black';
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
