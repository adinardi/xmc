function go_go_gadget_loader() {
  load_vm_list({all: false});
}

function load_vm_list(args) {
  var r = new thetr.Request({
    url: 'check.py/list_my_vms' + (args.all ? '?all=1' : ''),
    handler: handle_list_my_vms
    });
  r.send();
}

function handle_list_my_vms(args) {
  var data = eval("(" + args.request.data + ")");
  console.log(data);

  var cont = document.getElementById('vmcontainer');
  cont.innerHTML = '';
  for (var iter = 0, vm; vm = data[iter]; iter++) {
    var d = get_div();
    d.className = 'vmbox ' + (vm.online ? "vmon" : "vmoff");
    var content = [];
    content.push(vm.name);
    content.push(vm.owner);
    content.push('Mem: ' + vm.mem);
    content.push('Disk: ' + vm.disk);
    content.push('Swap: ' + vm.swap);
    d.innerHTML = content.join("<br>");
    cont.appendChild(d);
  }
}


