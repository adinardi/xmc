var LAST_LOADED_VM_LIST_ARGS = null;

function go_go_gadget_loader() {
  thetr.event.listen({
    on: CURRENT_USER_INFO,
    action: 'loaded',
    handler: user_info_loaded
    });
  load_user_info({createInfo: false});
  load_vm_list({all: false});
}

function load_vm_list(args) {
  LAST_LOADED_VM_LIST_ARGS = args;
  var r = new thetr.Request({
    url: 'check.py/list_my_vms' + (args.all ? '?all=1' : ''),
    handler: handle_list_my_vms
    });
  set_status_box({ msg: 'Loading VM List...' });
  r.send();
}

function user_info_loaded(args) {
  thetr.event.unlisten({
    on: CURRENT_USER_INFO,
    action: 'loaded',
    handler: user_info_loaded
    });
  var adminAll = document.getElementById('adminall');
  if (CURRENT_USER_INFO.user.admin == 1) {
    adminAll.style.display = '';
  }
}

function handle_list_my_vms(args) {
  var data = eval("(" + args.request.data + ")");

  var cont = document.getElementById('vmcontainer');
  cont.innerHTML = '';
  for (var iter = 0, vm; vm = data[iter]; iter++) {
    var d = get_div();
    d.className = 'vmbox ' + (vm.online.power_state == 'Running' ? "vmon" : "vmoff");
    var content = [];
    content.push(vm.name);
    content.push(vm.owner);
    content.push('Mem: ' + vm.mem);
    content.push('Disk: ' + vm.disk);
    content.push('Swap: ' + vm.swap);
    content.push('Mac: ' + vm.mac);
    content.push(vm.online.power_state);
    if (vm.enabled == 1) {
      if (vm.online.power_state == 'Running') {
        content.push('<button onclick="do_shutdown({name:\'' + vm.name + '\'})">Shutdown</button>');
      } else if (vm.online.power_state == 'Halted') {
        content.push('<button onclick="do_destroy({name:\'' + vm.name + '\'})">Destroy</button>');
      } else if (vm.online.power_state == 'Off') {
        content.push('<button onclick="do_boot({name:\'' + vm.name + '\'})">Boot</button>');
      }
    } else {
      content.push('<font color=red><b>Creating...</b></font>');
      content.push('Wait to boot...');
    }
    d.innerHTML = content.join("<br>");
    cont.appendChild(d);
  }
  set_status_box({ msg: 'Loaded VM List', time: 500});
}

function do_shutdown(args) {
  var check = confirm("Are you sure you want to shutdown " + args.name + "?");
  if (!check) {
    return;
  }
  var r = new thetr.Request({
    url: 'check.py/shutdown_vm?name=' + args.name,
    handler: handle_shutdown
    });
  set_status_box({ msg: 'Shutting down ' + args.name + '...' });
  r.send();
}

function handle_shutdown(args) {
  set_status_box({ msg: 'Shutdown successful', time: 500 });
  load_vm_list(LAST_LOADED_VM_LIST_ARGS);
}

function do_destroy(args) {
  var r = new thetr.Request({
    url: 'check.py/destroy_vm?name=' + args.name,
    handler: handle_destroy
    });
  r.send();
}

function handle_destroy(args) {

}

function do_boot(args) {
  var check = confirm("Are you sure you want to boot " + args.name + "?");
  if (!check) {
    return;
  }
  var r = new thetr.Request({
    url: 'check.py/boot_vm?name=' + args.name,
    handler: handle_boot
    });
  set_status_box({ msg: 'Booting ' + args.name + '...' });
  r.send();
}

function handle_boot(args) {
  set_status_box({ msg: 'Boot successful', time: 500 });
  load_vm_list(LAST_LOADED_VM_LIST_ARGS);
}
