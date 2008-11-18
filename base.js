var CURRENT_USER_INFO = {};

function set_load_indicator(load) {
  var load_indicator = document.getElementById('load_indicator');
  load_indicator.innerHTML = load;
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
