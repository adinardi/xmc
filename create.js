var IN_DRAG_VM = false;
var CURRENT_OVER_PM = null;
var CURRENT_USER_INFO = null;

function go_go_gadget_loader() {
  go_go_load_data();
}

function go_go_load_data() {
  var r = new thetr.Request({
    url: 'check.py/get_create_user_info',
    handler: userInfoHandler
    });
  var container = document.getElementById('container');
  set_load_indicator('Loading User Data...');
  r.send();
}

function userInfoHandler(args) {
  var data = eval( "(" + args.request.data + ")" );
  set_load_indicator('');
  //console.log(data);
  document.getElementById('username').innerHTML = data.user.username + (data.user.admin == 1 ? " (admin)" : "");
  document.getElementById('avail_vms').innerHTML = data.allocvms.length;
  CURRENT_USER_INFO = data;
  load_allocvms();
}

function load_allocvms() {
  var data = CURRENT_USER_INFO.allocvms; 
  var tbody = document.getElementById('allocvms_tbody');
  tbody.innerHTML = '';
  for (var iter = 0, vm; vm = data[iter]; iter++) {
    var tr = document.createElement('tr');
    var td = document.createElement('td');
    td.innerHTML = vm.disk;
    tr.appendChild(td);

    td = document.createElement('td');
    td.innerHTML = vm.swap;
    tr.appendChild(td);

    td = document.createElement('td');
    td.innerHTML = vm.mem;
    tr.appendChild(td);

    td = document.createElement('td');
    td.innerHTML = vm.mac;
    tr.appendChild(td);
    tr.style.cursor = 'pointer';
    tbody.appendChild(tr);

    thetr.event.listen({
      on: tr,
      action: 'click',
      handler: go_create_alloc_vm,
      args: {
        specs: vm
        }
      });

    thetr.event.listen({
      on: tr,
      action: 'mouseover',
      handler: hover_over_tr,
      args: {
        tr: tr
        }
      });
    thetr.event.listen({
      on: tr,
      action: 'mouseout',
      handler: hover_out_tr,
      args: {
        tr: tr
        }
      });
  }

  if (CURRENT_USER_INFO.user.admin == 1) {
    var tr = document.createElement('tr');
    var td = document.createElement('td');
    td.innerHTML = 'New (admin create freeform VM)';
    td.colSpan = 4;
    tr.appendChild(td);
    tr.style.cursor = 'pointer';
    tbody.appendChild(tr);

    thetr.event.listen({
      on: tr,
      action: 'click',
      handler: go_create_alloc_vm,
      args: {
        specs: {},
        create_new: true
        }
      });

    thetr.event.listen({
      on: tr,
      action: 'mouseover',
      handler: hover_over_tr,
      args: {
        tr: tr
        }
      });

    thetr.event.listen({
      on: tr,
      action: 'mouseout',
      handler: hover_out_tr,
      args: {
        tr: tr
        }
      });
  }
}

function hover_out_tr(args) {
  args.tr.style.backgroundColor = '';
  args.tr.style.color = '';
}

function hover_over_tr(args) {
  args.tr.style.backgroundColor = 'grey';
  args.tr.style.color = 'white';
}

function go_create_alloc_vm(args) {
  var hname = document.getElementById('hname');
  var dsize = document.getElementById('dsize');
  var ssize = document.getElementById('ssize');
  var imagename = document.getElementById('imagename');
  var mac_address = document.getElementById('mac_address');
  var mem = document.getElementById('mem');
  var owner = document.getElementById('owner');
/*
  if (args.create_new) {

  } else {*/
    var specs = args.specs;
    hname.value = '';
    dsize.value = (specs.disk ? specs.disk : '');
    dsize.disabled = specs.disk;
    ssize.value = (specs.swap ? specs.swap : '');
    ssize.disabled = specs.swap;
    mac_address.value = (specs.mac ? specs.mac : '');
    mac_address.disabled = specs.mac;
    mem.value = (specs.mem ? specs.mem : '');
    mem.disabled = specs.mem;
    owner.value = (specs.owner ? specs.owner : '');
    owner.disabled = (specs.owner);
    imagename.value = '';
    CHOSEN_VM_SPEC = specs;
  //}
  
  document.getElementById('vmconfig').style.display = '';
}

function go_create_vm() {
  var hname = document.getElementById('hname').value;
  var dsize = document.getElementById('dsize').value;
  var ssize = document.getElementById('ssize').value;
  var imagename = document.getElementById('imagename').value;
  var mac_address = document.getElementById('mac_address').value;
  var mem = document.getElementById('mem').value;
  var owner = document.getElementById('owner').value;

  if (hname == '' || dsize == '' || ssize == '' || imagename == '' || mac_address == '' || mem == '' || owner == '') {
    alert('All fields need to be completed');
    return;
  }

  var postArgs = new thetr.Request.ArgGen({
    hname: hname,
    mac: mac_address,
    imagename: imagename,
    dsize: dsize,
    ssize: ssize,
    mem: mem,
    owner: owner,
    allocid: (CHOSEN_VM_SPEC.id ? CHOSEN_VM_SPEC.id : 'new')
    });
  var r = new thetr.Request({
    url: 'check.py/create_vm',
    handler: go_create_vm_handler,
    post: postArgs.toString()
    });
  set_load_indicator('Creating...');
  r.send(); 
  document.getElementById('vmconfig').style.display = 'none';
}

function go_create_vm_handler(args) {
  var data = eval("(" + args.request.data + ")");
  if (data.status == 'FAIL') {
    alert('Failed to create VM:' + data.reason);
  }
  document.getElementById('vmconfigStatus').innerHTML = 'Create OK';
  setTimeout(function() {
    document.getElementById('vmconfigStatus').innerHTML = '';
    }, 6000);
  document.getElementById('hname').value = '';
  document.getElementById('hname').disabled = '';
  document.getElementById('dsize').value = '';
  document.getElementById('dsize').disabled = '';
  document.getElementById('ssize').value = '';
  document.getElementById('ssize').disabled = '';
  document.getElementById('imagename').value = '';
  document.getElementById('imagename').disabled = '';
  document.getElementById('mac_address').value = '';
  document.getElementById('mac_address').disabled = '';
  document.getElementById('mem').value = '';
  document.getElementById('mem').disabled = '';
  document.getElementById('owner').value = '';
  document.getElementById('owner').disabled = '';

  go_go_load_data();
}

