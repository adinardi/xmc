var CURRENT_USER_INFO = {};
var STATUS_BOX_TIMEOUT = null;

function set_load_indicator(load) {
  set_status_box({msg: load});
}

/**
 * @param {string} msg
 * @param {number} time (Optional) Time before disapearing. 
 */
function set_status_box(args) {
  if (STATUS_BOX_TIMEOUT) {
    clearTimeout(STATUS_BOX_TIMEOUT);
    STATUS_BOX_TIMEOUT = null;
  }

  var load_indicator = document.getElementById('status_box');
  if (args.msg && args.msg != '') {
    load_indicator.style.display = '';
  } else {
    load_indicator.style.display = 'none';
  }
  load_indicator.innerHTML = args.msg;

  if (args.time) {
    STATUS_BOX_TIMEOUT = setTimeout(
      function() {
        set_status_box({msg: null});
      },
      args.time
      );
  }
}

function get_div() {
  return document.createElement('div');
}

/**
 * Function to load user info. 
 * @param {boolean} createInfo True to load full info with allocated VMS. Std info otherwise.
 */
function load_user_info(args) {
  var url = 'check.py/get_user_info';
  if (args && args.createInfo) {
    url = 'check.py/get_create_user_info';
  }

  var r = new thetr.Request({
    url: url,
    handler: load_user_info_handler
    });
  r.send();
}

function load_user_info_handler(args) {
  var data = eval( "(" + args.request.data + ")" );
  CURRENT_USER_INFO.user = data.user;
  CURRENT_USER_INFO.allocvms = data.allocvms;
  if (CURRENT_USER_INFO.onloaded) {
    CURRENT_USER_INFO.onloaded();
  }
}

function load_last_refresh_time() {
    var url = 'check.py/get_last_sync_time';
    var r = new thetr.Request({
        url: url,
        handler: load_last_refresh_time_handler
    });
    r.send();
}

function load_last_refresh_time_handler(args) {
    var data = eval( "(" + args.request.data + ")" );
    document.getElementById('last_refresh_time').innerHTML = data.last_sync_time;
}